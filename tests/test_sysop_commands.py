import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest

from cis_sysop import CommandOutputLimitExceeded, run_os_command


def shell_command(*args):
    if os.name == 'nt':
        return subprocess.list2cmdline(args)
    return shlex.join(args)


class SysopCommandLimitsTests(unittest.TestCase):
    def test_combined_output_limit_stops_command(self):
        code = "import sys; sys.stdout.write('x'*800); sys.stdout.flush(); sys.stderr.write('y'*800)"
        with self.assertRaises(CommandOutputLimitExceeded):
            run_os_command(shell_command(sys.executable, '-c', code), max_output=1024)

    def test_exact_output_limit_preserves_both_streams(self):
        code = "import sys; sys.stdout.write('x'*512); sys.stderr.write('y'*512)"
        rc, out, err = run_os_command(shell_command(sys.executable, '-c', code), max_output=1024)
        self.assertEqual((rc, out, err), (0, 'x'*512, 'y'*512))

    def test_stdin_is_closed(self):
        rc, out, err = run_os_command(shell_command(
            sys.executable, '-c', "import sys; print(repr(sys.stdin.read()))"))
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "''")
        self.assertEqual(err, '')

    def test_timeout_stops_child_before_it_can_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            child = root / 'child.py'
            ready = root / 'ready'
            survivor = root / 'survivor'
            child.write_text(
                'import time\nfrom pathlib import Path\n'
                f'Path({str(ready)!r}).touch()\n'
                'time.sleep(3)\n'
                f'Path({str(survivor)!r}).touch()\n', encoding='utf-8')
            parent = root / 'parent.py'
            parent.write_text(
                'import subprocess, sys\n'
                f'subprocess.run([sys.executable, {str(child)!r}], check=True)\n',
                encoding='utf-8')
            with self.assertRaises(subprocess.TimeoutExpired):
                run_os_command(shell_command(sys.executable, str(parent)), timeout=1.5)
            self.assertTrue(ready.exists(), 'Child must have started before timeout')
            time.sleep(2)
            self.assertFalse(survivor.exists(), 'Child survived command timeout')

