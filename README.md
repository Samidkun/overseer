# Overseer — Real-Time Agent Telemetry & Visualizer Dashboard



<p align="center">
  <img src="docs/screenshots/preview.png" alt="Application Preview" width="100%" style="border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1);" />
</p>

A lightweight, zero-dependency visual mission control for autonomous AI agents (Hermes & background subagents). Built using the Spec-Driven Development (SDD) SOP with an animated 2D Anime Chibi topology canvas.

## Features
- **Procedural 2D Anime Chibi Topology Canvas:** Supervisor Commander at the center, satellite worker chibis (coding, thinking, resting/stuck, attacking), and real-time directional data stream lasers.
- **2-Second Fleet Health Bar:** Instant glanceable status pills: Active, Idle, Stuck Alert, and Error counts.
- **Stuck & Timeout Detection:** Automatically alerts in Amber/Red when an active background subagent hangs or stops emitting tool traces for > 60 seconds.
- **Zero Heavy Infrastructure:** Backend runs on pure Python 3.12+ stdlib (< 20MB RAM); Frontend runs on pure HTML5 Canvas + Vanilla JS (no node_modules required).
- **Auto-Port Fallback:** Automatically selects alternative ports (`7789`, `7790`) if port `7788` is occupied.

## Quickstart

```bash
# 1-Click Launch (starts daemon & opens browser)
./run.sh

# Or start manually:
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python3 -m backend.serve --port 7788
```

Open in browser: `http://localhost:7788`

## Autostart on Boot (Systemd User Service)

To run Overseer in the background automatically when your laptop boots:

```bash
# Link or copy systemd unit to user services
mkdir -p ~/.config/systemd/user/
cp deploy/overseer.service ~/.config/systemd/user/

# Enable and start
systemctl --user daemon-reload
systemctl --user enable --now overseer.service

# Check status
systemctl --user status overseer.service
```

## Running with Docker

```bash
cd deploy
docker compose up -d
```

## Verification & CI

```bash
./scripts/local-ci.sh
```
Runs secret scans, syntax compilation, pytest (17 tests), and the bidirectional specification drift gate.