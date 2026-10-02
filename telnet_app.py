"""Small Telnet-style TCP gateway for period terminal clients.

Hardened for internet exposure:
  * MAX_SESSIONS caps concurrent connections (each one spawns a
    compuserve.py subprocess, so uncapped connections = trivial DoS).
  * MAX_SESSIONS_PER_IP caps concurrent connections from one address,
    so a single client can't crowd out everyone else.
  * IDLE_TIMEOUT disconnects clients that send nothing for a while,
    so abandoned connections can't accumulate forever.
  * MAX_BUFFERED_INPUT drops clients that stream bytes without ever
    sending a line terminator (unbounded input buffers = memory DoS).
"""

import asyncio
import logging
import os
import socket
import sys
import time
import uuid
from contextlib import suppress
from pathlib import Path

import cis_activity


BASE_DIR = Path(__file__).resolve().parent
MAX_LINE = 4096
# A client that never sends a line terminator (or never terminates a
# telnet subnegotiation) must not be able to grow the input buffers
# without bound. No legitimate terminal does this.
MAX_BUFFERED_INPUT = 65536
LOGGER = logging.getLogger("compuserve.telnet")

# Tunables (env-overridable).
MAX_SESSIONS = int(os.environ.get("CIS_TELNET_MAX_SESSIONS", "20"))
MAX_SESSIONS_PER_IP = int(os.environ.get("CIS_TELNET_MAX_SESSIONS_PER_IP", "3"))
IDLE_TIMEOUT = float(os.environ.get("CIS_TELNET_IDLE_TIMEOUT", "900"))  # seconds
# Opt-in per-session protocol trace for troubleshooting (CIS_TELNET_DEBUG=1).
# Logs raw client bytes, line endings, IAC, echo transitions, and markers.
# Password bytes are never logged (masked while echo is suppressed).
TELNET_DEBUG = os.environ.get("CIS_TELNET_DEBUG", "") == "1"

# Created in main() so it binds to the running loop.
SESSION_SLOTS = None

# client_ip -> active session count, for the per-IP cap.
IP_SESSIONS = {}


def strip_telnet_commands(data):
    """Remove telnet IAC negotiation sequences from a byte stream.

    Handles WILL/WONT/DO/DONT, subnegotiations (IAC SB ... IAC SE), and
    escaped IAC IAC. Returns (cleaned, leftover): any trailing incomplete
    sequence is returned as leftover so the caller can prepend it to the
    next chunk instead of mis-parsing it.
    """
    result = bytearray()
    index = 0
    end = len(data)
    while index < end:
        byte = data[index]
        if byte != 255:  # IAC
            result.append(byte)
            index += 1
            continue
        if index + 1 >= end:
            break  # incomplete sequence; wait for more data
        command = data[index + 1]
        if command == 255:  # IAC IAC: escaped literal 255
            result.append(255)
            index += 2
        elif command == 250:  # IAC SB: skip through IAC SE
            term = data.find(b"\xff\xf0", index + 2)
            if term == -1:
                break  # incomplete subnegotiation; wait for more data
            index = term + 2
        elif command in (251, 252, 253, 254):  # WILL/WONT/DO/DONT + option byte
            if index + 2 >= end:
                break  # option byte not here yet; wait for more data
            index += 3
        else:  # other two-byte commands (NOP, DM, BRK, IP, AO, AYT, EC, EL, GA, SE)
            index += 2
    return bytes(result), bytes(data[index:])


def split_telnet_line(buf):
    """Split the first telnet line off buf.

    Telnet clients end lines with CRLF, CR NUL, CR, or LF (RFC 854).
    A CR always terminates the line; a LF or NUL immediately following
    it is consumed as part of the same terminator. Callers pause briefly
    for a CRLF split across reads before calling, so a trailing CR here
    is a genuine bare CR (e.g. a C64 RETURN key) and ends the line at
    once instead of hanging until the next keypress.
    Returns (line, rest); line is None when no terminator is buffered yet.
    """
    for index, byte in enumerate(buf):
        if byte == 0x0D:  # CR
            if index + 1 < len(buf) and buf[index + 1] in (0x0A, 0x00):
                return bytes(buf[:index]), bytes(buf[index + 2:])
            return bytes(buf[:index]), bytes(buf[index + 1:])
        if byte == 0x0A:  # LF
            return bytes(buf[:index]), bytes(buf[index + 1:])
    return None, buf


