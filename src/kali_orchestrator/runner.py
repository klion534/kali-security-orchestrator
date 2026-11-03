from dataclasses import dataclass
from datetime import datetime, timezone
import os
import re
import signal
import shlex
import subprocess
import time

from .catalog import ToolCatalog
from .policy import AuthorizationError, ExecutionPolicy


class RunnerError(RuntimeError):
    """Raised when a command cannot be safely scheduled or executed."""


@dataclass(frozen=True)
class RunResult:
    tool: str
    target: str
    profile: str
    status: str
    command: str
    tool_status: str
    started_at: str
    ended_at: str
    duration_seconds: float
    returncode: int | None
    stdout: str
    stderr: str

    def as_dict(self) -> dict:
        return {
            "tool": self.tool,
            "target": self.target,
            "profile": self.profile,
            "status": self.status,
            "command": self.command,
            "tool_status": self.tool_status,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_seconds": self.duration_seconds,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


class ToolRunner:
    def __init__(self, catalog: ToolCatalog):
        self.catalog = catalog

    def run(
        self,
        tool_name: str,
        *,
        profile: str,
        target: str,
        args: list[str] | tuple[str, ...],
        policy: ExecutionPolicy,
        dry_run: bool = True,
        timeout: float = 300.0,
    ) -> RunResult:
        if timeout <= 0:
            raise RunnerError("timeout must be greater than zero")
        try:
            tool = self.catalog.get(tool_name)
        except KeyError as error:
            raise RunnerError(f"unknown tool: {tool_name}") from error
        if profile not in tool.profiles:
            raise RunnerError(f"tool {tool_name} is not enabled for profile {profile}")
        try:
            policy.assert_can_run(profile, target)
        except AuthorizationError as error:
            raise RunnerError(str(error)) from error
        if not dry_run and not policy.authorized:
            raise RunnerError("real execution requires explicit authorization")

        command_args = _validate_args(args)
        executable = tool.executable()
        resolved_command = executable or tool.binary
        command = [resolved_command, *command_args]
        command_text = redact_text(shlex.join(command))
        started = datetime.now(timezone.utc)
        start_clock = time.monotonic()

        if dry_run:
            ended = datetime.now(timezone.utc)
            return RunResult(
                tool=tool.name,
                target=redact_text(target),
                profile=profile,
                status="planned",
                command=command_text,
                tool_status=tool.status(),
                started_at=started.isoformat(),
                ended_at=ended.isoformat(),
                duration_seconds=0.0,
                returncode=None,
                stdout="",
                stderr="",
            )

        if executable is None:
            raise RunnerError(f"tool is not installed: {tool_name}")

        process = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=(os.name == "posix"),
        )
        status = "completed"
        returncode = None
        stdout = ""
        stderr = ""
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            returncode = process.returncode
            if returncode != 0:
                status = "failed"
        except subprocess.TimeoutExpired as error:
            status = "timeout"
            _stop_process(process)
            stdout, stderr = process.communicate()
        except KeyboardInterrupt:
            status = "cancelled"
            _stop_process(process)
            stdout, stderr = process.communicate()

        ended = datetime.now(timezone.utc)
        return RunResult(
            tool=tool.name,
            target=redact_text(target),
            profile=profile,
            status=status,
            command=command_text,
            tool_status=tool.status(),
            started_at=started.isoformat(),
            ended_at=ended.isoformat(),
            duration_seconds=round(time.monotonic() - start_clock, 3),
            returncode=returncode,
            stdout=redact_text(stdout),
            stderr=redact_text(stderr),
        )


def _validate_args(args) -> tuple[str, ...]:
    if not isinstance(args, (list, tuple)):
        raise RunnerError("command arguments must be a list or tuple")
    for arg in args:
        if not isinstance(arg, str) or "\x00" in arg or "\n" in arg or "\r" in arg:
            raise RunnerError("command arguments contain invalid characters")
        if len(arg) > 4096:
            raise RunnerError("command argument exceeds the 4096-character limit")
    return tuple(args)


def _stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
            return
        except ProcessLookupError:
            return
    process.terminate()


def redact_text(value: str) -> str:
    redacted = value
    redacted = re.sub(r"(?i)(authorization\s*:\s*bearer\s+)[^\s]+", r"\1[REDACTED]", redacted)
    redacted = re.sub(
        r"(?i)\b(password|passwd|secret|token|api[_-]?key)\s*([:=])\s*[^\s,;]+",
        r"\1\2[REDACTED]",
        redacted,
    )
    redacted = re.sub(r"\b(?:sk|ghp|glpat)-[A-Za-z0-9_-]{12,}\b", "[REDACTED]", redacted)
    redacted = re.sub(r"AKIA[0-9A-Z]{16}", "[REDACTED]", redacted)
    return redacted
