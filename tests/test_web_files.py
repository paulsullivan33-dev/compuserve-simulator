"""Run with: python -m unittest discover -s tests -p test_web_files.py"""

import asyncio
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import AsyncMock, patch

from cis_web_files import offer_download

try:
    import web_app
except ImportError:
    web_app = None


@unittest.skipIf(web_app is None, 'Web dependencies are not installed')
class WebDownloadTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.sessions = patch.dict(web_app.DOWNLOAD_SESSIONS, {}, clear=True)
        self.sessions.start()
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        for session_id in ('a' * 32, 'b' * 32):
            temporary = tempfile.TemporaryDirectory()
            self.addCleanup(temporary.cleanup)
            web_app.DOWNLOAD_SESSIONS[session_id] = {'temporary': temporary, 'files': {}, 'expires': None}
        self.addCleanup(self.sessions.stop)

    async def make_download(self, session_id='a' * 32):
        source = Path(self.directory.name) / 'EXAMPLE.BAS'
        source.write_bytes(b'10 PRINT "READY"\r\n20 END\r\n')
        with patch.dict('os.environ', {'CIS_WEB_TERMINAL': '1', 'CIS_WEB_EXPORT_DIR': web_app.DOWNLOAD_SESSIONS[session_id]['temporary'].name}):
            self.assertTrue(offer_download(source))
        socket = AsyncMock()
        await web_app.send_downloads(socket, session_id)
        return source, socket.send_json.call_args.args[0], socket

    async def test_snapshot_attachment_and_session_isolation(self):
        source, message, socket = await self.make_download()
        token = message['url'].rsplit('/', 1)[1]
        expected = source.read_bytes()
        source.write_bytes(b'changed by a later transfer')
        response = await web_app.download_file('a' * 32, token)
        sent = []
        async def send(message):
            sent.append(message)
        await response({'type': 'http', 'method': 'GET', 'headers': [], 'extensions': {}}, AsyncMock(), send)
        self.assertEqual(b''.join(item.get('body', b'') for item in sent), expected)
        self.assertIn('attachment;', response.headers['content-disposition'])
        self.assertIn('EXAMPLE.BAS', response.headers['content-disposition'])
        self.assertEqual(response.headers['cache-control'], 'no-store')
        await web_app.send_downloads(socket, 'a' * 32)
        socket.send_json.assert_called_once()
        with self.assertRaises(web_app.HTTPException) as error:
            await web_app.download_file('b' * 32, token)
        self.assertEqual(error.exception.status_code, 404)

    async def test_expired_downloads_are_removed(self):
        _, message, _ = await self.make_download()
        session = web_app.DOWNLOAD_SESSIONS['a' * 32]
        path = Path(session['temporary'].name)
        session['expires'] = time.monotonic() - 1
        with self.assertRaises(web_app.HTTPException):
            await web_app.download_file('a' * 32, message['url'].rsplit('/', 1)[1])
        self.assertFalse(path.exists())
        self.assertIn('b' * 32, web_app.DOWNLOAD_SESSIONS)

    async def test_manifest_cannot_supply_a_path(self):
        directory = Path(web_app.DOWNLOAD_SESSIONS['a' * 32]['temporary'].name)
        token = 'c' * 32
        (directory / (token + '.bin')).write_bytes(b'not served')
        (directory / (token + '.json')).write_text(json.dumps({'name': '../secret.txt'}))
        socket = AsyncMock()
        await web_app.send_downloads(socket, 'a' * 32)
        socket.send_json.assert_not_called()
        with self.assertRaises(web_app.HTTPException):
            await web_app.download_file('a' * 32, '../secret.txt')

    async def test_console_does_not_queue_downloads(self):
        source = Path(self.directory.name) / 'LOCAL.TXT'
        source.write_text('local')
        with patch.dict('os.environ', {'CIS_WEB_TERMINAL': '0'}):
            self.assertFalse(offer_download(source))

    async def test_capture_off_offers_the_current_capture(self):
        import compuserve
        directory = web_app.DOWNLOAD_SESSIONS['a' * 32]['temporary'].name
        with patch.object(compuserve, 'BASE_DIR', Path(self.directory.name)), patch.object(compuserve, 'capture_path', None), patch.object(compuserve, 'ansi_scroll'), patch.dict('os.environ', {'CIS_WEB_TERMINAL': '1', 'CIS_WEB_EXPORT_DIR': directory}):
            compuserve.set_capture(True)
            path = compuserve.capture_path
            path.write_text('Captured session text\n', encoding='utf-8')
            compuserve.set_capture(False)
            self.assertIsNone(compuserve.capture_path)
        socket = AsyncMock()
        await web_app.send_downloads(socket, 'a' * 32)
        message = socket.send_json.call_args.args[0]
        self.assertEqual(message['name'], path.name)
        response = await web_app.download_file('a' * 32, message['url'].rsplit('/', 1)[1])
        self.assertEqual(Path(response.path).read_text(), 'Captured session text\n')


if __name__ == '__main__':
    unittest.main()
