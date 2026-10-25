// VerifAI web UI: hash routing, SSE chat, knowledge base, activity log. No framework.
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const pct = (x) => `${((x || 0) * 100).toFixed(1)}%`;
const num = (x) => Number(x || 0).toLocaleString("en-IN");
const icon = (id) => `<svg><use href="#i-${id}"/></svg>`;
const day = (iso) => (iso ? new Date(`${iso}T00:00`).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "—");
const TYPES = { factsheet: "Factsheet", sid_kim: "Scheme document", circular: "SEBI circular", research: "Investor education", internal: "Firm policy" };
const OUTCOME = {
  no_evidence: '<span class="pill warn">Not enough evidence</span>',
  advice: '<span class="pill bad">Advice boundary</span>',
  null: '<span class="pill ok">Answered</span>',
};
const BUDGET = 3000;
let turns = []; // {question, answer, citations, refusal}, oldest first
let active = null; // the turn whose citations the open chips belong to

// ---- routing ----
const PAGES = { ask: "Ask the documents", knowledge: "Knowledge base", activity: "Activity log" };
function route() {
  const name = location.hash.slice(1) in PAGES ? location.hash.slice(1) : "ask";
  document.querySelectorAll(".page").forEach((p) => (p.hidden = p.id !== `page-${name}`));
  document.querySelectorAll("[data-route]").forEach((a) =>
    a.dataset.route === name ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  $("#crumb").textContent = PAGES[name];
  if (name === "knowledge") loadKnowledge();
  if (name === "activity") loadActivity();
}
addEventListener("hashchange", route);

const getJSON = (url) => fetch(url).then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.status))));

// The free Render instance can still be building its index on the first request, so keep asking.
async function health(tries = 20) {
  try {
    const h = await getJSON("/health");
    $("#corpus-count").textContent = `Index ready · ${num(h.chunks_indexed)} passages`;
    $("#corpus-dot").className = "dot ok";
  } catch {
    if (tries > 1) return setTimeout(() => health(tries - 1), 3000);
    $("#corpus-count").textContent = "Index unavailable · refresh to retry";
    $("#corpus-dot").className = "dot bad";
  }
}

// ---- tiny markdown: paragraphs, **bold**, bullets, [n] citation chips ----
function md(text) {
  const inline = (s) => esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, (_, ns) =>
      ns.split(",").map((n) => `<button type="button" class="cite" data-n="${n.trim()}" aria-label="Source ${n.trim()}">${n.trim()}</button>`).join(""));
  return text.trim().split(/\n\s*\n/).map((block) => {
    const lines = block.split("\n");
    if (lines.every((l) => /^\s*[-*] /.test(l)))
      return `<ul>${lines.map((l) => `<li>${inline(l.replace(/^\s*[-*] /, ""))}</li>`).join("")}</ul>`;
    return `<p>${lines.map(inline).join("<br>")}</p>`;
  }).join("");
}

// ---- ask ----
const form = $("#ask-form");
const card = $("#answer");

$("#examples").addEventListener("click", (e) => {
  if (!e.target.matches(".example")) return;
  $("#question").value = e.target.textContent;
  form.requestSubmit();
});
$("#clear").addEventListener("click", () => {
  form.reset();
  $("#question").focus();
});
$("#question").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) form.requestSubmit();
});
$("#new-session").addEventListener("click", () => {
  turns = [];
  active = null;
  $("#history").innerHTML = "";
  card.hidden = true;
  $("#session").hidden = true;
  setMeter(0);
  closeEvidence();
  loadRecent();
});
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = $("#question").value.trim();
  if (q.length >= 3) ask(q);
});

function setMeter(tokens) {
  $("#meter-text").textContent = `${num(tokens)} / ${num(BUDGET)} tokens`;
  $("#meter-fill").style.width = `${Math.min(100, (tokens / BUDGET) * 100)}%`;
  $("#meter-fill").classList.toggle("over", tokens > BUDGET);
}

function archive() {
  // move the last finished answer into the history column before a new one streams in
  const t = turns.at(-1);
  if (!t || card.hidden || card.dataset.turn !== String(turns.length - 1)) return; // errors are not turns
  delete card.dataset.turn;
  const div = document.createElement("div");
  div.className = "panel past";
  div.dataset.turn = turns.length - 1;
  div.innerHTML = `<p class="answer-q">${esc(t.question)}</p><div class="prose">${md(t.answer || "")}</div>`;
  $("#history").append(div);
}

