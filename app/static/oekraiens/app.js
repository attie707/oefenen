"use strict";
const $ = (s, el = document) => el.querySelector(s);
const app = $("#app");
const esc = Portal.esc;
const MODULE = "oekraiens";
let ME = null, LANG = "en", TTS_SERVER = false, HOME = null, cleanup = null;

// ---------- texts (menus follow the user's language) ----------
const TXT = {
  en: {
    abc: "Alphabet", scores: "Scores", students: "Students", back: "← Back", stop: "← Stop", next: "Next ↵",
    what: "What do you want to do?", choose: "Choose", all: "🌍 Everything mixed", weak: "⚠️ What I find difficult",
    no_weak: "Nothing difficult yet. Well done! We'll practise everything.",
    hello: n => `Привіт, ${n}! 👋`, streak: n => `🔥 ${n} ${n === 1 ? "day" : "days"} in a row`, points: n => `⭐ ${n} points`,
    today: "Today", questions: "questions", to_repeat: n => `${n} things to repeat`, my_scores: "My scores", see_progress: "See how it's going",
    latin: "Show Latin letters", again: "🔊 Again", slow: "🐢 Slowly", listen: "Listen…",
    praise: ["Чудово! (Great!)", "Добре! (Good!)", "Super!", "Excellent!", "Молодець! (Well done!)"],
    oops: ["Oops!", "Not quite:", "Never mind, look:", "Have another look:"],
    almost: "Almost! Check the little marks (й, ї, є…).", you: "You:", empty: "(empty)",
    check: "Check", restart: "↺ Start over", tap_words: "Tap the words below", use_all: "Use all the words",
    own_kbd: "⌨️ use my own keyboard", screen_kbd: "⌨️ use the on-screen keyboard", type_here: "type here",
    abc_title: "🔤 The Ukrainian alphabet", abc_intro: "33 letters. Tap 🔊 to hear the letter and the example word. Start with group 1: those letters work just like ours.",
    practise_group: "Practise this group", scores_of: n => `Scores of ${n}`, all_students: "← All students", download: "⬇ Download (CSV)",
    answers: "answers", correct: "correct", last14: "Last 14 days", per_part: "Per part", to_practise: "Still to practise",
    nothing: "Nothing! Great 👏", last_mistakes: "Recent mistakes", no_mistakes: "No mistakes.", question: "Question", answer: "Answer",
    right_is: "Correct is", what_col: "What", ex_col: "Exercise", wrong_col: "Wrong", of: "of", better: "getting better",
    nothing_yet: "Nothing practised yet.", legend: ["✓ 80–100% correct", "~ 50–79%", "✗ below 50%"],
  },
  nl: {
    abc: "Alfabet", scores: "Scores", students: "Leerlingen", back: "← Terug", stop: "← Stoppen", next: "Volgende ↵",
    what: "Wat wil je doen?", choose: "Kies", all: "🌍 Alles door elkaar", weak: "⚠️ Wat ik nog moeilijk vind",
    no_weak: "Nog niets moeilijks. Goed bezig! We oefenen alles.",
    hello: n => `Привіт, ${n}! 👋`, streak: n => `🔥 ${n} ${n === 1 ? "dag" : "dagen"} op rij`, points: n => `⭐ ${n} punten`,
    today: "Vandaag", questions: "vragen", to_repeat: n => `${n} dingen om te herhalen`, my_scores: "Mijn scores", see_progress: "Bekijk hoe het gaat",
    latin: "Toon Latijnse letters", again: "🔊 Nog een keer", slow: "🐢 Langzaam", listen: "Luister…",
    praise: ["Чудово! (Geweldig!)", "Добре! (Goed!)", "Super!", "Uitstekend!", "Молодець! (Knap!)"],
    oops: ["Oeps!", "Net niet:", "Niet erg, kijk:", "Kijk nog eens:"],
    almost: "Bijna! Let op de tekentjes (й, ї, є…).", you: "Jij:", empty: "(leeg)",
    check: "Controleer", restart: "↺ Opnieuw", tap_words: "Tik op de woorden hieronder", use_all: "Gebruik alle woorden",
    own_kbd: "⌨️ mijn eigen toetsenbord", screen_kbd: "⌨️ toetsenbord op het scherm", type_here: "typ hier",
    abc_title: "🔤 Het Oekraïense alfabet", abc_intro: "33 letters. Tik op 🔊 om de letter en het voorbeeldwoord te horen. Begin met groep 1: die letters werken net als bij ons.",
    practise_group: "Oefen deze groep", scores_of: n => `Scores van ${n}`, all_students: "← Alle leerlingen", download: "⬇ Download (CSV)",
    answers: "antwoorden", correct: "goed", last14: "Laatste 14 dagen", per_part: "Per onderdeel", to_practise: "Nog oefenen",
    nothing: "Niets! Heel goed 👏", last_mistakes: "Laatste fouten", no_mistakes: "Geen fouten.", question: "Vraag", answer: "Antwoord",
    right_is: "Goed is", what_col: "Wat", ex_col: "Oefening", wrong_col: "Fout", of: "van", better: "gaat beter",
    nothing_yet: "Nog niets geoefend.", legend: ["✓ 80–100% goed", "~ 50–79%", "✗ onder 50%"],
  },
};
const t = (k, ...a) => { const v = (TXT[LANG] || TXT.en)[k] ?? TXT.en[k]; return typeof v === "function" ? v(...a) : v; };
const pick = a => a[Math.floor(Math.random() * a.length)];

