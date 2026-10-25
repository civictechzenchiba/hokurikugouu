// 「この情報について報告」リンク。日本語版・英語版で共通。
// data/report-config.json に Google フォームの URL と entry ID があればフォームへ（ページURL・対象を事前入力）、
// なければ GitHub Issue（プレフィル）へ。サーバーには何も送らない。個人情報は取らない。
// Report-a-problem links. Uses the Google Form in data/report-config.json when configured, otherwise a prefilled GitHub issue.
(function () {
  var EN = document.documentElement.lang === "en";
  var script = document.currentScript || (function () {
    var s = document.getElementsByTagName("script");
    return s[s.length - 1];
  })();
  var root = (script && script.src) ? script.src.replace(/js\/report\.js(\?.*)?$/, "") : "";
  var config = null;
  var repo = "";
  var readyCallbacks = [];
  var T = EN ? {
    footerLead: "Is something on this page wrong, outdated, or a broken link?",
    footerLink: "Report it (30 seconds, no name needed)",
    footerNote: "Volunteers verify against official sources before fixing. This is not an application desk; for emergencies call 119/110.",
    item: "Report",
    itemTitle: "Report a problem with this link",
    issueTitle: function (target) { return "[Report] " + (target || "This page"); },
    issueBody: function (page, target) {
      return "Page: " + page + "\nTarget: " + (target || "-") + "\n\nWhat is wrong (broken link / outdated / incorrect / missing): \n\nDetails: \n\nOfficial source URL (if any): \n";
    }
  } : {
    footerLead: "このページの情報が違う・古い・リンクが開かないときは",
    footerLink: "報告する（30秒、名前不要）",
    footerNote: "有志が公式で確認してから直します。申請窓口ではありません。緊急のときは 119／110 へ。",
    item: "報告",
    itemTitle: "このリンクの情報について報告する",
    issueTitle: function (target) { return "[報告] " + (target || "このページ"); },
    issueBody: function (page, target) {
      return "ページ: " + page + "\n対象: " + (target || "-") + "\n\nどんな問題か（リンク切れ／古い／違う／載っていない）: \n\nくわしく: \n\n正しい情報の出典URL（あれば）: \n";
    }
  };
  function pageUrl() { return location.href; }
  function link(target) {
    var page = pageUrl();
    if (config && config.form_url) {
      var u = config.form_url + (config.form_url.indexOf("?") >= 0 ? "&" : "?") + "usp=pp_url";
      var e = config.entries || {};
      if (e.page) u += "&" + encodeURIComponent(e.page) + "=" + encodeURIComponent(page);
      if (e.target && target) u += "&" + encodeURIComponent(e.target) + "=" + encodeURIComponent(target);
      return u;
    }
    return "https://github.com/" + repo + "/issues/new?title=" +
      encodeURIComponent(T.issueTitle(target)) + "&body=" + encodeURIComponent(T.issueBody(page, target));
  }
  function decorate(scope) {
    var els = (scope || document).querySelectorAll("a[data-report]");
    Array.prototype.forEach.call(els, function (a) {
      a.href = link(a.getAttribute("data-report-target") || "");
      a.target = "_blank";
      a.rel = "noopener";
    });
  }
  // 各リンク横の小さな「報告」/ small per-item link
  function itemLink(target) {
    var a = document.createElement("a");
    a.className = "report-link";
    a.setAttribute("data-report", "");
    a.setAttribute("data-report-target", target || "");
    a.title = T.itemTitle;
    a.textContent = T.item;
    a.href = link(target);
    a.target = "_blank";
    a.rel = "noopener";
    return a;
  }
  // フッターの共有ボタンの下に1行 / one line under the share buttons
  function mountFooter(rootEl) {
    if (rootEl.querySelector(".report-footer")) return;
    var p = document.createElement("p");
    p.className = "meta report-footer";
    p.appendChild(document.createTextNode(T.footerLead + " "));
    var a = document.createElement("a");
    a.textContent = T.footerLink;
    a.href = link(document.title);
    a.target = "_blank";
    a.rel = "noopener";
    // ページ名（市町村ページでは読み込み後に市町村名が入る）を押した時点で対象に入れる
    a.addEventListener("click", function () { a.href = link(document.title); });
    p.appendChild(a);
    p.appendChild(document.createTextNode(" " + T.footerNote));
    rootEl.appendChild(p);
  }
  function onReady(cb) { if (config !== null) cb(config); else readyCallbacks.push(cb); }
  window.Report = { link: link, decorate: decorate, itemLink: itemLink, onReady: onReady };

  document.querySelectorAll("[data-share]").forEach(mountFooter);
  // 通報先（report-config.json）と、Issue に落とすときの repo（config.json）を読む。
  // config.json が読めなくても通報先が決まっていれば困らないので、別々に失敗を飲む
  Promise.all([
    fetch(root + "data/report-config.json", { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (c) { config = c || {}; })
      .catch(function () { config = {}; }),
    fetch(root + "data/config.json", { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (c) { repo = (c && c.repo) || ""; })
      .catch(function () { repo = ""; })
  ])
    .then(function () {
      decorate(document);
      Array.prototype.forEach.call(document.querySelectorAll(".report-footer a"), function (a) { a.href = link(document.title); });
      readyCallbacks.forEach(function (cb) { cb(config); });
      readyCallbacks = [];
    });
})();
