# CONSTITUTION — Overseer

1. **Zero-overhead telemetry:** The monitoring daemon must never block, lag, or interfere with the execution of the agents it observes. Reading logs/state is asynchronous and read-only.
2. **Ultra-lean footprint:** The backend must require zero heavy infrastructure (no external Redis/Postgres for base operation). Memory usage under 30MB; container image under 50MB.
3. **Anti-slop design contract:** Strictly uphold `DESIGN.md`. Deep space / cyber-tactical command palette, zero template purple gradients, zero emoji buttons, purposeful motion, responsive 60 FPS Canvas rendering.
4. **Deterministic fail-safe stream:** Server-Sent Events (SSE) stream must recover state immediately upon client reconnection with zero missed active alerts.
5. **Path containment:** The telemetry watcher must strictly contain file access within declared log/project directories (path traversal guard, hazard #26).
6. **Same-commit rule:** Any contract, schema, or diagram change lands with its accompanying test and documentation in the same commit.
