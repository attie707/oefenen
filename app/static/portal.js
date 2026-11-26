"use strict";
const $ = (s, el = document) => el.querySelector(s);
const app = $("#app");
const esc = Portal.esc;
let ME = null, ST = null, LANG = (navigator.language || "en").toLowerCase().startsWith("nl") ? "nl" : "en";

// ---------- translations ----------
const TXT = {
  en: {
    home: "Subjects", students: "Students", admin: "Admin", settings: "Settings",
    welcome: "Welcome!", setup_intro: "First create an administrator account. After that you can add the rest of the family.",
    name: "Name", username: "Username", password: "Password", create_account: "Create account",
    hello: "Hello!", login: "Log in",
    sso_unlinked: e => `You are signed in with Google as <b>${e}</b>, but no account here is linked to that address yet. Ask the administrator to add it (Admin → e-mail), or log in with your username and password.`,
    email: "Google e-mail", email_hint: "Optional. With this address the person can log in with Google (via Cloudflare Access).",
    set_email: "E-mail", email_prompt: n => `Google e-mail address for ${n} (leave empty to remove):`, email_saved: "E-mail saved",
    linked_google: "Linked Google account", via_google: "You are logged in with Google.", not_linked: "not linked",
    cookie_lost: "Your password was correct, but this browser did not keep the login. Allow cookies for this site, or try the https address.",
    new_pw: "New password", new_pw_intro: n => `Hi ${n}! Please choose a new, strong password before you continue.`,
    current_pw: "Current (temporary) password", current_pw2: "Current password", new_pw_label: "New password", new_pw_again: "New password again",
    save_continue: "Save and continue", logout: "Log out", pw_mismatch: "The two new passwords are not the same",
    pw_saved: "Password saved 👍",
    rules: [n => `At least ${n} characters`, () => "A lowercase letter", () => "A capital letter", () => "A digit",
            () => "A special character, like ! ? # @ -", () => "Not your username"],
    greet: n => `Hi ${n}!`, choose_subject: "What do you want to practise today?",
    streak: n => `🔥 ${n} ${n === 1 ? "day" : "days"} in a row`, today_goal: "Today", questions: "questions",
    never: "not started yet", st_today: n => `today ${n}`, st_week: (n, p) => `this week ${n}${p != null ? ` · ${p}% correct` : ""}`,
    st_xp: n => `⭐ ${n}`, open: "Open",
    students_title: "👩‍🏫 Students", logged_in_as: "You are logged in as", students_intro: "Click a subject to see the details.",
    no_students: "There are no students yet.", add_student: "Add a student", ask_admin: "Ask the administrator to add a student.",
    export_all: "⬇ Export all (CSV)", last_active: "Last active", ago: d => d === 0 ? "today" : d === 1 ? "yesterday" : `${d} days ago`,
    needs_pw: "🔒 still has to choose a new password", total: "total",
    admin_title: "⚙️ Admin", roles_explained: "<b>Student</b>: practises and sees only their own scores. <b>Teacher / parent</b>: sees the progress of all students. <b>Administrator</b>: can also manage accounts.",
    role: "Role", today: "Today", temp_pw: "Temporary password", delete: "Delete", add_account: "Add account",
    add: "Add", first_login_note: "At the first login the user has to choose their own password.",
    added: (n, u) => `✅ <b>${n}</b> has been added. Username: <b>${u}</b>`, temp_for: n => `🔑 Temporary password for <b>${n}</b>:`,
    confirm_reset: n => `Give ${n} a new temporary password? They will be logged out and must choose a new password.`,
    confirm_delete: n => `Permanently delete ${n} and all their scores?`, deleted: "Deleted", role_changed: "Role changed",
    r_student: "🎒 Student", r_teacher: "👩‍🏫 Teacher / parent", r_admin: "🔑 Administrator", own_role: "You can't change your own role",
    settings_title: "⚙️ Settings", language: "Language", language_note: "Menus, the start page, scores and admin follow this language. The French course stays Dutch-based (as at school) and the Dutch course is all in Dutch on purpose.",
    display_name: "Your name", save: "Save", saved: "Saved", change_pw: "Change password", pw_changed: "Password changed",
    account: "Account", logged_in: "Logged in as",
  },
  nl: {
    home: "Vakken", students: "Leerlingen", admin: "Beheer", settings: "Instellingen",
    welcome: "Welkom!", setup_intro: "Maak eerst een beheerdersaccount aan. Daarna kun je de rest van de familie toevoegen.",
    name: "Naam", username: "Gebruikersnaam", password: "Wachtwoord", create_account: "Account aanmaken",
    hello: "Hallo!", login: "Inloggen",
    sso_unlinked: e => `Je bent met Google ingelogd als <b>${e}</b>, maar dat adres hoort nog bij geen enkel account. Vraag de beheerder om het toe te voegen (Beheer → e-mail), of log in met je gebruikersnaam en wachtwoord.`,
    email: "Google-e-mailadres", email_hint: "Optioneel. Met dit adres kan iemand inloggen met Google (via Cloudflare Access).",
    set_email: "E-mail", email_prompt: n => `Google-e-mailadres voor ${n} (leeg laten om te verwijderen):`, email_saved: "E-mail opgeslagen",
    linked_google: "Gekoppeld Google-account", via_google: "Je bent ingelogd met Google.", not_linked: "niet gekoppeld",
    cookie_lost: "Je wachtwoord klopte, maar deze browser heeft de login niet bewaard. Sta cookies toe voor deze site, of probeer het https-adres.",
    new_pw: "Nieuw wachtwoord", new_pw_intro: n => `Hallo ${n}! Kies eerst een nieuw, sterk wachtwoord voordat je verder gaat.`,
    current_pw: "Huidig (tijdelijk) wachtwoord", current_pw2: "Huidig wachtwoord", new_pw_label: "Nieuw wachtwoord", new_pw_again: "Nieuw wachtwoord nog een keer",
    save_continue: "Opslaan en verder", logout: "Uitloggen", pw_mismatch: "De twee nieuwe wachtwoorden zijn niet hetzelfde",
    pw_saved: "Wachtwoord opgeslagen 👍",
    rules: [n => `Minstens ${n} tekens`, () => "Een kleine letter", () => "Een hoofdletter", () => "Een cijfer",
            () => "Een speciaal teken, zoals ! ? # @ -", () => "Niet je gebruikersnaam"],
    greet: n => `Hallo ${n}!`, choose_subject: "Wat wil je vandaag oefenen?",
    streak: n => `🔥 ${n} ${n === 1 ? "dag" : "dagen"} op rij`, today_goal: "Vandaag", questions: "vragen",
    never: "nog niet begonnen", st_today: n => `vandaag ${n}`, st_week: (n, p) => `deze week ${n}${p != null ? ` · ${p}% goed` : ""}`,
    st_xp: n => `⭐ ${n}`, open: "Open",
    students_title: "👩‍🏫 Leerlingen", logged_in_as: "Je bent ingelogd als", students_intro: "Klik op een vak voor de details.",
    no_students: "Er zijn nog geen leerlingen.", add_student: "Leerling toevoegen", ask_admin: "Vraag de beheerder om een leerling toe te voegen.",
    export_all: "⬇ Exporteer alles (CSV)", last_active: "Laatst actief", ago: d => d === 0 ? "vandaag" : d === 1 ? "gisteren" : `${d} dagen geleden`,
    needs_pw: "🔒 moet nog een nieuw wachtwoord kiezen", total: "totaal",
    admin_title: "⚙️ Beheer", roles_explained: "<b>Leerling</b>: oefent en ziet alleen eigen scores. <b>Docent / ouder</b>: ziet de voortgang van alle leerlingen. <b>Beheerder</b>: kan ook accounts beheren.",
    role: "Rol", today: "Vandaag", temp_pw: "Tijdelijk wachtwoord", delete: "Verwijder", add_account: "Account toevoegen",
    add: "Toevoegen", first_login_note: "Bij de eerste keer inloggen moet de gebruiker zelf een nieuw wachtwoord kiezen.",
    added: (n, u) => `✅ <b>${n}</b> is toegevoegd. Gebruikersnaam: <b>${u}</b>`, temp_for: n => `🔑 Tijdelijk wachtwoord voor <b>${n}</b>:`,
    confirm_reset: n => `${n} een nieuw tijdelijk wachtwoord geven? Diegene wordt uitgelogd en moet daarna zelf een nieuw wachtwoord kiezen.`,
    confirm_delete: n => `${n} en alle scores definitief verwijderen?`, deleted: "Verwijderd", role_changed: "Rol aangepast",
    r_student: "🎒 Leerling", r_teacher: "👩‍🏫 Docent / ouder", r_admin: "🔑 Beheerder", own_role: "Je eigen rol kun je niet veranderen",
    settings_title: "⚙️ Instellingen", language: "Taal", language_note: "Menu's, de startpagina, scores en beheer volgen deze taal. De cursus Frans blijft op het Nederlands gebaseerd (zoals op school) en de cursus Nederlands is expres helemaal in het Nederlands.",
    display_name: "Je naam", save: "Opslaan", saved: "Opgeslagen", change_pw: "Wachtwoord wijzigen", pw_changed: "Wachtwoord gewijzigd",
    account: "Account", logged_in: "Ingelogd als",
  },
};
const t = (k, ...a) => { const v = (TXT[LANG] || TXT.en)[k] ?? TXT.en[k]; return typeof v === "function" ? v(...a) : v; };

