// 更新を止めたあとに来た人へ、いつの情報かを最初に伝える。
// site/data/site-status.json の archived を true にすると、全ページの先頭に帯が出る。
// ページ側の書き換えは要らない（26ページを触らずに切り替えるため）。
(function () {
  var script = document.currentScript;
  if (!script) return;
  var siteRoot = new URL("../", script.src);
  var isEnglish = document.documentElement.lang === "en";

  fetch(siteRoot + "data/site-status.json")
    .then(function (r) { return r.json(); })
    .then(function (st) {
      if (!st || !st.archived) return;
      var bar = document.createElement("div");
      bar.className = "archived-bar";
      bar.setAttribute("role", "note");
      var inner = document.createElement("div");
      inner.className = "archived-bar-inner";
      var strong = document.createElement("strong");
      strong.textContent = isEnglish
        ? "This site is no longer updated."
        : "このサイトの更新は終了しました。";
      var text = document.createElement("span");
      text.textContent = isEnglish
        ? " The content reflects " + (st.archived_at || "the date shown below") +
          ". Links to official pages may no longer work. Always check the municipal, prefectural and national official sites for current information."
        : "内容は" + (st.archived_at || "下記の日付") +
          "時点のものです。公式ページへのリンクは切れていることがあります。いまの情報は市町村・県・国の公式で確認してください。";
      inner.appendChild(strong);
      inner.appendChild(text);
      bar.appendChild(inner);
      document.body.insertBefore(bar, document.body.firstChild);
    })
    .catch(function () { /* 読めなければ何も出さない */ });
})();
