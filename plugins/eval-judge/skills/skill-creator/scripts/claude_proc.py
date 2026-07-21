#!/usr/bin/env python3
"""Cross-platform helpers for spawning `claude -p` from the skill-creator scripts.

Factored out of run_eval.py so that run_eval.py and improve_description.py share ONE
implementation of the Windows-portability fixes rather than each carrying its own copy:

- `resolve_claude()` — spawn the real launcher (`claude.cmd`/`.exe` on Windows), not the
  bare `claude` shell shim that `CreateProcess` can't exec (WinError 2).
- `empty_mcp_config()` — a zero-server MCP config so `claude -p` skips booting the project's
  MCP fleet; the triggering/description tasks don't need those servers, and their boot latency
  was what made headless runs time out with no output.

Pure-stdlib, no third-party deps; works on Windows and Unix.
"""

import atexit
import os
import shutil
import tempfile


def resolve_claude() -> str:
    """Resolve the claude executable cross-platform.

    On Windows a bare ``claude`` is a shell shim that ``CreateProcess`` cannot exec
    (``WinError 2``); the runnable launcher is ``claude.cmd``/``claude.exe``. ``shutil.which``
    honors PATHEXT but can return the extensionless shim first, so probe the launcher names
    explicitly on Windows before falling back to the plain name (the Unix path).
    """
    if os.name == "nt":
        for name in ("claude.cmd", "claude.exe", "claude.bat"):
            found = shutil.which(name)
            if found:
                return found
    found = shutil.which("claude")
    if found:
        return found
    return "claude.cmd" if os.name == "nt" else "claude"


_EMPTY_MCP_CACHE: dict[int, str] = {}


def empty_mcp_config() -> str:
    """Path to a temp JSON declaring zero MCP servers.

    Combined with ``--strict-mcp-config`` this makes ``claude -p`` skip booting the project's
    MCP fleet (zephyr / atlassian / azure / playwright / mssql / m365). These tasks only need
    the model (description triggering / improvement), so those servers are pure latency — and
    that boot latency was the real blocker: headless ``claude -p`` emitted no output before the
    per-query timeout. Cached per process (``ProcessPoolExecutor`` workers each create one) and
    cleaned up at exit.
    """
    pid = os.getpid()
    cached = _EMPTY_MCP_CACHE.get(pid)
    if cached and os.path.exists(cached):
        return cached
    fd, path = tempfile.mkstemp(prefix="skillcreator-empty-mcp-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write('{"mcpServers": {}}')
    _EMPTY_MCP_CACHE[pid] = path
    atexit.register(lambda p=path: os.path.exists(p) and os.remove(p))
    return path
