# SPEC — Overseer (Agent Telemetry & Orchestration Monitor)
**Level:** spec-anchored · **Tier:** T1 · **Ceremony:** M · **Mode:** solo
**Contract:** contracts/openapi.yaml · **Design:** DESIGN.md

## Goal
A high-density, real-time visual mission control dashboard that streams telemetry from Hermes and autonomous background subagents, rendering a 2D neural topology canvas and detecting stuck agents.

## Scope
- Lightweight backend daemon in Python stdlib (`http.server` + SSE).
- REST API for snapshot `/api/telemetry/snapshot` & event ingestion `/api/telemetry/event`.
- Real-time SSE stream `/api/telemetry/stream`.
- Static frontend server for the tactical HUD (`index.html`, `styles.css`, `app.js`).
- Automated agent log watcher parsing `~/.hermes/cache/delegation/live/`.
- Stuck detection (alerts when an active agent emits nothing for > 60s).
- Production-ready Dockerfile (< 50 MB, non-root user).

## Acceptance Criteria (EARS)

AC-1 (event) WHEN a client requests GET /, THE system SHALL serve the frontend HUD with status 200 and text/html content type.
Verify: tests/test_server.py::test_serve_frontend

AC-2 (event) WHEN a client requests GET /api/telemetry/snapshot, THE system SHALL return the current TelemetrySnapshot JSON matching contracts/openapi.yaml.
Verify: tests/test_server.py::test_get_telemetry_snapshot

AC-3 (event) WHEN a client connects to GET /api/telemetry/stream, THE system SHALL return HTTP 200 with Content-Type text/event-stream.
Verify: tests/test_server.py::test_sse_stream_connect

AC-4 (event) WHEN an agent emits a new tool call or log, THE daemon SHALL format and broadcast a 'log' event over the SSE stream.
Verify: tests/test_telemetry.py::test_broadcast_log_event

AC-5 (state) WHILE an active subagent has zero log activity for > 60 seconds, THE system SHALL mark its status as STUCK_ALERT.
Verify: tests/test_telemetry.py::test_stuck_agent_detection

AC-6 (event) WHEN a client POSTs a valid event to /api/telemetry/event, THE system SHALL accept it with 200 {"ok": true} and broadcast to stream.
Verify: tests/test_server.py::test_ingest_event_valid

AC-7 (unwanted) IF a client POSTs malformed or non-dict JSON to /api/telemetry/event, THEN THE system SHALL return 400 error envelope and SHALL NOT crash.
Verify: tests/test_server.py::test_ingest_event_malformed_400

AC-8 (unwanted) IF a client requests a static path containing traversal sequences (e.g. /../../etc/passwd), THEN THE system SHALL return 404.
Verify: tests/test_server.py::test_path_traversal_blocked_404

AC-9 (ubiquitous) THE system SHALL send security headers (Content-Security-Policy, X-Frame-Options, X-Content-Type-Options) on every HTTP response.
Verify: tests/test_server.py::test_security_headers_present

AC-10 (event) WHEN the frontend processes SSE telemetry, THE UI SHALL render active subagents and update the canvas node topology.
Verify: tests/test_frontend.py::test_frontend_renders_subagents

AC-11 (state) WHILE SSE is disconnected, THE frontend SHALL poll /api/telemetry/snapshot and display a reconnecting indicator.
Verify: tests/test_frontend.py::test_frontend_reconnect_handling

AC-12 (event) WHEN a telemetry snapshot is constructed, THE system SHALL contain supervisor, subagents, and metrics objects.
Verify: tests/test_telemetry.py::test_telemetry_snapshot_structure

AC-13 (event) WHEN an agent writes new output to a live log file, THE daemon SHALL ingest the delta incrementally.
Verify: tests/test_telemetry.py::test_log_file_ingestion

AC-14 (event) WHEN the frontend markup renders, THE DOM SHALL provide the required telemetry elements and topology canvas.
Verify: tests/test_frontend.py::test_frontend_markup_structure

AC-15 (event) WHEN the system runs end-to-end, ALL layers (static, API, ingest, security headers) SHALL operate cleanly without errors.
Verify: tests/e2e/test_overseer_e2e.py::test_full_e2e_lifecycle
