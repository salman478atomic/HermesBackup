// node-test-harness.js — run a single-file HTML app's <script> blocks in Node.
// Setup: extract blocks to ./block0.js … blockN.js, set N below, append tests.
// Run:   node node-test-harness.js
//
// WHY vm.runInThisContext: blocks often start with "use strict"; eval() of a
// strict block does NOT leak top-level `function` declarations into scope, so
// every test fails with "X is not defined". runInThisContext DOES leak them.
const fs = require("fs"), vm = require("vm");

const noop = () => {};
const fakeEl = new Proxy(function () {}, {
  get: (t, p) => {
    if (p === Symbol.toPrimitive) return () => "";
    if (p === "classList") return { add: noop, remove: noop, toggle: noop, contains: () => false };
    if (p === "style") return {};
    if (p === "children") return [];
    if (p === "textContent") return "";
    return noop;
  },
  apply: () => fakeEl,
  set: () => true,
});

global.document = {
  getElementById: () => fakeEl,
  querySelectorAll: () => [],
  querySelector: () => null,
  createElement: () => fakeEl,
  addEventListener: noop,
  documentElement: { setAttribute: noop },
  body: fakeEl,
};
global.window = { scrollTo: noop, addEventListener: noop, open: noop };
global.localStorage = { getItem: () => null, setItem: noop };
global.indexedDB = { open: () => ({}) };
global.fetch = () => Promise.reject(new Error("offline test"));
global.navigator = {};
global.confirm = () => false;
global.CSS = { escape: (s) => s };

const N = 7; // number of <script> blocks
const code = [];
for (let i = 0; i < N; i++) code.push(fs.readFileSync(`${__dirname}/block${i}.js`, "utf8"));
try {
  vm.runInThisContext(code.join("\n"), { filename: "app.js" });
} catch (e) {
  console.log("LOAD FAIL:", e.message);
  process.exit(1);
}
console.log(`all ${N} blocks loaded OK`);

// ---- tests below ----
const T = [];
const ck = (name, cond) => T.push([name, !!cond]);

// Example shapes:
// ck("pure fn works", myAppFunction("input") === "expected");
// const g = rawgAdapter([{ name: "Test", rating: 4.1 }])[0];
// ck("adapter maps rating", g.user_score === 82);

let fail = 0;
for (const [name, ok] of T) {
  if (!ok) fail++;
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}`);
}
console.log(`\n${T.length - fail}/${T.length} passed`);
process.exit(fail ? 1 : 0);
