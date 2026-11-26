"use strict";
const $ = (s, el = document) => el.querySelector(s);
const app = $("#app");
let ME = null;

// ---------- hulpjes ----------
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const MODULE = "nederlands";
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
const PRAISE = ["Heel goed!", "Super!", "Goed zo!", "Prima!", "Uitstekend!", "Knap!", "Helemaal goed!"];
const OOPS = ["Helaas!", "Bijna. Kijk nog eens:", "Jammer!", "Niet erg, kijk goed:"];
const RANKS = [[0, "Beginner"], [200, "Op weg"], [500, "Goed bezig"], [1000, "Gevorderd"], [2000, "Expert"], [4000, "Meester"], [8000, "Kampioen"]];
function rank(xp) {
  let i = 0; while (i + 1 < RANKS.length && xp >= RANKS[i + 1][0]) i++;
  const next = RANKS[i + 1];
  return { name: RANKS[i][1], next: next ? next[1] : null, need: next ? next[0] - xp : 0 };
}

// ---------- spraak: server (Piper/Azure) of anders de browser ----------
let TTS_SERVER = false, nlVoice = null;
function loadVoices() { const v = speechSynthesis.getVoices(); nlVoice = v.find(x => x.lang === "nl-NL") || v.find(x => x.lang.startsWith("nl")) || null; }
if ("speechSynthesis" in window) { loadVoices(); speechSynthesis.onvoiceschanged = loadVoices; }
const player = new Audio();
player.preservesPitch = true;
async function say(text, slow = false) {
  if (TTS_SERVER) {
    try {
      player.pause();
      player.src = `/api/m/${MODULE}/tts?v=2&t=` + encodeURIComponent(text);
      player.defaultPlaybackRate = player.playbackRate = slow ? 0.7 : 1;
      await player.play();
      return;
    } catch (e) { /* terugvallen op de browser */ }
  }
  if (!("speechSynthesis" in window)) return toast("Deze browser kan niet voorlezen");
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text); u.lang = "nl-NL"; if (nlVoice) u.voice = nlVoice; u.rate = slow ? 0.6 : 0.95;
  speechSynthesis.speak(u);
}
const sayBtn = text => `<button class="say" title="Luister" data-say="${esc(text)}">🔊</button>`;
document.addEventListener("click", e => { const b = e.target.closest("[data-say]"); if (b) { e.preventDefault(); say(b.dataset.say); } });

