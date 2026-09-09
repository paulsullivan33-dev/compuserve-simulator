"""Web terminal with per-session file delivery for Classic CompuServe."""

import asyncio
import json
import logging
import os
import sys
import uuid
import tempfile
import time
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
MAX_INPUT_LENGTH = 4_096
LOGGER = logging.getLogger("compuserve.web")
DOWNLOAD_TTL = 3600
DOWNLOAD_SESSIONS = {}


def prune_downloads():
    now = time.monotonic()
    for session_id, session in list(DOWNLOAD_SESSIONS.items()):
        if session['expires'] is not None and session['expires'] <= now:
            session['temporary'].cleanup()
            del DOWNLOAD_SESSIONS[session_id]


@asynccontextmanager
async def lifespan(app):
    async def cleanup():
        while True:
            await asyncio.sleep(60)
            prune_downloads()
    cleanup_task = asyncio.create_task(cleanup())
    try:
        yield
    finally:
        cleanup_task.cancel()
        await asyncio.gather(cleanup_task, return_exceptions=True)
        for session in DOWNLOAD_SESSIONS.values():
            session['temporary'].cleanup()
        DOWNLOAD_SESSIONS.clear()

app = FastAPI(title="Classic CompuServe Web Terminal", docs_url=None, redoc_url=None, lifespan=lifespan)
app.mount("/assets", StaticFiles(directory=WEB_DIR), name="assets")


@app.get("/")
async def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get('/downloads/{session_id}/{token}')
async def download_file(session_id: str, token: str):
    prune_downloads()
    session = DOWNLOAD_SESSIONS.get(session_id)
    record = session['files'].get(token) if session else None
    if not record or not record['path'].is_file():
        raise HTTPException(status_code=404, detail='Download unavailable or expired. Transfer the file again.')
    return FileResponse(record['path'], filename=record['name'], media_type='application/octet-stream',
                        headers={'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'})


async def send_downloads(websocket, session_id):
    session = DOWNLOAD_SESSIONS[session_id]
    directory = Path(session['temporary'].name)
    for manifest in sorted(directory.glob('*.json')):
        token = manifest.stem
        if token in session['files']:
            continue
        # Only the child session can publish these manifests; never accept a path from the browser.
        if len(token) != 32 or any(c not in '0123456789abcdef' for c in token):
            continue
        payload = json.loads(manifest.read_text(encoding='utf-8'))
        name = payload.get('name', '')
        snapshot = directory / (token + '.bin')
        if not name or Path(name).name != name or '/' in name or '\\' in name or not snapshot.is_file() or snapshot.is_symlink():
            continue
        session['files'][token] = {'name': name, 'path': snapshot}
        await websocket.send_json({'type': 'download', 'name': name,
                                   'url': f'/downloads/{session_id}/{token}'})


async def relay_downloads(websocket, session_id):
    while True:
        await send_downloads(websocket, session_id)
        await asyncio.sleep(0.2)


def local_origin_allowed(websocket):
    """Allow the terminal page's origin while rejecting cross-site control."""
    origin = websocket.headers.get("origin")
    if not origin:
        return True
    try:
        origin_url = urlparse(origin)
        request_host = websocket.headers.get("host", "")
        return origin_url.netloc.lower() == request_host.lower()
    except ValueError:
        return False


async def stop_process(process):
    if process.returncode is not None:
        return
    process.terminate()
    try:
        await asyncio.wait_for(process.wait(), timeout=2)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()


async def relay_output(websocket, process):
    while True:
        chunk = await process.stdout.read(512)
        if not chunk:
            break
        await websocket.send_json({
            "type": "output",
            "data": chunk.decode("utf-8", errors="replace"),
        })


async def relay_input(websocket, process):
    while process.returncode is None:
        message = await websocket.receive_json()
        if message.get("type") == "disconnect":
            return
        if message.get("type") != "input":
            continue
        value = str(message.get("data", ""))[:MAX_INPUT_LENGTH]
        process.stdin.write((value + "\n").encode("utf-8"))
        await process.stdin.drain()


@app.websocket("/terminal")
async def terminal(websocket: WebSocket):
    if not local_origin_allowed(websocket):
        await websocket.close(code=1008)
        return
    await websocket.accept()
    session_id = uuid.uuid4().hex
    prune_downloads()
    temporary = tempfile.TemporaryDirectory(prefix='cis-web-')
    DOWNLOAD_SESSIONS[session_id] = {'temporary': temporary, 'files': {}, 'expires': None}
    process = None
    tasks = set()
    try:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                "-u",
                str(BASE_DIR / "compuserve.py"),
                cwd=BASE_DIR,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={
                    **os.environ,
                    "CIS_WEB_TERMINAL": "1",
                    "CIS_TRANSPORT": "WEB",
                    "CIS_SESSION_ID": session_id,
                    "CIS_WEB_EXPORT_DIR": temporary.name,
                },
            )
            LOGGER.info("terminal connected session=%s client=%s", session_id, websocket.client)
            await websocket.send_json({"type": "status", "data": "CONNECTED"})
            output_task = asyncio.create_task(relay_output(websocket, process))
            input_task = asyncio.create_task(relay_input(websocket, process))
            wait_task = asyncio.create_task(process.wait())
            download_task = asyncio.create_task(relay_downloads(websocket, session_id))
            tasks = {output_task, input_task, wait_task, download_task}
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )
            if wait_task in done:
                await output_task
                await send_downloads(websocket, session_id)
                with suppress(RuntimeError, WebSocketDisconnect):
                    await websocket.send_json({
                        "type": "status",
                        "data": f"SESSION ENDED ({process.returncode})",
                    })
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
    except WebSocketDisconnect:
        LOGGER.info("terminal disconnected session=%s", session_id)
    except Exception:
        LOGGER.exception("terminal failed session=%s", session_id)
        raise
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        if process is not None:
            await stop_process(process)
        with suppress(RuntimeError, WebSocketDisconnect, OSError):
            await send_downloads(websocket, session_id)
        DOWNLOAD_SESSIONS[session_id]['expires'] = time.monotonic() + DOWNLOAD_TTL
        LOGGER.info("terminal stopped session=%s", session_id)


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=os.environ.get("CIS_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    uvicorn.run(
        app,
        host=os.environ.get("CIS_WEB_HOST", "0.0.0.0"),
        port=int(os.environ.get("CIS_WEB_PORT", "8000")),
    )