async function ask(question) {
  archive();
  closeEvidence();
  $("#recent").hidden = true;
  const btn = $("#submit");
  btn.disabled = true;
  card.hidden = false;
  card.innerHTML = `<p class="answer-q">${esc(question)}</p>
    <div class="wait">Searching the approved documents · <b id="waited">0 s</b> · the free-tier model can take up to a minute to start.</div>`;
  const t0 = Date.now();
  const tick = setInterval(() => ($("#waited") ? ($("#waited").textContent = `${Math.round((Date.now() - t0) / 1000)} s`) : clearInterval(tick)), 1000);
  card.scrollIntoView({ behavior: "smooth", block: "start" });
  const body = {
    question,
    history: turns.slice(-4).map((t) => [t.question, t.answer]),
    issuer: $("#issuer").value || null,
    doc_type: $("#doc_type").value || null,
  };
  let text = "";
  try {
    const res = await fetch("/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(typeof err.detail === "string" ? err.detail : `The server answered ${res.status}.`);
    }
    const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
    let buf = "";
    let done = null;
    for (;;) {
      const { value, done: end } = await reader.read();
      if (end) break;
      buf += value;
      let i;
      while ((i = buf.indexOf("\n\n")) >= 0) {
        const raw = buf.slice(0, i);
        buf = buf.slice(i + 2);
        const event = raw.match(/^event: (.*)$/m)?.[1];
        const data = JSON.parse(raw.match(/^data: (.*)$/m)?.[1] ?? "null");
        if (event === "token") {
          text += data;
          card.innerHTML = `<p class="answer-q">${esc(question)}</p><div class="prose">${md(text)}</div>`;
        } else if (event === "error") throw new Error(data.message);
        else if (event === "done") done = data;
      }
    }
    if (!done) throw new Error("The answer stream ended early.");
    const turn = { question, answer: done.answer, citations: done.citations || [], refusal: done.refusal };
    turns.push(turn);
    renderAnswer(turn, done);
    renderSession();
    form.reset();
  } catch (err) {
    card.innerHTML = `<p class="answer-q">${esc(question)}</p>
      <div class="notice bad"><span class="notice-title">${icon("alert")}The answer couldn't be completed</span>
      <p>${esc(err.message)} Nothing was saved; you can try again.</p>
      <button type="button" class="btn" id="retry">${icon("reset")}Retry</button></div>`;
    $("#retry").onclick = () => ask(question);
  } finally {
    clearInterval(tick);
    btn.disabled = false;
  }
}

function gate(tr) {
  const top = tr.top_score ?? 0;
  const th = tr.threshold ?? 0;
  const ok = top >= th;
  return `<span class="gate ${ok ? "" : "fail"}" title="Best match against the evidence threshold">
    <span class="gate-track"><span class="gate-fill" style="width:${Math.min(100, top * 100)}%"></span><span class="gate-tick" style="left:calc(${th * 100}% - 1px)"></span></span>
    Best match <b>${top.toFixed(3)}</b> ${ok ? "≥" : "<"} ${th.toFixed(2)}</span>`;
}

