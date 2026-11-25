// 할 일 패널 포맷터/문구가 실제로 한국어를 내는지 VM에서 직접 실행해 확인.
import fs from "node:fs";
import vm from "node:vm";

const P = "C:/Users/krez13/.dsh/profiles/desktop/node_modules/dsh-pet/runtime/electron-helper/shared-core.js";
const src = fs.readFileSync(P, "utf8");

// shared-core는 IIFE로 로드된다. 로더 스텁을 심고 export된 함수를 꺼낸다.
let captured = null;
const doc = {
  createElement: () => ({ style: {}, dataset: {}, classList: { add() {}, toggle() {} }, setAttribute() {}, appendChild() {}, append() {} }),
  addEventListener() {}, removeEventListener() {},
  querySelector: () => null, querySelectorAll: () => [], body: { append() {} },
};
const sandbox = {
  window: { addEventListener() {}, removeEventListener() {}, __ModuleLoader__: { load(m) { captured = m; } } },
  document: doc,
  navigator: { language: "ko-KR" },
  console: { log() {}, warn() {}, error() {} },
  setTimeout, clearTimeout, setInterval, clearInterval, Date, Math, JSON,
  URL, URLSearchParams, TextEncoder, TextDecoder,
};
sandbox.globalThis = sandbox;
sandbox.self = sandbox;
vm.createContext(sandbox);
try {
  vm.runInContext(src, sandbox, { filename: "shared-core.js" });
} catch (e) {
  console.error("로드 실패:", e.message);
  process.exit(1);
}

// shared-core가 노출하는 형태 확인
if (captured && typeof captured.factory === "function") {
  const mod = captured.factory((id) => ({}));
  console.log("export keys:", Object.keys(mod).slice(0, 20).join(", "));
}

const HAN = /[\u4e00-\u9fff]/;
// 직접 포맷터 로직을 번들에서 뽑아 실행 (함수 본문이 같은 파일에 있음)
function grab(name) {
  const i = src.indexOf(`function ${name}(`);
  if (i < 0) return null;
  let depth = 0, j = src.indexOf("{", i);
  const start = j;
  for (; j < src.length; j++) {
    if (src[j] === "{") depth++;
    else if (src[j] === "}") { depth--; if (depth === 0) break; }
  }
  return src.slice(i, j + 1);
}

const helpers = ["spanText", "dueLabel", "remainingLabel", "metaLabel", "pad2$1", "dayDiff", "startOfDay"];
const consts = `
const MINUTE_MS = 60e3, HOUR_MS = 60*MINUTE_MS, DAY_MS = 24*HOUR_MS;
const WEEKDAYS = ["일","월","화","수","목","금","토"];
`;
let code = consts;
for (const h of helpers) {
  const fn = grab(h);
  if (fn) code += "\n" + fn;
}
// WEEKDAYS가 번역됐는지
const wd = src.match(/const WEEKDAYS = \[([\s\S]*?)\];/);
if (wd && HAN.test(wd[1])) console.log("WEEKDAYS: 중문 남음!", wd[1]);
else console.log("WEEKDAYS:", (wd?.[1] ?? "").replace(/\s+/g, " ").trim());

const now = Date.now();
code += `
const out = {
  due_null: dueLabel(null, ${now}),
  due_today: dueLabel(${now} + 3600e3, ${now}),
  due_tomorrow: dueLabel(${now} + 26*3600e3, ${now}),
  remaining_soon: remainingLabel(${now} + 90*60e3, ${now}),
  meta_done: metaLabel({done:true, dueAt:null}, ${now}),
  span_min: spanText(30*60e3),
  span_hour: spanText(3*3600e3),
  span_day: spanText(5*24*3600e3),
};
out;
`;
const out = vm.runInContext(code, sandbox);
console.log("\n포맷 결과:");
for (const [k, v] of Object.entries(out)) {
  console.log(`  ${k.padEnd(16)} ${JSON.stringify(v)}${HAN.test(String(v)) ? "  <-- 중문!" : ""}`);
}
const bad = Object.values(out).filter((v) => HAN.test(String(v)));
console.log(bad.length ? `\nRESULT: ${bad.length}개 중문 남음` : "\nRESULT: OK — 할 일 포맷이 전부 한국어");
process.exit(bad.length ? 1 : 0);