// ---------- router ----------
window.addEventListener("hashchange", render);
let cleanup = null, HOME = null, STAFF = false;
async function render() {
  if (cleanup) { cleanup(); cleanup = null; }
  const b = await Portal.boot(MODULE);
  if (!b) return;
  ME = b.me; STAFF = b.staff; TTS_SERVER = b.tts;
  const [route, a, c] = location.hash.replace(/^#\/?/, "").split("/");
  const views = { "": viewHome, groep: viewGroup, oefen: viewPlay, scores: viewScores, lessen: viewLessons, les: viewLesson };
  (views[route] || viewHome)(a, c);
}

// ---------- start ----------
async function viewHome() {
  const h = HOME = await api("home");
  const r = rank(h.xp);
  const goalPct = Math.min(100, Math.round(100 * h.today / h.goal));
  app.innerHTML = `
    <h1>Hallo ${esc(h.name)}!</h1>
    <div class="chips">
      <span class="chip">🔥 ${h.streak} ${h.streak === 1 ? "dag" : "dagen"} op rij</span>
      <span class="chip">⭐ ${h.xp} punten · ${esc(r.name)}</span>
    </div>
    <div class="card" style="margin-bottom:12px">
      <div class="spread"><b>Doel van vandaag</b><span class="muted">${h.today} / ${h.goal} ${goalPct >= 100 ? "✅" : ""}</span></div>
      <div class="bar ${goalPct >= 100 ? "good" : ""}" style="margin-top:8px"><i style="width:${goalPct}%"></i></div>
      ${r.next ? `<div class="small muted" style="margin-top:10px">Nog ${r.need} punten tot <b>${esc(r.next)}</b></div>` : ""}
    </div>
    <a class="card tile" href="#/lessen" style="margin-bottom:12px;display:block">
      <div class="spread"><h3>📘 Lessen · Lessons</h3><span class="chip">${h.lessons_done} / ${h.lessons_total} ✅</span></div>
      <div class="muted small">How to build a Dutch sentence, step by step, with colours and examples. Start here if you don't know the rules yet.</div></a>
    <div class="grid">
      ${h.groups.map(g => `<a class="card tile" href="#/groep/${g.key}"><div class="ico">${g.icon}</div><h3>${esc(g.name)}</h3><div class="muted small">${esc(g.desc)}</div></a>`).join("")}
      <a class="card tile" href="#/scores"><div class="ico">📊</div><h3>Mijn scores</h3><div class="muted small">${h.weak_count ? `${h.weak_count} dingen om te herhalen` : "Bekijk hoe het gaat"}</div></a>
    </div>`;
}

async function viewGroup(key) {
  const h = HOME || await api("home");
  const g = h.groups.find(x => x.key === key);
  if (!g) { location.hash = "#/"; return; }
  let ex = g.ex[0][0];
  const focus = [["alle", "Alles door elkaar"], ...g.focus, ["zwak", "⚠️ Wat ik nog moeilijk vind"]];
  app.innerHTML = `<a href="#/">← Terug</a><h1>${g.icon} ${esc(g.name)}</h1>
    ${g.ex.length > 1 ? `<h2>Wat wil je doen?</h2><div class="grid">${g.ex.map(e => `<button class="card tile ${e[0] === ex ? "sel" : ""}" data-ex="${e[0]}"><h3>${esc(e[1])}</h3><div class="muted small">${esc(e[2])}</div></button>`).join("")}</div>` : `<p class="muted">${esc(g.ex[0][2])}</p>`}
    <h2>Kies</h2><div class="grid">${focus.map(f => `<button class="card tile" data-f="${f[0]}"><h3>${esc(f[1])}</h3></button>`).join("")}</div>`;
  app.querySelectorAll("[data-ex]").forEach(b => b.onclick = () => {
    ex = b.dataset.ex; app.querySelectorAll("[data-ex]").forEach(x => x.classList.toggle("sel", x === b));
  });
  app.querySelectorAll("[data-f]").forEach(b => b.onclick = () => (location.hash = `#/oefen/${ex}/${b.dataset.f}`));
}

// ---------- oefenen ----------
function promptHTML(q) {
  const p = q.prompt;
  let h = `<div class="prompt">`;
  if (p.listen) h += `<div style="font-size:60px">🎧</div>`;
  if (p.emoji) h += `<div class="emoji">${esc(p.emoji)}</div>`;
  if (p.big) h += `<div class="fr">${esc(p.big)} ${p.say ? sayBtn(p.say) : ""}</div>`;
  if (p.sub) h += `<div class="inf">${esc(p.sub)} ${p.say_hint ? sayBtn(p.say_hint) : ""}</div>`;
  if (p.text) h += `<div class="nl">${esc(p.text)}</div>`;
  if (p.cat) h += `<div class="small muted">${esc(p.cat)}</div>`;
  h += `</div>`;
  if (p.listen) h += `<div class="row" style="justify-content:center;margin-top:6px"><button class="secondary" data-play>🔊 Nog een keer</button><button class="secondary" data-slow>🐢 Langzaam</button></div>`;
  return h;
}
function feedbackHTML(res, given) {
  const ok = res.result === "correct";
  const t = ok ? pick(PRAISE) : res.result === "almost" ? "Bijna! Kijk naar de spelling." : pick(OOPS);
  const info = res.info || {};
  const tbl = info.rows && !ok ? `<div class="small muted" style="margin-top:10px"><b>${esc(info.rows.verb)}</b> · ${esc(info.rows.nl)}</div>
    <table class="conj">${info.rows.rows.map(r => `<tr class="${r.hl ? "hl" : ""}"><td>${esc(r.pron)}</td><td>${esc(r.form)}</td></tr>`).join("")}</table>` : "";
  return `<div class="feedback ${res.result} pop">
    <div class="title">${ok ? "✅" : res.result === "almost" ? "🟡" : "❌"} ${esc(t)} ${res.xp_gained ? `<span class="small muted">+${res.xp_gained}</span>` : ""}</div>
    ${!ok && given !== undefined && given !== null && res.kind !== "choice" ? `<div class="small muted">Jij: <s>${esc(given) || "(leeg)"}</s></div>` : ""}
    <div class="sol">${info.emoji ? `<span style="font-size:34px;vertical-align:middle">${esc(info.emoji)}</span> ` : ""}${esc(info.line || res.answer)} ${sayBtn(res.say)}</div>
    ${tbl}
    ${res.lesson && !ok ? `<div style="margin-top:10px"><a class="btn secondary" href="#/les/${res.lesson.id}">📘 ${esc(res.lesson.title)}</a></div>` : ""}</div>`;
}

async function viewPlay(ex, focus) {
  const s = { n: 0, ok: 0 };
  let q, answered = false, built = [];
  const bar = () => `<span class="chip">✅ ${s.ok} / ${s.n}</span>`;

  async function next() {
    answered = false; built = [];
    try { q = await api("question", { ex, focus }); }
    catch (e) { toast(e.message); history.back(); return; }
    const grp = (HOME?.groups || []).find(g => g.ex.some(e => e[0] === ex));
    let body = promptHTML(q);
    if (q.kind === "choice") {
      const cls = q.opt_style === "emoji" ? "emoji" : q.options.length === 2 ? "two" : "";
      body += `<div class="options ${cls}">${q.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="n">${i + 1}</span>${esc(o)}</button>`).join("")}</div>`;
    } else if (q.kind === "type") {
      body += `<form class="answer-row" id="f"><input id="inp" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" placeholder="typ hier"><button>OK</button></form>`;
    } else {
      body += `<div class="build-line" id="line"></div>
        <div class="tiles" id="tiles">${q.tiles.map((t, i) => `<button class="tilebtn" data-t="${i}">${esc(t)}</button>`).join("")}</div>
        <div class="row" style="justify-content:center;margin-top:14px"><button class="secondary" id="clear">↺ Opnieuw</button><button id="check">Controleer</button></div>`;
    }
    app.innerHTML = `<div class="qhead"><a href="#/groep/${grp ? grp.key : ""}">← Stoppen</a>${bar()}</div>
      <div class="card">${q.note ? `<p class="small muted">${esc(q.note)}</p>` : ""}${body}<div id="fb"></div></div>`;

    app.querySelector("[data-play]")?.addEventListener("click", () => say(q.prompt.say));
    app.querySelector("[data-slow]")?.addEventListener("click", () => say(q.prompt.say, true));
    if (q.prompt.listen) setTimeout(() => say(q.prompt.say), 250);

    if (q.kind === "choice") app.querySelectorAll(".opt").forEach(b => b.onclick = () => answer(q.options[+b.dataset.i], +b.dataset.i));
    if (q.kind === "type") {
      const inp = $("#inp"); inp.focus();
      $("#f").onsubmit = e => { e.preventDefault(); answered ? next() : answer(inp.value); };
    }
    if (q.kind === "build") {
      const drawLine = () => {
        $("#line").innerHTML = built.map((i, k) => `<button class="tilebtn" data-b="${k}">${esc(q.tiles[i])}</button>`).join("") +
          (built.length ? `<span class="end">${esc(q.prompt.end || "")}</span>` : `<span class="muted small">Tik op de woorden hieronder</span>`);
        app.querySelectorAll("#tiles .tilebtn").forEach(b => b.classList.toggle("used", built.includes(+b.dataset.t)));
        app.querySelectorAll("[data-b]").forEach(b => b.onclick = () => { if (!answered) { built.splice(+b.dataset.b, 1); drawLine(); } });
      };
      app.querySelectorAll("#tiles .tilebtn").forEach(b => b.onclick = () => {
        const i = +b.dataset.t; if (answered || built.includes(i)) return;
        built.push(i); drawLine();
        if (built.length === q.tiles.length) $("#check").focus();
      });
      $("#clear").onclick = () => { if (!answered) { built = []; drawLine(); } };
      $("#check").onclick = () => {
        if (answered) return next();
        if (built.length < q.tiles.length) return toast("Gebruik alle woorden");
        answer(built.map(i => q.tiles[i]).join(" "));
      };
      drawLine();
    }
  }

  async function answer(given, idx) {
    if (answered) return; answered = true;
    const res = await api("answer", { qid: q.qid, answer: given });
    s.n++; if (res.result === "correct") s.ok++;
    $(".qhead .chip").outerHTML = bar();
    if (q.kind === "choice") {
      app.querySelectorAll(".opt").forEach((b, j) => {
        b.disabled = true;
        if (res.accepted.includes(q.options[j])) b.classList.add("right");
        else if (j === idx) b.classList.add("wrong");
      });
    }
    if (q.kind === "type") {
      const inp = $("#inp"); inp.readOnly = true;
      inp.style.borderColor = res.result === "correct" ? "var(--good)" : res.result === "almost" ? "var(--warn)" : "var(--bad)";
    }
    if (q.kind === "build") { $("#check").textContent = "Volgende ↵"; $("#clear").disabled = true; }
    if (res.result === "wrong") $(".card").classList.add("shake");
    $("#fb").innerHTML = feedbackHTML(res, q.kind === "choice" ? null : given) + (q.kind === "build" ? "" : `<button class="next" id="nx">Volgende ↵</button>`);
    $("#nx")?.addEventListener("click", next);
    (q.kind === "type" ? $("#inp") : q.kind === "build" ? $("#check") : $("#nx")).focus();
    say(res.say);
  }

  const key = e => {
    if (!q || q.kind !== "choice") return;
    if (!answered && /^[1-5]$/.test(e.key) && +e.key <= q.options.length) answer(q.options[+e.key - 1], +e.key - 1);
    else if (answered && e.key === "Enter") { e.preventDefault(); next(); }
  };
  document.addEventListener("keydown", key);
  cleanup = () => { document.removeEventListener("keydown", key); player.pause(); if ("speechSynthesis" in window) speechSynthesis.cancel(); };
  next();
}