function renderAnswer(turn, d) {
  const tr = d.trace || {};
  active = turn;
  card.dataset.turn = turns.length - 1;
  setMeter(tr.context_tokens || 0);
  const n = new Set(turn.citations.map((c) => c.source_name)).size;
  const facts = [
    tr.model ? `<span class="fact">Model <b>${esc(tr.model)}</b></span>` : "",
    d.refusal === "no_evidence" ? "" : `<span class="fact">Cited <b>${n} document${n === 1 ? "" : "s"}</b></span>`,
  ].join("");
  let status, bodyHTML;
  if (d.refusal === "no_evidence") {
    status = `<span class="pill warn">${icon("alert")}Not enough evidence</span>`;
    bodyHTML = `<div class="notice warn"><span class="notice-title">${icon("alert")}No approved passage is close enough</span>
      <p>The best match scored ${(tr.top_score ?? 0).toFixed(3)}, below the ${(tr.threshold ?? 0).toFixed(2)} evidence threshold, so VerifAI won't answer from memory.</p></div>
      <div class="prose">${md(d.answer)}</div>`;
  } else if (d.refusal === "advice") {
    const [boundary, ...rest] = d.answer.trim().split(/\n\s*\n/);
    status = `<span class="pill bad">${icon("alert")}Advice boundary</span>`;
    bodyHTML = `<div class="notice bad"><span class="notice-title">${icon("alert")}Facts, not a recommendation</span><p>${md(boundary).replace(/^<p>|<\/p>$/g, "")}</p></div>
      ${rest.length ? `<p class="facts-label">What the approved documents say</p><div class="prose">${md(rest.join("\n\n"))}</div>`
        : `<p class="muted">No approved passage cleared the evidence threshold, so there are no facts to add.</p>`}`;
  } else {
    status = `<span class="pill ok">${icon("shield")}Grounded in approved documents</span>`;
    bodyHTML = `<div class="prose">${md(d.answer)}</div>`;
  }
  const cites = turn.citations.map((c) => `
    <button type="button" class="cite-card" data-n="${c.n}">
      <span class="row"><span class="tag">[${c.n}]</span><span class="match">${pct(c.score)} match</span></span>
      <span class="cite-title">${esc(c.title)}</span>
      <span class="cite-meta">Page ${esc(c.page)} · ${day(c.published_date)} · v${esc(c.version)}</span>
      <span class="cite-ex">“${esc(c.text.slice(0, 220))}…”</span>
      <span class="cite-foot">Read the passage ${icon("arrow")}</span>
    </button>`).join("");
  const rewritten = d.standalone_question && d.standalone_question !== turn.question;
  const pass = (tr.top_score ?? 0) >= (tr.threshold ?? 0);
  const stage = (name, value, note) => `<div class="stage"><span class="stage-name">${name}</span><span class="stage-value">${value}</span><p>${note}</p></div>`;
  card.innerHTML = `<div class="answer-top">${status}${gate(tr)}${facts}</div>
    <p class="answer-q">${esc(turn.question)}</p>
    ${bodyHTML}
    ${cites ? `<div class="section-head"><h3>Sources behind this answer</h3><span class="fact">${turn.citations.length} passage${turn.citations.length === 1 ? "" : "s"}</span></div><div class="cite-grid">${cites}</div>` : ""}
    <details class="why" open><summary>${icon("chevron")}Why this answer</summary><div class="stages">
      ${stage("Query", rewritten ? "Rewritten" : "As asked", rewritten ? `From the conversation: <i>${esc(d.standalone_question)}</i>` : "No earlier turns to resolve.")}
      ${stage("Vector search", `${num(tr.candidates)} passages`, "From the latest approved versions only.")}
      ${stage("Re-rank and gate", `${num(tr.reranked)} kept`, `<span class="${pass ? "" : "fail"}">Best ${(tr.top_score ?? 0).toFixed(3)} ${pass ? "cleared" : "missed"} the ${(tr.threshold ?? 0).toFixed(2)} gate.</span>`)}
      ${stage("Context", `${num(tr.context_tokens)} tokens`, `${num(tr.context_chunks)} passages plus ${num(tr.neighbours)} same-page neighbours.`)}
    </div></details>
    <p class="answer-foot">First token after ${(d.first_token_s ?? 0).toFixed(1)} s</p>`;
}

function renderSession() {
  $("#session").hidden = false;
  const cls = { no_evidence: "warn", advice: "bad" };
  $("#session-list").innerHTML = turns.map((t) =>
    `<li><span class="dot ${cls[t.refusal] || "ok"}"></span>${esc(t.question)}</li>`).join("");
}

// ---- recently asked (real rows from the activity log) ----
async function loadRecent() {
  try {
    const rows = await getJSON("/activity");
    const seen = new Set();
    const top = rows.filter((r) => !seen.has(r.question) && seen.add(r.question)).slice(0, 5);
    if (!top.length || turns.length) return;
    $("#recent-list").innerHTML = top.map((r) => `<li>
      <button type="button" class="recent-q">${esc(r.question)}</button>
      ${OUTCOME[r.refusal] || OUTCOME.null}<span class="when">${(r.latency_s ?? 0).toFixed(1)} s</span></li>`).join("");
    $("#recent").hidden = false;
  } catch { /* the list is a convenience; the page works without it */ }
}
$("#recent-list").addEventListener("click", (e) => {
  const b = e.target.closest(".recent-q");
  if (!b) return;
  $("#question").value = b.textContent;
  form.requestSubmit();
});

// ---- evidence panel ----
function closeEvidence() {
  $("#evidence-tag").textContent = "No source open";
  $("#evidence-body").innerHTML = `<p class="ev-empty">Open a numbered source on an answer to read the exact passage, with its document, page, date and version.</p>
    <ul class="rules">
      <li>${icon("shield")}<span>Only the latest approved version of each document is searched.</span></li>
      <li>${icon("shield")}<span>Below a 0.72 match VerifAI says it has no evidence instead of answering.</span></li>
      <li>${icon("shield")}<span>Questions asking for advice get facts, never a recommendation.</span></li>
      <li>${icon("shield")}<span>Every claim carries a numbered citation to a page.</span></li>
    </ul>`;
}
function openEvidence(turn, n) {
  const c = turn?.citations.find((x) => String(x.n) === String(n));
  if (!c) return;
  document.querySelectorAll(".cite.on, .cite-card.on").forEach((el) => el.classList.remove("on"));
  card.querySelectorAll(`[data-n="${c.n}"]`).forEach((el) => el.classList.add("on"));
  $("#evidence-tag").textContent = `Source [${c.n}]`;
  $("#evidence-body").innerHTML = `<h3 class="ev-title">${esc(c.title)}</h3>
    <dl class="kv">
      <dt>Document</dt><dd class="mono">${esc(c.source_name)}</dd>
      <dt>Page</dt><dd>${esc(c.page)}</dd>
      <dt>Published</dt><dd>${day(c.published_date)}</dd>
      <dt>Version</dt><dd>v${esc(c.version)}</dd>
      <dt>Match</dt><dd>${(c.score ?? 0).toFixed(3)} cosine</dd>
      <dt>Passage ID</dt><dd class="mono">${esc(c.chunk_id)}</dd>
    </dl>
    <p class="ev-text">${esc(c.text)}</p>`;
  if (innerWidth <= 1100) $("#evidence").scrollIntoView({ behavior: "smooth" });
}
document.addEventListener("click", (e) => {
  const el = e.target.closest(".cite, .cite-card");
  if (!el) return;
  const past = el.closest(".past");
  openEvidence(past ? turns[past.dataset.turn] : active, el.dataset.n);
});

