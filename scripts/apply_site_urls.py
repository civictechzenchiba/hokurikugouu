# -*- coding: utf-8 -*-
"""site/data/config.json の repo と base_url を、ページと文書のべた書きに行き渡らせる。

HTML の canonical・og:url・hreflang・GitHub へのリンク、README や docs の公開 URL は
静的に書いてあるので、config.json を書き換えただけでは変わらない。
このスクリプトが、いま書かれている古い値を見つけて config.json の値に置き換える。

古い値は site/index.html から読む（canonical の href がサイトの URL、
最初の https://github.com/<owner>/<repo> が repo）。別の値から置き換えたいときは
--from-base / --from-repo で指定する。

使い方:
    python3 scripts/apply_site_urls.py --dry-run   # 置き換える箇所を数えるだけ
    python3 scripts/apply_site_urls.py             # 置き換える

sitemap.xml と robots.txt はここでは触らない（build_sitemap.py が config から作る）。
インフォグラフィック（site/img/info-*.png）の脚注も build_infographics*.py で描き直す。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import site_config  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

# 置き換えの対象。生成物（site/data・sitemap・robots）と docs/output（過去の要件書）は含めない
TARGETS = [
    SITE.glob("*.html"),
    (SITE / "resident").glob("*.html"),
    (SITE / "supporters").glob("*.html"),
    (SITE / "en").rglob("*.html"),
    (SITE / "js").glob("*.js"),
    [ROOT / "README.md"],
    (ROOT / "docs").glob("*.md"),
]


def detect_current() -> tuple[str, str]:
    """site/index.html に書いてある、いまのサイト URL と repo。"""
    text = (SITE / "index.html").read_text(encoding="utf-8")
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
    repo = re.search(r"https://github\.com/([\w.-]+/[\w.-]+)", text)
    if not canonical or not repo:
        raise SystemExit("site/index.html から canonical か GitHub のリンクが見つからない")
    return canonical.group(1).rstrip("/") + "/", repo.group(1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-base", help="置き換え前のサイト URL（既定: site/index.html の canonical）")
    ap.add_argument("--from-repo", help="置き換え前の owner/repo（既定: site/index.html の GitHub リンク）")
    ap.add_argument("--dry-run", action="store_true", help="書き換えずに件数だけ出す")
    args = ap.parse_args()

    cur_base, cur_repo = detect_current()
    old_base = (args.from_base or cur_base).rstrip("/") + "/"
    old_repo = args.from_repo or cur_repo
    new_base = site_config.base_url()
    new_repo = site_config.repo()

    # scheme を落とした形（インフォグラフィックの脚注や本文に出る短い書き方）も拾う
    pairs = [
        (old_base, new_base),
        (old_base.split("://", 1)[-1], new_base.split("://", 1)[-1]),
        (f"https://github.com/{old_repo}", f"https://github.com/{new_repo}"),
    ]
    pairs = [(a, b) for a, b in pairs if a != b]
    if not pairs:
        print(f"config.json と site/index.html が一致している（{new_base} / {new_repo}）。置き換えなし")
        return 0

    total = 0
    for group in TARGETS:
        for path in sorted(group):
            text = path.read_text(encoding="utf-8")
            new_text = text
            for a, b in pairs:
                new_text = new_text.replace(a, b)
            n = sum(text.count(a) for a, _ in pairs)
            if n == 0:
                continue
            total += n
            print(f"{'(dry) ' if args.dry_run else ''}{path.relative_to(ROOT)}: {n}")
            if not args.dry_run:
                path.write_text(new_text, encoding="utf-8")
    print(f"{old_base} → {new_base} / {old_repo} → {new_repo}: {total} 箇所")
    if not args.dry_run and total:
        print("次に python3 scripts/build_sitemap.py と build_infographics.py / build_infographics_en.py を流す")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
