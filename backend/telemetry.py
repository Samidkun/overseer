"""Telemetry engine and agent log watcher for Overseer.
Asynchronously observes agent state without blocking execution.
"""
import os
import re
import time
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Callable, Any

class TelemetryManager:
    def __init__(self, watch_dir: str | None = None, stuck_threshold_sec: int = 60):
        self.watch_dir = Path(watch_dir) if watch_dir else None
        self.stuck_threshold_sec = stuck_threshold_sec
        self._lock = threading.RLock()
        self._subscribers: list[Callable[[str, dict], None]] = []
        
        # State tracking
        self.supervisor = {
            "status": "ORCHESTRATING",
            "current_task": "Overseeing multi-agent workflow & telemetry streams.",
            "active_tool": "idle",
            "model": "ag/gemini-3.8-flash-high"
        }
        self.subagents: dict[str, dict[str, Any]] = {}
        self.metrics = {
            "active_agents": 0,
            "wave": "WAVE 1",
            "drift_gate": "PASS",
            "test_suite": "ALL PASS"
        }
        self._file_offsets: dict[str, int] = {}

    def add_subscriber(self, callback: Callable[[str, dict], None]) -> None:
        with self._lock:
            self._subscribers.append(callback)

    def remove_subscriber(self, callback: Callable[[str, dict], None]) -> None:
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    def broadcast(self, event_type: str, data: dict) -> None:
        with self._lock:
            subs = list(self._subscribers)
        for sub in subs:
            try:
                sub(event_type, data)
            except Exception:
                pass

    def emit_log(self, agent_id: str, tag: str, message: str) -> None:
        now_str = datetime.now(timezone.utc).isoformat(timespec="seconds")
        payload = {
            "timestamp": now_str,
            "agent_id": agent_id,
            "tag": tag,
            "message": message
        }
        self.broadcast("log", payload)

    def update_subagent(self, agent_id: str, **kwargs) -> None:
        with self._lock:
            sa = self.subagents.setdefault(agent_id, {
                "id": agent_id,
                "name": f"Subagent {agent_id}",
                "role": "Worker",
                "type": "worker",
                "status": "IDLE",
                "running_seconds": 0,
                "current_task": "Awaiting assignment",
                "last_action": "None",
                "last_seen": time.time(),
                "stuck_seconds": 0
            })
            for k, v in kwargs.items():
                sa[k] = v
            sa["last_seen"] = time.time()
            if sa["status"] != "STUCK_ALERT":
                sa["stuck_seconds"] = 0
            
            # Recalculate metrics
            active = sum(1 for a in self.subagents.values() if a["status"] not in ("IDLE", "COMPLETED"))
            self.metrics["active_agents"] = active

        self.broadcast("agent_update", dict(sa))

    def get_subagent(self, agent_id: str) -> dict[str, Any] | None:
        with self._lock:
            sa = self.subagents.get(agent_id)
            return dict(sa) if sa else None

    def check_stuck_agents(self) -> None:
        now = time.time()
        with self._lock:
            for sa in self.subagents.values():
                if sa["status"] in ("TOOL_EXEC", "THINKING"):
                    elapsed = now - sa.get("last_seen", now)
                    if elapsed >= self.stuck_threshold_sec:
                        sa["status"] = "STUCK_ALERT"
                        sa["stuck_seconds"] = int(elapsed)
                        self.broadcast("agent_update", dict(sa))
                elif sa["status"] == "STUCK_ALERT":
                    elapsed = now - sa.get("last_seen", now)
                    sa["stuck_seconds"] = int(elapsed)
                    self.broadcast("agent_update", dict(sa))

    def get_snapshot(self) -> dict[str, Any]:
        with self._lock:
            subs = [dict(s) for s in self.subagents.values()]
            return {
                "supervisor": dict(self.supervisor),
                "subagents": subs,
                "metrics": dict(self.metrics)
            }

    def scan_log_files(self) -> None:
        """Incrementally read log files in watch_dir and update state."""
        if not self.watch_dir or not self.watch_dir.is_dir():
            return

        for path in self.watch_dir.glob("*.log"):
            agent_id = path.stem
            prev_offset = self._file_offsets.get(str(path), 0)
            
            try:
                size = path.stat().st_size
                if size < prev_offset:
                    prev_offset = 0 # file rotated/truncated
                
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(prev_offset)
                    new_text = f.read()
                    self._file_offsets[str(path)] = f.tell()

                if new_text:
                    for line in new_text.splitlines():
                        self._parse_agent_line(agent_id, line)
            except OSError:
                continue

    def _parse_agent_line(self, agent_id: str, line: str) -> None:
        line_clean = line.strip()
        if not line_clean:
            return

        # Typical line: HH:MM:SS tool | -> terminal(pytest)
        m_tool = re.search(r"tool\s+\|\s+->\s+(\w+)\((.*?)\)", line_clean)
        m_think = re.search(r"think\s+\|\s+(.*)", line_clean)
        m_res = re.search(r"result\s+\|\s+(\w+)\s+(ok|ERROR)\s+(.*)", line_clean)

        if m_tool:
            tool_name = m_tool.group(1)
            call_preview = m_tool.group(0)
            self.update_subagent(
                agent_id,
                status="TOOL_EXEC",
                active_tool=tool_name,
                last_action=call_preview
            )
            self.emit_log(agent_id, "tool", call_preview)
        elif m_think:
            thought = m_think.group(1)[:120]
            self.update_subagent(
                agent_id,
                status="THINKING",
                last_action=thought
            )
        elif m_res:
            res_summary = m_res.group(0)[:120]
            self.emit_log(agent_id, "exec", res_summary)
            self.update_subagent(
                agent_id,
                status="THINKING",
                last_action=res_summary
            )
        else:
            self.emit_log(agent_id, "stdout", line_clean[:120])