// ---------- helpers ----------
async function api(path, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  const r = await fetch("/api/" + path, opt);
  const data = await r.json().catch(() => ({}));
  if (r.status === 401 && path !== "login") { ME = null; location.hash = "#/"; render(); throw new Error(data.error); }
  if (r.status === 403 && data.error === "must_change") { render(); throw new Error(data.error); }
  if (!r.ok) throw new Error(data.error || "Something went wrong");
  return data;
}
function toast(msg, ms = 2600) {
  const el = $("#toast"); el.textContent = msg; el.hidden = false;
  clearTimeout(toast._t); toast._t = setTimeout(() => (el.hidden = true), ms);
}
const modTitle = m => m.title[LANG] || m.title.en;
const modDesc = m => m.desc[LANG] || m.desc.en;
const agoTs = ts => ts ? t("ago", Math.floor((Date.now() / 1000 - ts) / 86400)) : t("never");

// ---------- passwords ----------
let PW_MIN = 10;
const PW_TESTS = [pw => pw.length >= PW_MIN, pw => /[a-z]/.test(pw), pw => /[A-Z]/.test(pw), pw => /[0-9]/.test(pw), pw => /[^A-Za-z0-9]/.test(pw)];
function pwChecklist(input, username = () => "") {
  const ul = document.createElement("ul"); ul.className = "pwcheck";
  const draw = () => {
    const pw = input.value, u = (typeof username === "function" ? username() : username).toLowerCase();
    const rules = t("rules");
    ul.innerHTML = PW_TESTS.map((f, i) => `<li class="${f(pw) ? "ok" : ""}">${esc(rules[i](PW_MIN))}</li>`).join("") +
      `<li class="${pw && !(u && pw.toLowerCase().includes(u)) ? "ok" : ""}">${esc(rules[5]())}</li>`;
  };
  input.addEventListener("input", draw);
  (input.parentElement.classList.contains("row") ? input.parentElement : input).after(ul); draw();
}
function makePassword() {
  const w = ["Sun", "Cat", "Apple", "Cheese", "Moon", "Bike", "Beach", "Book", "Tree", "Train", "Cloud", "Star", "Boat", "Tulip", "Mango"];
  const r = n => crypto.getRandomValues(new Uint32Array(1))[0] % n;
  const a = r(w.length), b = (a + 1 + r(w.length - 1)) % w.length;
  return w[a] + "-" + w[b] + (10 + r(90)) + "!?#@"[r(4)];
}

