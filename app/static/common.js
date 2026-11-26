"use strict";
// Shared by every subject page: checks the login (handled by the portal) and fills in the header.
const Portal = {
  async boot(moduleKey) {
    const st = await fetch("/api/state").then(r => r.json()).catch(() => ({}));
    if (!st.user || st.user.must_change) { location.href = "/"; return null; }
    const me = st.user, staff = me.role === "teacher" || me.role === "admin";
    const who = document.getElementById("who");
    if (who) who.innerHTML = `<span class="nm">${Portal.esc(me.name)}</span> <span class="role ${me.role}">${Portal.esc(me.role_name)}</span>`;
    const sl = document.getElementById("nav-staff");
    if (sl) sl.hidden = !staff;
    document.documentElement.lang = me.lang;
    const mod = (st.modules || []).find(m => m.key === moduleKey) || {};
    return { st, me, staff, tts: !!mod.tts };
  },
  esc: s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])),
};
