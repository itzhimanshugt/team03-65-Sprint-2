// K7, machine-measured: runs the usability test's 5 tasks in a headless browser against the
// live UI and times each one from submit to the cited answer on screen. It measures the
// system's share of K7; a person's typing and reading time is not included.
// Run: node scripts/k7_timing.mjs [site] [runs]   (Node 22+; Chrome or Edge, or set CHROME to its path)
import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const SITE = process.argv[2] || "https://verifai-vysj.onrender.com";
const RUNS = Number(process.argv[3] || 3);
if (!Number.isInteger(RUNS) || RUNS < 1) throw new Error(`runs must be a whole number ≥ 1, got ${process.argv[3]}`);
const OUT = "docs/usability/results/k7_automated.csv";
const browser = [
  process.env.CHROME,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
].find((p) => p && existsSync(p));
if (!browser) throw new Error("No Chrome or Edge found; set CHROME to its path.");

// Same tasks and success rules as docs/usability/usability-test.md.
const TASKS = [
  { id: "T1", ask: ["What is the benchmark of HSBC Infrastructure Fund?"], expect: /Nifty Infrastructure/i, source: "hsbc-factsheet-2026-08" },
  { id: "T2", ask: ["When did Parag Parikh ELSS Tax Saver Fund start?"], expect: /July 24, 2019|24 July 2019/i, source: "ppfas-factsheet-2026-09" },
  { id: "T3", ask: ["What is the AUM of HSBC Liquid Fund?", "And how risky is it?"], expect: /Low to Moderate/i, source: "hsbc-factsheet-2026-08" },
  { id: "T4", ask: ["What is the exit load of SBI Bluechip Fund?"], refusal: "no_evidence" },
  { id: "T5", knowledge: true },
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const profile = mkdtempSync(join(tmpdir(), "k7-"));
// Port 0: the browser picks a free port and writes it to DevToolsActivePort, so a stale browser can't answer.
const proc = spawn(browser, ["--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "about:blank"], { stdio: "ignore" });
let ws;
const rows = [];
try {
  for (let i = 0; i < 80 && !ws; i++) {
    await sleep(250);
    try {
      const port = readFileSync(join(profile, "DevToolsActivePort"), "utf8").split("\n")[0];
      const t = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((x) => x.type === "page");
      ws = new WebSocket(t.webSocketDebuggerUrl);
    } catch { /* browser still starting */ }
  }
  if (!ws) throw new Error("The browser's DevTools endpoint never came up.");
  await new Promise((ok, fail) => {
    ws.addEventListener("open", ok);
    ws.addEventListener("error", () => fail(new Error("DevTools connection failed.")));
    setTimeout(() => fail(new Error("DevTools connection timed out.")), 15000);
  });

  let id = 0;
  const pending = new Map(); // request id → {ok, fail}; a Map so a reply's id can't reach a prototype method
  ws.addEventListener("message", (m) => {
    const d = JSON.parse(m.data);
    const p = pending.get(d.id);
    if (!p) return;
    pending.delete(d.id);
    if (d.error) p.fail(new Error(`${d.error.message} (${d.error.code})`));
    else p.ok(d.result);
  });
  const cdp = (method, params = {}) => new Promise((ok, fail) => { pending.set(++id, { ok, fail }); ws.send(JSON.stringify({ id, method, params })); });
  const js = async (expr) => (await cdp("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result?.value;

  await cdp("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  const open = async (hash) => {
    await cdp("Page.navigate", { url: `${SITE}/${hash}` });
    await js("new Promise(r=>{const t=setInterval(()=>{if(/Index ready/.test(document.querySelector('#corpus-count')?.textContent||'')){clearInterval(t);r(1)}},250);setTimeout(r,90000)})");
  };

  // One question: submit, wait for the finished answer card, return seconds and what it showed.
  // The question goes in as a call argument, never spliced into page code.
  const ASK_FN = `async function (q) {const t0=performance.now();document.querySelector('#question').value=q;
    document.querySelector('#ask-form').requestSubmit();await new Promise(r=>setTimeout(r,300));
    for(let i=0;i<1200&&document.querySelector('#submit').disabled;i++)await new Promise(r=>setTimeout(r,100));
    const a=document.querySelector('#answer');return{s:(performance.now()-t0)/1000,text:a.innerText,
    refused:/Not enough evidence/.test(a.innerText),sources:[...a.querySelectorAll('.cite-meta')].length}}`;
  const ask = async (q) => {
    const { result: win } = await cdp("Runtime.evaluate", { expression: "window" });
    const out = await cdp("Runtime.callFunctionOn", {
      functionDeclaration: ASK_FN, objectId: win.objectId, arguments: [{ value: String(q) }], awaitPromise: true, returnByValue: true,
    });
    if (!out.result?.value) throw new Error("The page returned no answer.");
    return out.result.value;
  };

  // Warm-up so a cold free-tier start is not counted (the human protocol does the same).
  console.log("browser up, warming the site");
  await open("#ask");
  await ask("What is the benchmark of HSBC Large Cap Fund?");

  for (let run = 1; run <= RUNS; run++) {
    for (const t of TASKS) {
      const t0 = Date.now();
      let seconds = 0;
      let ok = false;
      try {
        if (t.knowledge) {
          await open("#knowledge");
          const table = await js("new Promise(r=>{const t=setInterval(()=>{const b=document.querySelector('#kb-table tbody');if(b&&b.rows.length>1){clearInterval(t);r(b.innerText)}},100);setTimeout(()=>r(''),30000)})");
          seconds = (Date.now() - t0) / 1000;
          ok = /HSBC MF Factsheet[^\n]*August 2026[\s\S]*?Searched/.test(table) && /July 2026[\s\S]*?Superseded/.test(table);
        } else {
          await open("#ask");
          let res;
          for (const q of t.ask) { res = await ask(q); seconds += res.s; }
          if (t.refusal) ok = res.refused;
          else {
            await js("document.querySelector('#answer .cite-card')?.click()");
            const ev = await js("document.querySelector('#evidence-body').innerText");
            ok = t.expect.test(res.text) && res.sources > 0 && ev.includes(t.source);
          }
        }
      } catch (err) {
        seconds = seconds || (Date.now() - t0) / 1000; // a failed task keeps its row, marked unsuccessful
        console.log(`run ${run} ${t.id} error: ${err.message}`);
      }
      rows.push([`run${run}`, t.id, seconds.toFixed(1), ok ? 1 : 0]);
      console.log(`run ${run} ${t.id} ${seconds.toFixed(1)} s ${ok ? "ok" : "FAILED"}`);
    }
  }
} finally {
  if (rows.length) {
    writeFileSync(OUT, ["run,task,seconds,success", ...rows.map((r) => r.join(","))].join("\n") + "\n");
    console.log(`wrote ${OUT}`);
  }
  ws?.close();
  proc.kill();
  await sleep(500);
  rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
}
process.exit(0);
