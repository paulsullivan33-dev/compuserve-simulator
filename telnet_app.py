"""Small Telnet-style TCP gateway for period terminal clients.

Hardened for internet exposure:
  * MAX_SESSIONS caps concurrent connections (each one spawns a
    compuserve.py subprocess, so uncapped connections = trivial DoS).
  * IDLE_TIMEOUT disconnects clients that send nothing for a while,
    so abandoned connections can't accumulate forever.
"""

import asyncio
import logging
import os
import sys
import time
import uuid
from contextlib import suppress
from pathlib import Path

import cis_activity


BASE_DIR = Path(__file__).resolve().parent
MAX_LINE = 4096
LOGGER = logging.getLogger("compuserve.telnet")

# Tunables (env-overridable).
MAX_SESSIONS = int(os.environ.get("CIS_TELNET_MAX_SESSIONS", "20"))
IDLE_TIMEOUT = float(os.environ.get("CIS_TELNET_IDLE_TIMEOUT", "900"))  # seconds

# Created in main() so it binds to the running loop.
SESSION_SLOTS = None


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
    Returns (line, rest); line is None when no terminator is buffered yet.
    A trailing bare CR waits for the next byte in case CRLF/CR NUL follows.
    """
    for index, byte in enumerate(buf):
        if byte == 0x0D:  # CR
            if index + 1 >= len(buf):
                return None, buf
            rest_at = index + 2 if buf[index + 1] in (0x0A, 0x00) else index + 1
            return bytes(buf[:index]), bytes(buf[rest_at:])
        if byte == 0x0A:  # LF
            return bytes(buf[:index]), bytes(buf[index + 1:])
    return None, buf


async def forward_telnet_input(reader, writer, process, session_id, peer):
    """Forward client keystrokes to the terminal subprocess, one line at a time.

    Negotiation bytes are stripped from the raw stream before line
    splitting, so they can never swallow the terminator of the user's
    first Enter keypress.

    Returns the reason input forwarding stopped: "idle_timeout",
    "client_closed", or "session_ended".
    """
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
        raw_buf += chunk
        cleaned, raw_buf = strip_telnet_commands(raw_buf)
        line_buf += cleaned
        while True:
            line, line_buf = split_telnet_line(line_buf)
            if line is None:
                break
            # Bare Enter (empty line) still counts as a keypress.
            process.stdin.write(line[:MAX_LINE] + b"\n")
            await process.stdin.drain()
    return "session_ended"


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


async def serve_terminal(reader, writer):
    peer = writer.get_extra_info("peername")
    try:
        await asyncio.wait_for(SESSION_SLOTS.acquire(), timeout=5)
    except asyncio.TimeoutError:
        await _reject_busy(writer, peer)
        return
    try:
        await _handle_session(reader, writer, peer)
    finally:
        SESSION_SLOTS.release()


async def _handle_session(reader, writer, peer):
    session_id = uuid.uuid4().hex
    client_ip = _peer_ip(peer)
    started = time.monotonic()
    LOGGER.info("terminal connected session=%s client=%s", session_id, peer)
    cis_activity.log_event("session_connected", session_id=session_id, client_ip=client_ip)
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

    async def output():
        while chunk := await process.stdout.read(512):
            writer.write(chunk.replace(b"\n", b"\r\n"))
            await writer.drain()

    async def input_lines():
        nonlocal disconnect_reason
        disconnect_reason = await forward_telnet_input(reader, writer, process, session_id, peer)

    output_task = asyncio.create_task(output())
    input_task = asyncio.create_task(input_lines())
    wait_task = asyncio.create_task(process.wait())
    tasks = {output_task, input_task, wait_task}
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    if wait_task in done:
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
