"""Mocked web terminal admission and idle cleanup; no listener or child processes."""
import asyncio
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

import web_app


class AdmissionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.counts = patch.dict(web_app.IP_SESSIONS, {}, clear=True)
        self.counts.start()
        self.addCleanup(self.counts.stop)

    def socket(self, host='192.0.2.1'):
        socket = AsyncMock()
        socket.headers = {}
        socket.client = SimpleNamespace(host=host)
        return socket

    async def test_global_limit_rejects_before_session_allocation(self):
        web_app.IP_SESSIONS['other'] = 2
        socket = self.socket()
        with patch.object(web_app, 'MAX_SESSIONS', 2), patch.object(web_app, '_terminal_session', new_callable=AsyncMock) as start:
            await web_app.terminal(socket)
        start.assert_not_called()
        socket.accept.assert_not_called()
        socket.close.assert_awaited_once_with(code=1013, reason='Terminal capacity reached')

    async def test_per_ip_limit_does_not_block_other_addresses(self):
        web_app.IP_SESSIONS['192.0.2.1'] = 1
        with patch.object(web_app, 'MAX_SESSIONS_PER_IP', 1), patch.object(web_app, '_terminal_session', new_callable=AsyncMock) as start:
            await web_app.terminal(self.socket())
            start.assert_not_called()
            await web_app.terminal(self.socket('192.0.2.2'))
            start.assert_awaited_once()
        self.assertEqual(web_app.IP_SESSIONS, {'192.0.2.1': 1})

    async def test_failure_and_cancellation_release_the_reserved_slot(self):
        for error in (OSError('spawn failed'), asyncio.CancelledError()):
            with self.subTest(error=type(error)), patch.object(web_app, '_terminal_session', new_callable=AsyncMock, side_effect=error):
                with self.assertRaises(type(error)):
                    await web_app.terminal(self.socket())
                self.assertEqual(web_app.IP_SESSIONS, {})

    async def test_concurrent_attempt_observes_reserved_slot(self):
        entered, release = asyncio.Event(), asyncio.Event()
        async def session(socket):
            entered.set()
            await release.wait()
        with patch.object(web_app, 'MAX_SESSIONS', 1), patch.object(web_app, '_terminal_session', side_effect=session) as start:
            task = asyncio.create_task(web_app.terminal(self.socket()))
            try:
                await asyncio.wait_for(entered.wait(), timeout=2)
                await web_app.terminal(self.socket('192.0.2.2'))
                self.assertEqual(start.call_count, 1)
            finally:
                release.set()
                await task
        self.assertEqual(web_app.IP_SESSIONS, {})

    async def test_idle_input_closes_without_writing_to_child(self):
        socket = self.socket()
        socket.receive_json.side_effect = asyncio.TimeoutError
        process = Mock(returncode=None)
        await web_app.relay_input(socket, process)
        socket.close.assert_awaited_once_with(code=1008, reason='Terminal idle timeout')
        process.stdin.write.assert_not_called()
