// Bilingual toggle. Mark copy as <span lang="en">…</span><span lang="zh">…</span>;
// any element with [data-lang-toggle] switches. Choice persists; ?lang=zh|en overrides.
(() => {
  const q = new URLSearchParams(location.search).get("lang");
  const pick = q || localStorage.getItem("ui-remix-lang") || (navigator.language.startsWith("zh") ? "zh" : "en");
  const set = l => { document.documentElement.dataset.lang = l; localStorage.setItem("ui-remix-lang", l); };
  const st = document.createElement("style");
  // CJK has no true italic; browsers fake an oblique that looks broken, so never slant Chinese.
  st.textContent = 'html[data-lang="en"] [lang="zh"], html[data-lang="zh"] [lang="en"] { display: none !important; }'
    + ' [lang="zh"] em, [lang="zh"] i { font-style: normal !important; }';
  document.head.append(st);
  set(pick);
  addEventListener("click", e => {
    if (e.target.closest("[data-lang-toggle]")) set(document.documentElement.dataset.lang === "zh" ? "en" : "zh");
  });
})();
