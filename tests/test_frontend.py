import pytest
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

def test_frontend_markup_structure():
    index_html = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
    assert "topologyCanvas" in index_html
    assert "terminalFeed" in index_html
    assert "subagentsContainer" in index_html
    assert "hudProjectName" in index_html

def test_frontend_renders_subagents():
    app_js = (FRONTEND_DIR / "app.js").read_text(encoding="utf-8")
    # Verify subagent rendering and state mapping logic exists
    assert "renderChibi" in app_js or "drawChibi" in app_js
    assert "STUCK_ALERT" in app_js
    assert "TOOL_EXEC" in app_js
    assert "THINKING" in app_js

def test_frontend_reconnect_handling():
    app_js = (FRONTEND_DIR / "app.js").read_text(encoding="utf-8")
    # Verify auto-reconnect and snapshot fallback logic
    assert "EventSource" in app_js
    assert "reconnect" in app_js.lower()
    assert "/api/telemetry/snapshot" in app_js