// ---------- scores ----------
const fmtDay = d => { const [, m, dd] = d.split("-"); return `${+dd}/${+m}`; };
const lvl = p => p >= 80 ? "g" : p >= 50 ? "w" : "b";
async function viewScores(uid) {
  const s = await api("stats" + (uid ? `?user=${encodeURIComponent(uid)}` : ""));
  const maxN = Math.max(1, ...s.days.map(d => d.n));
  const self = !uid || +uid === ME.id;
  const groups = {};
  s.cats.forEach(c => (groups[c.grp] = groups[c.grp] || []).push(c));
  app.innerHTML = `${self ? "" : `<a href="/#/students">← Alle leerlingen</a>`}
    <div class="spread"><h1>📊 ${self ? "Mijn scores" : "Scores van " + esc(s.user.name)}</h1>
      <a class="btn secondary" href="/api/export.csv?module=nederlands${uid ? `&user=${encodeURIComponent(uid)}` : ""}">⬇ Download (CSV)</a></div>
    <div class="chips">
      <span class="chip">📝 ${s.total} antwoorden</span>
      <span class="chip">🎯 ${s.pct ?? "–"}% goed</span>
      <span class="chip">🔥 ${s.streak} ${s.streak === 1 ? "dag" : "dagen"} op rij</span>
      <span class="chip">⭐ ${s.xp} punten · ${esc(rank(s.xp).name)}</span>
    </div>
    <div class="card"><h3>Laatste 14 dagen</h3><div class="small muted">Aantal vragen per dag</div>
      <div class="days">${s.days.map(d => `<div class="d" data-tip="${fmtDay(d.day)}: ${d.n} vragen${d.n ? `, ${d.pct}% goed` : ""}"><i style="height:${Math.round(100 * d.n / maxN)}%"></i></div>`).join("")}</div>
      <div class="days-x">${s.days.map((d, i) => `<span>${i % 2 === 1 ? fmtDay(d.day) : ""}</span>`).join("")}</div>
    </div>
    <h2>Per onderdeel</h2>
    <div class="card">${Object.keys(groups).length ? Object.entries(groups).map(([g, list]) => `<h3 style="margin-top:8px">${esc(g)}</h3>
      ${list.map(c => `<div class="cat-row" data-tip="${esc(c.cat)}: ${c.pct}% goed (${c.n}×)"><span class="lab">${esc(c.cat)}</span><div class="bar ${lvl(c.pct)}"><i style="width:${c.pct}%"></i></div><span class="pct">${lvl(c.pct) === "g" ? "✓" : lvl(c.pct) === "w" ? "~" : "✗"} ${c.pct}% · ${c.n}×</span></div>`).join("")}`).join("")
      : `<p class="muted">Nog niets geoefend.</p>`}
      ${Object.keys(groups).length ? `<div class="legend"><span style="--c:#0ca30c">✓ 80–100% goed</span><span style="--c:#fab219">~ 50–79%</span><span style="--c:#d03b3b">✗ onder 50%</span></div>` : ""}</div>
    <h2>Nog oefenen</h2>
    <div class="card">${s.weak.length ? `<div class="tablewrap"><table class="list"><tr><th>Wat</th><th>Oefening</th><th>Fout</th></tr>
      ${s.weak.map(w => `<tr><td><b>${esc(w.label)}</b> ${w.say ? sayBtn(w.say) : ""}</td><td class="small">${esc(w.ex)}</td><td>${w.wrong}× van ${w.seen}${w.box >= 3 ? " <span class='small muted'>· gaat beter</span>" : ""}</td></tr>`).join("")}
      </table></div>` : `<p class="muted">Niets! Heel goed 👏</p>`}</div>
    <h2>Laatste fouten</h2>
    <div class="card">${s.mistakes.length ? `<div class="tablewrap"><table class="list"><tr><th>Vraag</th><th>Antwoord</th><th>Goed is</th></tr>
      ${s.mistakes.map(m => `<tr><td>${esc(m.prompt)}</td><td><s>${esc(m.given) || "(leeg)"}</s></td><td><b>${esc(m.expected)}</b></td></tr>`).join("")}
      </table></div>` : `<p class="muted">Geen fouten.</p>`}</div>`;
  bindTips();
}
function bindTips() {
  let tip;
  app.querySelectorAll("[data-tip]").forEach(el => {
    el.addEventListener("mouseenter", () => { tip = document.createElement("div"); tip.className = "tip"; tip.textContent = el.dataset.tip; document.body.append(tip); });
    el.addEventListener("mousemove", e => { if (tip) { tip.style.left = Math.min(e.clientX + 12, innerWidth - tip.offsetWidth - 8) + "px"; tip.style.top = (e.clientY - 34) + "px"; } });
    el.addEventListener("mouseleave", () => { tip?.remove(); tip = null; });
    el.addEventListener("click", () => toast(el.dataset.tip));
  });
}

