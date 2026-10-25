// VerifAI web UI: hash routing, SSE chat, knowledge base, activity log. No framework.
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const pct = (x) => `${((x || 0) * 100).toFixed(1)}%`;
const num = (x) => Number(x || 0).toLocaleString("en-IN");
const icon = (id) => `<svg><use href="#i-${id}"/></svg>`;
const BUDGET = 3000;
let turns = []; // {question, answer, citations, refusal}, oldest first
let active = null; // the turn whose citations the open chips belong to

// ---- routing ----
function route() {
  const name = ["ask", "knowledge", "activity"].includes(location.hash.slice(1)) ? location.hash.slice(1) : "ask";
  document.querySelectorAll(".page").forEach((p) => (p.hidden = p.id !== `page-${name}`));
  document.querySelectorAll("[data-route]").forEach((a) =>
    a.dataset.route === name ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  if (name === "knowledge") loadKnowledge();
  if (name === "activity") loadActivity();
}
addEventListener("hashchange", route);

const getJSON = (url) => fetch(url).then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.status))));

getJSON("/health").then((h) => {
  $("#corpus-count").textContent = `${num(h.chunks_indexed)} chunks indexed`;
  $("#corpus-baseline").textContent = `Corpus: ${num(h.chunks_indexed)} chunks`;
}).catch(() => ($("#corpus-count").textContent = "Index unavailable"));

// ---- tiny markdown: paragraphs, **bold**, bullets, [n] citation chips ----
function md(text) {
  const inline = (s) => esc(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, (_, ns) =>
      ns.split(",").map((n) => `<button type="button" class="cite" data-n="${n.trim()}">${n.trim()}</button>`).join(""));
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
  div.className = "card past";
  div.dataset.turn = turns.length - 1;
  div.innerHTML = `<p class="answer-q">${esc(t.question)}</p><div class="prose">${md(t.answer || "")}</div>`;
  $("#history").append(div);
}

