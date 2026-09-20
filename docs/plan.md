# PLAN — Overseer (P5)

Dependency-ordered execution plan. Each task follows strict TDD (RED-first).

| # | Task | Ceremony | Depends on | Done when |
|---|------|----------|------------|-----------|
| T1 | Telemetry Aggregator (`backend/telemetry.py`) | M | — | Log parsing, state caching, stuck detection unit tests GREEN |
| T2 | HTTP Daemon & SSE Router (`backend/server.py`) | M | T1 | Endpoints `/snapshot`, `/stream`, `/event`, static serving GREEN |
| T3 | Frontend Mission Control HUD (`frontend/*`) | M | T2 | Canvas topology, node pulse, SSE auto-reconnect verified |
| T4 | E2E Integration & Drift Gate | M | T2, T3 | 11 ACs verified in drift gate + e2e test passing |
| T5 | Container Deployment (`Dockerfile`) | S | T2, T3 | Multi-stage slim image built & running non-root |

## Waves (E3)
- **Wave 1:** T1 (Core telemetry & stuck detection engine)
- **Wave 2:** T2 (HTTP server, static containment, SSE broadcast)
- **Wave 3:** T3 (Frontend HUD, live canvas topology, reconnect handler)
- **Wave 4:** T4 & T5 (Drift gate, Local CI, Docker deploy)