// ---------- lessons (explanations in English) ----------
const ROLE_NAMES = { s: "who", v: "verb", v2: "2nd verb / end", t: "time / place", n: "niet / geen", q: "question word", c: "omdat / dat / als", r: "rest" };
const sentHTML = parts => `<div class="sent">${parts.map(([w, r]) => `<span class="blk ${r}">${esc(w)}</span>`).join("")}</div>`;
const normSent = x => x.toLowerCase().replace(/[.,?!]/g, " ").split(/\s+/).filter(Boolean).join(" ");

async function viewLessons() {
  const list = await api("lessons");
  const next = (list.find(l => !l.done) || {}).id;
  app.innerHTML = `<a href="#/">← Terug</a><h1>📘 Lessons</h1>
    <p class="muted">Short lessons about how Dutch sentences work. Each lesson: a few cards with examples, then a little practice.
      Do them in order: each lesson builds on the one before.</p>
    <div class="roles">${Object.entries(ROLE_NAMES).map(([r, n]) => `<span class="blk ${r}">${n}</span>`).join("")}</div>
    <div class="grid" style="margin-top:12px">${list.map(l => `<a class="card tile ${l.id === next ? "sel" : ""}" href="#/les/${l.id}">
      <div class="spread"><h3>${esc(l.title)}</h3>${l.done ? "✅" : l.tried ? "🔁" : ""}</div>
      <div class="muted small">${esc(l.short)}${l.id === next ? " · 👉 <b>next</b>" : ""}</div></a>`).join("")}</div>`;
}

