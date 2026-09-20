# HANDOFF.md — Planning → Execution Contract (Overseer)

> Produced by `sop-planning` (P6), consumed by `sop-execution` (E0).
> Every section is filled, or marked `N/A — <reason>`. **"TBD" is forbidden.**
> Frozen at handoff; changes are amendments recorded in §12.

---

## 1. Identity

| Field | Value |
|-------|-------|
| Project | Overseer — Real-Time Agent Telemetry & Orchestration Monitor |
| Tier | T1 (Portfolio client-grade, deployable, zero bloat) |
| Ceremony level | M (Standard: Telemetry engine + SSE + Canvas HUD) |
| Spec level | spec-anchored |
| Team size | solo |
| Stack | Python 3.12+ stdlib (http.server, threading, json), HTML5 Canvas, Vanilla CSS/JS, Docker |
| Constitution | CONSTITUTION.md |
| Handoff date | 2026-09-20 |
| Frozen by | Samid & Hermes |

## 2. Goal & Scope

- **Goal (one sentence):** A lightweight, deployable visual mission control dashboard that streams telemetry from Hermes and autonomous background subagents, rendering a 2D neural topology canvas and detecting stuck agents.
- **In scope:**
  - Python stdlib daemon: log/state watcher, stuck detection, SSE broadcaster, static file server.
  - REST API: `GET /api/telemetry/snapshot`, `POST /api/telemetry/event`.
  - Real-time SSE stream: `GET /api/telemetry/stream`.
  - Tactical Canvas HUD: Supervisor node, satellite subagent nodes, laser data stream particles, live terminal feed.
  - Slim Dockerfile (< 50MB, non-root user).
  - Drift gate & local CI scripts.
- **Out of scope (explicit):**
  - Database persistence (no SQLite/Postgres needed; runs purely in-memory/filesystem).
  - Agent process kill controls (read-only telemetry observer; does not terminate host processes).
  - Cloud user accounts / multi-tenant authentication (local developer tool / LAN deploy).
- **Definition of done (tier-based):**
  - All AC-1..AC-11 pass via pytest.
  - Drift gate PASS.
  - Docker image builds and runs non-root.
  - Zero console errors in browser.

## 2b. Boundaries

- **Always:** Read-only observation of agent files; send security headers on every response; sanitize static file paths against traversal.
- **Ask first:** Adding external heavyweight dependencies (e.g. databases, heavy frontend frameworks).
- **Never:** Block the execution of monitored agents; log credentials or API keys; allow directory traversal out of project root.

## 2c. Capability Map
`N/A — Single capability system (agent telemetry observability).`

## 3. Prompt-Roast Result

- Six-axis score (Goal/Context/Scope/Success/Constraints/Ambiguity): 12 / 12
- Gaps named: None (all core parameters established).
- False premise checked against repo: Checked — fresh directory created at `/mnt/data/01_Projects/Porto/overseer`.
- **Assumptions surfaced (Rulings):**
  - R-1: Stdlib Python backend chosen for zero-dependency portability and instant boot.
  - R-2: Server-Sent Events (SSE) chosen over WebSockets because telemetry is primarily unidirectional (server -> client), avoiding WS handshake overhead.
  - R-3: Telemetry sources from local directory `~/.hermes/cache/delegation/live/` or custom `--watch-dir`.
- **Clarify gate (P1.5):** No material ambiguity open — yes.

## 4. Design Contract (UI only)

**4a. `DESIGN.md` spine**
- Subject / audience / primary job: Multi-agent developers / instant situational awareness of agent states without terminal scrolling blindness.
- Voice: Tactical · Precise · Obsidian-Clean.
- Token spine: Base Dark `#070a0f`, Panel `#111a27`, Border `#1e2c3f`, Cyan `#38bdf8`, Emerald `#10b981`, Amber `#f59e0b`, Rose `#f43f5e`. Typography: JetBrains Mono + Space Grotesk.
- **Signature bet:** Tactical 2D Neural Canvas Topology with rotating 360° radar sweep and directional laser data stream particles connecting supervisor to worker satellites.
- Knobs: DESIGN_VARIANCE: 4, VISUAL_DENSITY: 8, MOTION_INTENSITY: 5.
- **Anti-Slop Test:** Passed ("would you believe AI made this?" → No).
- Banned-pattern check: Verified (no purple gradients, no emoji buttons, no nested cards).

