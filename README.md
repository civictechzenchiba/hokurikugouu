# 令和8年8月石川・富山・福井豪雨 — CTZC 復興支援ポータル（要件）

CivicTechZenChiba（CTZC）として、令和8年8月石川・富山・福井豪雨の復興・災害対策のために検討しているポータルサイトの**要件定義**と、GitHub Pages 上の簡易公開サイトです。

**公開サイト:** https://civictechzenchiba.github.io/hokurikugouu/

検証・添削・協働編集を歓迎します。Issue や Pull Request で指摘してください。

## 更新を止めました（2026-10-25）

千葉版（civictechzenchiba/chibagouu）と合わせて、2026-10-25 を最終更新日として自動処理を止めました。
全ページの先頭に「このサイトの更新は終了しました」の帯が出ます。公式ページへのリンクは切れていくことがあります。

北陸版は 2026-09-02 に千葉版を複製して立ち上げたあと、収集・更新検知・Wayback 保存・Slack 通知の 4 本を有効にしないまま来たので、
公式ページの更新検知の記録（`site/data/watch-log/`）はありません。残っているのは支援策の一覧 `data/supports.csv`（84 行）と、
止める日に 1 回だけ流した Wayback の保存（`site/data/archive-index.json`）です。

再開するときは `site/data/site-status.json` の `archived` を `false` に戻し、`.github/workflows/` の 4 本の `schedule:` のコメントを外します。手順は [`docs/archive-runbook.md`](./docs/archive-runbook.md)。

## 似た仕組みを作るとき

このリポジトリは千葉版 [civictechzenchiba/chibagouu](https://github.com/civictechzenchiba/chibagouu) を 2026-09-02 に複製して作った。
作った経緯・動いている仕組み・差し替える設定の一覧・踏んだ罠は、千葉版の README の「似た仕組みを作るとき」にまとめてある。
複製の手順は [`docs/replication-checklist.md`](./docs/replication-checklist.md)、止め方は [`docs/archive-runbook.md`](./docs/archive-runbook.md)。

北陸版で千葉版と違えたのは次の点。

- 災害名：気象庁の命名が無いので「令和8年8月石川・富山・福井豪雨」とし、国の呼び名「令和8年8月27日からの大雨」を併記（`site/data/config.json` の `_name_comment`）
- `regions` に石川・富山・福井の 3 県を並べ、NHK の県別ページの番号（`nhk_area`）を持たせた
- 市町村ページの災害救助法の表示を、収集スクリプトが実際に書く値に合わせた（PR #2）

## このリポジトリで見ること

要件の本体は [`docs/input/`](./docs/input/) です。

| ファイル | 内容 |
|----------|------|
| [docs/input/README.md](./docs/input/README.md) | プロジェクト概要 |
| [docs/input/business-requirements.md](./docs/input/business-requirements.md) | ビジネス要件 |
| [docs/input/user-personas.md](./docs/input/user-personas.md) | ターゲットユーザー |
| [docs/input/product-requirements.md](./docs/input/product-requirements.md) | プロダクト要件 |
| [docs/input/user-flows.md](./docs/input/user-flows.md) | ユーザーフロー |
| [docs/input/feature-list.md](./docs/input/feature-list.md) | 機能一覧 |
| [docs/input/mvp-scope.md](./docs/input/mvp-scope.md) | MVP範囲 |
| [docs/input/ui-ux-direction.md](./docs/input/ui-ux-direction.md) | UI/UX方針 |
| [docs/input/source-allowlist.md](./docs/input/source-allowlist.md) | 行政・報道の収集許可リスト（毎日 6:00 JST） |
| [docs/output/system_requirements.md](./docs/output/system_requirements.md) | システム要件 |
| [docs/output/detailed_requirements_specification.md](./docs/output/detailed_requirements_specification.md) | 詳細要件（実装向け） |
| [運用スプレッドシート](https://docs.google.com/spreadsheets/d/1_dHZHMLvTx6iTCzwvbw6U9cTHjTIH_6RlEob81Ng7KM/edit?usp=sharing) | 許可リスト・やること・訂正。リンクを知っている人は閲覧可 |

`docs/prompts/` と `docs/template/` は、要件を引き出すためのプロンプトとテンプレートです。

## 日本語版・英語版の更新

- 日本語版は `site/`、英語版は同じ構成の `site/en/` にあります。
- 表示文言、リンク、メタデータ、動的UI、インフォグラフィックを変更するときは、日英を同じ変更で更新します。
- `python scripts/sync_language_chrome.py` で全ページの言語切替と `hreflang` を補完します。
- 日英双方を確認後、`python scripts/check_bilingual.py --update-manifest` で同期記録を更新します。
- 通常の確認は `python scripts/check_bilingual.py` です。GitHub Pages の公開前にも同じ検査が動きます。

## プロダクトの骨格（要約）

一つのサイトに二つの入口を持つ。

1. **県民向け** — 市町村ごとの被害状況ログ（過去〜現在）と、いま受けられる支援策
2. **支援者向け** — 有志が集まり、行政情報の収集と伝達拡散を分担する場

先行事例として [シビックテック袖ケ浦の災害支援ナビゲーター](https://civictechsodegaura.org/) を県全域・市町村別に広げる（ソース再利用は作成後に確認）。現地の行政プロセスは「とある行政」の知見として一般化しており、個人名・特定の内部情報は出さない。

初日に被害ログを出す対象は、警戒レベル5（大雨特別警報）が出た自治体および流山市。県民向け情報は行政機関と報道機関から収集し、1日1回自動更新する。

## 検証してほしいこと

- 県民入口と支援者入口の切り分けは分かりそうか
- 市町村ページのテンプレート（ログ／いまの支援策／生活再建の段取り）に足りない欄はないか
- MVP の切り方（枠は全市町村、初日ログはレベル5対象＋流山市）は現場で回るか
- 公式情報の扱いに危うい断定がないか（金額・日数は裏取り前に断定しない方針）
- 既存の行政・社協・他団体の取り組みと重複していないか

## 注意

- 本資料は有志の検討用であり、行政の公式発表ではない
- 制度の金額・所要日数・適用可否は各実施機関の判断。公開前に公式で確認する
- `[仮]` や `[要公式確認]` が付いた項目は未確定

## 連絡

- CTZC ウェブサイト: https://sites.google.com/view/civictechzenchiba/
- Facebook グループ: https://www.facebook.com/groups/civictechzenchiba/
- Facebook ページ: https://www.facebook.com/p/Civic-Tech-Zen-Chiba-100064346395345/
- CTZC Slack: https://civictechzenchiba.slack.com/archives/C0BPSMN4L5D