async function viewLesson(id) {
  const L = await api("lesson?id=" + encodeURIComponent(id));
  const steps = [...L.cards.map(c => ({ kind: "card", c })), ...L.practice.map(p => ({ kind: "practice", p }))];
  let i = 0, score = 0;
  const dots = () => `<div class="steps-dots">${steps.map((_, k) => `<i class="${k === i ? "on" : k < i ? "done" : ""}"></i>`).join("")}</div>`;
  function draw() {
    if (i >= steps.length) return finish();
    const st = steps[i];
    const head = `<div class="qhead"><a href="#/lessen">← Lessons</a><span class="small muted">${esc(L.title)}</span></div>${dots()}`;
    if (st.kind === "card") {
      const c = st.c;
      app.innerHTML = `${head}<div class="card"><h2 style="margin-top:0">${esc(c.title)}</h2>
        <p class="lesson-text">${esc(c.text)}</p>
        ${c.examples.map(e => `<div class="ex"><div class="row" style="flex-wrap:nowrap;align-items:flex-start">${sentHTML(e.parts)}${sayBtn(e.say)}</div><div class="en">${esc(e.en)}</div></div>`).join("")}
        ${c.tip ? `<div class="tipbox">💡 ${esc(c.tip)}</div>` : ""}
        <div class="roles">${[...new Set(c.examples.flatMap(e => e.parts.map(p => p[1])))].map(r => `<span class="blk ${r}">${ROLE_NAMES[r]}</span>`).join("")}</div>
        <div class="row" style="justify-content:space-between;margin-top:14px">
          <button class="secondary" id="prev" ${i === 0 ? "disabled" : ""}>← Back</button><button id="nxt">Next →</button></div></div>`;
      $("#prev").onclick = () => { i--; draw(); };
      $("#nxt").onclick = () => { i++; draw(); };
      return;
    }
    const p = st.p;
    const n = i - L.cards.length + 1;
    let answered = false;
    const done = (ok, why, say) => {
      answered = true; if (ok) score++;
      $("#fb").innerHTML = `<div class="feedback ${ok ? "correct" : "wrong"} pop"><div class="title">${ok ? "✅ " + pick(PRAISE) : "❌ " + pick(OOPS)}</div>
        ${why ? `<div class="why">${esc(why)}</div>` : ""}${say ? `<div class="sol" style="font-size:19px;margin-top:6px">${esc(say)} ${sayBtn(say)}</div>` : ""}</div>
        <button class="next" id="nx">Next ↵</button>`;
      $("#nx").onclick = () => { i++; draw(); };
      if (say) say && window.say(say);
    };
    if (p.type === "choice") {
      app.innerHTML = `${head}<div class="card"><div class="small muted">Practice ${n} of ${L.practice.length}</div>
        <div class="prompt"><div class="nl big">${esc(p.q)}</div></div>
        <div class="options ${p.options.length === 2 ? "two" : ""}">${p.options.map((o, k) => `<button class="opt" data-k="${k}"><span class="n">${k + 1}</span>${esc(o)}</button>`).join("")}</div>
        <div id="fb"></div></div>`;
      app.querySelectorAll(".opt").forEach(b => b.onclick = () => {
        if (answered) return;
        const k = +b.dataset.k;
        app.querySelectorAll(".opt").forEach((x, j) => { x.disabled = true; if (j === p.answer) x.classList.add("right"); else if (j === k) x.classList.add("wrong"); });
        const full = p.options[p.answer];
        done(k === p.answer, p.why, p.q.includes("___") ? p.q.replace("___", full) : full);
      });
    } else {
      const words = p.nl.replace(/[.,?!]/g, "").split(/\s+/).map(w => w === w.toUpperCase() || ["Utrecht", "Anna", "Amsterdam", "Nederlands"].includes(w) ? w : w.toLowerCase());
      let tiles = [...words]; for (let t = 0; t < 10 && tiles.join() === words.join(); t++) tiles.sort(() => Math.random() - .5);
      let built = [];
      const end = /[?]$/.test(p.nl) ? "?" : ".";
      app.innerHTML = `${head}<div class="card"><div class="small muted">Practice ${n} of ${L.practice.length}</div>
        <div class="prompt"><div class="small muted">Make this sentence in Dutch:</div><div class="nl big">${esc(p.en)}</div></div>
        <div class="build-line" id="line"></div>
        <div class="tiles" id="tiles">${tiles.map((w, k) => `<button class="tilebtn" data-t="${k}">${esc(w)}</button>`).join("")}</div>
        <div class="row" style="justify-content:center;margin-top:14px"><button class="secondary" id="clear">↺ Again</button><button id="check">Check</button></div>
        <div id="fb"></div></div>`;
      const drawLine = () => {
        $("#line").innerHTML = built.map((k, j) => `<button class="tilebtn" data-b="${j}">${esc(tiles[k])}</button>`).join("") +
          (built.length ? `<span class="end">${end}</span>` : `<span class="muted small">Tap the words below</span>`);
        app.querySelectorAll("#tiles .tilebtn").forEach(b => b.classList.toggle("used", built.includes(+b.dataset.t)));
        app.querySelectorAll("[data-b]").forEach(b => b.onclick = () => { if (!answered) { built.splice(+b.dataset.b, 1); drawLine(); } });
      };
      app.querySelectorAll("#tiles .tilebtn").forEach(b => b.onclick = () => { const k = +b.dataset.t; if (!answered && !built.includes(k)) { built.push(k); drawLine(); } });
      $("#clear").onclick = () => { if (!answered) { built = []; drawLine(); } };
      $("#check").onclick = () => {
        if (answered) return;
        if (built.length < tiles.length) return toast("Use all the words");
        const given = normSent(built.map(k => tiles[k]).join(" "));
        const ok = [p.nl, ...(p.alts || [])].some(x => normSent(x) === given);
        $("#check").disabled = true; $("#clear").disabled = true;
        done(ok, ok ? "" : "Look at the order of the coloured blocks in the lesson: where does the verb go?", p.nl);
      };
      drawLine();
    }
  }
  async function finish() {
    const r = await api("lesson/done", { id: L.id, score, total: L.practice.length });
    app.innerHTML = `<div class="card center" style="margin-top:20px"><div style="font-size:56px">${r.passed ? "🎉" : "💪"}</div>
      <h2>${esc(L.title)}</h2><p>${score} of ${L.practice.length} correct${r.xp_gained ? ` · +${r.xp_gained} points` : ""}</p>
      <p class="muted">${r.passed ? "Lesson done! Now practise it a bit more, so it sticks." : "Read the cards once more and try again. You'll get there!"}</p>
      <div class="row" style="justify-content:center">
        ${r.passed ? "" : `<a class="btn" href="#/les/${L.id}" onclick="setTimeout(render)">↺ Try again</a>`}
        ${L.practise ? `<a class="btn ${r.passed ? "" : "secondary"}" href="#/oefen/z-bouw/${L.practise}">🧩 Practise more</a>` : ""}
        ${L.next ? `<a class="btn secondary" href="#/les/${L.next}">Next lesson →</a>` : ""}
        <a class="btn secondary" href="#/lessen">All lessons</a></div></div>`;
  }
  draw();
}

render();
