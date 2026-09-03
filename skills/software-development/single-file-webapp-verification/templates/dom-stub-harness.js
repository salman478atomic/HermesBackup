// DOM-stub harness for single-file HTML apps.
// Copy to /tmp/<app>/harness.js and adjust <app> / BLOCKS, then append app-specific tests.
// Prereq: extract <script> blocks first (python):
//   import re
//   src = open('<path/to/app.html>').read()
//   blocks = re.findall(r'<script>(.*?)</script>', src, re.DOTALL)
//   for i, b in enumerate(blocks): open(f'/tmp/<app>/block{i}.js', 'w').write(b)
const fs = require("fs"), vm = require("vm");

const noop = () => {};
const fakeEl = new Proxy(function(){}, {
  get: (t, p) => {
    if (p === Symbol.toPrimitive) return () => "";
    if (p === "classList") return { add: noop, remove: noop, toggle: noop, contains: () => false };
    if (p === "style") return {};
    if (p === "querySelectorAll") return () => [];
    if (p === "querySelector") return () => null;
    if (p === "children") return [];
    return noop;
  },
  apply: () => fakeEl, set: () => true,
});
global.document = { getElementById: () => fakeEl, querySelectorAll: () => [], querySelector: () => null,
  createElement: () => fakeEl, addEventListener: noop, documentElement: { setAttribute: noop }, body: fakeEl };
global.window = { scrollTo: noop, addEventListener: noop, open: noop };
global.localStorage = { getItem: () => null, setItem: noop };
global.indexedDB = { open: () => ({}) };
global.fetch = () => Promise.reject(new Error("offline test"));
global.navigator = {}; global.confirm = () => false; global.CSS = { escape: (s) => s };

// IMPORTANT: runInThisContext, NOT indirect eval — apps starting with "use strict"
// keep their top-level function declarations scoped under eval, so app functions
// would NOT become globals and every test would throw ReferenceError.
const BLOCKS = 7; // <-- adjust to the app's script-block count
const code = [];
for (let i = 0; i < BLOCKS; i++) code.push(fs.readFileSync(`/tmp/<app>/block${i}.js`, "utf8"));
try {
  vm.runInThisContext(code.join("\n"), { filename: "app.js" });
} catch (e) {
  console.log("LOAD FAIL:", e.message);
  process.exit(1);
}
console.log(`all ${BLOCKS} blocks loaded OK`);

// ================= APP-SPECIFIC TESTS =================
const T = [];
const ck = (name, cond) => T.push([name, !!cond]);

// Example shape — replace with real checks against the app's pure functions:
// ck("adapter clamps user_score", appFn(input).field === expected);
// Idempotency pattern: run the normalizer twice, expect byte-identical records.
// Negative-path pattern: null / "" / "None" / garbage-string into every parser.
// Data fixture pattern: sample REAL rows from the dataset JSON, don't invent records.

// ================= REPORT =================
let fail = 0;
for (const [n, ok] of T) { if (!ok) fail++; console.log(`${ok ? "PASS" : "FAIL"}  ${n}`); }
console.log(`\n${T.length - fail}/${T.length} passed`);
process.exit(fail ? 1 : 0);
