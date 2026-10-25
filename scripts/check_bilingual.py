# -*- coding: utf-8 -*-
"""日本語版と英語版のページ構成・更新記録を検査する。"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import site_config

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
EN = SITE / "en"
MANIFEST = EN / ".mirror-manifest.json"
BASE = site_config.base_url()
BASE_PATH = urlsplit(BASE).path

PAIRED_ASSETS = [
    ("site/js/ideas-vote.js", "site/js/ideas-vote-en.js"),
    ("site/data/feature-ideas.json", "site/data/feature-ideas-en.json"),
    ("scripts/build_infographics.py", "scripts/build_infographics_en.py"),
]

EN_INFOGRAPHICS = [
    "info-portal-en.png",
    "info-resident-en.png",
    "info-housing-en.png",
    "info-life-en.png",
    "info-business-en.png",
    "info-municipalities-en.png",
    "info-municipality-en.png",
    "info-prefecture-en.png",
    "info-supporters-en.png",
    "info-ideas-en.png",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_pairs() -> list[tuple[Path, Path]]:
    pages: list[Path] = []
    pages.extend(SITE.glob("*.html"))
    pages.extend((SITE / "resident").glob("*.html"))
    pages.extend((SITE / "supporters").glob("*.html"))
    return [(jp, EN / jp.relative_to(SITE)) for jp in sorted(pages)]


def attrs(text: str, name: str) -> set[str]:
    return set(re.findall(rf'\b{name}="([^"]+)"', text))


def broken_internal_links(path: Path, text: str) -> list[str]:
    broken = []
    for href in attrs(text, "href"):
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or href.startswith(("#", "mailto:", "tel:")):
            continue
        target_path = unquote(parsed.path)
        if not target_path:
            continue
        if target_path.startswith("/"):
            if BASE_PATH not in target_path:
                continue
            target = SITE / target_path.split(BASE_PATH, 1)[1]
        else:
            target = path.parent / target_path
        if target_path.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            broken.append(href)
    return broken


def validate() -> tuple[list[str], list[tuple[Path, Path]]]:
    errors: list[str] = []
    pairs = page_pairs()

    for jp, en in pairs:
        rel = jp.relative_to(SITE).as_posix()
        if not en.exists():
            errors.append(f"英語版がありません: site/en/{rel}")
            continue

        jp_text = jp.read_text(encoding="utf-8")
        en_text = en.read_text(encoding="utf-8")
        if '<html lang="ja">' not in jp_text:
            errors.append(f"日本語ページの lang が ja ではありません: site/{rel}")
        if '<html lang="en">' not in en_text:
            errors.append(f"英語ページの lang が en ではありません: site/en/{rel}")
        if 'property="og:locale" content="en_US"' not in en_text:
            errors.append(f"英語ページの og:locale が en_US ではありません: site/en/{rel}")
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', en_text)
        if not canonical or not canonical.group(1).startswith(BASE + "en/"):
            errors.append(f"英語ページの canonical が /en/ ではありません: site/en/{rel}")
        if "language-switch.js" not in jp_text:
            errors.append(f"日本語ページに言語切替JSがありません: site/{rel}")
        if "language-switch.js" not in en_text:
            errors.append(f"英語ページに言語切替JSがありません: site/en/{rel}")
        if 'hreflang="ja"' not in en_text or 'hreflang="en"' not in en_text:
            errors.append(f"英語ページの hreflang が不足しています: site/en/{rel}")

        jp_ids = {value for value in attrs(jp_text, "id") if not value.startswith("alternate-")}
        en_ids = {value for value in attrs(en_text, "id") if not value.startswith("alternate-")}
        if jp_ids != en_ids:
            missing = sorted(jp_ids - en_ids)
            extra = sorted(en_ids - jp_ids)
            errors.append(
                f"日英で id が不一致: {rel} "
                f"(EN不足={missing or '-'}, ENのみ={extra or '-'})"
            )
        for name in ("data-sit", "data-tags"):
            if attrs(jp_text, name) != attrs(en_text, name):
                errors.append(f"日英で {name} が不一致: {rel}")
        for broken in broken_internal_links(en, en_text):
            errors.append(f"英語ページの内部リンク切れ: site/en/{rel} -> {broken}")

    for jp_rel, en_rel in PAIRED_ASSETS:
        jp = ROOT / jp_rel
        en = ROOT / en_rel
        if not jp.exists():
            errors.append(f"日本語側の対ファイルがありません: {jp_rel}")
        if not en.exists():
            errors.append(f"英語側の対ファイルがありません: {en_rel}")

    for name in EN_INFOGRAPHICS:
        if not (SITE / "img" / name).exists():
            errors.append(f"英語インフォグラフィックがありません: site/img/{name}")

    return errors, pairs


def tracked_files(pairs: list[tuple[Path, Path]]) -> list[Path]:
    files = [path for pair in pairs for path in pair]
    for jp_rel, en_rel in PAIRED_ASSETS:
        files.extend((ROOT / jp_rel, ROOT / en_rel))
    return sorted(set(files))


def manifest_data(pairs: list[tuple[Path, Path]]) -> dict[str, str]:
    return {
        path.relative_to(ROOT).as_posix(): digest(path)
        for path in tracked_files(pairs)
        if path.exists()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update-manifest",
        action="store_true",
        help="日英双方をレビューした後に同期済みハッシュを更新する",
    )
    args = parser.parse_args()

    errors, pairs = validate()
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1

    current = manifest_data(pairs)
    if args.update_manifest:
        EN.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(
            json.dumps(current, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"updated {MANIFEST.relative_to(ROOT)} ({len(current)} files)")
        return 0

    if not MANIFEST.exists():
        print(
            "ERROR: ミラーマニフェストがありません。日英双方をレビュー後、"
            "`python scripts/check_bilingual.py --update-manifest` を実行してください。",
            file=sys.stderr,
        )
        return 1
    recorded = json.loads(MANIFEST.read_text(encoding="utf-8"))
    changed = sorted(
        path for path in set(recorded) | set(current)
        if recorded.get(path) != current.get(path)
    )
    if changed:
        print("ERROR: 日英レビュー後にマニフェスト更新が必要です:", file=sys.stderr)
        for path in changed:
            print(f"  - {path}", file=sys.stderr)
        return 1

    print(f"bilingual check passed ({len(pairs)} page pairs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