async function logout() {
  const r = await api("logout", {});
  if (r.sso_logout) { location.href = r.sso_logout; return; }
  location.hash = "#/"; render();
}

// ---------- router ----------
window.addEventListener("hashchange", render);
async function render() {
  ST = await api("state").catch(() => ({}));
  ME = ST.user;
  if (ME) LANG = ME.lang;
  PW_MIN = ST.pw_min || 10;
  document.documentElement.lang = LANG;
  const staff = !!ME && (ME.role === "teacher" || ME.role === "admin");
  $("#nav").hidden = !ME || ME.must_change;
  $("#nav-home").textContent = t("home");
  $("#nav-staff").textContent = t("students"); $("#nav-staff").hidden = !staff;
  $("#nav-admin").textContent = t("admin"); $("#nav-admin").hidden = !(ME && ME.role === "admin");
  if (ME) $("#who").innerHTML = `<span class="nm">${esc(ME.name)}</span> <span class="role ${ME.role}">${esc(ME.role_name)}</span>`;
  if (ST.setup_needed) return viewSetup();
  if (!ME) return viewLogin();
  if (ME.must_change) return viewForceChange();
  const route = location.hash.replace(/^#\/?/, "").split("/")[0];
  const views = { "": viewLanding, students: viewStudents, admin: viewAdmin, settings: viewSettings };
  (views[route] || viewLanding)();
}

function langSwitch() {
  return `<div class="seg" style="margin-bottom:12px">${["en", "nl"].map(l => `<button type="button" data-lang="${l}" class="${LANG === l ? "on" : ""}">${l === "en" ? "English" : "Nederlands"}</button>`).join("")}</div>`;
}
function bindLangSwitch(redraw) {
  app.querySelectorAll("[data-lang]").forEach(b => b.onclick = () => { LANG = b.dataset.lang; redraw(); });
}

// ---------- login ----------
function viewSetup() {
  app.innerHTML = `<div class="card" style="max-width:440px;margin:30px auto">${langSwitch()}
    <h1>${t("welcome")} 👋</h1><p class="muted">${t("setup_intro")}</p>
    <form id="f"><label>${t("name")}</label><input name="name" required>
    <label>${t("username")}</label><input name="username" autocapitalize="none" required>
    <label>${t("password")}</label><input name="password" id="pw1" type="password" autocomplete="new-password" required>
    <div class="error" id="err"></div><br><button>${t("create_account")}</button></form></div>`;
  bindLangSwitch(viewSetup);
  pwChecklist($("#pw1"), () => $("[name=username]").value);
  $("#f").onsubmit = async e => {
    e.preventDefault();
    try { await api("setup", { ...Object.fromEntries(new FormData(e.target)), lang: LANG }); location.hash = "#/admin"; render(); }
    catch (er) { $("#err").textContent = er.message; }
  };
}
function viewLogin() {
  app.innerHTML = `<div class="card" style="max-width:420px;margin:30px auto">${langSwitch()}
    <h1>${t("hello")} 🎓</h1>
    ${ST.sso && ST.sso.unlinked_email ? `<div class="banner">${t("sso_unlinked", esc(ST.sso.unlinked_email))}</div>` : ""}
    <form id="f"><label>${t("username")}</label><input name="username" autocapitalize="none" autocomplete="username" required>
    <label>${t("password")}</label><input name="password" type="password" autocomplete="current-password" required>
    <div class="error" id="err"></div><br><button style="width:100%">${t("login")}</button></form></div>`;
  bindLangSwitch(viewLogin);
  $("#f").onsubmit = async e => {
    e.preventDefault();
    try {
      await api("login", Object.fromEntries(new FormData(e.target)));
      const st = await api("state");
      if (!st.user) { $("#err").textContent = t("cookie_lost"); return; }
      render();
    } catch (er) { $("#err").textContent = er.message; }
  };
}
function viewForceChange() {
  app.innerHTML = `<div class="card" style="max-width:440px;margin:30px auto">
    <h1>🔒 ${t("new_pw")}</h1>
    <div class="banner">${esc(t("new_pw_intro", ME.name))}</div>
    <form id="f"><label>${t("current_pw")}</label><input name="old" type="password" autocomplete="current-password" required>
    <label>${t("new_pw_label")}</label><input id="pw1" type="password" autocomplete="new-password" required>
    <label>${t("new_pw_again")}</label><input id="pw2" type="password" autocomplete="new-password" required>
    <div class="error" id="err"></div><br><button style="width:100%">${t("save_continue")}</button></form>
    <p class="center"><button class="link" id="out">${t("logout")}</button></p></div>`;
  pwChecklist($("#pw1"), ME.username);
  $("#f").onsubmit = async e => {
    e.preventDefault();
    if ($("#pw1").value !== $("#pw2").value) return ($("#err").textContent = t("pw_mismatch"));
    try { await api("password", { old: e.target.old.value, new: $("#pw1").value }); toast(t("pw_saved")); location.hash = "#/"; render(); }
    catch (er) { $("#err").textContent = er.message; }
  };
  $("#out").onclick = logout;
}

// ---------- landing page ----------
function modStats(s) {
  if (!s.total) return `<div class="mod-stats"><span class="chip">${t("never")}</span></div>`;
  return `<div class="mod-stats"><span class="chip">${t("st_today", s.today)}</span>
    <span class="chip">${t("st_week", s.week, s.week_pct)}</span><span class="chip">${t("st_xp", s.xp)}</span>
    ${s.streak ? `<span class="chip">🔥 ${s.streak}</span>` : ""}</div>`;
}
async function viewLanding() {
  const p = await api("portal");
  const goal = Math.min(100, Math.round(100 * p.today / p.goal));
  app.innerHTML = `<h1>${esc(t("greet", ME.name))}</h1>
    <div class="chips"><span class="chip">${t("streak", p.streak)}</span><span class="chip">${t("today_goal")}: ${p.today} ${t("questions")}</span></div>
    <div class="bar ${goal >= 100 ? "good" : ""}" style="margin:-4px 0 18px"><i style="width:${goal}%"></i></div>
    <h2 style="margin-top:4px">${t("choose_subject")}</h2>
    <div class="grid">${ST.modules.map(m => `<a class="card tile mod-tile" href="/${m.key}/">
      <div class="ico">${m.icon}</div><h3>${esc(modTitle(m))}</h3><div class="muted small">${esc(modDesc(m))}</div>
      ${modStats(p.modules[m.key])}</a>`).join("")}</div>`;
}

// ---------- students overview (teacher / parent / admin) ----------
async function viewStudents() {
  if (!(ME.role === "teacher" || ME.role === "admin")) { location.hash = "#/"; return; }
  const users = (await api("users")).filter(u => u.role === "student");
  app.innerHTML = `<div class="spread"><h1>${t("students_title")}</h1>
      ${users.length ? `<a class="btn secondary" href="/api/export.csv?user=all">${t("export_all")}</a>` : ""}</div>
    <p class="muted">${t("logged_in_as")} <span class="role ${ME.role}">${esc(ME.role_name)}</span>. ${t("students_intro")}</p>
    ${users.length ? users.map(u => `<div class="card" style="margin-bottom:12px">
      <div class="spread"><h3>🎒 ${esc(u.name)} <span class="small muted">${esc(u.username)}</span></h3>
        <span class="small muted">${t("last_active")}: ${agoTs(u.last_ts)}</span></div>
      ${u.must_change ? `<div class="small muted">${t("needs_pw")}</div>` : ""}
      <div class="grid" style="margin-top:10px">${ST.modules.map(m => {
        const s = u.modules[m.key];
        return `<a class="card tile" href="/${m.key}/#/scores/${u.id}" style="padding:12px">
          <b>${m.icon} ${esc(modTitle(m))}</b>${modStats(s)}
          ${s.total ? `<div class="small muted" style="margin-top:6px">${s.total} ${t("total")} · ${t("last_active")}: ${agoTs(s.last_ts)}</div>` : ""}</a>`;
      }).join("")}</div></div>`).join("")
      : `<div class="card"><p>${t("no_students")}</p>${ME.role === "admin" ? `<a class="btn" href="#/admin">${t("add_student")}</a>` : `<p class="muted">${t("ask_admin")}</p>`}</div>`}`;
}

// ---------- admin ----------
async function viewAdmin(msg) {
  if (ME.role !== "admin") { location.hash = "#/"; return; }
  const users = await api("users");
  const roleSel = u => `<select data-role="${u.id}" ${u.id === ME.id ? `disabled title="${esc(t("own_role"))}"` : ""}>
      ${[["student", t("r_student")], ["teacher", t("r_teacher")], ["admin", t("r_admin")]].map(([k, l]) => `<option value="${k}" ${u.role === k ? "selected" : ""}>${l}</option>`).join("")}</select>`;
  app.innerHTML = `<div class="spread"><h1>${t("admin_title")}</h1><a class="btn secondary" href="/api/export.csv?user=all">${t("export_all")}</a></div>
    ${typeof msg === "string" ? `<div class="banner">${msg}</div>` : ""}
    <p class="small muted">${t("roles_explained")}</p>
    <div class="card"><div class="tablewrap"><table class="list"><tr><th>${t("name")}</th><th>${t("role")}</th><th>${t("today")}</th><th>${t("total")}</th><th>${t("last_active")}</th><th></th></tr>
    ${users.map(u => `<tr><td><b>${esc(u.name)}</b><div class="small muted">${esc(u.username)}${u.must_change ? " · 🔒" : ""}</div>
      <div class="small">${u.email ? `✉️ ${esc(u.email)}` : ""} <button class="link small" data-email="${u.id}" data-name="${esc(u.name)}" data-cur="${esc(u.email || "")}">${t("set_email")}</button></div></td><td>${roleSel(u)}</td>
      <td>${u.today}</td><td>${u.total}</td><td class="small">${agoTs(u.last_ts)}</td>
      <td><div class="row"><button class="link" data-pw="${u.id}" data-name="${esc(u.name)}">${t("temp_pw")}</button>
      ${u.id !== ME.id ? `<button class="link" style="color:var(--bad)" data-del="${u.id}" data-name="${esc(u.name)}">${t("delete")}</button>` : ""}</div></td></tr>`).join("")}
    </table></div></div>
    <h2>${t("add_account")}</h2>
    <form class="card" id="f"><div class="grid">
      <div><label>${t("name")}</label><input name="name" required></div>
      <div><label>${t("username")}</label><input name="username" autocapitalize="none" required></div>
      <div><label>${t("role")}</label><select name="role"><option value="student">${t("r_student")}</option><option value="teacher">${t("r_teacher")}</option><option value="admin">${t("r_admin")}</option></select></div>
      <div><label>${t("email")}</label><input name="email" type="email" autocapitalize="none" placeholder="name@gmail.com"></div>
      <div><label>${t("language")}</label><select name="lang"><option value="en">English</option><option value="nl">Nederlands</option></select></div>
      <div><label>${t("temp_pw")}</label><div class="row" style="flex-wrap:nowrap"><input name="password" id="newpw" required><button type="button" class="secondary" id="gen" title="🎲">🎲</button></div></div>
    </div><p class="small muted">${t("first_login_note")} ${t("email_hint")}</p>
    <div class="error" id="err"></div><button>${t("add")}</button></form>`;
  const np = $("#newpw"); np.value = makePassword();
  pwChecklist(np, () => $("#f [name=username]").value);
  $("#gen").onclick = () => { np.value = makePassword(); np.dispatchEvent(new Event("input")); };
  $("#f").onsubmit = async e => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(e.target));
    try { await api("users/create", d); viewAdmin(`${t("added", esc(d.name), esc(d.username.trim().toLowerCase()))}<br>${t("temp_pw")}: <span class="temp-pw">${esc(d.password)}</span>`); }
    catch (er) { $("#err").textContent = er.message; }
  };
  app.querySelectorAll("[data-role]").forEach(sel => sel.onchange = async () => {
    try { await api("users/role", { id: +sel.dataset.role, role: sel.value }); toast(t("role_changed")); viewAdmin(); }
    catch (er) { toast(er.message); viewAdmin(); }
  });
  app.querySelectorAll("[data-pw]").forEach(b => b.onclick = async () => {
    const pw = makePassword();
    if (!confirm(t("confirm_reset", b.dataset.name))) return;
    try { await api("users/password", { id: +b.dataset.pw, password: pw }); viewAdmin(`${t("temp_for", esc(b.dataset.name))} <span class="temp-pw">${esc(pw)}</span>`); }
    catch (er) { toast(er.message); }
  });
  app.querySelectorAll("[data-email]").forEach(b => b.onclick = async () => {
    const v = prompt(t("email_prompt", b.dataset.name), b.dataset.cur);
    if (v === null) return;
    try { await api("users/email", { id: +b.dataset.email, email: v }); toast(t("email_saved")); viewAdmin(); } catch (er) { toast(er.message); }
  });
  app.querySelectorAll("[data-del]").forEach(b => b.onclick = async () => {
    if (!confirm(t("confirm_delete", b.dataset.name))) return;
    try { await api("users/delete", { id: +b.dataset.del }); toast(t("deleted")); viewAdmin(); } catch (er) { toast(er.message); }
  });
}