// ---- knowledge base ----
const cell = (label, value, note = "") => `<div><span>${label}</span><b>${value}</b>${note ? `<small>${note}</small>` : ""}</div>`;
const emptyRow = (cols, msg) => `<tr><td class="empty" colspan="${cols}">${msg}</td></tr>`;

async function loadKnowledge() {
  const tbody = $("#kb-table tbody");
  try {
    const docs = await getJSON("/documents");
    const latest = docs.filter((d) => d.is_latest);
    $("#kb-stats").innerHTML = cell("Searchable documents", num(latest.length), `${num(docs.length - latest.length)} older versions on record`) +
      cell("Passages indexed", num(docs.reduce((s, d) => s + d.chunks, 0))) +
      cell("Issuers", num(new Set(docs.map((d) => d.issuer)).size)) +
      cell("Newest document", day(docs.map((d) => d.published_date).sort().at(-1)));
    tbody.innerHTML = docs.length ? docs.map((d) => `<tr class="${d.is_latest ? "" : "old"}">
      <td><div class="doc">${esc(d.title)}</div><div class="mono">${esc(d.source_name)}</div></td>
      <td>${esc(TYPES[d.doc_type] || d.doc_type)}</td><td>${esc(d.issuer)}</td><td class="num">${esc(d.published_date)}</td>
      <td class="num">v${esc(d.version)}</td>
      <td>${d.is_latest ? '<span class="pill ok">Searched</span>' : '<span class="pill off">Superseded</span>'}</td>
      <td class="num">${num(d.chunks)}</td></tr>`).join("") : emptyRow(7, "No documents indexed yet. Add one below.");
  } catch {
    tbody.innerHTML = emptyRow(7, "Couldn't load the document list. Refresh to try again.");
  }
}

$("#upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = $("#upload-msg");
  const btn = e.target.querySelector("button");
  btn.disabled = true;
  msg.className = "";
  msg.textContent = "Indexing… a large PDF takes about a minute.";
  try {
    const res = await fetch("/documents", { method: "POST", body: new FormData(e.target) });
    const out = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof out.detail === "string" ? out.detail : `Upload failed (${res.status}).`);
    msg.className = "ok";
    msg.textContent = `${out.status}: ${num(out.chunks)} passages added${out.superseded_chunks ? `, ${num(out.superseded_chunks)} older passages superseded` : ""}.`;
    e.target.reset();
    loadKnowledge();
  } catch (err) {
    msg.className = "bad";
    msg.textContent = err.message;
  } finally {
    btn.disabled = false;
  }
});

// ---- activity log ----
async function loadActivity() {
  const tbody = $("#log-table tbody");
  try {
    const [s, rows] = await Promise.all([getJSON("/stats"), getJSON("/activity")]);
    $("#log-stats").innerHTML = cell("Questions", num(s.requests)) +
      cell("Answered", num(s.requests - s.refusals)) +
      cell("Declined", num(s.refusals), "No evidence or advice boundary") +
      cell("95th percentile latency", `${(s.p95_latency_s ?? 0).toFixed(1)} s`);
    tbody.innerHTML = rows.length ? rows.map((r) => `<tr>
      <td class="num">${esc(String(r.ts).replace("T", " ").slice(0, 16))}</td>
      <td class="q">${esc(r.question)}</td><td>${OUTCOME[r.refusal] || OUTCOME.null}</td>
      <td class="mono">${esc((r.cited_doc_ids || []).join(", ") || "—")}</td>
      <td>${r.cached ? "Hit" : "Miss"}</td><td class="num">${(r.latency_s ?? 0).toFixed(1)} s</td></tr>`).join("")
      : emptyRow(6, "No questions asked since the server started.");
  } catch {
    tbody.innerHTML = emptyRow(6, "Couldn't load the activity log. Refresh to try again.");
  }
}

health();
closeEvidence();
loadRecent();
route();
