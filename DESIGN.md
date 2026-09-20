# DESIGN.md — Overseer

## Subject / Audience / Job
- **Subject:** Autonomous AI multi-agent orchestration and telemetry monitor.
- **Audience:** Developers running multi-agent workflows who are tired of terminal scrolling blindness.
- **Job:** Instant, high-density situational awareness of what the supervisor and background subagents are executing, what files they touch, and whether any agent is stuck or timing out.

## Voice
- **Tactical · Precise · Obsidian-Clean.**
- Clean, restrained, professional observability interface. No fluff, no marketing slogans, no decorative slop.

## Token Spine
- **Surfaces:**
  - Base Dark: `#070a0f`
  - Card/HUD Layer: `#0d131d`
  - Panel Elevation: `#111a27`
  - Border Dim: `#1e2c3f`
  - Border Bright: `#2f4563`
- **Semantic Accents:**
  - Supervisor / Main: Tactical Cyan `#38bdf8`
  - Active Worker / Success: Laser Emerald `#10b981`
  - Warning / Stuck / High Latency: Alert Amber `#f59e0b`
  - Error / Adversarial Attack: Threat Rose `#f43f5e`
- **Typography:**
  - Code & Metrics: `'JetBrains Mono', 'Fira Code', monospace`
  - Headers & Brand: `'Space Grotesk', system-ui, sans-serif`
- **Spacing:** 4px, 8px, 12px, 16px, 24px
- **Radius:** 3px (badges), 4px (buttons/cards), 6px (containers)
- **Shadows:** Crisp 1px borders paired with subtle 8px neon drop glow on active nodes.

## Signature Bet
**Tactical 2D Neural Canvas Topology with Orbital Radar, Flow Particles & 2-Second Fleet Health Bar.**
Instead of a boring table or generic SaaS card grid, Overseer visualizes the agent hierarchy as an animated orbital constellation:
- Top Strip (2-Second Glanceable Health): Total agents count, Active, Idle, Stuck Alert, and Error counts with colored badge counters.
- Center: Supervisor agent with 360° radar sweep and pulsating activity core.
- Orbit: Satellite nodes for each subagent, color-coded by role (Worker vs Reviewer).
- Edges: Dynamic directional particle lasers showing live message exchanges, task dispatches, and return summaries.
- Stuck Detection: An agent that takes > 60 seconds without emitting events pulses with an amber reticle and warning ring; at > 120s it escalates to critical threat state.
- Split-View Feed: Bottom-right pane provides a live, syntax-highlighted streaming execution trace of tool calls and command outputs.

## Anti-Slop Test & Banned Tells
- [x] No purple/blue hero gradient.
- [x] No Inter/Roboto defaults by reflex; JetBrains Mono + Space Grotesk used.
- [x] No emoji buttons; clean SVG/Unicode glyphs (`◈`, `☵`, `⚡`).
- [x] No cards inside cards.
- [x] No pure `#000000` flat black.
- [x] High visual density: fits within 100vh viewport without unnecessary scroll.