// ---------- settings ----------
function viewSettings() {
  app.innerHTML = `<h1>${t("settings_title")}</h1>
    <div class="card" style="max-width:520px;margin-bottom:14px">
      <h3>${t("language")}</h3>${langSwitch()}<p class="small muted">${t("language_note")}</p>
      <label>${t("display_name")}</label><div class="row" style="flex-wrap:nowrap"><input id="nm" value="${esc(ME.name)}"><button id="savename">${t("save")}</button></div>
    </div>
    <div class="card" style="max-width:520px">
      <p class="small">${t("linked_google")}: <b>${esc(ME.email || t("not_linked"))}</b>${ME.sso ? ` · ${t("via_google")}` : ""}</p>
      <h3>${t("change_pw")}</h3>
      <p class="small muted">${t("logged_in")} <b>${esc(ME.username)}</b> <span class="role ${ME.role}">${esc(ME.role_name)}</span></p>
      <form id="f"><label>${t("current_pw2")}</label><input name="old" type="password" autocomplete="current-password" required>
      <label>${t("new_pw_label")}</label><input id="pw1" type="password" autocomplete="new-password" required>
      <label>${t("new_pw_again")}</label><input id="pw2" type="password" autocomplete="new-password" required>
      <div class="error" id="err"></div><br><button>${t("change_pw")}</button></form>
      <hr style="border:0;border-top:1px solid var(--line);margin:20px 0"><button class="secondary" id="out">${t("logout")}</button>
    </div>`;
  app.querySelectorAll("[data-lang]").forEach(b => b.onclick = async () => {
    await api("settings", { lang: b.dataset.lang }); toast("✓"); render();
  });
  $("#savename").onclick = async () => { await api("settings", { name: $("#nm").value }); toast(t("saved")); render(); };
  pwChecklist($("#pw1"), ME.username);
  $("#f").onsubmit = async e => {
    e.preventDefault();
    if ($("#pw1").value !== $("#pw2").value) return ($("#err").textContent = t("pw_mismatch"));
    try { await api("password", { old: e.target.old.value, new: $("#pw1").value }); toast(t("pw_changed")); e.target.reset(); $("#pw1").dispatchEvent(new Event("input")); }
    catch (er) { $("#err").textContent = er.message; }
  };
  $("#out").onclick = logout;
}

render();