**4b. UI hygiene**
- Playbook loaded: `reference/operate.md` (Observability & dashboard).
- **Design system:** Establish (defined in `DESIGN.md` token spine).
- Figma involved: N/A.
- **States required:**
  - Empty state: "No active agents running. Ready for dispatch."
  - Loading: Reconnecting pulse indicator.
  - Error: Threat Rose badge on agent failure.
  - Warning: Alert Amber pulse ring on stuck agent (>60s silence).
  - Active: Laser Emerald and Tactical Cyan pulses.
- UI detail checklist items in scope:
  - Empty states, offline/reconnecting banner, dark mode token spine, keyboard escape, responsive 100vh canvas.
- UI detail checklist items deliberately excluded:
  - i18n (single language: developer English/Indo), SEO/OG tags (local operational dashboard).

**4c. UX floor (P2.4)**
- User flow: Described in `docs/ux-floor.md`.
- Nielsen heuristics: H1 status visibility & H5 error prevention prioritized.
- Microcopy: Concrete operational badges (`TOOL_EXEC`, `STUCK_ALERT`, `COMPLETED`).
- UX coverage walked: Onboarding (empty state), Incident recovery (reconnect banner).

**4d. Diagrams as code (P2.6)**
- ERD: N/A (no database tables).
- User flow: `docs/diagrams/diagrams.md` §1 & §3.
- Sequence: `docs/diagrams/diagrams.md` §2.
- Architecture: `docs/diagrams/diagrams.md` §1.
- All in-repo, versioned Mermaid sources: yes.

## 5. Acceptance Criteria — EARS, binary-testable

See `docs/spec.md` for AC-1 through AC-11.
- AC-1: Static frontend served (200 text/html) -> `tests/test_server.py::test_serve_frontend`
- AC-2: Telemetry snapshot JSON -> `tests/test_server.py::test_get_telemetry_snapshot`
- AC-3: SSE stream connection -> `tests/test_server.py::test_sse_stream_connect`
- AC-4: Broadcast log event -> `tests/test_telemetry.py::test_broadcast_log_event`
- AC-5: Stuck agent alert (>60s) -> `tests/test_telemetry.py::test_stuck_agent_detection`
- AC-6: Ingest valid event -> `tests/test_server.py::test_ingest_event_valid`
- AC-7: Ingest malformed event (400) -> `tests/test_server.py::test_ingest_event_malformed_400`
- AC-8: Path traversal blocked (404) -> `tests/test_server.py::test_path_traversal_blocked_404`
- AC-9: Security headers -> `tests/test_server.py::test_security_headers_present`
- AC-10: Frontend renders subagents -> `tests/test_frontend.py::test_frontend_renders_subagents`
- AC-11: Frontend reconnect handling -> `tests/test_frontend.py::test_frontend_reconnect_handling`

## 5b. Drift Contract (spec-drift-gate)

- Spec artifact path: `docs/spec.md`
- Criteria live in: `docs/spec.md` (AC-1..AC-11)
- Rule: spec + code land in the **same commit**; divergence is a blocking merge condition.
- Drift gate command: `bash scripts/drift-gate.sh`

## 6. Feature Completeness (decided)

- **In scope:**
  - Health check endpoint (`GET /healthz`).
  - Structured logging.
  - Live SSE broadcasting.
  - Automated directory watcher.
  - Security headers & path containment.
  - Standalone Docker image.
- **Deliberate exclusions:**
  - User authentication/login (local developer tool).
  - Database persistence (zero bloat, in-memory aggregation).
