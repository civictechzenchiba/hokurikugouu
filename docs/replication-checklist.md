# 別の災害・地域へ複製するときの手順

このサイトの仕組み（公式ページの更新検知・候補の自動収集・支援策の一覧・日英ミラー）を、
別の災害へ持っていくための手順です。千葉版で実際に動いているものを前提にしています。

## 方式

**fork ではなく、新しいリポジトリを作って履歴ごと移します。**
fork にすると PR の base が既定で千葉版に向き、内容が新しいリポジトリの main に届かない事故が起きます
（千葉版でも base の取り違えが3回ありました）。

```
git clone --bare https://github.com/civictechzenchiba/hokurikugouu.git /tmp/seed.git
cd /tmp/seed.git && git push --mirror https://github.com/<owner>/<new-repo>.git
```

履歴を残すのは、「なぜそうしたか」がコミットメッセージに残っているためです。

## 1. 設定を差し替える

`site/data/config.json` が、サイト固有の値を集めた場所です。ここを書き換えると、
スクリプトが名乗る UA・通知に出るサイトURL・sitemap の URL・時期別ページの発災日が
まとめて変わります。

```json
{
  "repo": "<owner>/<new-repo>",
  "base_url": "https://<owner>.github.io/<new-repo>/",
  "ua_prefix": "CTZC-<new-repo>",
  "disaster": { "name": "…", "name_en": "…", "onset": "YYYY-MM-DD" },
  "regions": [ { "slug": "pref-xxx", "name": "○○県", "name_en": "…" } ]
}
```

`regions` は市町村以外のまとまり（県・国）です。**複数県にまたがる災害では、県のぶんだけ並べます。**

config.json を書き換えたら、ページと文書に静的に書いてある古い URL（canonical・og:url・hreflang・
GitHub へのリンク・README）を新しい値に行き渡らせます。sitemap と robots、インフォグラフィックの
脚注はそれぞれの生成スクリプトで作り直します。

```
python3 scripts/apply_site_urls.py --dry-run   # 置き換える箇所を数えるだけ
python3 scripts/apply_site_urls.py
python3 scripts/build_sitemap.py
python3 scripts/build_infographics.py && python3 scripts/build_infographics_en.py   # Pillow が要る
python3 scripts/check_bilingual.py --update-manifest
```

## 2. 外部サービスをつなぎ替える（忘れると事故になる）

**このまま複製すると、新しいサイトに届いた通報が千葉のフォームに入ります。** 必ず差し替えてください。

| ファイル | 中身 | 対応 |
|---|---|---|
| `site/data/report-config.json` | 「この情報は違う」の通報先 Google フォーム | 新しいフォームを作って差し替える。**空にすると GitHub Issue へのフォールバック**になるので、用意できるまでは空でよい |
| `site/data/vote-config.json` | 運用スプレッドシート | 差し替えるか空にする |
| `site/supporters/index.html` | 同じスプレッドシートのURLが直書き | 見落としやすい。必ず確認する |
| リポジトリの Secrets | `SLACK_WEBHOOK_URL` | **千葉版と別のチャンネル**にする。同じにすると通知が混ざる |

## 3. 地域と支援策のデータを作る

| ファイル | 作り方 |
|---|---|
| `site/data/municipalities.json` | 対象市町村の `slug` / `name` / `kana` / `url`（公式トップ）。`bousai` に防災・災害情報ページを入れると、候補の自動収集がそこも見る |
| `data/supports.csv` | ヘッダだけ残して空にし、`python scripts/discover_candidates.py` で候補を出してから人が採否を決める |

まず要るのは **罹災証明・災害ごみ・消毒・住まい** の4つです。ここが埋まれば使えるサイトになります。

## 4. 前のデータを消す

```
data/watch-state.json          （監視の基準。消すと初回は全ページ first_seen になり通知は出ない）
site/data/watch.json  watch-log/  collection.json  press.json  candidates.json
site/data/supports.json  archive-index.json  archive-summary.json
site/img/info-*.png            （インフォグラフィック。文言を直して作り直す）
```

## 5. 文言を置き換える

`config.json` に入らない、ページ本文の地名とリンクです。

- リポジトリ名の直書き（canonical・hreflang・og:url など）は機械置換で済みます
  `grep -rl '<old-repo>' site | xargs sed -i '' 's|<old-repo>|<new-repo>|g'`
- 地名は目視で直します。**国や全国団体へのリンク（罹災証明の考え方、写真の撮り方、悪質商法、
  被災者生活再建支援制度など）はそのまま使えます。** 千葉版では外部リンクの約半分がこれでした
- `scripts/build_collection.py` と `scripts/build_press.py` は、その災害の被害状況・報道を
  直接書いたものです。**設定では吸収できないので、新しい災害の内容に書き直します**
- 日本語ページを変えたら英語ページも同じ変更を入れ、最後に
  `python scripts/check_bilingual.py --update-manifest` を実行します（忘れるとデプロイが止まります）

## 6. 動かし始める

1. ワークフロー4本は最初 Disable にしておく（前のデータのまま動くと誤った通知が出るため）
2. `Daily collect` を手動実行 → 生成物を確認
3. `Watch official pages` を手動実行 → 初回は全ページが基準作成だけで、更新イベントは出ない
4. 4本を Enable にする
5. 翌朝の Slack 通知を確認する

## 覚えておくこと

- `watch.yml` の schedule は3時間おきですが、GitHub 側の都合で**実際は4〜8時間おき**になります。
  表示の文言を「数時間おき」にしてあるのはこのためです
- `archive.yml` は1件あたり45秒前後かかります。160件で2時間半。`--max-minutes` で自前に
  止めているので、ジョブのタイムアウトで途中経過を失うことはありません
- 行政ページは数日で404になります（千葉版の実績で 4日間に8〜11件）。監視の存在理由そのものです