def _debug_bytes(label, session_id, data, echo_state):
    """Log raw protocol bytes for troubleshooting (CIS_TELNET_DEBUG=1).

    Password bytes are never logged: once the terminal is selected and
    echo is suppressed, only the byte count is shown.
    """
    if not TELNET_DEBUG:
        return
    if echo_state.term_selected and not echo_state.enabled:
        LOGGER.info("telnet_debug session=%s %s <hidden %d bytes>",
                    session_id, label, len(data))
    else:
        LOGGER.info("telnet_debug session=%s %s hex=%s repr=%r",
                    session_id, label, data.hex(), data)


async def forward_telnet_input(reader, writer, process, session_id, peer,
                               echo_state=None):
    """Forward client keystrokes to the terminal subprocess, one line at a time.

    Negotiation bytes are stripped from the raw stream before line
    splitting, so they can never swallow the terminator of the user's
    first Enter keypress.

    A chunk ending in CR may be a CRLF/CR NUL split across reads
    (char-at-a-time clients); wait briefly for the rest before
    splitting, so a genuine bare CR (C64 RETURN key) still ends the
    line promptly instead of hanging until the next keypress.

    Keystrokes are echoed back (remote echo) unless echo_state says
    otherwise, so terminals without local echo can see what they type.

    Returns the reason input forwarding stopped: "idle_timeout",
    "client_closed", "input_flood", or "session_ended".
    """
    echo_state = echo_state or _EchoState()
    raw_buf = b""
    line_buf = b""
    while process.returncode is None:
        try:
            chunk = await asyncio.wait_for(reader.read(1024), timeout=IDLE_TIMEOUT)
        except asyncio.TimeoutError:
            LOGGER.info("terminal idle timeout session=%s client=%s", session_id, peer)
            with suppress(Exception):
                writer.write(b"\r\nIdle too long. Disconnecting. Goodbye!\r\n")
                await writer.drain()
            return "idle_timeout"
        if not chunk:
            return "client_closed"  # client disconnected
        _debug_bytes("recv", session_id, chunk, echo_state)
        if chunk.endswith(b"\r"):
            # Possible split CRLF/CR NUL: wait briefly for the rest.
            # A true bare CR completes on timeout.
            with suppress(asyncio.TimeoutError):
                extra = await asyncio.wait_for(reader.read(1024), timeout=0.1)
                if extra:
                    _debug_bytes("recv-extra", session_id, extra, echo_state)
                chunk += extra
        raw_buf += chunk
        cleaned, raw_buf = strip_telnet_commands(raw_buf)
        if cleaned != chunk:
            _debug_bytes("cleaned", session_id, cleaned, echo_state)
        if cleaned and echo_state.enabled:
            writer.write(_echo_bytes(cleaned))
            await writer.drain()
        line_buf += cleaned
        if len(raw_buf) > MAX_BUFFERED_INPUT or len(line_buf) > MAX_BUFFERED_INPUT:
            LOGGER.warning("terminal input flood session=%s client=%s", session_id, peer)
            with suppress(Exception):
                writer.write(b"\r\nInput overflow. Disconnecting.\r\n")
                await writer.drain()
            return "input_flood"
        while True:
            line, line_buf = split_telnet_line(line_buf)
            if line is None:
                break
            # Bare Enter (empty line) still counts as a keypress.
            _debug_bytes("line->sim", session_id, line, echo_state)
            process.stdin.write(line[:MAX_LINE] + b"\n")
            await process.stdin.drain()
    return "session_ended"


async def _input_reason(reader, writer, process, session_id, peer, echo_state):
    """forward_telnet_input's reason, or "client_error" if it dies abruptly.

    An abrupt client drop (connection reset) raises out of the reader instead
    of returning cleanly; map that to a real reason so the activity log never
    shows "unknown".
    """
    try:
        return await forward_telnet_input(reader, writer, process, session_id,
                                          peer, echo_state)
    except Exception:
        LOGGER.exception("input forwarder failed session=%s", session_id)
        return "client_error"


def _peer_ip(peer):
    """Best-effort client IP from an asyncio peername."""
    if isinstance(peer, (tuple, list)) and peer:
        return str(peer[0])
    return None


async def _reject_busy(writer, peer):
    LOGGER.warning("session rejected (server busy) client=%s", peer)
    cis_activity.log_event("session_rejected_busy", client_ip=_peer_ip(peer))
    with suppress(Exception):
        writer.write(b"Sorry, the system is busy. Please try again later.\r\n")
        await writer.drain()
    writer.close()
    with suppress(Exception):
        await writer.wait_closed()


async def _reject_over_ip_limit(writer, peer, client_ip):
    LOGGER.warning("session rejected (per-IP limit) client=%s", peer)
    cis_activity.log_event("session_rejected_per_ip", client_ip=client_ip)
    with suppress(Exception):
        writer.write(b"Too many connections from your address. Please try again later.\r\n")
        await writer.drain()
    writer.close()
    with suppress(Exception):
        await writer.wait_closed()


