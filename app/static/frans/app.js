"use strict";
const $ = (s, el = document) => el.querySelector(s);
const app = $("#app");
let ME = null;

// ---------- helpers ----------
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const MODULE = "frans";
async function api(path, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const r = await fetch(`/api/m/${MODULE}/` + path, opt);
  const data = await r.json().catch(() => ({}));
  if (r.status === 401 || (r.status === 403 && data.error === "must_change")) { location.href = "/"; throw new Error(data.error); }
  if (!r.ok) throw new Error(data.error || "Er ging iets mis");
  return data;
}
function toast(msg, ms = 2600) {
  const t = $("#toast"); t.textContent = msg; t.hidden = false;
  clearTimeout(toast._t); toast._t = setTimeout(() => (t.hidden = true), ms);
}
const pick = a => a[Math.floor(Math.random() * a.length)];
const PRAISE = ["Très bien !", "Parfait !", "Super !", "Bravo !", "Excellent !", "Génial !", "C'est ça !"];
const OOPS = ["Oeps!", "Pas grave, kijk even goed:", "Helaas!", "Dommage!"];
const RANKS = [[0, "Débutant"], [200, "Apprenti"], [500, "Bon élève"], [1000, "Champion"], [2000, "Expert"], [4000, "Maître"], [8000, "Légende"]];
function rank(xp) {
  let i = 0; while (i + 1 < RANKS.length && xp >= RANKS[i + 1][0]) i++;
  const next = RANKS[i + 1];
  return { name: RANKS[i][1], next: next ? next[1] : null, pct: next ? Math.round(100 * (xp - RANKS[i][0]) / (next[0] - RANKS[i][0])) : 100, need: next ? next[0] - xp : 0 };
}

// uitspraak: eerst de server (Piper/Azure, natuurlijke stem), anders de stem van de browser
let TTS_SERVER = false;
let frVoice = null;
function loadVoices() { const v = speechSynthesis.getVoices(); frVoice = v.find(x => x.lang === "fr-FR") || v.find(x => x.lang.startsWith("fr")) || null; }
if ("speechSynthesis" in window) { loadVoices(); speechSynthesis.onvoiceschanged = loadVoices; }
const player = new Audio();
player.preservesPitch = true;
function browserSay(text, rate) {
  if (!("speechSynthesis" in window)) return toast("Je browser kan niet voorlezen");
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text); u.lang = "fr-FR"; if (frVoice) u.voice = frVoice; u.rate = rate;
  speechSynthesis.speak(u);
}
async function say(text, slow = false) {
  if (typeof slow === "number") slow = slow < 0.8;
  if (TTS_SERVER) {
    try {
      player.pause();
      player.src = `/api/m/${MODULE}/tts?v=2&t=` + encodeURIComponent(text);
      player.defaultPlaybackRate = player.playbackRate = slow ? 0.7 : 1;
      await player.play();
      return;
    } catch (e) { /* valt terug op de browser */ }
  }
  browserSay(text, slow ? 0.55 : 0.9);
}
const sayBtn = text => `<button class="say" title="Laat horen" data-say="${esc(text)}">🔊</button>`;
document.addEventListener("click", e => { const b = e.target.closest("[data-say]"); if (b) say(b.dataset.say); });

function conjTable(t) {
  return `<div class="small muted" style="margin-top:10px"><b>${esc(t.verb)}</b> (${esc(t.nl)})</div>
  <table class="conj">${t.rows.map(r => `<tr class="${r.hl ? "hl" : ""}"><td>${esc(r.pron)}</td><td>${esc(r.form)}</td></tr>`).join("")}</table>`;
}

