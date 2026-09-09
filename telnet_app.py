"""Small Telnet-style TCP gateway for period terminal clients."""

import asyncio
import logging
import os
import sys
import uuid
from contextlib import suppress
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MAX_LINE = 4096
LOGGER = logging.getLogger("compuserve.telnet")


def strip_telnet_commands(data):
    """Remove basic IAC negotiation sequences from a terminal input stream."""
    result = bytearray()
    index = 0
    while index < len(data):
        if data[index] == 255:
            index += 3
        else:
            result.append(data[index])
            index += 1
    return bytes(result)


async def serve_terminal(reader, writer):
    peer = writer.get_extra_info("peername")
    session_id = uuid.uuid4().hex
    LOGGER.info("terminal connected session=%s client=%s", session_id, peer)
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
            "CIS_ANSI": os.environ.get("CIS_TELNET_ANSI", "1"),
        },
    )

    async def output():
        while chunk := await process.stdout.read(512):
            writer.write(chunk.replace(b"\n", b"\r\n"))
            await writer.drain()

    async def input_lines():
        while process.returncode is None:
            data = strip_telnet_commands(await reader.readline())[:MAX_LINE]
            if not data:
                break
            process.stdin.write(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
            await process.stdin.drain()

    tasks = {asyncio.create_task(output()), asyncio.create_task(input_lines()), asyncio.create_task(process.wait())}
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
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
    LOGGER.info("terminal disconnected session=%s client=%s", session_id, peer)


async def main():
    host = os.environ.get("CIS_TELNET_HOST", "0.0.0.0")
    port = int(os.environ.get("CIS_TELNET_PORT", "2323"))
    server = await asyncio.start_server(serve_terminal, host, port)
    print(f"Classic CompuServe terminal listening on {host}:{port}")
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
