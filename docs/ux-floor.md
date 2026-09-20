# UX Floor — Overseer (P2.4)

## 1. User Flow & Information Architecture
```text
1. Entry: Open Overseer at http://localhost:7788 (or embedded in IDE/browser window)
   ├── A. Instant Snapshot: Fetch GET /api/telemetry/snapshot (render immediate state)
   └── B. Live Stream: Open SSE EventSource at GET /api/telemetry/stream
2. Monitoring:
   ├── Canvas view: Visual graph of Supervisor + Subagents (idle / executing / stuck)
   ├── Telemetry bar: Active wave, token velocity, test pass count, drift gate status
   └── Tactical feed: Tail of actual tool execution logs (terminal, read, write)
3. Incident Detection:
   └── If subagent silent for > 60s without terminal/tool output:
       └── Status updates to STUCK (amber warning ring + elapsed timer)
4. Recovery:
   └── If connection to daemon drops:
       └── Header shows RECONNECTING with spinner, falls back to polling /snapshot every 2s
```

## 2. Nielsen Usability Heuristics Audit
- **H1 (Status Visibility):** Persistent connection indicator (🟢 CONNECTED / 🟡 RECONNECTING / 🔴 OFFLINE); exact runtime seconds for each agent.
- **H2 (Real World Match):** Uses developer-native terms: *Wave, Subagent, Supervisor, Tool Call, Drift Gate, Stdout*.
- **H5 (Error Prevention):** Read-only telemetry: the dashboard cannot accidentally terminate or corrupt live agent sessions.
- **H8 (Aesthetic & Minimalist):** No decorative clutter. Every pixel conveys status, link topology, or execution trace.
- **H9 (Error Recovery):** Transparent stream reconnects with zero page refresh required.

## 3. Microcopy Rules
- Badges: `IDLE`, `THINKING`, `TOOL_EXEC`, `STUCK_ALERT`, `COMPLETED`.
- Metrics: Specific numbers with units (`19/19 tests`, `0.03s`, `3 workers`).
- Error messages: `Stream connection interrupted. Reconnecting in 2s...`