// ---------- router ----------
window.addEventListener("hashchange", render);
let cleanup = null, STAFF = false;
async function render() {
  if (cleanup) { cleanup(); cleanup = null; }
  const b = await Portal.boot(MODULE);
  if (!b) return;
  ME = b.me; STAFF = b.staff; TTS_SERVER = b.tts;
  const [route, arg] = location.hash.replace(/^#\/?/, "").split("/");
  const views = { "": viewHome, meerkeuze: viewMC, spelling: viewSpell, snel: viewSpeed, luisteren: viewListen, scores: viewScores };
  (views[route] || viewHome)(arg);
}

// ---------- start ----------
async function viewHome() {
  const h = await api("home");
  const r = rank(h.xp);
  const goalPct = Math.min(100, Math.round(100 * h.today / h.goal));
  const nextLevel = h.levels.filter(l => l.unlocked).pop();
  app.innerHTML = `
    <h1>Salut ${esc(h.name)} !</h1>
    <div class="chips">
      <span class="chip">🔥 ${h.streak} ${h.streak === 1 ? "dag" : "dagen"} op rij</span>
      <span class="chip">⭐ ${h.xp} XP · ${esc(r.name)}</span>
      <span class="chip">⚡ Record: ${h.speed_best}</span>
    </div>
    <div class="card" style="margin-bottom:12px">
      <div class="spread"><b>Doel van vandaag</b><span class="muted">${h.today} / ${h.goal} vragen ${goalPct >= 100 ? "✅" : ""}</span></div>
      <div class="bar ${goalPct >= 100 ? "good" : ""}" style="margin-top:8px"><i style="width:${goalPct}%"></i></div>
      ${r.next ? `<div class="small muted" style="margin-top:10px">Nog ${r.need} XP tot <b>${esc(r.next)}</b></div>` : `<div class="small muted" style="margin-top:10px">Hoogste rang bereikt. Respect! 👑</div>`}
    </div>
    <div class="grid">
      <a class="card tile" href="#/meerkeuze"><div class="ico">🎯</div><h3>Meerkeuze</h3><div class="muted small">Kies het goede antwoord uit 5. Toets 1–5 werkt ook.</div></a>
      <a class="card tile" href="#/spelling"><div class="ico">✍️</div><h3>Spelling</h3><div class="muted small">Zelf typen. Nu op niveau ${nextLevel.n}: ${esc(nextLevel.name)}</div></a>
      <a class="card tile" href="#/luisteren"><div class="ico">🎧</div><h3>Luisteren</h3><div class="muted small">Hoor het Frans en kies wat het betekent, of schrijf het op (dictee).</div></a>
      <a class="card tile" href="#/snel"><div class="ico">⚡</div><h3>Snelheidsronde</h3><div class="muted small">60 seconden. Hoeveel heb jij goed?</div></a>
      <a class="card tile" href="#/scores"><div class="ico">📊</div><h3>Mijn scores</h3><div class="muted small">${h.weak_count ? `${h.weak_count} dingen om nog te oefenen` : "Bekijk je voortgang"}</div></a>
    </div>`;
}

// ---------- gedeelde vraag-logica ----------
function promptHTML(q) {
  if (q.fmt === "fill") return `<div class="prompt"><div class="fr">${esc(q.prompt.fr)}</div><div class="inf">(${esc(q.prompt.inf)})</div><div class="nl">${esc(q.prompt.nl)}</div></div>`;
  return `<div class="prompt"><div class="small muted">Vertaal naar het Frans:</div><div class="nl big">${esc(q.prompt.nl)}</div></div>`;
}
function feedbackHTML(res, given) {
  const t = res.result === "correct" ? pick(PRAISE) : res.result === "almost" ? "Bijna! Let op de accenten" : pick(OOPS);
  const sol = res.accepted.length > 1 ? res.accepted.join("  /  ") : res.answer;
  return `<div class="feedback ${res.result} pop">
    <div class="title">${res.result === "correct" ? "✅" : res.result === "almost" ? "🟡" : "❌"} ${esc(t)} ${res.xp_gained ? `<span class="small muted">+${res.xp_gained} XP</span>` : ""}</div>
    ${res.result !== "correct" ? `${given !== undefined ? `<div class="small muted">Jij: <s>${esc(given) || "(leeg)"}</s></div>` : ""}<div class="sol">${esc(sol)} ${sayBtn(res.say)}</div>` : `<div>${esc(res.say)} ${sayBtn(res.say)}</div>`}
    ${res.result !== "correct" ? conjTable(res.table) : ""}
    ${res.unlocked ? `<div style="margin-top:10px;font-weight:700">🎉 Nieuw niveau vrijgespeeld: ${esc(res.unlocked.name)}! (+50 XP)</div>` : ""}
  </div>`;
}
function sessionBar(s) { return `<span class="chip">✅ ${s.ok} / ${s.n}</span>`; }

// ---------- meerkeuze ----------
async function viewMC(focus) {
  if (!focus) {
    const h = await api("home");
    app.innerHTML = `<h1>🎯 Meerkeuze</h1><p class="muted">Wat wil je oefenen?</p>
      <div class="grid">${h.focus.map(f => `<a class="card tile" href="#/meerkeuze/${f.key}"><h3>${esc(f.name)}</h3>
      <div class="muted small">${f.key === "weak" ? `${h.weak_count} keer fout gegaan` : f.key === "etre_avoir" ? "zijn & hebben" : f.key === "er" ? "parler, jouer, manger …" : "de hele mix"}</div></a>`).join("")}</div>`;
    return;
  }
  const s = { n: 0, ok: 0 };
  let q, answered = false;
  async function next() {
    answered = false;
    q = await api("question", { mode: "mc", focus });
    app.innerHTML = `<div class="qhead"><a href="#/meerkeuze">← Stoppen</a>${sessionBar(s)}</div>
      <div class="card">${q.note ? `<p class="small muted">${esc(q.note)}</p>` : ""}${promptHTML(q)}
      <div class="options">${q.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="n">${i + 1}</span>${esc(o)}</button>`).join("")}</div>
      <div id="fb"></div></div>`;
    app.querySelectorAll(".opt").forEach(b => b.onclick = () => answer(+b.dataset.i));
  }
  async function answer(i) {
    if (answered) return; answered = true;
    const res = await api("answer", { qid: q.qid, answer: q.options[i] });
    s.n++; if (res.result === "correct") s.ok++;
    app.querySelectorAll(".opt").forEach((b, j) => {
      b.disabled = true;
      if (q.options[j] === res.answer || res.accepted.includes(q.options[j])) b.classList.add("right");
      else if (j === i) b.classList.add("wrong");
    });
    if (res.result !== "correct") $(".card").classList.add("shake");
    $(".qhead .chip").outerHTML = sessionBar(s);
    $("#fb").innerHTML = feedbackHTML(res) + `<button class="next" id="nx">Volgende ↵</button>`;
    $("#nx").onclick = next; $("#nx").focus();
    if (res.result === "correct") say(res.say);
  }
  const key = e => {
    if (!answered && /^[1-5]$/.test(e.key) && q) answer(+e.key - 1);
    else if (answered && e.key === "Enter") { e.preventDefault(); next(); }
  };
  document.addEventListener("keydown", key);
  cleanup = () => document.removeEventListener("keydown", key);
  next();
}

// ---------- spelling ----------
function accentBar() {
  return `<div class="accents">${["é", "è", "ê", "à", "ç", "ô", "î", "'"].map(c => `<button type="button" data-acc="${c}">${c}</button>`).join("")}</div>`;
}
function bindAccents(input) {
  app.querySelectorAll("[data-acc]").forEach(b => b.onclick = () => {
    const [a, z] = [input.selectionStart, input.selectionEnd];
    input.value = input.value.slice(0, a) + b.dataset.acc + input.value.slice(z);
    input.focus(); input.setSelectionRange(a + 1, a + 1);
  });
}
async function viewSpell(level) {
  if (!level) {
    const h = await api("home");
    app.innerHTML = `<h1>✍️ Spelling</h1><p class="muted">Haal 80% goed van je laatste 20 antwoorden om het volgende niveau vrij te spelen.</p>
      <div class="grid">${h.levels.map(l => `<a class="card tile ${l.unlocked ? "" : "locked"}" ${l.unlocked ? `href="#/spelling/${l.n}"` : ""}>
        <div class="spread"><h3>${l.unlocked ? "" : "🔒 "}${l.n}. ${esc(l.name)}</h3>${l.passed ? "✅" : ""}</div>
        <div class="muted small">${esc(l.desc)}</div>
        ${l.unlocked ? `<div class="bar ${l.passed ? "good" : ""}" style="margin-top:10px"><i style="width:${l.answered ? l.score : 0}%"></i></div>
        <div class="small muted" style="margin-top:4px">${l.answered ? `${l.score}% van laatste ${l.answered}` : "nog niet geoefend"}</div>` : ""}
      </a>`).join("")}</div>`;
    return;
  }
  const s = { n: 0, ok: 0 };
  let q, answered = false;
  async function next() {
    answered = false;
    try { q = await api("question", { mode: "spell", level: +level }); }
    catch (e) { toast(e.message); location.hash = "#/spelling"; return; }
    app.innerHTML = `<div class="qhead"><a href="#/spelling">← Stoppen</a><span class="small muted">Niveau ${level}</span>${sessionBar(s)}</div>
      <div class="card">${promptHTML(q)}
      <form class="answer-row" id="f"><input id="inp" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" placeholder="${q.fmt === "fill" ? "vorm" : "Franse zin"}"><button>OK</button></form>
      ${accentBar()}<div id="fb"></div></div>`;
    const inp = $("#inp"); inp.focus(); bindAccents(inp);
    $("#f").onsubmit = e => { e.preventDefault(); answered ? next() : answer(inp.value); };
  }
  async function answer(given) {
    if (answered) return; answered = true;
    const res = await api("answer", { qid: q.qid, answer: given });
    s.n++; if (res.result === "correct") s.ok++;
    $(".qhead .chip").outerHTML = sessionBar(s);
    const inp = $("#inp"); inp.readOnly = true;
    inp.style.borderColor = res.result === "correct" ? "var(--good)" : res.result === "almost" ? "var(--warn)" : "var(--bad)";
    if (res.result === "wrong") $(".card").classList.add("shake");
    $("#fb").innerHTML = feedbackHTML(res, given) + `<button class="next" id="nx">Volgende ↵</button>`;
    $("#nx").onclick = next; inp.focus();
    if (res.result === "correct") say(res.say);
    if (res.unlocked) toast(`🎉 Niveau ${res.unlocked.n} vrijgespeeld!`, 4000);
  }
  next();
}

// ---------- luisteren ----------
function listenFeedback(res, given) {
  const ok = res.result === "correct";
  const t = ok ? pick(PRAISE) : res.result === "almost" ? "Bijna! Let op de accenten" : pick(OOPS);
  const same = res.fmt === "dictee" ? res.accepted : null;
  return `<div class="feedback ${res.result} pop">
    <div class="title">${ok ? "✅" : res.result === "almost" ? "🟡" : "❌"} ${esc(t)} ${res.xp_gained ? `<span class="small muted">+${res.xp_gained} XP</span>` : ""}</div>
    ${!ok && given !== undefined && res.fmt === "dictee" ? `<div class="small muted">Jij: <s>${esc(given) || "(leeg)"}</s></div>` : ""}
    <div>Je hoorde: <span class="sol">${esc(res.say)}</span> ${sayBtn(res.say)}</div>
    <div class="muted">= ${esc(res.nl)}</div>
    ${same && same.length > 1 ? `<div class="small" style="margin-top:6px">👂 Klinkt precies hetzelfde: <b>${same.map(esc).join("</b> en <b>")}</b>. Allebei goed!</div>` : ""}
    ${!ok ? conjTable(res.table) : ""}
  </div>`;
}
async function viewListen(arg) {
  const [kind, focus] = (arg || "").split(":");
  if (!kind || !focus) {
    const h = await api("home");
    const noVoice = !TTS_SERVER && "speechSynthesis" in window && speechSynthesis.getVoices().length && !frVoice;
    app.innerHTML = `<h1>🎧 Luisteren</h1>
      ${noVoice ? `<p class="error">Dit apparaat heeft geen Franse stem. Het kan raar klinken. Op een telefoon kun je in de instellingen een Franse stem downloaden.</p>` : ""}
      <h2>Wat wil je doen?</h2>
      <div class="grid">
        <button class="card tile ${kind !== "dictee" ? "sel" : ""}" data-k="listen"><div class="ico">👂</div><h3>Wat hoor je?</h3><div class="muted small">Luister en kies de Nederlandse betekenis.</div></button>
        <button class="card tile ${kind === "dictee" ? "sel" : ""}" data-k="dictee"><div class="ico">📝</div><h3>Dictee</h3><div class="muted small">Luister en schrijf het in het Frans op.</div></button>
      </div>
      <h2>Welke werkwoorden?</h2>
      <div class="grid">${h.focus.map(f => `<button class="card tile" data-f="${f.key}"><h3>${esc(f.name)}</h3></button>`).join("")}</div>`;
    let k = kind === "dictee" ? "dictee" : "listen";
    app.querySelectorAll("[data-k]").forEach(b => b.onclick = () => {
      k = b.dataset.k; app.querySelectorAll("[data-k]").forEach(x => x.classList.toggle("sel", x === b));
    });
    app.querySelectorAll("[data-f]").forEach(b => b.onclick = () => (location.hash = `#/luisteren/${k}:${b.dataset.f}`));
    return;
  }
  const s = { n: 0, ok: 0 };
  let q, answered = false;
  const controls = `<div class="row" style="justify-content:center;margin-top:6px">
      <button class="secondary" id="play">🔊 Nog eens</button><button class="secondary" id="slow">🐢 Langzaam</button></div>`;
  async function next() {
    answered = false;
    q = await api("question", { mode: kind, focus });
    const top = `<div class="qhead"><a href="#/luisteren/${kind}">← Stoppen</a><span class="small muted">${kind === "dictee" ? "Dictee" : "Wat hoor je?"}</span>${sessionBar(s)}</div>`;
    const head = `${q.note ? `<p class="small muted">${esc(q.note)}</p>` : ""}<div class="prompt"><div style="font-size:54px">🎧</div><div class="muted">${kind === "dictee" ? "Schrijf op wat je hoort" : "Wat betekent dit?"}</div></div>${controls}`;
    if (kind === "dictee") {
      app.innerHTML = `${top}<div class="card">${head}
        <form class="answer-row" id="f"><input id="inp" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" placeholder="wat hoor je?"><button>OK</button></form>
        ${accentBar()}<div id="fb"></div></div>`;
      const inp = $("#inp"); bindAccents(inp); inp.focus();
      $("#f").onsubmit = e => { e.preventDefault(); answered ? next() : answer(inp.value); };
    } else {
      app.innerHTML = `${top}<div class="card">${head}
        <div class="options">${q.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="n">${i + 1}</span>${esc(o)}</button>`).join("")}</div>
        <div id="fb"></div></div>`;
      app.querySelectorAll(".opt").forEach(b => b.onclick = () => answer(q.options[+b.dataset.i], +b.dataset.i));
    }
    $("#play").onclick = () => say(q.prompt.say);
    $("#slow").onclick = () => say(q.prompt.say, true);
    setTimeout(() => say(q.prompt.say), 250);
  }
  async function answer(given, idx) {
    if (answered) return; answered = true;
    const res = await api("answer", { qid: q.qid, answer: given });
    s.n++; if (res.result === "correct") s.ok++;
    $(".qhead .chip").outerHTML = sessionBar(s);
    if (kind === "dictee") {
      const inp = $("#inp"); inp.readOnly = true;
      inp.style.borderColor = res.result === "correct" ? "var(--good)" : res.result === "almost" ? "var(--warn)" : "var(--bad)";
    } else {
      app.querySelectorAll(".opt").forEach((b, j) => {
        b.disabled = true;
        if (res.accepted.includes(q.options[j])) b.classList.add("right");
        else if (j === idx) b.classList.add("wrong");
      });
    }
    if (res.result === "wrong") $(".card").classList.add("shake");
    $("#fb").innerHTML = listenFeedback(res, given) + `<button class="next" id="nx">Volgende ↵</button>`;
    $("#nx").onclick = next;
    (kind === "dictee" ? $("#inp") : $("#nx")).focus();
  }
  const key = e => {
    if (kind !== "dictee" && !answered && q && /^[1-5]$/.test(e.key)) answer(q.options[+e.key - 1], +e.key - 1);
    else if (kind !== "dictee" && answered && e.key === "Enter") { e.preventDefault(); next(); }
  };
  document.addEventListener("keydown", key);
  cleanup = () => { document.removeEventListener("keydown", key); player.pause(); if ("speechSynthesis" in window) speechSynthesis.cancel(); };
  next();
}

// ---------- snelheidsronde ----------
async function viewSpeed() {
  const h = await api("home");
  app.innerHTML = `<h1>⚡ Snelheidsronde</h1><div class="card center">
    <p>60 seconden meerkeuze. Elk goed antwoord = 1 punt + bonus-XP.<br>Gebruik toetsen <b>1–5</b> voor extra snelheid!</p>
    <p class="muted">Jouw record: <b>${h.speed_best}</b></p><button id="go" style="font-size:20px;padding:14px 30px">Start!</button></div>`;
  $("#go").onclick = start;
  let timer, q, sid, end, busy = false;
  async function start() {
    const r = await api("speed/start", {});
    sid = r.sid; end = Date.now() + r.seconds * 1000;
    app.innerHTML = `<div class="qhead"><span class="timer" id="tm">60</span><span class="chip" id="sc">0 punten</span></div><div class="card" id="qc"></div>`;
    timer = setInterval(tick, 200); tick(); next();
  }
  function tick() {
    const left = Math.max(0, Math.ceil((end - Date.now()) / 1000));
    const t = $("#tm"); if (t) { t.textContent = left; t.classList.toggle("low", left <= 10); }
    if (left <= 0) finish();
  }
  async function next() {
    q = await api("question", { mode: "mc", focus: "all", speed: sid });
    busy = false;
    $("#qc").innerHTML = promptHTML(q) + `<div class="options">${q.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="n">${i + 1}</span>${esc(o)}</button>`).join("")}</div>`;
    app.querySelectorAll(".opt").forEach(b => b.onclick = () => answer(+b.dataset.i));
  }
  async function answer(i) {
    if (busy || !sid) return; busy = true;
    const res = await api("answer", { qid: q.qid, answer: q.options[i] });
    $("#qc").classList.remove("flash-ok", "flash-bad"); void $("#qc").offsetWidth;
    $("#qc").classList.add(res.result === "correct" ? "flash-ok" : "flash-bad");
    if (res.speed_score !== null) $("#sc").textContent = `${res.speed_score} punten`;
    if (res.result !== "correct") toast(`✗ ${res.say}`, 1200);
    if (Date.now() < end) next();
  }
  async function finish() {
    clearInterval(timer); if (!sid) return;
    const id = sid; sid = null;
    const r = await api("speed/finish", { sid: id });
    app.innerHTML = `<h1>⚡ Tijd is om!</h1><div class="card center">
      <div class="big-score">${r.score}</div><p>${r.record ? "🏆 <b>Nieuw record!</b>" : `Record: ${r.best}`}</p>
      <div class="row" style="justify-content:center"><a class="btn" href="#/snel" onclick="setTimeout(render)">Nog een keer</a><a class="btn secondary" href="#/">Home</a></div></div>`;
  }
  const key = e => { if (sid && /^[1-5]$/.test(e.key)) answer(+e.key - 1); };
  document.addEventListener("keydown", key);
  cleanup = () => { clearInterval(timer); document.removeEventListener("keydown", key); };
}