async function ask(question) {
  archive();
  closeEvidence();
  const btn = $("#submit");
  btn.disabled = true;
  card.hidden = false;
  card.innerHTML = `<p class="answer-q">${esc(question)}</p>
    <div class="wait"><span class="pulse"></span>Searching the approved documents… the free-tier model can take up to a minute to start.</div>`;
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
      <button type="button" class="btn-line" id="retry">${icon("reset")}Retry</button></div>`;
    $("#retry").onclick = () => ask(question);
  } finally {
    btn.disabled = false;
  }
}

function renderAnswer(turn, d) {
  const tr = d.trace || {};
  active = turn;
  card.dataset.turn = turns.length - 1;
  setMeter(tr.context_tokens || 0);
  let head, bodyHTML;
  if (d.refusal === "no_evidence") {
    head = `<span class="badge warn">${icon("alert")}Not enough evidence</span>
      <span class="stat"><span class="mono-xs muted">Top match</span><b>${(tr.top_score ?? 0).toFixed(3)}</b></span>
      <span class="stat"><span class="mono-xs muted">Threshold</span><b>${(tr.threshold ?? 0).toFixed(2)}</b></span>`;
    bodyHTML = `<div class="notice warn"><span class="notice-title">${icon("alert")}No approved passage is close enough</span>
      <p>The best match scored ${(tr.top_score ?? 0).toFixed(3)}, below the ${(tr.threshold ?? 0).toFixed(2)} evidence threshold, so VerifAI won't answer from memory.</p></div>
      <div class="prose">${md(d.answer)}</div>`;
  } else {
    const n = new Set(turn.citations.map((c) => c.source_name)).size;
    head = `${n ? `<span class="badge ok">${icon("shield")}Grounded</span>` : `<span class="badge bad">${icon("alert")}Advice boundary</span>`}
      <span class="stat"><span class="mono-xs muted">Top match</span><b>${pct(tr.top_score)}</b></span>
      ${tr.model ? `<span class="stat"><span class="mono-xs muted">Engine</span><b>${esc(tr.model)}</b></span>` : ""}
      <span class="stat"><span class="mono-xs muted">Cited</span><b>${n} source${n === 1 ? "" : "s"}</b></span>`;
    if (d.refusal === "advice") {
      const [boundary, ...facts] = d.answer.trim().split(/\n\s*\n/);
      bodyHTML = `<div class="notice bad"><span class="notice-title">${icon("alert")}Advice boundary</span><p>${md(boundary).replace(/^<p>|<\/p>$/g, "")}</p></div>
        ${facts.length ? `<span class="label gold">What the approved documents say</span><div class="prose" style="margin-top:12px">${md(facts.join("\n\n"))}</div>`
          : `<p class="muted small">No approved passage cleared the evidence threshold, so there are no facts to add.</p>`}`;
    } else {
      bodyHTML = `<span class="label gold">Answer from approved documents</span><div class="prose" style="margin-top:12px">${md(d.answer)}</div>`;
    }
  }
  const cites = turn.citations.map((c) => `
    <button type="button" class="cite-card" data-n="${c.n}">
      <span class="row"><span class="tag">[${c.n}]</span><span class="pill">${pct(c.score)} match</span></span>
      <span class="cite-title">${esc(c.title)}</span>
      <span class="mono-sm">Page ${esc(c.page)} · ${esc(c.published_date)}</span>
      <span class="cite-ex">“${esc(c.text.slice(0, 220))}…”</span>
      <span class="cite-foot">Inspect excerpt →</span>
    </button>`).join("");
  const rewritten = d.standalone_question && d.standalone_question !== turn.question;
  const gate = (tr.top_score ?? 0) >= (tr.threshold ?? 0);
  const stage = (name, lines) => `<div class="stage"><span class="mono-xs gold">${name[0]}</span><span class="stage-name">${name[1]}</span>${lines}</div>`;
  card.innerHTML = `<div class="answer-top">${head}</div>
    <p class="answer-q">${esc(turn.question)}</p>
    ${bodyHTML}
    ${cites ? `<div class="section-head"><span class="label">Sources cited</span><span class="mono-xs muted">Threshold: cosine ≥ ${(tr.threshold ?? 0).toFixed(2)}</span></div><div class="cite-grid">${cites}</div>` : ""}
    <details class="why" open><summary><span class="label">Why this answer</span>${icon("chevron")}</summary><div class="stages">
      ${stage(["Stage 1", "Query"], `<p>${rewritten ? `Rewritten from the conversation:<br><i>${esc(d.standalone_question)}</i>` : "Searched as asked."}</p>`)}
      ${stage(["Stage 2", "Vector search"], `<p>${num(tr.candidates)} candidate passages from the latest approved versions.</p>`)}
      ${stage(["Stage 3", "Re-rank + gate"], `<p>${num(tr.reranked)} kept after re-ranking.</p><p class="${gate ? "" : "fail"}">Top ${(tr.top_score ?? 0).toFixed(3)} ${gate ? "≥" : "<"} ${(tr.threshold ?? 0).toFixed(2)} · ${gate ? "passed" : "declined"}</p>`)}
      ${stage(["Stage 4", "Context"], `<p>${num(tr.context_chunks)} chunks (+${num(tr.neighbours)} neighbours), ${num(tr.context_tokens)} tokens to ${esc(tr.model || "the model")}.</p>`)}
    </div></details>
    <p class="mono-xs muted" style="margin:18px 0 0">First token in ${(d.first_token_s ?? 0).toFixed(1)} s</p>`;
}

function renderSession() {
  $("#session").hidden = false;
  $("#session-list").innerHTML = turns.map((t) =>
    `<li><span class="dot ${t.refusal === "no_evidence" ? "amber" : t.refusal === "advice" ? "red" : "green"}"></span>${esc(t.question)}</li>`).join("");
}

// ---- evidence panel ----
function closeEvidence() {
  $("#evidence-tag").textContent = "No source open";
  $("#evidence-body").innerHTML = `<p class="muted small">Open a source on an answer to read the exact passage it was built from, with its document, page, date and version.</p>`;
}
function openEvidence(turn, n) {
  const c = turn?.citations.find((x) => String(x.n) === String(n));
  if (!c) return;
  document.querySelectorAll(".cite.on, .cite-card.on").forEach((el) => el.classList.remove("on"));
  card.querySelectorAll(`[data-n="${c.n}"]`).forEach((el) => el.classList.add("on"));
  $("#evidence-tag").textContent = `Citation [${c.n}]`;
  $("#evidence-body").innerHTML = `<h3 class="ev-title">${esc(c.title)}</h3>
    <dl class="ev-meta">
      <dt>Document</dt><dd>${esc(c.source_name)}</dd>
      <dt>Page</dt><dd>${esc(c.page)}</dd>
      <dt>Published</dt><dd>${esc(c.published_date)}</dd>
      <dt>Version</dt><dd>v${esc(c.version)}</dd>
      <dt>Cosine</dt><dd><span class="pill">${(c.score ?? 0).toFixed(3)} · ${pct(c.score)}</span></dd>
      <dt>Chunk</dt><dd class="ev-id">${esc(c.chunk_id)}</dd>
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
const stat = (label, value) => `<div class="card stat-card"><span class="label-sm">${label}</span><b>${value}</b></div>`;
const emptyRow = (cols, msg) => `<tr><td class="empty" colspan="${cols}">${msg}</td></tr>`;

async function loadKnowledge() {
  const tbody = $("#kb-table tbody");
  try {
    const docs = await getJSON("/documents");
    const latest = docs.filter((d) => d.is_latest);
    $("#kb-stats").innerHTML = stat("Documents", num(docs.length)) + stat("Searchable (latest)", num(latest.length)) +
      stat("Chunks", num(docs.reduce((s, d) => s + d.chunks, 0))) + stat("Issuers", num(new Set(docs.map((d) => d.issuer)).size));
    tbody.innerHTML = docs.length ? docs.map((d) => `<tr>
      <td><div class="doc">${esc(d.title)}</div><div class="mono">${esc(d.source_name)}</div></td>
      <td class="mono">${esc(d.doc_type)}</td><td>${esc(d.issuer)}</td><td class="mono">${esc(d.published_date)}</td>
      <td class="mono">v${esc(d.version)}</td>
      <td>${d.is_latest ? '<span class="pill">Latest</span>' : '<span class="chip-line">Superseded</span>'}</td>
      <td class="num">${num(d.chunks)}</td></tr>`).join("") : emptyRow(7, "No documents indexed yet. Upload one below.");
  } catch {
    tbody.innerHTML = emptyRow(7, "Couldn't load the document list. Refresh to try again.");
  }
}

$("#upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = $("#upload-msg");
  const btn = e.target.querySelector("button");
  btn.disabled = true;
  msg.className = "small";
  msg.textContent = "Indexing… large PDFs take a minute.";
  try {
    const res = await fetch("/documents", { method: "POST", body: new FormData(e.target) });
    const out = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(typeof out.detail === "string" ? out.detail : `Upload failed (${res.status}).`);
    msg.className = "small ok";
    msg.textContent = `${out.status}: ${num(out.chunks)} chunks added${out.superseded_chunks ? `, ${num(out.superseded_chunks)} older chunks superseded` : ""}.`;
    e.target.reset();
    loadKnowledge();
  } catch (err) {
    msg.className = "small bad";
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
    $("#log-stats").innerHTML = stat("Questions", num(s.requests)) + stat("Cache hits", num(s.cache_hits)) +
      stat("Declined", num(s.refusals)) + stat("p95 latency", `${(s.p95_latency_s ?? 0).toFixed(1)} s`);
    const outcome = (r) => r.refusal === "no_evidence" ? '<span class="badge warn">Not enough evidence</span>'
      : r.refusal === "advice" ? '<span class="badge bad">Advice boundary</span>' : '<span class="badge ok">Answered</span>';
    tbody.innerHTML = rows.length ? rows.map((r) => `<tr>
      <td class="mono">${esc(String(r.ts).replace("T", " "))}</td>
      <td class="q">${esc(r.question)}</td><td>${outcome(r)}</td>
      <td class="mono">${esc((r.cited_doc_ids || []).join(", ") || "—")}</td>
      <td class="mono">${r.cached ? "Hit" : "Miss"}</td><td class="num mono">${(r.latency_s ?? 0).toFixed(1)} s</td></tr>`).join("")
      : emptyRow(6, "No questions asked since the server started.");
  } catch {
    tbody.innerHTML = emptyRow(6, "Couldn't load the activity log. Refresh to try again.");
  }
}

route();
