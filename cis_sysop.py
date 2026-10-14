def account_rows(profiles):
    rows = []
    for user_id, profile in sorted(profiles.items()):
        state = "DISABLED" if profile.get("disabled") else "LOCKED" if profile.get("locked") else "ACTIVE"
        role = "SYSOP" if profile.get("is_sysop") else "MEMBER"
        rows.append((user_id, role, state))
    return rows


def unlock_account(profiles, user_id):
    profile = profiles.get(user_id)
    if not profile:
        return False
    profile["locked"] = False
    profile.pop("locked_at", None)
    profile["failed_logins"] = 0
    return True


def toggle_disabled(profiles, user_id):
    profile = profiles.get(user_id)
    if not profile:
        return None
    profile["disabled"] = not profile.get("disabled", False)
    return profile["disabled"]


def reset_password(profiles, user_id):
    profile = profiles.get(user_id)
    if not profile:
        return False
    profile.pop("password_hash", None)
    profile["locked"] = False
    profile.pop("locked_at", None)
    profile["failed_logins"] = 0
    return True


def pending_uploads(library_files):
    return [
        (section, file)
        for section, files in library_files.items()
        for file in files
        if file.get("status") == "pending"
    ]


def set_upload_status(library_files, number, status):
    if status not in ("approved", "rejected"):
        raise ValueError("Invalid upload status")
    for files in library_files.values():
        for file in files:
            if file.get("number") == number:
                file["status"] = status
                return True
    return False


import subprocess
import locale
import os
import signal
import threading
import time


MAX_COMMAND_OUTPUT = 1024 * 1024


class CommandOutputLimitExceeded(RuntimeError):
    """The command exceeded the combined stdout/stderr byte limit."""


def _stop_command(proc):
    """Terminate the shell and its ordinary descendants."""
    try:
        if os.name == "nt":
            result = subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    timeout=10, check=False)
            if result.returncode and proc.poll() is None:
                raise OSError("Could not verify command process-tree cleanup")
        else:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    finally:
        if proc.poll() is None:
            proc.kill()
        proc.wait(timeout=10)


def run_os_command(command, timeout=60, max_output=MAX_COMMAND_OUTPUT):
    """Run a shell command, returning (returncode, stdout, stderr).

    Bound combined output bytes and terminate the process tree on timeout or
    excess output. Detached descendants are outside this lifecycle boundary.
    """
    if timeout <= 0 or max_output <= 0:
        raise ValueError("Command timeout and output limit must be positive")
    proc = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=os.name != "nt",
    )
    output = [bytearray(), bytearray()]
    lock = threading.Lock()
    exceeded = threading.Event()
    done = [threading.Event(), threading.Event()]
    size = 0

    def collect(index, stream):
        nonlocal size
        try:
            while True:
                chunk = stream.read1(8192)
                if not chunk:
                    break
                with lock:
                    remaining = max_output - size
                    output[index].extend(chunk[:remaining])
                    size += min(len(chunk), remaining)
                    if len(chunk) > remaining:
                        exceeded.set()
                if exceeded.is_set():
                    break
        finally:
            stream.close()
            done[index].set()

    workers = [threading.Thread(target=collect, args=(i, stream), daemon=True)
               for i, stream in enumerate((proc.stdout, proc.stderr))]
    for worker in workers:
        worker.start()
    deadline = time.monotonic() + timeout
    try:
        while True:
            if exceeded.is_set():
                raise CommandOutputLimitExceeded("Command output exceeded its byte limit")
            if proc.poll() is not None and all(event.is_set() for event in done):
                break
            if time.monotonic() >= deadline:
                raise subprocess.TimeoutExpired(command, timeout)
            exceeded.wait(min(0.02, max(0, deadline - time.monotonic())))
    except BaseException:
        _stop_command(proc)
        raise
    finally:
        for worker in workers:
            worker.join(timeout=1)
    encoding = locale.getpreferredencoding(False)
    return proc.returncode, *(bytes(data).decode(encoding, errors="replace") for data in output)