- **Security/reliability rows:**
  - Security headers: CSP, X-Frame-Options, nosniff.
  - Containment: Path.resolve() containment guard (hazard #26).
  - SLO: p95 broadcast latency < 100ms.

## 7. Interfaces & File Paths

- **Files to create:**
  - `backend/telemetry.py`: TelemetryManager, log file scanner, stuck detector.
  - `backend/server.py`: HTTP handler, SSE broadcaster, static server.
  - `backend/serve.py`: Production entrypoint.
  - `frontend/index.html`: Mission Control HUD markup.
  - `frontend/styles.css`: Tactical cyber styling.
  - `frontend/app.js`: Canvas topology engine & SSE client.
  - `tests/test_telemetry.py`: Unit tests for telemetry logic.
  - `tests/test_server.py`: API and HTTP tests.
  - `tests/test_frontend.py`: DOM/UI logic tests.
  - `tests/e2e/test_overseer_e2e.py`: End-to-end integration test.
  - `scripts/drift_gate.py` & `scripts/drift-gate.sh`: Drift gate validator.
  - `scripts/local-ci.sh`: CI verification suite.
  - `deploy/Dockerfile` & `deploy/compose.yaml`: Containerization.
  - `README.md`, `.env.example`, `.gitignore`.

## 7b. Interface Contracts

- **Layers & responsibilities:**
  - Frontend: Interactive Canvas rendering & SSE event consumption.
  - Backend: Log ingestion, state aggregation, SSE broadcast, HTTP routing.
- **Boundary contract:** `contracts/openapi.yaml`
- **Error envelope:** `{"error": {"code": str, "message": str}}`
- **Enforcement:** Contract test in `tests/test_server.py` validates schema and status codes.

## 8. Constraints (verbatim)

- Python 3.12+ stdlib only for backend (zero runtime pip dependencies).
- Frontend: Vanilla HTML5 Canvas + JS (no build step, no node_modules required to run).
- Memory footprint: < 30 MB RAM.
- Port: Default 7788 (configurable via `PORT` env).

## 9. Plan Artifact

- Plan required? yes (multi-task wave execution).
- Path to plan file: `docs/plan.md`
- Global constraints section included verbatim: yes.

## 10. Factory Bootstrap

- Bootstrap run? Deferred — stdlib project, factory tooling wired directly in `scripts/local-ci.sh` (secret scan, syntax check, pytest, drift gate).
- Result recorded: yes.

## 11. Accepted Risks

| Risk | Why accepted | Owner |
|------|--------------|-------|
| In-memory state only | Telemetry is ephemeral; agent logs are stored on disk by Hermes | Samid |
| No auth | Local tool designed for localhost/internal LAN | Samid |

## 12. Amendments (changelog)

| Date | Change | Reason | Re-approved by |
|------|--------|--------|----------------|
| | | | |

## 13. P7 Readiness Gate

- [x] Tier + team + ceremony level written (§1)
- [x] Spec level declared (§1)
- [x] Constitution present (§1)
- [x] Boundaries recorded (§2b)
- [x] Capability map N/A (§2c)
- [x] Prompt-roast scored (12/12) (§3)
- [x] False premise checked (§3)
- [x] Assumptions surfaced & Rulings recorded (§3)
- [x] Clarify gate passed (§3)
- [x] Brainstorm approval obtained (§2/P1)
- [x] Design contract present (`DESIGN.md`) (§4)
- [x] Acceptance criteria EARS-shaped with Verify (§5)
- [x] Drift contract recorded (§5b)
- [x] Feature Completeness walked (§6)
- [x] Security rows named (§6)
- [x] Interfaces exact (§7)
- [x] File paths listed (§7)
- [x] Constraints copied verbatim (§8)
- [x] No TBD/TODO anywhere (§1-13)
- [x] Factory bootstrap deferral stated (§10)
- [x] Spec approved by the human

**Frozen:** ☑  ·  **Handoff path:** `/mnt/data/01_Projects/Porto/overseer/HANDOFF.md`  ·  **Seen by human:** ☑