async def serve_terminal(reader, writer):
    peer = writer.get_extra_info("peername")
    client_ip = _peer_ip(peer)
    if IP_SESSIONS.get(client_ip, 0) >= MAX_SESSIONS_PER_IP:
        await _reject_over_ip_limit(writer, peer, client_ip)
        return
    # Counted before any await, so concurrent connects can't race past the cap.
    IP_SESSIONS[client_ip] = IP_SESSIONS.get(client_ip, 0) + 1
    try:
        try:
            await asyncio.wait_for(SESSION_SLOTS.acquire(), timeout=5)
        except asyncio.TimeoutError:
            await _reject_busy(writer, peer)
            return
        try:
            await _handle_session(reader, writer, peer)
        finally:
            SESSION_SLOTS.release()
    finally:
        remaining = IP_SESSIONS.get(client_ip, 1) - 1
        if remaining <= 0:
            IP_SESSIONS.pop(client_ip, None)
        else:
            IP_SESSIONS[client_ip] = remaining


# Echo-control markers emitted by the sim. Translated here into telnet option
# negotiation so remote clients stop their local echo while a secret is
# typed (like real telnetd). NUL-delimited so they never collide with real
# output; only emitted for remote terminals.
#
# No IAC is sent before the terminal type is selected: the sim emits
# TERM_SELECTED right after its startup configuration, and only then does
# the gateway send WILL ECHO and start remote echo. Before that the client
# is on its own (dumb-terminal behavior).
_ECHO_OFF_MARKER = b"\x00[ECHOOFF]\x00"
_ECHO_ON_MARKER = b"\x00[ECHOON]\x00"
_TERM_SELECTED_MARKER = b"\x00[TERMSELECTED]\x00"
_IAC_WILL_ECHO = b"\xff\xfb\x01"  # server takes over echo: client, stop echoing


class _EchoState:
    """Whether the gateway echoes client keystrokes back.

    True from connect (so terminals without local echo see what they
    type); the sim's password markers flip it off and on via
    _EchoTranslator. The IAC WILL ECHO negotiation itself is deferred
    until the terminal type is selected. One instance is shared by a
    session's input and output tasks.
    """

    def __init__(self):
        self.enabled = True
        self.term_selected = False


def _echo_bytes(data):
    """Translate input bytes for remote echo.

    Keystrokes are reflected back so clients without local echo (e.g.
    C64 terminals) see what they type. CR, LF, CRLF, and CR NUL each
    echo as a single CRLF so the cursor lands on a fresh line.
    """
    out = bytearray()
    i = 0
    end = len(data)
    while i < end:
        byte = data[i]
        if byte == 0x0D:  # CR: echo CRLF, swallow one following LF/NUL
            out += b"\r\n"
            if i + 1 < end and data[i + 1] in (0x0A, 0x00):
                i += 1
        elif byte == 0x0A:  # bare LF
            out += b"\r\n"
        else:
            out.append(byte)
        i += 1
    return bytes(out)


class _EchoTranslator:
    """Strip echo-control markers from sim output, yielding IAC negotiation.

    Markers can straddle read-chunk boundaries, so a trailing partial marker
    is held back until the next feed(). Call flush() at end of stream.

    TERM_SELECTED (terminal type chosen) sends WILL ECHO and enables the
    gateway's remote echo; ECHO_OFF clears echo_state.enabled (the server
    stops echoing the password); ECHO_ON sets it again. The client was told
    WILL ECHO at terminal selection and keeps its local echo off throughout,
    so no WONT ECHO is ever sent.
    """

    def __init__(self, echo_state=None):
        self._pending = b""
        self._echo_state = echo_state or _EchoState()

    def feed(self, chunk):
        """Return (forward_bytes, iac_bytes) for one chunk of sim output."""
        data = self._pending + chunk
        self._pending = b""
        forward = bytearray()
        iac = bytearray()
        index = 0
        end = len(data)
        while index < end:
            if data.startswith(_TERM_SELECTED_MARKER, index):
                # Terminal type selected: take over echo from here on.
                if TELNET_DEBUG:
                    LOGGER.info("telnet_debug MARKER TERM_SELECTED")
                iac += _IAC_WILL_ECHO
                self._echo_state.enabled = True
                self._echo_state.term_selected = True
                index += len(_TERM_SELECTED_MARKER)
            elif data.startswith(_ECHO_OFF_MARKER, index):
                if TELNET_DEBUG:
                    LOGGER.info("telnet_debug MARKER ECHO_OFF (password start)")
                self._echo_state.enabled = False
                index += len(_ECHO_OFF_MARKER)
            elif data.startswith(_ECHO_ON_MARKER, index):
                if TELNET_DEBUG:
                    LOGGER.info("telnet_debug MARKER ECHO_ON (password end)")
                self._echo_state.enabled = True
                index += len(_ECHO_ON_MARKER)
            elif data[index:index + 1] == b"\x00" and end - index < len(_TERM_SELECTED_MARKER):
                self._pending = data[index:]  # split marker; wait for more
                break
            else:
                forward.append(data[index])
                index += 1
        return bytes(forward), bytes(iac)

    def flush(self):
        """Return any held-back bytes (only a truncated marker can remain)."""
        pending, self._pending = self._pending, b""
        return pending


