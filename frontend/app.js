/**
 * Overseer — High-Precision 2D Anime Chibi Telemetry Visualizer.
 * Zero-bloat, 60 FPS HTML5 Canvas engine with real-time SSE streaming.
 */
(() => {
  "use strict";

  // --- DOM REFERENCES ---
  const canvas = document.getElementById("topologyCanvas");
  const ctx = canvas.getContext("2d");
  const terminalFeed = document.getElementById("terminalFeed");
  const subagentsContainer = document.getElementById("subagentsContainer");
  const hudClock = document.getElementById("hudClock");
  const connStatus = document.getElementById("connStatus");
  const connText = document.getElementById("connText");
  const countActive = document.getElementById("countActive");
  const countIdle = document.getElementById("countIdle");
  const countStuck = document.getElementById("countStuck");
  const countError = document.getElementById("countError");
  const mainStatusBadge = document.getElementById("mainStatusBadge");
  const mainCurrentTask = document.getElementById("mainCurrentTask");
  const mainActiveTool = document.getElementById("mainActiveTool");
  const metricActiveAgents = document.getElementById("metricActiveAgents");
  const metricWave = document.getElementById("metricWave");
  const metricDriftGate = document.getElementById("metricDriftGate");
  const metricTestSuite = document.getElementById("metricTestSuite");
  const subagentCountPill = document.getElementById("subagentCountPill");

  // --- STATE ---
  let width, height;
  let supervisor = {
    x: 0, y: 0,
    status: "ORCHESTRATING",
    task: "Monitoring agent fleet telemetry.",
    activeTool: "listener",
    blinkTimer: 0
  };
  let subagents = [];
  let packets = [];
  let particles = [];
  let sseSource = null;
  let isSimulating = false;

  // --- RESIZE CANVAS ---
  function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    width = rect.width;
    height = rect.height;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    ctx.scale(dpr, dpr);

    supervisor.x = width / 2;
    supervisor.y = height / 2;
    repositionNodes();
  }
  window.addEventListener("resize", resizeCanvas);

  function repositionNodes() {
    if (subagents.length === 0) return;
    const radius = Math.min(width, height) * 0.33;
    const step = (Math.PI * 2) / subagents.length;

    subagents.forEach((sa, i) => {
      const angle = i * step - Math.PI / 2;
      sa.targetX = supervisor.x + Math.cos(angle) * radius;
      sa.targetY = supervisor.y + Math.sin(angle) * radius;
      if (!sa.x) {
        sa.x = sa.targetX;
        sa.y = sa.targetY;
      }
    });
  }

  // --- PROCEDURAL 2D ANIME CHIBI RENDERER ---
  function drawChibi(ctx, x, y, state, role, type, timeSec, label) {
    ctx.save();
    ctx.translate(x, y);

    const isBlinking = Math.sin(timeSec * 1.5 + x) > 0.94;
    const breathe = Math.sin(timeSec * 3) * 1.5;

    // 1. Aura / Status Ring
    ctx.beginPath();
    let ringColor = "rgba(56, 189, 248, 0.25)";
    if (state === "TOOL_EXEC") ringColor = "rgba(16, 185, 129, 0.3)";
    if (state === "STUCK_ALERT") ringColor = "rgba(245, 158, 11, 0.4)";
    if (state === "ATTACKING" || type === "reviewer") ringColor = "rgba(244, 63, 94, 0.35)";

    ctx.arc(0, 4, 30 + Math.sin(timeSec * 4) * 2, 0, Math.PI * 2);
    ctx.strokeStyle = ringColor;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // 2. Body / Clothes
    ctx.fillStyle = type === "reviewer" ? "#881337" : (type === "supervisor" ? "#0f172a" : "#1e293b");
    ctx.beginPath();
    ctx.roundRect(-12, 10 + breathe, 24, 18, [4, 4, 8, 8]);
    ctx.fill();

    // Collar / Scarf
    ctx.fillStyle = type === "reviewer" ? "#e11d48" : (type === "supervisor" ? "#0284c7" : "#059669");
    ctx.fillRect(-8, 9 + breathe, 16, 4);

    // 3. Head & Skin
    ctx.beginPath();
    ctx.arc(0, -4 + breathe, 18, 0, Math.PI * 2);
    ctx.fillStyle = "#ffe4d6";
    ctx.fill();

    // Anime Blush Cheeks
    ctx.fillStyle = "rgba(251, 113, 133, 0.45)";
    ctx.beginPath();
    ctx.arc(-11, -1 + breathe, 3.5, 0, Math.PI * 2);
    ctx.arc(11, -1 + breathe, 3.5, 0, Math.PI * 2);
    ctx.fill();

    // 4. Anime Hair (Stylized bangs & locks)
    ctx.fillStyle = type === "reviewer" ? "#4c0519" : (type === "supervisor" ? "#0369a1" : "#0f766e");
    ctx.beginPath();
    // Back hair
    ctx.arc(0, -6 + breathe, 20, Math.PI * 0.9, Math.PI * 2.1);
    ctx.fill();

    // Front bangs
    ctx.beginPath();
    ctx.moveTo(-18, -8 + breathe);
    ctx.quadraticCurveTo(-10, 4 + breathe, -6, -4 + breathe);
    ctx.quadraticCurveTo(0, 5 + breathe, 4, -4 + breathe);
    ctx.quadraticCurveTo(12, 4 + breathe, 18, -8 + breathe);
    ctx.quadraticCurveTo(0, -22 + breathe, -18, -8 + breathe);
    ctx.fill();

    // 5. Anime Eyes & Expressions
    if (state === "STUCK_ALERT") {
      // Dizzy Spiral / Sleeping flat lines
      ctx.strokeStyle = "#b45309";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(-10, -5 + breathe); ctx.lineTo(-4, -5 + breathe);
      ctx.moveTo(4, -5 + breathe); ctx.lineTo(10, -5 + breathe);
      ctx.stroke();

      // Sweat Drop
      ctx.fillStyle = "#38bdf8";
      ctx.beginPath();
      ctx.arc(14, -14 + breathe, 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Floating Zzz Bubble
      ctx.font = "bold 11px 'JetBrains Mono'";
      ctx.fillStyle = "#f59e0b";
      ctx.fillText("Zzz...", 16, -18 - (timeSec * 8) % 12);
    } else if (state === "COMPLETED" || state === "DONE") {
      // Joyful Crescent Eyes (^ ^)
      ctx.strokeStyle = "#047857";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(-7, -4 + breathe, 4, Math.PI * 1.1, Math.PI * 1.9);
      ctx.arc(7, -4 + breathe, 4, Math.PI * 1.1, Math.PI * 1.9);
      ctx.stroke();

      // Cute smile
      ctx.beginPath();
      ctx.arc(0, 3 + breathe, 3, 0, Math.PI);
      ctx.stroke();
    } else if (isBlinking) {
      // Cute Closed Blink Line
      ctx.strokeStyle = "#1e293b";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(-7, -4 + breathe, 4, Math.PI * 1.1, Math.PI * 1.9);
      ctx.arc(7, -4 + breathe, 4, Math.PI * 1.1, Math.PI * 1.9);
      ctx.stroke();
    } else {
      // Big Expressive Glossy Anime Eyes
      const eyeColor = type === "reviewer" ? "#e11d48" : (type === "supervisor" ? "#0284c7" : "#10b981");

      // Left Eye
      ctx.beginPath();
      ctx.ellipse(-7, -5 + breathe, 3.5, 5, 0, 0, Math.PI * 2);
      ctx.fillStyle = eyeColor;
      ctx.fill();
      ctx.fillStyle = "#ffffff";
      ctx.beginPath(); // Glossy highlight
      ctx.arc(-8, -7 + breathe, 1.5, 0, Math.PI * 2);
      ctx.fill();

      // Right Eye
      ctx.beginPath();
      ctx.ellipse(7, -5 + breathe, 3.5, 5, 0, 0, Math.PI * 2);
      ctx.fillStyle = eyeColor;
      ctx.fill();
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(6, -7 + breathe, 1.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // 6. Action Props & Props per State
    if (type === "supervisor") {
      // Tactical Hologram Visor & Floating Screen
      ctx.fillStyle = "rgba(56, 189, 248, 0.25)";
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(-14, 14 + breathe, 28, 14, 2);
      ctx.fill();
      ctx.stroke();

      // Hologram lines
      ctx.fillStyle = "#38bdf8";
      ctx.fillRect(-10, 17 + breathe, 12, 2);
      ctx.fillRect(-10, 21 + breathe, 20, 2);
    } else if (state === "TOOL_EXEC") {
      // Cyber Laptop & Rapid Typing Hands
      ctx.fillStyle = "#0f172a";
      ctx.strokeStyle = "#10b981";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(-14, 14 + breathe, 28, 12, 2);
      ctx.fill();
      ctx.stroke();

      // Glowing screen reflection
      ctx.fillStyle = "rgba(16, 185, 129, 0.4)";
      ctx.fillRect(-12, 16 + breathe, 24, 7);

      // Rapid Typing Hands (Alternating motion)
      const handOffset = Math.sin(timeSec * 25) * 2;
      ctx.fillStyle = "#ffe4d6";
      ctx.beginPath();
      ctx.arc(-8, 15 + breathe + handOffset, 2.5, 0, Math.PI * 2);
      ctx.arc(8, 15 + breathe - handOffset, 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Floating Code Particle Glyphs
      if (Math.random() < 0.2 && particles.length < 25) {
        particles.push({
          x: x + (Math.random() * 20 - 10),
          y: y + 10,
          vy: -0.8 - Math.random() * 0.8,
          alpha: 1.0,
          text: ["{ }", "λ", "=>", "pytest", "def"][Math.floor(Math.random() * 5)]
        });
      }
    } else if (state === "THINKING") {
      // Animated Question Mark / Gear
      ctx.font = "bold 13px 'JetBrains Mono'";
      ctx.fillStyle = "#a855f7";
      ctx.fillText("?", 14, -14 + Math.sin(timeSec * 5) * 3);
    } else if (type === "reviewer" || state === "ATTACKING") {
      // Crimson Scanner Targeting Line
      ctx.save();
      ctx.rotate(timeSec * 2);
      ctx.strokeStyle = "rgba(244, 63, 94, 0.5)";
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(28, 0);
      ctx.stroke();
      ctx.restore();
    }

    // 7. Name & Role Labels
    ctx.font = "bold 11px 'JetBrains Mono'";
    ctx.fillStyle = "#e2e8f0";
    ctx.textAlign = "center";
    ctx.fillText(label, 0, 36);

    ctx.font = "9px 'JetBrains Mono'";
    ctx.fillStyle = "#8496ae";
    ctx.fillText(role, 0, 48);

    ctx.restore();
  }

  // --- ANIMATION LOOP ---
  function animate() {
    ctx.clearRect(0, 0, width, height);
    const nowSec = performance.now() / 1000;

    // Smooth movement for subagent nodes
    subagents.forEach(sa => {
      sa.x += (sa.targetX - sa.x) * 0.1;
      sa.y += (sa.targetY - sa.y) * 0.1;
    });

    // 1. Draw connection links
    subagents.forEach(sa => {
      ctx.beginPath();
      ctx.moveTo(supervisor.x, supervisor.y);
      ctx.lineTo(sa.x, sa.y);
      ctx.strokeStyle = sa.type === "reviewer" ? "rgba(244, 63, 94, 0.25)" : "rgba(56, 189, 248, 0.2)";
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);
    });

    // 2. Draw Packet Particles
    for (let i = packets.length - 1; i >= 0; i--) {
      const p = packets[i];
      p.progress += p.speed;
      const curX = p.startX + (p.targetX - p.startX) * p.progress;
      const curY = p.startY + (p.targetY - p.startY) * p.progress;

      ctx.beginPath();
      ctx.arc(curX, curY, 3, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.shadowColor = p.color;
      ctx.shadowBlur = 6;
      ctx.fill();
      ctx.shadowBlur = 0;

      if (p.progress >= 1) packets.splice(i, 1);
    }

    // Random bursts
    if (subagents.length > 0 && Math.random() < 0.08) {
      const target = subagents[Math.floor(Math.random() * subagents.length)];
      packets.push({
        startX: supervisor.x, startY: supervisor.y,
        targetX: target.x, targetY: target.y,
        progress: 0, speed: 0.02 + Math.random() * 0.015,
        color: target.type === "reviewer" ? "#f43f5e" : "#38bdf8"
      });
    }

    // 3. Draw Floating Code Particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const cp = particles[i];
      cp.y += cp.vy;
      cp.alpha -= 0.02;
      ctx.font = "9px 'JetBrains Mono'";
      ctx.fillStyle = `rgba(16, 185, 129, ${Math.max(0, cp.alpha)})`;
      ctx.fillText(cp.text, cp.x, cp.y);
      if (cp.alpha <= 0) particles.splice(i, 1);
    }

    // 4. Draw Supervisor Commander Chibi
    drawChibi(ctx, supervisor.x, supervisor.y, supervisor.status, "Orchestrator", "supervisor", nowSec, "SUPERVISOR");

    // 5. Draw Subagent Chibis
    subagents.forEach(sa => {
      drawChibi(ctx, sa.x, sa.y, sa.status, sa.role || "Worker", sa.type || "worker", nowSec, sa.name || sa.id);
    });

    requestAnimationFrame(animate);
  }

  // --- TERMINAL LOG HELPER ---
  function appendLog(tag, msg) {
    const entry = document.createElement("div");
    entry.className = "log-entry";
    const now = new Date().toTimeString().split(" ")[0];
    entry.innerHTML = `
      <span class="log-time">[${now}]</span>
      <span class="log-tag ${tag}">[${tag.toUpperCase()}]</span>
      <span class="log-msg">${escapeHtml(msg)}</span>
    `;
    terminalFeed.appendChild(entry);
    terminalFeed.scrollTop = terminalFeed.scrollHeight;
  }

  function escapeHtml(str) {
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  document.getElementById("btnClearLog").addEventListener("click", () => {
    terminalFeed.innerHTML = "";
  });

  // --- UPDATE SIDEBAR & HEALTH STRIP ---
  function updateRosterAndMetrics() {
    let active = 0, idle = 0, stuck = 0, err = 0;

    subagentsContainer.innerHTML = "";
    if (subagents.length === 0) {
      subagentsContainer.innerHTML = `<div style="color:var(--text-dim);font-size:10px;padding:12px;text-align:center;">No subagents in this stage.</div>`;
    } else {
      subagents.forEach(sa => {
        if (sa.status === "TOOL_EXEC" || sa.status === "THINKING") active++;
        else if (sa.status === "IDLE") idle++;
        else if (sa.status === "STUCK_ALERT") stuck++;
        else if (sa.status === "ERROR") err++;

        const card = document.createElement("div");
        card.className = `worker-card ${sa.status.toLowerCase()} ${sa.type}`;
        card.innerHTML = `
          <div class="worker-card-head">
            <span class="worker-id">${escapeHtml(sa.name || sa.id)}</span>
            <span class="status-badge ${sa.status.toLowerCase()}">${sa.status}</span>
          </div>
          <div class="worker-task-desc">${escapeHtml(sa.current_task || "Executing task")}</div>
          ${sa.last_action ? `<div class="worker-action-code"><code>${escapeHtml(sa.last_action)}</code></div>` : ""}
        `;
        subagentsContainer.appendChild(card);
      });
    }

    countActive.textContent = active;
    countIdle.textContent = idle;
    countStuck.textContent = stuck;
    countError.textContent = err;
    metricActiveAgents.textContent = active;
    subagentCountPill.textContent = `${subagents.length} WORKERS`;
  }

  // --- SSE CLIENT WITH AUTO-RECONNECT (AC-3, AC-11) ---
  function initSSE() {
    if (isSimulating) return;

    if (sseSource) {
      sseSource.close();
    }

    connStatus.className = "conn-status-badge reconnecting";
    connText.textContent = "CONNECTING...";

    sseSource = new EventSource("/api/telemetry/stream");

    sseSource.onopen = () => {
      connStatus.className = "conn-status-badge connected";
      connText.textContent = "CONNECTED (SSE)";
    };

    sseSource.addEventListener("snapshot", (e) => {
      try {
        const snap = JSON.parse(e.data);
        handleSnapshot(snap);
      } catch (err) {}
    });

    sseSource.addEventListener("agent_update", (e) => {
      try {
        const sa = JSON.parse(e.data);
        handleAgentUpdate(sa);
      } catch (err) {}
    });

    sseSource.addEventListener("log", (e) => {
      try {
        const item = JSON.parse(e.data);
        appendLog(item.tag || "exec", item.message || "");
      } catch (err) {}
    });

    sseSource.onerror = () => {
      connStatus.className = "conn-status-badge reconnecting";
      connText.textContent = "RECONNECTING...";
      sseSource.close();
      // Fallback polling (AC-11)
      setTimeout(() => {
        fetch("/api/telemetry/snapshot")
          .then(r => r.json())
          .then(snap => handleSnapshot(snap))
          .catch(() => {});
        initSSE();
      }, 2000);
    };
  }

  function handleSnapshot(snap) {
    if (snap.supervisor) {
      supervisor.status = snap.supervisor.status;
      mainStatusBadge.textContent = snap.supervisor.status;
      mainCurrentTask.textContent = snap.supervisor.current_task;
      mainActiveTool.textContent = snap.supervisor.active_tool;
    }
    if (snap.metrics) {
      metricWave.textContent = snap.metrics.wave;
      metricDriftGate.textContent = snap.metrics.drift_gate;
      metricTestSuite.textContent = snap.metrics.test_suite;
    }
    if (Array.isArray(snap.subagents)) {
      subagents = snap.subagents.map(sa => ({
        ...sa,
        x: 0, y: 0, targetX: 0, targetY: 0
      }));
      repositionNodes();
      updateRosterAndMetrics();
    }
  }

  function handleAgentUpdate(sa) {
    const idx = subagents.findIndex(item => item.id === sa.id);
    if (idx >= 0) {
      subagents[idx] = { ...subagents[idx], ...sa };
    } else {
      subagents.push({ ...sa, x: 0, y: 0, targetX: 0, targetY: 0 });
      repositionNodes();
    }
    updateRosterAndMetrics();
  }

  // --- DEMO / SIMULATION HOOKS ---
  document.getElementById("btnSimWave1").addEventListener("click", () => {
    isSimulating = true;
    if (sseSource) sseSource.close();
    connStatus.className = "conn-status-badge connected";
    connText.textContent = "DEMO: WAVE 1";
    supervisor.status = "ORCHESTRATING";
    mainStatusBadge.textContent = "ORCHESTRATING";
    mainCurrentTask.textContent = "Parallel Wave 1: 3 workers executing records, stats, report.";
    mainActiveTool.textContent = "delegate_task(action='list')";
    metricWave.textContent = "WAVE 1 / PARALLEL";
    subagents = [
      { id: "sa-1", name: "Worker A", role: "CSV Parser", status: "TOOL_EXEC", type: "worker", current_task: "TDD: parsing rows & numeric validation", last_action: "pytest tests/test_records.py" },
      { id: "sa-2", name: "Worker B", role: "Stats Engine", status: "TOOL_EXEC", type: "worker", current_task: "TDD: categories, totals & tie-breaking", last_action: "patch tally/stats.py" },
      { id: "sa-3", name: "Worker C", role: "Formatter", status: "TOOL_EXEC", type: "worker", current_task: "TDD: plain text ASCII layout", last_action: "pytest tests/test_report.py" }
    ];
    repositionNodes();
    updateRosterAndMetrics();
    appendLog("tool", "Wave 1: Dispatched 3 parallel subagents matching CONTRACT.md");
  });

  document.getElementById("btnSimStuck").addEventListener("click", () => {
    isSimulating = true;
    if (subagents.length > 0) {
      subagents[0].status = "STUCK_ALERT";
      subagents[0].current_task = "STUCK DETECTED: 75s without tool output (API Timeout)";
      subagents[0].last_action = "Waiting on upstream LLM response...";
      updateRosterAndMetrics();
      appendLog("warn", "STUCK ALERT: Worker A silent for 75s. Upstream API lag detected.");
    }
  });

  document.getElementById("btnSimReview").addEventListener("click", () => {
    isSimulating = true;
    metricWave.textContent = "WAVE 3 / REVIEW";
    subagents = [
      { id: "sa-hunter", name: "Reviewer Ninja", role: "Adversarial Hunter", status: "ATTACKING", type: "reviewer", current_task: "Probing boundaries: path traversal, timing oracles, race conditions", last_action: "pytest tests/test_adversarial.py" }
    ];
    repositionNodes();
    updateRosterAndMetrics();
    appendLog("warn", "Adversarial Reviewer active: attacking boundary contracts...");
  });

  document.getElementById("btnSimAllGreen").addEventListener("click", () => {
    isSimulating = true;
    metricWave.textContent = "SHIP COMPLETE";
    metricDriftGate.textContent = "AC-1..11 PASSED";
    metricTestSuite.textContent = "19/19 PASSED (0.03s)";
    subagents.forEach(sa => sa.status = "COMPLETED");
    updateRosterAndMetrics();
    appendLog("pass", "LOCAL CI: ALL GREEN. 19 tests passed, 0 errors, ready to ship.");
  });

  // --- CLOCK ---
  function updateClock() {
    hudClock.textContent = new Date().toTimeString().split(" ")[0] + " WIB";
  }
  setInterval(updateClock, 1000);
  updateClock();

  // --- BOOTSTRAP ---
  resizeCanvas();
  animate();
  initSSE();
})();
