# 更新を止めるときの手順（アーカイブ化）

このサイトは、発災から1か月ほどで更新を止め、記録として残す想定です。
止めたあとに来た人が「いつの情報か」「いまはどこを見ればよいか」を判断できる状態にしてから止めます。

止める日は決まっていません。決まったら、この順に進めてください。

## 決めておくこと

| 項目 | 決め方 |
|---|---|
| 最終更新日 | 自動処理を止める日。この日付が全ページの帯に出る |
| リンク切れの扱い | 更新を止めると行政ページは数日で404になっていきます（実績: 8/16→8/20 で8件、8/20→8/23 で11件）。直さないなら、その旨を帯に書いてあるので追加の作業は要りません |
| 残すもの | 既定では、サイト全体・更新検知の記録・supports.csv の履歴（git）・Wayback の保存分 |

## 手順

### 1. 記録の要約を作る

```
python scripts/build_archive_summary.py
```

`site/data/archive-summary.json` に、期間・検知件数・市町村別・種類別・日別の集計が出ます。
54市町村の公式ページが何をどう変えたかの記録は、ほかに残っていません。**これがこのサイトで一番残す価値のあるものです。**

### 2. 全ページを Wayback に保存する

```
python scripts/archive_pages.py
```

`archive.yml` が日曜 3:10 JST に回していますが、最後にもう一度、手で流します。
このサイト自身のページ（`site/data/config.json` の `base_url` 以下）も
[Save Page Now](https://web.archive.org/save) で保存しておいてください。

### 3. 帯を出す

`site/data/site-status.json` を書き換えます。**ページ側の書き換えは要りません。**

```json
{
  "archived": true,
  "archived_at": "2026-09-13",
  "note": ""
}
```

全26ページの先頭に、次の帯が出ます（英語版は英文）。

> **このサイトの更新は終了しました。** 内容は2026-09-13時点のものです。公式ページへのリンクは切れていることがあります。いまの情報は市町村・県・国の公式で確認してください。

反映は push 時のデプロイ、または日次ジョブです。

### 4. 自動処理を止める

`.github/workflows/` の4本の `schedule:` をコメントアウトするか、GitHub の Actions 画面で
各ワークフローを Disable にします。

| ワークフロー | 中身 |
|---|---|
| `daily.yml` | 6:00 JST の収集とデプロイ |
| `watch.yml` | 3時間おきの更新検知 |
| `archive.yml` | 日曜の Wayback 保存 |
| `notify.yml` | 7:00 JST の Slack 通知 |

`notify.yml` を最後に止めると、止めたこと自体を Slack に流せます。

### 5. README に追記する

いつ止めたか、何が残っているか、再開する場合はどこを触るかを書きます。

## 止めたあとに残るもの

| もの | 場所 |
|---|---|
| サイト本体 | GitHub Pages（帯つき） |
| 更新検知の記録 | `site/data/watch-log/YYYY-MM.json`（追記専用） |
| 記録の要約 | `site/data/archive-summary.json` |
| 支援策の一覧と、その変化の履歴 | `data/supports.csv` と git の履歴 |
| 行政ページの当時の姿 | Wayback Machine（`site/data/watch.json` の `archive_url`） |

## 再開する場合

`site/data/site-status.json` の `archived` を `false` に戻し、ワークフローを Enable にします。
`data/watch-state.json` は残っているので、更新検知は前回の続きから動きます。
ただし止めていた間の変化は、まとめて1回の検知として出ます。