// ---------- helpers ----------
async function api(path, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const r = await fetch(`/api/m/${MODULE}/` + path, opt);
  const data = await r.json().catch(() => ({}));
  if (r.status === 401 || (r.status === 403 && data.error === "must_change")) { location.href = "/"; throw new Error(data.error); }
  if (!r.ok) throw new Error(data.error || "Something went wrong");
  return data;
}
function toast(msg, ms = 2600) {
  const el = $("#toast"); el.textContent = msg; el.hidden = false;
  clearTimeout(toast._t); toast._t = setTimeout(() => (el.hidden = true), ms);
}
let LATIN = (() => { try { return localStorage.getItem("uk_latin") !== "0"; } catch (e) { return true; } })();
function setLatin(on) { LATIN = on; document.body.classList.toggle("hide-latin", !on); try { localStorage.setItem("uk_latin", on ? "1" : "0"); } catch (e) { /* ignore */ } }
const latinSwitch = () => `<label class="switch"><input type="checkbox" id="latin" ${LATIN ? "checked" : ""}> ${t("latin")}</label>`;
function bindLatin() { const c = $("#latin"); if (c) c.onchange = () => setLatin(c.checked); }
const tr = s => s ? `<div class="tr">${esc(s)}</div>` : "";

// speech: Ukrainian voice from the server (Piper/Azure), otherwise the browser
let ukVoice = null;
function loadVoices() { const v = speechSynthesis.getVoices(); ukVoice = v.find(x => x.lang === "uk-UA") || v.find(x => x.lang.startsWith("uk")) || null; }
if ("speechSynthesis" in window) { loadVoices(); speechSynthesis.onvoiceschanged = loadVoices; }
const player = new Audio();
player.preservesPitch = true;
async function say(text, slow = false) {
  if (TTS_SERVER) {
    try {
      player.pause();
      player.src = `/api/m/${MODULE}/tts?t=` + encodeURIComponent(text);
      player.defaultPlaybackRate = player.playbackRate = slow ? 0.7 : 1;
      await player.play();
      return;
    } catch (e) { /* fallback */ }
  }
  if (!("speechSynthesis" in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text); u.lang = "uk-UA"; if (ukVoice) u.voice = ukVoice; u.rate = slow ? 0.6 : 0.9;
  speechSynthesis.speak(u);
}
const sayBtn = s => `<button class="say" data-say="${esc(s)}" title="🔊">🔊</button>`;
document.addEventListener("click", e => { const b = e.target.closest("[data-say]"); if (b) { e.preventDefault(); say(b.dataset.say); } });

// ---------- on-screen Cyrillic keyboard ----------
const KB_ROWS = ["йцукенгшщзхї", "фівапролджє", "ячсмитьбюґ'"];
function keyboardHTML() {
  return `<div class="kbd" id="kbd">${KB_ROWS.map(r => `<div class="krow">${[...r].map(c => `<button type="button" data-k="${c}">${c === "'" ? "ʼ" : c}</button>`).join("")}</div>`).join("")}
    <div class="krow"><button type="button" class="mid" data-k="⇧">⇧</button><button type="button" class="wide" data-k=" ">␣</button><button type="button" class="mid" data-k="⌫">⌫</button></div></div>`;
}
function bindKeyboard(input) {
  let shift = false;
  app.querySelectorAll("[data-k]").forEach(b => b.onclick = () => {
    const k = b.dataset.k;
    const [a, z] = [input.selectionStart ?? input.value.length, input.selectionEnd ?? input.value.length];
    if (k === "⇧") { shift = !shift; b.style.background = shift ? "var(--blue-soft)" : ""; return; }
    if (k === "⌫") {
      const from = a === z ? Math.max(0, a - 1) : a;
      input.value = input.value.slice(0, from) + input.value.slice(z); input.setSelectionRange(from, from);
    } else {
      const c = shift ? k.toUpperCase() : k;
      input.value = input.value.slice(0, a) + c + input.value.slice(z); input.setSelectionRange(a + 1, a + 1);
      if (shift) { shift = false; app.querySelector('[data-k="⇧"]').style.background = ""; }
    }
    input.focus({ preventScroll: true });
  });
}
let OWN_KBD = false;

// ---------- router ----------
window.addEventListener("hashchange", render);
async function render() {
  if (cleanup) { cleanup(); cleanup = null; }
  const b = await Portal.boot(MODULE);
  if (!b) return;
  ME = b.me; LANG = ME.lang || "en"; TTS_SERVER = b.tts;
  document.documentElement.lang = LANG;
  $("#nav-abc").textContent = t("abc"); $("#nav-scores").textContent = t("scores"); $("#nav-staff").textContent = t("students");
  setLatin(LATIN);
  HOME = await api("home");
  const [route, a, c] = location.hash.replace(/^#\/?/, "").split("/");
  const views = { "": viewHome, groep: viewGroup, oefen: viewPlay, abetka: viewAlphabet, scores: viewScores };
  (views[route] || viewHome)(a, c);
}

// ---------- home ----------
function viewHome() {
  const h = HOME;
  const goal = Math.min(100, Math.round(100 * h.today / h.goal));
  app.innerHTML = `<h1>${esc(t("hello", h.name))}</h1>
    <div class="chips"><span class="chip">${t("streak", h.streak)}</span><span class="chip">${t("points", h.xp)}</span>
      <span class="chip">${t("today")}: ${h.today} / ${h.goal} ${goal >= 100 ? "✅" : ""}</span></div>
    <div class="bar ${goal >= 100 ? "good" : ""}" style="margin:-4px 0 18px"><i style="width:${goal}%"></i></div>
    <div class="grid">
      ${h.groups.map(g => `<a class="card tile" href="#/groep/${g.key}"><div class="ico">${g.icon}</div><h3>${esc(g.title)}</h3><div class="muted small">${esc(g.desc)}</div></a>`).join("")}
      <a class="card tile" href="#/abetka"><div class="ico">📜</div><h3>${t("abc_title").replace("🔤 ", "")}</h3><div class="muted small">А Б В Г Ґ Д Е Є Ж З И І Ї Й …</div></a>
      <a class="card tile" href="#/scores"><div class="ico">📊</div><h3>${t("my_scores")}</h3><div class="muted small">${h.weak_count ? t("to_repeat", h.weak_count) : t("see_progress")}</div></a>
    </div>`;
}

function viewGroup(key) {
  const g = HOME.groups.find(x => x.key === key);
  if (!g) { location.hash = "#/"; return; }
  let ex = g.ex[0].key;
  const focus = [["alle", t("all")], ...g.focus.map(f => [f.key, f.name]), ["zwak", t("weak")]];
  app.innerHTML = `<a href="#/">${t("back")}</a><h1>${g.icon} ${esc(g.title)}</h1>
    <h2>${t("what")}</h2><div class="grid">${g.ex.map(e => `<button class="card tile ${e.key === ex ? "sel" : ""}" data-ex="${e.key}"><h3>${esc(e.name)}</h3><div class="muted small">${esc(e.desc)}</div></button>`).join("")}</div>
    <h2>${t("choose")}</h2><div class="grid">${focus.map(f => `<button class="card tile" data-f="${f[0]}"><h3>${esc(f[1])}</h3></button>`).join("")}</div>`;
  app.querySelectorAll("[data-ex]").forEach(b => b.onclick = () => { ex = b.dataset.ex; app.querySelectorAll("[data-ex]").forEach(x => x.classList.toggle("sel", x === b)); });
  app.querySelectorAll("[data-f]").forEach(b => b.onclick = () => (location.hash = `#/oefen/${ex}/${b.dataset.f}`));
}

// ---------- practising ----------
function promptHTML(q) {
  const p = q.prompt;
  const ex = HOME.groups.flatMap(g => g.ex).find(e => e.key === q.ex);
  let h = `<div class="prompt"><div class="nl">${esc(ex ? ex.desc : "")}</div>`;
  if (p.listen) h += `<div style="font-size:56px">🎧</div>`;
  if (p.letter) h += `<div class="letter-big">${esc(p.letter)}</div>`;
  if (p.word) h += `<div class="cyr">${esc(p.word)}</div>${q.ex === "a-read" ? "" : tr(p.word_tr)}`;
  if (p.phrase) h += `<div class="cyr" style="font-size:30px">${esc(p.phrase)}</div>${tr(p.phrase_tr)}`;
  if (p.meaning) h += `<div class="nl big">${esc(p.meaning)}</div>`;
  h += `</div>`;
  if (p.listen) h += `<div class="row" style="justify-content:center;margin-top:6px"><button class="secondary" data-play>${t("again")}</button><button class="secondary" data-slow>${t("slow")}</button></div>`;
  return h;
}
function feedbackHTML(res, given) {
  const ok = res.result === "correct";
  const title = ok ? pick(t("praise")) : res.result === "almost" ? t("almost") : pick(t("oops"));
  const i = res.info || {};
  return `<div class="feedback ${res.result} pop">
    <div class="title">${ok ? "✅" : res.result === "almost" ? "🟡" : "❌"} ${esc(title)} ${res.xp_gained ? `<span class="small muted">+${res.xp_gained}</span>` : ""}</div>
    ${!ok && given && res.kind !== "choice" ? `<div class="small muted">${t("you")} <s>${esc(given)}</s></div>` : ""}
    ${i.big ? `<div class="sol" style="font-size:26px">${esc(i.big)} ${sayBtn(res.say)}</div>${tr(i.translit)}` : ""}
    <div style="margin-top:4px">${esc(i.line || res.answer)} ${i.say2 ? sayBtn(i.say2) : ""}</div>
    ${i.hint ? `<div class="small muted" style="margin-top:4px">🗣️ ${esc(i.hint)}</div>` : ""}</div>`;
}

async function viewPlay(ex, focus) {
  const s = { n: 0, ok: 0 };
  let q, answered = false, built = [];
  const bar = () => `<span class="chip">✅ ${s.ok} / ${s.n}</span>`;
  async function next() {
    answered = false; built = [];
    try { q = await api("question", { ex, focus }); } catch (e) { toast(e.message); history.back(); return; }
    const grp = HOME.groups.find(g => g.ex.some(e => e.key === ex));
    let body = promptHTML(q);
    if (q.kind === "choice") {
      const cls = q.opt_style === "letter" ? "letter" : "";
      body += `<div class="options ${cls}">${q.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="n">${i + 1}</span>${esc(o)}${q.opt_translit ? `<span class="tr">${esc(q.opt_translit[i])}</span>` : ""}</button>`).join("")}</div>`;
    } else if (q.kind === "type") {
      body += `<form class="answer-row" id="f"><input id="inp" lang="uk" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" placeholder="${t("type_here")}" ${OWN_KBD ? "" : 'inputmode="none"'}><button>OK</button></form>
        ${OWN_KBD ? "" : keyboardHTML()}<p class="center small"><button class="link" id="kbdswitch">${OWN_KBD ? t("screen_kbd") : t("own_kbd")}</button></p>`;
    } else {
      body += `<div class="build-line" id="line"></div>
        <div class="tiles" id="tiles">${q.tiles.map((w, i) => `<button class="tilebtn" data-t="${i}">${esc(w)}${q.tiles_tr ? `<span class="tr">${esc(q.tiles_tr[i])}</span>` : ""}</button>`).join("")}</div>
        <div class="row" style="justify-content:center;margin-top:14px"><button class="secondary" id="clear">${t("restart")}</button><button id="check">${t("check")}</button></div>`;
    }
    app.innerHTML = `<div class="qhead"><a href="#/groep/${grp ? grp.key : ""}">${t("stop")}</a>${latinSwitch()}${bar()}</div>
      <div class="card">${q.note ? `<p class="small muted">${esc(t(q.note))}</p>` : ""}${body}<div id="fb"></div></div>`;
    bindLatin();
    app.querySelector("[data-play]")?.addEventListener("click", () => say(q.prompt.say));
    app.querySelector("[data-slow]")?.addEventListener("click", () => say(q.prompt.say, true));
    if (q.prompt.listen) setTimeout(() => say(q.prompt.say), 250);

    if (q.kind === "choice") app.querySelectorAll(".opt").forEach(b => b.onclick = () => answer(q.options[+b.dataset.i], +b.dataset.i));
    if (q.kind === "type") {
      const inp = $("#inp"); inp.focus({ preventScroll: true });
      if (!OWN_KBD) bindKeyboard(inp);
      $("#kbdswitch").onclick = () => { OWN_KBD = !OWN_KBD; const v = inp.value; next_same(v); };
      $("#f").onsubmit = e => { e.preventDefault(); answered ? next() : answer(inp.value); };
    }
    if (q.kind === "build") {
      const draw = () => {
        $("#line").innerHTML = built.map((i, k) => `<button class="tilebtn" data-b="${k}">${esc(q.tiles[i])}</button>`).join("") +
          (built.length ? `<span class="end">${esc(q.prompt.end || "")}</span>` : `<span class="muted small">${t("tap_words")}</span>`);
        app.querySelectorAll("#tiles .tilebtn").forEach(b => b.classList.toggle("used", built.includes(+b.dataset.t)));
        app.querySelectorAll("[data-b]").forEach(b => b.onclick = () => { if (!answered) { built.splice(+b.dataset.b, 1); draw(); } });
      };
      app.querySelectorAll("#tiles .tilebtn").forEach(b => b.onclick = () => {
        const i = +b.dataset.t; if (answered || built.includes(i)) return;
        built.push(i); draw(); if (built.length === q.tiles.length) $("#check").focus();
      });
      $("#clear").onclick = () => { if (!answered) { built = []; draw(); } };
      $("#check").onclick = () => {
        if (answered) return next();
        if (built.length < q.tiles.length) return toast(t("use_all"));
        answer(built.map(i => q.tiles[i]).join(" "));
      };
      draw();
    }
  }
  // redraw the same question after switching keyboards (keeps what was typed)
  function next_same(v) {
    const form = $("#f");
    const holder = form.parentElement;
    form.nextElementSibling?.classList.contains("kbd") && form.nextElementSibling.remove();
    form.outerHTML = `<form class="answer-row" id="f"><input id="inp" lang="uk" autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" placeholder="${t("type_here")}" ${OWN_KBD ? "" : 'inputmode="none"'}><button>OK</button></form>${OWN_KBD ? "" : keyboardHTML()}`;
    const inp = $("#inp", holder); inp.value = v; inp.focus();
    if (!OWN_KBD) bindKeyboard(inp);
    $("#kbdswitch").textContent = OWN_KBD ? t("screen_kbd") : t("own_kbd");
    $("#f").onsubmit = e => { e.preventDefault(); answered ? next() : answer(inp.value); };
  }
  async function answer(given, idx) {
    if (answered) return; answered = true;
    const res = await api("answer", { qid: q.qid, answer: given });
    s.n++; if (res.result === "correct") s.ok++;
    $(".qhead .chip").outerHTML = bar();
    if (q.kind === "choice") app.querySelectorAll(".opt").forEach((b, j) => {
      b.disabled = true;
      if (res.accepted.includes(q.options[j])) b.classList.add("right"); else if (j === idx) b.classList.add("wrong");
    });
    if (q.kind === "type") { const inp = $("#inp"); inp.readOnly = true; inp.style.borderColor = res.result === "correct" ? "var(--good)" : res.result === "almost" ? "var(--warn)" : "var(--bad)"; }
    if (q.kind === "build") { $("#check").textContent = t("next"); $("#clear").disabled = true; }
    if (res.result === "wrong") $(".card").classList.add("shake");
    $("#fb").innerHTML = feedbackHTML(res, given) + (q.kind === "build" ? "" : `<button class="next" id="nx">${t("next")}</button>`);
    $("#nx")?.addEventListener("click", next);
    (q.kind === "build" ? $("#check") : $("#nx")).focus({ preventScroll: true });
    say(res.say);
  }
  const key = e => {
    if (!q) return;
    if (q.kind === "choice" && !answered && /^[1-5]$/.test(e.key)) answer(q.options[+e.key - 1], +e.key - 1);
    else if (answered && e.key === "Enter" && $("#nx") && document.activeElement !== $("#nx")) { e.preventDefault(); next(); }
  };
  document.addEventListener("keydown", key);
  cleanup = () => { document.removeEventListener("keydown", key); player.pause(); if ("speechSynthesis" in window) speechSynthesis.cancel(); };
  next();
}

// ---------- alphabet chart ----------
async function viewAlphabet() {
  const a = await api("alphabet");
  app.innerHTML = `<div class="spread"><h1>${t("abc_title")}</h1>${latinSwitch()}</div><p class="muted">${t("abc_intro")}</p>
    ${Object.entries(a.groups).map(([g, name]) => `<div class="spread" style="margin-top:22px"><h2 style="margin:0">${esc(name)}</h2>
      <a class="btn secondary" href="#/oefen/a-sound/${g}">${t("practise_group")}</a></div>
      <div class="abc-grid" style="margin-top:10px">${a.letters.filter(l => l.group === g).map(l => `<div class="abc">
        <div class="L">${l.up} ${l.low} ${sayBtn(l.name)}</div><div class="s">${esc(l.sound)}</div>
        <div class="h">${esc(l.hint)}</div>
        <div class="w">${l.emoji} <b>${esc(l.word)}</b> ${sayBtn(l.word)}</div>${tr(l.word_tr)}<div class="small muted">${esc(l.meaning)}</div></div>`).join("")}</div>`).join("")}`;
  bindLatin();
}

// ---------- scores ----------
const lvl = p => p >= 80 ? "g" : p >= 50 ? "w" : "b";
async function viewScores(uid) {
  const s = await api("stats" + (uid ? `?user=${encodeURIComponent(uid)}` : ""));
  const self = !uid || +uid === ME.id;
  const maxN = Math.max(1, ...s.days.map(d => d.n));
  const fmtDay = d => { const [, m, dd] = d.split("-"); return `${+dd}/${+m}`; };
  const groups = {};
  s.cats.forEach(c => (groups[c.grp] = groups[c.grp] || []).push(c));
  const L = t("legend");
  app.innerHTML = `${self ? "" : `<a href="/#/students">${t("all_students")}</a>`}
    <div class="spread"><h1>📊 ${self ? t("my_scores") : esc(t("scores_of", s.user.name))}</h1>
      <a class="btn secondary" href="/api/export.csv?module=oekraiens${uid ? `&user=${encodeURIComponent(uid)}` : ""}">${t("download")}</a></div>
    <div class="chips"><span class="chip">📝 ${s.total} ${t("answers")}</span><span class="chip">🎯 ${s.pct ?? "–"}% ${t("correct")}</span>
      <span class="chip">${t("streak", s.streak)}</span><span class="chip">${t("points", s.xp)}</span></div>
    <div class="card"><h3>${t("last14")}</h3>
      <div class="days">${s.days.map(d => `<div class="d" title="${fmtDay(d.day)}: ${d.n}${d.n ? `, ${d.pct}%` : ""}"><i style="height:${Math.round(100 * d.n / maxN)}%"></i></div>`).join("")}</div>
      <div class="days-x">${s.days.map((d, i) => `<span>${i % 2 === 1 ? fmtDay(d.day) : ""}</span>`).join("")}</div></div>
    <h2>${t("per_part")}</h2>
    <div class="card">${Object.keys(groups).length ? Object.entries(groups).map(([g, list]) => `<h3 style="margin-top:8px">${esc(g)}</h3>
      ${list.map(c => `<div class="cat-row"><span class="lab">${esc(c.cat)}</span><div class="bar ${lvl(c.pct)}"><i style="width:${c.pct}%"></i></div>
        <span class="pct">${lvl(c.pct) === "g" ? "✓" : lvl(c.pct) === "w" ? "~" : "✗"} ${c.pct}% · ${c.n}×</span></div>`).join("")}`).join("") +
      `<div class="legend"><span style="--c:#0ca30c">${L[0]}</span><span style="--c:#fab219">${L[1]}</span><span style="--c:#d03b3b">${L[2]}</span></div>`
      : `<p class="muted">${t("nothing_yet")}</p>`}</div>
    <h2>${t("to_practise")}</h2>
    <div class="card">${s.weak.length ? `<div class="tablewrap"><table class="list"><tr><th>${t("what_col")}</th><th>${t("ex_col")}</th><th>${t("wrong_col")}</th></tr>
      ${s.weak.map(w => `<tr><td><b>${esc(w.label)}</b> ${w.say ? sayBtn(w.say) : ""}</td><td class="small">${esc(w.ex)}</td><td>${w.wrong}× ${t("of")} ${w.seen}${w.box >= 3 ? ` <span class='small muted'>· ${t("better")}</span>` : ""}</td></tr>`).join("")}
      </table></div>` : `<p class="muted">${t("nothing")}</p>`}</div>
    <h2>${t("last_mistakes")}</h2>
    <div class="card">${s.mistakes.length ? `<div class="tablewrap"><table class="list"><tr><th>${t("question")}</th><th>${t("answer")}</th><th>${t("right_is")}</th></tr>
      ${s.mistakes.map(m => `<tr><td>${esc(m.prompt)}</td><td><s>${esc(m.given) || t("empty")}</s></td><td><b>${esc(m.expected)}</b></td></tr>`).join("")}
      </table></div>` : `<p class="muted">${t("no_mistakes")}</p>`}</div>`;
}

render();
