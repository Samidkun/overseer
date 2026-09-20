import time
import tempfile
from pathlib import Path
import pytest

from backend.telemetry import TelemetryManager

def test_telemetry_snapshot_structure():
    mgr = TelemetryManager(watch_dir=tempfile.mkdtemp())
    snapshot = mgr.get_snapshot()
    assert "supervisor" in snapshot
    assert "subagents" in snapshot
    assert "metrics" in snapshot
    assert snapshot["supervisor"]["status"] in ("IDLE", "ORCHESTRATING", "PLANNING")

def test_broadcast_log_event():
    mgr = TelemetryManager(watch_dir=tempfile.mkdtemp())
    received = []
    mgr.add_subscriber(lambda event_type, data: received.append((event_type, data)))

    mgr.emit_log(agent_id="sa-01", tag="tool", message="terminal(pytest)")
    assert len(received) == 1
    event_type, payload = received[0]
    assert event_type == "log"
    assert payload["agent_id"] == "sa-01"
    assert payload["tag"] == "tool"
    assert payload["message"] == "terminal(pytest)"
    assert "timestamp" in payload

def test_stuck_agent_detection():
    mgr = TelemetryManager(watch_dir=tempfile.mkdtemp(), stuck_threshold_sec=2)
    # Register active subagent
    mgr.update_subagent("sa-stuck", name="Worker Stalled", role="Parser", status="TOOL_EXEC")
    
    # Immediately check: not stuck
    sub = mgr.get_subagent("sa-stuck")
    assert sub["status"] == "TOOL_EXEC"

    # Sleep past threshold (2s in test)
    time.sleep(2.1)
    mgr.check_stuck_agents()

    sub = mgr.get_subagent("sa-stuck")
    assert sub["status"] == "STUCK_ALERT"
    assert sub["stuck_seconds"] >= 2

def test_log_file_ingestion():
    tmp_dir = Path(tempfile.mkdtemp())
    mgr = TelemetryManager(watch_dir=str(tmp_dir))
    log_file = tmp_dir / "task-0.log"
    
    # Agent writes a line
    log_file.write_text("20:45:00 tool | -> terminal(pytest -q)\n", encoding="utf-8")
    mgr.scan_log_files()

    snapshot = mgr.get_snapshot()
    assert len(snapshot["subagents"]) >= 1
    sa = snapshot["subagents"][0]
    assert sa["id"] == "task-0"
    assert sa["status"] == "TOOL_EXEC"
    assert "terminal" in sa["last_action"]
