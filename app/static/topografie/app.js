"use strict";
const $ = (s, el = document) => el.querySelector(s);
const app = $("#app");
const esc = Portal.esc;
const MODULE = "topografie";
let ME = null, TTS_SERVER = false, MAP = null, HOME = null, cleanup = null;

// ---------- helpers ----------
async function api(path, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const r = await fetch(`/api/m/${MODULE}/` + path, opt);
  const data = await r.json().catch(() => ({}));
  if (r.status === 401 || (r.status === 403 && data.error === "must_change")) { location.href = "/"; throw new Error(data.error); }
  if (!r.ok) throw new Error(data.error || "Er ging iets mis");
  return data;
}
function toast(msg, ms = 2400) {
  const t = $("#toast"); t.textContent = msg; t.hidden = false;
  clearTimeout(toast._t); toast._t = setTimeout(() => (t.hidden = true), ms);
}
const pick = a => a[Math.floor(Math.random() * a.length)];
const PRAISE = ["Goed zo!", "Super!", "Helemaal goed!", "Knap!", "Top!", "Prima!"];
const OOPS = ["Helaas!", "Bijna, kijk goed:", "Jammer!", "Niet erg!"];

// speech: server voice, otherwise the browser
let nlVoice = null;
function loadVoices() { const v = speechSynthesis.getVoices(); nlVoice = v.find(x => x.lang === "nl-NL") || v.find(x => x.lang.startsWith("nl")) || null; }
if ("speechSynthesis" in window) { loadVoices(); speechSynthesis.onvoiceschanged = loadVoices; }
const player = new Audio();
async function say(text) {
  if (TTS_SERVER) {
    try { player.pause(); player.src = `/api/m/${MODULE}/tts?t=` + encodeURIComponent(text); await player.play(); return; } catch (e) { /* fallback */ }
  }
  if (!("speechSynthesis" in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text); u.lang = "nl-NL"; if (nlVoice) u.voice = nlVoice; u.rate = 0.95;
  speechSynthesis.speak(u);
}
const sayBtn = t => `<button class="say" data-say="${esc(t)}" title="Luister">🔊</button>`;
document.addEventListener("click", e => { const b = e.target.closest("[data-say]"); if (b) { e.preventDefault(); say(b.dataset.say); } });

// ---------- map ----------
const PALETTE = ["#f6c28b", "#f3a683", "#a8d5a2", "#f7d794", "#e8a5c5", "#c5b3e6", "#9ad0e0"];
async function loadMap() {
  if (!MAP) MAP = await fetch("/topografie/europe.json").then(r => r.json());
  return MAP;
}
function viewBox(view) {
  const nums = view && view !== "alle" ? (HOME.regions.find(r => r.key === view) || {}).nums : null;
  if (!nums) return [0, 0, MAP.w, MAP.h];
  let [x0, y0, x1, y1] = [1e9, 1e9, -1e9, -1e9];
  nums.forEach(n => { const b = MAP.countries[n].box; x0 = Math.min(x0, b[0]); y0 = Math.min(y0, b[1]); x1 = Math.max(x1, b[2]); y1 = Math.max(y1, b[3]); });
  if (view === "oost") { x1 = Math.min(x1, 930); y0 = Math.max(y0, 180); }     // Russia is huge: keep the region readable
  let w = x1 - x0, h = y1 - y0;
  const pad = Math.max(w, h) * 0.18;
  x0 -= pad; y0 -= pad; w += 2 * pad; h += 2 * pad;
  const minW = 260;
  if (w < minW) { x0 -= (minW - w) / 2; w = minW; }
  if (h < minW * 0.75) { y0 -= (minW * 0.75 - h) / 2; h = minW * 0.75; }
  return [x0, y0, w, h];
}
function mapSVG({ view = "alle", highlight = null, numbers = false, names = false, clickable = false, marks = {} } = {}) {
  const vb = viewBox(view);
  const scale = vb[2] / MAP.w;                       // smaller when zoomed in
  const fs = Math.max(7, (view === "alle" ? 17 : 16) * Math.sqrt(scale));
  let s = `<svg class="map ${clickable ? "clickable" : ""}" viewBox="${vb.map(v => v.toFixed(1)).join(" ")}" xmlns="http://www.w3.org/2000/svg">
    <rect class="sea" x="-50" y="-50" width="${MAP.w + 100}" height="${MAP.h + 100}"/><path class="other" d="${MAP.other}"/>`;
  for (const [n, c] of Object.entries(MAP.countries)) {
    const cls = ["c", +n === highlight ? "hl" : "", marks[n] || ""].join(" ");
    s += `<path class="${cls}" data-n="${n}" d="${c.d}" fill="${PALETTE[n % PALETTE.length]}"/>`;
  }
  for (const [n, c] of Object.entries(MAP.countries)) {
    const [bx0, by0, bx1, by1] = c.box;
    const small = (bx1 - bx0) < 16 || (by1 - by0) < 16;
    if (c.dot) s += `<circle class="c dot ${+n === highlight ? "hl" : ""} ${marks[n] || ""}" data-n="${n}" cx="${c.label[0]}" cy="${c.label[1]}" r="${4.5 * Math.sqrt(scale) + 1.5}" fill="${PALETTE[n % PALETTE.length]}"/>`;
    if (clickable && (small || c.dot)) s += `<circle class="hit" data-n="${n}" cx="${c.label[0]}" cy="${c.label[1]}" r="${10 * Math.sqrt(scale) + 2}"/>`;
  }
  if (numbers || names) {
    for (const [n, c] of Object.entries(MAP.countries)) {
      const [x, y] = c.label;
      if (numbers) s += `<text class="num" x="${x}" y="${c.dot ? y + fs : y}" style="font-size:${fs}px">${n}</text>`;
      if (names) s += `<text class="name" x="${x}" y="${y + (numbers ? fs : 0)}" style="font-size:${fs * 0.8}px">${esc(c.name)}</text>`;
    }
  }
  return s + `</svg>`;
}

// ---------- router ----------
window.addEventListener("hashchange", render);
async function render() {
  if (cleanup) { cleanup(); cleanup = null; }
  const b = await Portal.boot(MODULE);
  if (!b) return;
  ME = b.me; TTS_SERVER = b.tts;
  await loadMap();
  HOME = await api("home");
  const [route, a, c] = location.hash.replace(/^#\/?/, "").split("/");
  const views = { "": viewHome, kies: viewFocus, oefen: viewPlay, toets: viewToets, kaart: viewKaart, scores: viewScores };
  (views[route] || viewHome)(a, c);
}

// ---------- home ----------
function viewHome() {
  const h = HOME;
  const goal = Math.min(100, Math.round(100 * h.today / h.goal));
  const steps = h.exercises.filter(e => e.key !== "t-toets");
  const toets = h.exercises.find(e => e.key === "t-toets");
  // recommend the first step that isn't mastered yet (80% of the last 20)
  const rec = (steps.find(e => !(e.n >= 20 && e.pct >= 80)) || toets).key;
  app.innerHTML = `<h1>Hoi ${esc(h.name)}! 🗺️</h1>
    <div class="chips"><span class="chip">🔥 ${h.streak} ${h.streak === 1 ? "dag" : "dagen"} op rij</span>
      <span class="chip">⭐ ${h.xp} punten</span><span class="chip">🏆 Beste proeftoets: ${h.best ? h.best + "%" : "–"}</span></div>
    <div class="card" style="margin-bottom:12px">
      <div class="spread"><b>Ik ken al ${h.known} van de ${h.total} landen</b><span class="muted small">${h.today} / ${h.goal} vragen vandaag ${goal >= 100 ? "✅" : ""}</span></div>
      <div class="bar ${h.known >= h.total ? "good" : ""}" style="margin-top:8px"><i style="width:${Math.round(100 * h.known / h.total)}%"></i></div>
      <div class="small muted" style="margin-top:6px">Een land telt als 'gekend' als je de naam een paar keer achter elkaar goed hebt getypt.</div>
    </div>
    <div class="grid steps">
      ${steps.map(e => `<a class="card tile ${e.key === rec ? "sel" : ""}" href="#/kies/${e.key}"><h3>${esc(e.name)}</h3>
        <div class="muted small">${esc(e.desc)}</div>
        <div class="pct">${e.n ? `${e.pct}% goed (laatste ${e.n})${e.n >= 20 && e.pct >= 80 ? " ✅" : ""}` : "nog niet geoefend"}${e.key === rec ? " · 👉 <b>doe dit nu</b>" : ""}</div></a>`).join("")}
      <a class="card tile ${rec === "t-toets" ? "sel" : ""}" href="#/toets"><h3>📝 ${esc(toets.name)}</h3><div class="muted small">${esc(toets.desc)}</div>
        <div class="pct">${h.best ? `Beste: ${h.best}%` : "Nog niet gedaan"}</div></a>
      <a class="card tile" href="#/kaart"><h3>🔍 Bekijk de kaart</h3><div class="muted small">Tik op een land om de naam te zien en te horen.</div></a>
    </div>`;
}

function viewFocus(ex) {
  const e = HOME.exercises.find(x => x.key === ex);
  if (!e) { location.hash = "#/"; return; }
  app.innerHTML = `<a href="#/">← Terug</a><h1>${esc(e.name)}</h1><p class="muted">${esc(e.desc)}</p>
    <h2>Welke landen?</h2>
    <p class="small muted">Tip: oefen eerst per deel van Europa, en daarna alles door elkaar.</p>
    <div class="grid">
      ${HOME.regions.map(r => `<a class="card tile" href="#/oefen/${ex}/${r.key}"><h3>${esc(r.name)}</h3><div class="muted small">${r.nums.length} landen</div></a>`).join("")}
      <a class="card tile" href="#/oefen/${ex}/alle"><h3>🌍 Alles door elkaar</h3><div class="muted small">alle 45 landen</div></a>
      <a class="card tile" href="#/oefen/${ex}/zwak"><h3>⚠️ Mijn moeilijke landen</h3><div class="muted small">${HOME.weak_count} landen</div></a>
    </div>`;
}

// ---------- practising ----------
function promptHTML(q) {
  const p = q.prompt;
  return `<div class="q-text">${esc(p.text)}</div>${p.big ? `<div class="q-big">${esc(p.big)}${q.kind === "click" || q.kind === "number" ? "?" : ""} ${sayBtn(p.big)}</div>` : ""}`;
}
function feedbackHTML(res) {
  const ok = res.result === "correct";
  const t = ok ? pick(PRAISE) : res.result === "almost" ? "Bijna! Let op de spelling (puntjes ¨)." : pick(OOPS);
  return `<div class="feedback ${res.result} pop"><div class="title">${ok ? "✅" : res.result === "almost" ? "🟡" : "❌"} ${esc(t)}
    ${res.xp_gained ? `<span class="small muted">+${res.xp_gained}</span>` : ""}</div>
    <div class="sol">${res.num}. ${esc(res.name)} ${sayBtn(res.say)}</div></div>`;
}

// One question on the screen. onDone(res) is called after answering.
async function showQuestion(container, ex, focus, onDone, opts = {}) {
  const q = await api("question", { ex, focus });
  let answered = false;
  const p = q.prompt;
  let input = "";
  if (q.kind === "choice") input = `<div class="options">${q.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="n">${i + 1}</span>${esc(o)}</button>`).join("")}</div>`;
  if (q.kind === "type") input = `<form class="answer-row" id="f"><input id="inp" autocomplete="off" autocapitalize="words" autocorrect="off" spellcheck="false" placeholder="naam van het land"><button>OK</button></form>`;
  if (q.kind === "number") input = `<form class="answer-row" id="f"><input id="inp" inputmode="numeric" pattern="[0-9]*" autocomplete="off" placeholder="nummer"><button>OK</button></form>`;
  container.innerHTML = `${q.note ? `<p class="small muted">${esc(q.note)}</p>` : ""}${promptHTML(q)}
    ${q.kind === "number" ? input : ""}
    <div class="map-wrap" id="mapbox">${mapSVG({ view: p.view, highlight: p.highlight, numbers: p.numbers, clickable: q.kind === "click" })}</div>
    ${q.kind !== "number" ? input : ""}<div id="fb"></div>`;
  const inp = $("#inp", container);
  if (inp && !opts.noFocus) inp.focus();

  async function answer(given, idx) {
    if (answered) return; answered = true;
    const res = await api("answer", { qid: q.qid, answer: String(given) });
    const marks = { [res.num]: "right" };
    if (q.kind === "click" && res.result !== "correct" && given) marks[given] = "wrong";
    $("#mapbox", container).innerHTML = mapSVG({ view: p.view, highlight: null, numbers: p.numbers || res.result !== "correct", marks });
    if (q.kind === "choice") container.querySelectorAll(".opt").forEach((b, j) => {
      b.disabled = true;
      if (q.options[j] === res.name) b.classList.add("right"); else if (j === idx) b.classList.add("wrong");
    });
    if (inp) { inp.readOnly = true; inp.style.borderColor = res.result === "correct" ? "var(--good)" : res.result === "almost" ? "var(--warn)" : "var(--bad)"; }
    if (res.result === "wrong") container.classList.add("shake");
    say(res.say);
    onDone(res, q);
  }
  if (q.kind === "click") $("#mapbox", container).addEventListener("click", e => {
    const el = e.target.closest("[data-n]"); if (el) answer(el.dataset.n);
  });
  if (q.kind === "choice") container.querySelectorAll(".opt").forEach(b => b.onclick = () => answer(q.options[+b.dataset.i], +b.dataset.i));
  if (inp) $("#f", container).onsubmit = e => { e.preventDefault(); if (!answered && inp.value.trim()) answer(inp.value.trim()); };
  return { q, isAnswered: () => answered, answerChoice: i => q.kind === "choice" && answer(q.options[i], i) };
}

async function viewPlay(ex, focus) {
  const s = { n: 0, ok: 0 };
  let cur = null;
  const bar = () => `<span class="chip">✅ ${s.ok} / ${s.n}</span>`;
  async function next() {
    app.innerHTML = `<div class="qhead"><a href="#/kies/${ex}">← Stoppen</a>${bar()}</div><div class="card" id="qc"></div>`;
    cur = await showQuestion($("#qc"), ex, focus, res => {
      s.n++; if (res.result === "correct") s.ok++;
      $(".qhead .chip").outerHTML = bar();
      $("#fb").innerHTML = feedbackHTML(res) + `<button class="next" id="nx">Volgende ↵</button>`;
      $("#nx").onclick = next;
      if (!$("#inp")) $("#nx").focus();
    });
  }
  const key = e => {
    if (!cur) return;
    if (!cur.isAnswered() && /^[1-5]$/.test(e.key) && cur.q.kind === "choice") cur.answerChoice(+e.key - 1);
    else if (cur.isAnswered() && e.key === "Enter" && $("#nx")) { e.preventDefault(); next(); }
  };
  document.addEventListener("keydown", key);
  cleanup = () => document.removeEventListener("keydown", key);
  next();
}

// ---------- practice test ----------
async function viewToets(focus) {
  if (!focus) {
    app.innerHTML = `<a href="#/">← Terug</a><h1>📝 Proeftoets</h1>
      <p>20 vragen door elkaar: aanwijzen op de kaart, nummers zoeken en namen typen. Aan het eind krijg je een cijfer.</p>
      <div class="grid">
        <a class="card tile" href="#/toets/alle"><h3>🌍 Heel Europa</h3><div class="muted small">zoals de echte toets</div></a>
        ${HOME.regions.map(r => `<a class="card tile" href="#/toets/${r.key}"><h3>${esc(r.name)}</h3></a>`).join("")}
      </div>`;
    return;
  }
  const N = 20, results = [];
  async function next() {
    if (results.length >= N) return finish();
    app.innerHTML = `<div class="qhead"><a href="#/toets">← Stoppen</a><span class="small muted">Vraag ${results.length + 1} van ${N}</span></div>
      <div class="toets-bar"><i style="width:${100 * results.length / N}%"></i></div><div class="card" id="qc"></div>`;
    await showQuestion($("#qc"), "t-toets", focus, res => {
      results.push(res);
      $("#fb").innerHTML = feedbackHTML(res) + `<button class="next" id="nx">${results.length >= N ? "Bekijk je cijfer" : "Volgende ↵"}</button>`;
      $("#nx").onclick = next;
      if (!$("#inp")) $("#nx").focus();
    });
  }
  async function finish() {
    const points = results.reduce((a, r) => a + (r.result === "correct" ? 1 : r.result === "almost" ? 0.5 : 0), 0);
    const pct = Math.round(100 * points / N);
    const grade = Math.max(1, Math.round((1 + 9 * points / N) * 10) / 10);
    const r = await api("toets/finish", { score: pct });
    const wrong = results.filter(x => x.result !== "correct");
    app.innerHTML = `<h1>📝 Klaar!</h1><div class="card center">
      <div class="grade">${grade.toFixed(1).replace(".", ",")}</div>
      <p>${points} van de ${N} goed (${pct}%) ${pct >= r.best && pct > 0 ? "· 🏆 je beste score!" : `· beste: ${r.best}%`}</p>
      ${wrong.length ? `<h3>Nog even oefenen:</h3><p>${wrong.map(w => `${w.num}. ${esc(w.name)} ${sayBtn(w.name)}`).join("<br>")}</p>` : "<p>Alles goed! 🎉</p>"}
      <div class="row" style="justify-content:center"><a class="btn" href="#/toets/${focus}" onclick="setTimeout(render)">Nog een keer</a><a class="btn secondary" href="#/">Klaar</a></div></div>`;
  }
  const key = e => { if (e.key === "Enter" && $("#nx")) { e.preventDefault(); $("#nx").click(); } };
  document.addEventListener("keydown", key);
  cleanup = () => document.removeEventListener("keydown", key);
  next();
}

// ---------- study map ----------
function viewKaart(view = "alle") {
  let numbers = true, names = false;
  const draw = () => {
    app.innerHTML = `<h1>🔍 De kaart van Europa</h1>
      <p class="muted small">Tik op een land om de naam te zien en te horen.</p>
      <div class="regions"><button class="${view === "alle" ? "" : "secondary"}" data-v="alle">Heel Europa</button>
        ${HOME.regions.map(r => `<button class="${view === r.key ? "" : "secondary"}" data-v="${r.key}">${esc(r.name)}</button>`).join("")}</div>
      <div class="row"><label style="margin:0;font-weight:500"><input type="checkbox" id="cn" ${numbers ? "checked" : ""} style="width:auto"> nummers</label>
        <label style="margin:0;font-weight:500"><input type="checkbox" id="cm" ${names ? "checked" : ""} style="width:auto"> namen</label></div>
      <div class="map-wrap" id="mapbox">${mapSVG({ view, numbers, names, clickable: true })}</div>`;
    app.querySelectorAll("[data-v]").forEach(b => b.onclick = () => { view = b.dataset.v; draw(); });
    $("#cn").onchange = e => { numbers = e.target.checked; draw(); };
    $("#cm").onchange = e => { names = e.target.checked; draw(); };
    $("#mapbox").addEventListener("click", e => {
      const el = e.target.closest("[data-n]"); if (!el) return;
      const c = MAP.countries[el.dataset.n];
      $("#mapbox").innerHTML = mapSVG({ view, numbers, names, clickable: true, marks: { [el.dataset.n]: "right" } });
      toast(`${el.dataset.n}. ${c.name}`); say(c.name);
    });
  };
  draw();
}

// ---------- scores ----------
const lvl = p => p >= 80 ? "g" : p >= 50 ? "w" : "b";
async function viewScores(uid) {
  const s = await api("stats" + (uid ? `?user=${encodeURIComponent(uid)}` : ""));
  const self = !uid || +uid === ME.id;
  const maxN = Math.max(1, ...s.days.map(d => d.n));
  const fmtDay = d => { const [, m, dd] = d.split("-"); return `${+dd}/${+m}`; };
  app.innerHTML = `${self ? "" : `<a href="/#/students">← Alle leerlingen</a>`}
    <div class="spread"><h1>📊 ${self ? "Mijn scores" : "Scores van " + esc(s.user.name)}</h1>
      <a class="btn secondary" href="/api/export.csv?module=topografie${uid ? `&user=${encodeURIComponent(uid)}` : ""}">⬇ Download (CSV)</a></div>
    <div class="chips"><span class="chip">📝 ${s.total} antwoorden</span><span class="chip">🎯 ${s.pct ?? "–"}% goed</span>
      <span class="chip">🔥 ${s.streak} dagen op rij</span><span class="chip">🏆 Proeftoets: ${s.best ? s.best + "%" : "–"}</span></div>
    <div class="card"><h3>Laatste 14 dagen</h3>
      <div class="days">${s.days.map(d => `<div class="d" title="${fmtDay(d.day)}: ${d.n} vragen${d.n ? `, ${d.pct}% goed` : ""}"><i style="height:${Math.round(100 * d.n / maxN)}%"></i></div>`).join("")}</div>
      <div class="days-x">${s.days.map((d, i) => `<span>${i % 2 === 1 ? fmtDay(d.day) : ""}</span>`).join("")}</div></div>
    <h2>Per land</h2>
    <div class="card">${s.regions.map(r => `<h3 style="margin-top:10px">${esc(r.name)}</h3>
      ${r.countries.map(c => `<div class="country-row"><span class="nm">${c.num}. ${esc(c.name)}</span>
        <div class="bar ${c.n ? lvl(c.pct) : ""}"><i style="width:${c.n ? c.pct : 0}%"></i></div>
        <span class="pc">${c.n ? `${lvl(c.pct) === "g" ? "✓" : lvl(c.pct) === "w" ? "~" : "✗"} ${c.pct}% · ${c.n}×` : "–"}</span></div>`).join("")}`).join("")}
      <div class="legend"><span style="--c:#0ca30c">✓ 80–100% goed</span><span style="--c:#fab219">~ 50–79%</span><span style="--c:#d03b3b">✗ onder 50%</span></div></div>
    <h2>Laatste fouten</h2>
    <div class="card">${s.mistakes.length ? `<div class="tablewrap"><table class="list"><tr><th>Vraag</th><th>Antwoord</th><th>Goed is</th></tr>
      ${s.mistakes.map(m => `<tr><td>${esc(m.prompt)}</td><td><s>${esc(m.given) || "(leeg)"}</s></td><td><b>${esc(m.expected)}</b></td></tr>`).join("")}</table></div>`
      : `<p class="muted">Geen fouten.</p>`}</div>`;
}

render();