// ---------- scores ----------
const fmtDay = d => { const [, m, dd] = d.split("-"); return `${+dd}/${+m}`; };
function heatClass(p) { return p >= 80 ? "g" : p >= 50 ? "w" : "b"; }
async function viewScores(uid) {
  const s = await api("stats" + (uid ? `?user=${encodeURIComponent(uid)}` : ""));
  const maxN = Math.max(1, ...s.days.map(d => d.n));
  const self = !uid || +uid === ME.id;
  const heatRows = Object.entries(s.heat);
  app.innerHTML = `
    ${self ? "" : `<a href="/#/students">← Alle leerlingen</a>`}
    <div class="spread"><h1>📊 ${self ? "Mijn scores" : "Scores van " + esc(s.user.name)}</h1>
      <a class="btn secondary" href="/api/export.csv?module=frans${uid ? `&user=${encodeURIComponent(uid)}` : ""}">⬇ Exporteer (CSV)</a></div>
    <div class="chips">
      <span class="chip">📝 ${s.total} antwoorden</span>
      <span class="chip">🎯 ${s.pct ?? "–"}% goed</span>
      <span class="chip">🔥 ${s.streak} ${s.streak === 1 ? "dag" : "dagen"} op rij</span>
      <span class="chip">⭐ ${s.xp} XP · ${esc(rank(s.xp).name)}</span>
      <span class="chip">⚡ Record ${s.speed_best}</span>
    </div>

    <div class="card"><h3>Laatste 14 dagen</h3><div class="small muted">Aantal vragen per dag (wijs een balk aan voor het percentage goed)</div>
      <div class="days" id="days">${s.days.map(d => `<div class="d" data-tip="${fmtDay(d.day)}: ${d.n} vragen${d.n ? `, ${d.pct}% goed` : ""}"><i style="height:${Math.round(100 * d.n / maxN)}%"></i></div>`).join("")}</div>
      <div class="days-x">${s.days.map((d, i) => `<span>${i % 2 === 1 ? fmtDay(d.day) : ""}</span>`).join("")}</div>
    </div>

    <h2>Niveaus spelling</h2><div class="card">${s.levels.map(l => `<div class="lvl"><span style="width:180px">${l.unlocked ? "" : "🔒 "}${l.n}. ${esc(l.name)}</span>
      <div class="bar ${l.passed ? "good" : ""}"><i style="width:${l.answered ? l.score : 0}%"></i></div><span class="small muted" style="width:70px;text-align:right">${l.answered ? l.score + "%" : "–"}${l.passed ? " ✅" : ""}</span></div>`).join("")}</div>

    <h2>Per werkwoord en persoon</h2>
    <div class="card">${heatRows.length ? `<div class="tablewrap"><table class="heat"><tr><th></th>${s.prons.map(p => `<th>${p === "il" ? "il/elle/on" : p === "ils" ? "ils/elles" : p}</th>`).join("")}</tr>
      ${heatRows.map(([v, row]) => `<tr><th class="v">${esc(v)}</th>${s.prons.map(p => row[p] ? `<td class="${heatClass(row[p].pct)}" data-tip="${esc(v)} · ${p}: ${row[p].pct}% goed (${row[p].n}×)">${row[p].pct}</td>` : `<td class="none">·</td>`).join("")}</tr>`).join("")}
      </table></div>
      <div class="legend"><span style="--c:#0ca30c">✓ 80–100% goed</span><span style="--c:#fab219">~ 50–79%</span><span style="--c:#d03b3b">✗ onder 50%</span><span style="--c:#f0efec">nog niet geoefend</span></div>`
      : `<p class="muted">Nog niets geoefend.</p>`}</div>

    <h2>Moet nog geoefend worden</h2>
    <div class="card">${s.weak.length ? `<div class="tablewrap"><table class="list"><tr><th>Frans</th><th>Nederlands</th><th>Fout</th><th>Onderdeel</th></tr>
      ${s.weak.map(w => `<tr><td><b>${esc(w.fr)}</b> ${sayBtn(w.fr)}</td><td>${esc(w.nl)}</td><td>${w.wrong}× van ${w.seen}</td><td class="small muted">${w.mode}${w.box >= 3 ? " · gaat al beter" : ""}</td></tr>`).join("")}
      </table></div>` : `<p class="muted">Niets! Très bien 👏</p>`}</div>

    <h2>Recente fouten</h2>
    <div class="card">${s.mistakes.length ? `<div class="tablewrap"><table class="list"><tr><th>Vraag</th><th>Antwoord</th><th>Goed is</th></tr>
      ${s.mistakes.map(m => `<tr><td>${esc(m.prompt)}</td><td><s>${esc(m.given) || "(leeg)"}</s>${m.result === 1 ? " <span class='small muted'>(accent)</span>" : ""}</td><td><b>${esc(m.expected)}</b></td></tr>`).join("")}
      </table></div>` : `<p class="muted">Geen fouten. Wauw.</p>`}</div>`;
  bindTips();
}
function bindTips() {
  let tip;
  app.querySelectorAll("[data-tip]").forEach(el => {
    el.addEventListener("mouseenter", () => { tip = document.createElement("div"); tip.className = "tip"; tip.textContent = el.dataset.tip; document.body.append(tip); });
    el.addEventListener("mousemove", e => { if (tip) { tip.style.left = Math.min(e.clientX + 12, innerWidth - tip.offsetWidth - 8) + "px"; tip.style.top = (e.clientY - 34) + "px"; } });
    el.addEventListener("mouseleave", () => { tip?.remove(); tip = null; });
    el.addEventListener("click", () => toast(el.dataset.tip));   // tik op mobiel
  });
}

render();
