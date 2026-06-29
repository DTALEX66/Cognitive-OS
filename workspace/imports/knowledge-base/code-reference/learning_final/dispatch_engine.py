"""Dispatch Engine - enhanced with CC tool execution patterns (toolExecution.ts, StreamingToolExecutor, toolHooks)"""
from __future__ import annotations
from datetime import datetime, timezone
import time

class DispatchResult:
    def __init__(self, status="ok", result="", error="", duration_ms=0):
        self.status = status; self.result = result; self.error = error; self.duration_ms = duration_ms
    def to_dict(self): return {"status": self.status, "result": self.result, "error": self.error, "duration_ms": self.duration_ms}

class DispatchEngine:
    def __init__(self):
        self._cmds = {}; self._tools = {}; self._history = []; self._hooks = {"pre": [], "post": []}
    def reg_cmd(self, name, handler=None): self._cmds[name] = handler or "default"
    def reg_tool(self, name, handler=None): self._tools[name] = handler or "default"
    def add_hook(self, stage, fn):
        if stage in self._hooks: self._hooks[stage].append(fn)
    def run_cmd(self, name, prompt=""):
        start = time.time(); cmd = self._cmds.get(name)
        if not cmd: return DispatchResult(status="error", error="unknown: "+name).to_dict()
        self._run_hooks("pre", {"type": "cmd", "name": name})
        r = DispatchResult(duration_ms=int((time.time()-start)*1000))
        self._history.append({"type":"cmd","name":name,"ts":datetime.now(timezone.utc).isoformat()})
        self._run_hooks("post", {"type": "cmd", "name": name, "result": r})
        return r.to_dict()
    def run_tool(self, name, payload=""):
        start = time.time(); t = self._tools.get(name)
        if not t: return DispatchResult(status="error", error="unknown: "+name).to_dict()
        self._run_hooks("pre", {"type": "tool", "name": name})
        r = DispatchResult(duration_ms=int((time.time()-start)*1000))
        self._history.append({"type":"tool","name":name,"ts":datetime.now(timezone.utc).isoformat()})
        self._run_hooks("post", {"type": "tool", "name": name, "result": r})
        return r.to_dict()
    def stream(self, name, payload=""):
        yield {"type":"stream_start","name":name}
        yield {"type":"hook_pre","stage":"pre"}
        result = self.run_tool(name, payload)
        yield {"type":"hook_post","stage":"post"}
        yield {"type":"stream_result","data":result}
        yield {"type":"stream_end"}
    def _run_hooks(self, stage, ctx):
        for hook in self._hooks.get(stage, []):
            try: hook(ctx)
            except: pass
    def list_cmds(self): return list(self._cmds.keys())
    def list_tools(self): return list(self._tools.keys())
    def recent(self, limit=20): return self._history[-limit:]