async def _handle_session(reader, writer, peer):
    session_id = uuid.uuid4().hex
    client_ip = _peer_ip(peer)
    started = time.monotonic()
    LOGGER.info("terminal connected session=%s client=%s", session_id, peer)
    cis_activity.log_event("session_connected", session_id=session_id, client_ip=client_ip)
    # Disable Nagle's algorithm: interactive keystrokes must not wait for
    # TCP buffering (causes visible typing lag on retro terminals).
    with suppress(Exception):
        sock = writer.get_extra_info("socket")
        if sock is not None:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    process = None
    disconnect_reason = "unknown"
    echo_state = _EchoState()
    echo = _EchoTranslator(echo_state)

    # Greet immediately: spawning the sim subprocess (cold Python +
    # imports) can take ~10s, and a client staring at a blank screen
    # that long assumes the connection is dead and hangs up. Plain text
    # only -- no control characters are sent before the terminal type is
    # selected (the sim reports that with TERM_SELECTED, and only then
    # does the gateway negotiate WILL ECHO).
    with suppress(Exception):
        writer.write(b"\r\nConnecting to CompuServe...\r\n")
        await writer.drain()

    process = await asyncio.create_subprocess_exec(
        sys.executable, "-u", str(BASE_DIR / "compuserve.py"),
        cwd=BASE_DIR,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env={
            **os.environ,
            "CIS_REMOTE_TERMINAL": "1",
            "CIS_TRANSPORT": "TELNET",
            "CIS_SESSION_ID": session_id,
            "CIS_CLIENT_IP": client_ip or "",
            "CIS_ANSI": os.environ.get("CIS_TELNET_ANSI", "1"),
        },
    )

    disconnect_reason = "unknown"
    echo = _EchoTranslator(echo_state)

    async def output():
        while chunk := await process.stdout.read(512):
            forward, iac = echo.feed(chunk)
            if iac:
                if TELNET_DEBUG:
                    LOGGER.info("telnet_debug session=%s send-iac hex=%s",
                                session_id, iac.hex())
                writer.write(iac)
            if forward:
                writer.write(forward.replace(b"\n", b"\r\n"))
            await writer.drain()
        if tail := echo.flush():
            writer.write(tail.replace(b"\n", b"\r\n"))
            await writer.drain()

    async def input_lines():
        nonlocal disconnect_reason
        disconnect_reason = await _input_reason(reader, writer, process,
                                               session_id, peer, echo_state)

    output_task = asyncio.create_task(output())
    input_task = asyncio.create_task(input_lines())
    wait_task = asyncio.create_task(process.wait())
    tasks = {output_task, input_task, wait_task}
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    if disconnect_reason == "unknown" and (wait_task in done or process.returncode is not None):
        disconnect_reason = "session_ended"  # sim exited on its own (e.g. failed login)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    if process.returncode is None:
        process.terminate()
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(process.wait(), 2)
        if process.returncode is None:
            process.kill()
    writer.close()
    await writer.wait_closed()
    duration = round(time.monotonic() - started, 1)
    LOGGER.info("terminal disconnected session=%s client=%s", session_id, peer)
    cis_activity.log_event(
        "session_disconnected",
        session_id=session_id,
        client_ip=client_ip,
        detail={"duration_s": duration, "reason": disconnect_reason},
    )


async def main():
    global SESSION_SLOTS
    SESSION_SLOTS = asyncio.Semaphore(MAX_SESSIONS)
    host = os.environ.get("CIS_TELNET_HOST", "0.0.0.0")
    port = int(os.environ.get("CIS_TELNET_PORT", "2323"))
    server = await asyncio.start_server(serve_terminal, host, port)
    print(f"Classic CompuServe terminal listening on {host}:{port} "
          f"(max_sessions={MAX_SESSIONS} idle_timeout={IDLE_TIMEOUT}s)")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(
        level=os.environ.get("CIS_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
