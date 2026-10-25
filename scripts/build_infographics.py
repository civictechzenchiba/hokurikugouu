# -*- coding: utf-8 -*-
"""各公開ページ用の A4 縦インフォグラフィック（PNG）を描画する。"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

import site_config

ROOT = Path(__file__).resolve().parents[1]
# 脚注に出すサイトの URL。scheme を落として短く見せる
SITE_LABEL = site_config.base_url().split("://", 1)[-1]
# 引数にファイル名を渡すと、その分だけ描き直す（例: info-portal.png）。無指定なら全部。
ONLY = set(sys.argv[1:])
OUT = ROOT / "site" / "img"
# 描画に使う日本語フォント。上から順に、最初に見つかったものを使う。
# Windows・macOS・Linux のどこで実行しても描けるようにするため。書体は環境で変わる。
FONT_CANDIDATES = {
    "r": [
        r"C:\Windows\Fonts\YuGothR.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    ],
    "m": [
        r"C:\Windows\Fonts\YuGothM.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W5.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    ],
    "b": [
        r"C:\Windows\Fonts\YuGothB.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    ],
}

# A4 縦 150dpi（210mm x 297mm）
W, H = 1240, 1754
M = 64
ACCENT = (11, 92, 171)
ACCENT_DK = (8, 62, 118)
INK = (26, 26, 26)
MUTED = (92, 92, 92)
LINE = (216, 220, 227)
CARD = (255, 255, 255)
PAGE = (244, 245, 247)
PRESS = (138, 90, 0)
OK = (27, 107, 42)
WARN_BG = (255, 248, 230)
WARN_BD = (234, 217, 168)
BLUE_BG = (231, 241, 251)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size, index=0)


def font_path(kind: str) -> str:
    """kind（r=標準 / m=中太 / b=太字）に対して、この環境にあるフォントを1つ返す。"""
    for path in FONT_CANDIDATES[kind]:
        if Path(path).exists():
            return path
    tried = "\n  ".join(FONT_CANDIDATES[kind])
    raise SystemExit(
        "描画に使えるフォントが見つかりません。いずれかを入れるか、"
        f"FONT_CANDIDATES に足してください:\n  {tried}"
    )


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        line = ""
        for ch in para:
            trial = line + ch
            if draw.textlength(trial, font=fnt) <= max_w:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = ch
        lines.append(line)
    return lines


def round_rect(draw: ImageDraw.ImageDraw, box, fill, outline=None, width=1, radius=18):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_block(draw, xy, text, fnt, fill, max_w, leading=None):
    x, y = xy
    lh = leading or int(fnt.size * 1.45)
    lines = wrap(draw, text, fnt, max_w)
    for i, line in enumerate(lines):
        draw.text((x, y + i * lh), line, font=fnt, fill=fill)
    return y + len(lines) * lh


class Sheet:
    def __init__(
        self,
        kicker: str,
        title: str,
        subtitle: str,
        guide_image: str,
        guide_message: str,
        guide_center: tuple[float, float] = (0.5, 0.5),
    ):
        self.im = Image.new("RGB", (W, H), PAGE)
        self.d = ImageDraw.Draw(self.im)
        self.kicker = kicker
        self.title = title
        self.subtitle = subtitle
        self.guide_image = OUT / guide_image
        self.guide_message = guide_message
        self.guide_center = guide_center
        self._header()
        self.y = 332
        self._footer()

    def f(self, kind: str, size: int) -> ImageFont.FreeTypeFont:
        return font(font_path(kind), size)

    def _header(self):
        self.d.rectangle((0, 0, W, 228), fill=ACCENT)
        self.d.rectangle((0, 228, W, 236), fill=ACCENT_DK)
        guide = Image.open(self.guide_image).convert("RGB")
        guide = ImageOps.fit(guide, (310, 212), method=Image.Resampling.LANCZOS, centering=self.guide_center)
        mask = Image.new("L", guide.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 309, 211), radius=20, fill=255)
        self.im.paste(guide, (866, 12), mask)
        self.d.rounded_rectangle((864, 10, 1178, 226), radius=22, outline=(255, 255, 255), width=4)
        f_k = self.f("m", 28)
        f_t = self.f("b", 52)
        f_s = self.f("r", 24)
        self.d.text((M, 28), self.kicker, font=f_k, fill=(210, 228, 248))
        self.d.text((M, 68), self.title, font=f_t, fill=(255, 255, 255))
        text_block(self.d, (M, 140), self.subtitle, f_s, (230, 240, 250), 760, 33)
        self.d.rectangle((0, 236, W, 318), fill=WARN_BG)
        self.d.rectangle((0, 318, W, 322), fill=WARN_BD)
        self.d.polygon(((1000, 236), (1050, 236), (1025, 250)), fill=WARN_BG)
        f_w = self.f("b", 25)
        self.d.text(
            (M, 258),
            "案内役：「" + self.guide_message + "」",
            font=f_w,
            fill=PRESS,
        )

    def _footer(self):
        y = H - 148
        self.d.rectangle((0, y, W, H), fill=ACCENT_DK)
        f = self.f("r", 22)
        fb = self.f("b", 22)
        self.d.text((M, y + 18), "図の中はタップしても進みません。実際のボタンはページの上にあります。", font=fb, fill=(255, 232, 170))
        self.d.text((M, y + 56), "CTZC（CivicTechZenChiba）有志運営　／　行政の公式発表ではありません", font=f, fill=(230, 240, 250))
        self.d.text((M, y + 92), "申請・対象・期間は市町村・県・国の公式窓口で確認　／　" + SITE_LABEL, font=f, fill=(180, 206, 232))

    def space(self, n=18):
        self.y += n

    def h2(self, text: str):
        f = self.f("b", 30)
        self.d.text((M, self.y), text, font=f, fill=ACCENT)
        self.y += 48

    def note(self, text: str):
        top = self.y
        f = self.f("r", 24)
        lines = wrap(self.d, text, f, W - M * 2 - 36)
        h = 28 + len(lines) * 34 + 16
        round_rect(self.d, (M, top, W - M, top + h), WARN_BG, WARN_BD, 2, 14)
        text_block(self.d, (M + 20, top + 16), text, f, PRESS, W - M * 2 - 40, 34)
        self.y = top + h + 20

    def para(self, text: str):
        f = self.f("r", 26)
        self.y = text_block(self.d, (M, self.y), text, f, INK, W - M * 2, 38) + 12

    def steps(self, items: list[str]):
        f_n = self.f("b", 28)
        f_b = self.f("m", 26)
        f_r = self.f("r", 24)
        for i, item in enumerate(items, 1):
            if "：" in item:
                head, rest = item.split("：", 1)
            elif ":" in item:
                head, rest = item.split(":", 1)
            else:
                head, rest = item, ""
            box_top = self.y
            body = wrap(self.d, rest.strip(), f_r, W - M * 2 - 92)
            h = 70 + (len(body) * 34 if rest else 0)
            round_rect(self.d, (M, box_top, W - M, box_top + h), CARD, LINE, 2, 16)
            self.d.ellipse((M + 18, box_top + 16, M + 62, box_top + 60), fill=ACCENT)
            tw = self.d.textlength(str(i), font=f_n)
            self.d.text((M + 40 - tw / 2, box_top + 20), str(i), font=f_n, fill=(255, 255, 255))
            self.d.text((M + 78, box_top + 20), head.strip(), font=f_b, fill=INK)
            if rest:
                text_block(self.d, (M + 78, box_top + 58), rest.strip(), f_r, MUTED, W - M * 2 - 92, 34)
            self.y = box_top + h + 12

    def grid(self, cells: list[tuple[str, str]], cols=2):
        f_h = self.f("b", 26)
        f_b = self.f("r", 22)
        gap = 16
        inner = W - M * 2
        cw = (inner - gap * (cols - 1)) // cols
        # measure rows
        i = 0
        while i < len(cells):
            row = cells[i : i + cols]
            heights = []
            for title, body in row:
                lines = wrap(self.d, body, f_b, cw - 36)
                heights.append(56 + len(lines) * 32 + 20)
            rh = max(heights)
            for c, (title, body) in enumerate(row):
                x0 = M + c * (cw + gap)
                y0 = self.y
                round_rect(self.d, (x0, y0, x0 + cw, y0 + rh), CARD, LINE, 2, 16)
                self.d.rectangle((x0, y0, x0 + 10, y0 + rh), fill=ACCENT)
                self.d.text((x0 + 24, y0 + 16), title, font=f_h, fill=ACCENT)
                text_block(self.d, (x0 + 24, y0 + 52), body, f_b, INK, cw - 40, 32)
            self.y += rh + gap
            i += cols

    def compare(self, left_title: str, left: list[str], right_title: str, right: list[str]):
        gap = 16
        cw = (W - M * 2 - gap) // 2
        f_h = self.f("b", 26)
        f_b = self.f("r", 22)
        def col_h(items):
            n = 0
            for t in items:
                n += len(wrap(self.d, "・" + t, f_b, cw - 40))
            return 70 + n * 32 + 16
        rh = max(col_h(left), col_h(right))
        for x0, title, items, color in (
            (M, left_title, left, ACCENT),
            (M + cw + gap, right_title, right, OK),
        ):
            round_rect(self.d, (x0, self.y, x0 + cw, self.y + rh), CARD, LINE, 2, 16)
            self.d.rectangle((x0, self.y, x0 + cw, self.y + 52), fill=color)
            self.d.text((x0 + 18, self.y + 12), title, font=f_h, fill=(255, 255, 255))
            yy = self.y + 64
            for t in items:
                yy = text_block(self.d, (x0 + 18, yy), "・" + t, f_b, INK, cw - 36, 32)
        self.y += rh + 18

    def pills(self, labels: list[str]):
        f = self.f("m", 22)
        x, y = M, self.y
        for lab in labels:
            tw = self.d.textlength(lab, font=f)
            pw, ph = tw + 28, 44
            if x + pw > W - M:
                x = M
                y += 54
            round_rect(self.d, (x, y, x + pw, y + ph), BLUE_BG, ACCENT, 2, 22)
            self.d.text((x + 14, y + 8), lab, font=f, fill=ACCENT)
            x += pw + 10
        self.y = y + 60

    def save(self, name: str):
        if ONLY and name not in ONLY:
            return
        path = OUT / name
        self.im.save(path, "PNG", optimize=True)
        print("wrote", path)


def build_all() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    s = Sheet(
        "令和8年8月石川・富山・福井豪雨　復興支援ポータル",
        "このサイトの入り口",
        "被災された方が、市町村と困りごとから必要な公式情報にたどりつくためのページです。",
        "anime-guide-map.jpg",
        "ページの上から、市町村と困りごとを順に選んでください。",
        (0.5, 0.55),
    )
    s.note("有志運営です。行政の公式発表ではありません。申請は県・市町村の公式窓口へ。")
    s.h2("三つの手順（ボタンはページの上）")
    s.steps(
        [
            "お住まいの市町村を選ぶ：公式のお知らせ・支援策・被害の経過が市町村ごとに出ます。選択はこの端末に残ります。",
            "いま困っていることを選ぶ：床上浸水・車の水没・賃貸・持病など、状況ごとの案内に直接進みます。",
            "いますぐの3つ：片付ける前に写真、領収書を全部残す、直す前に市町村へ確認。",
        ]
    )
    s.h2("支援・協働する方へ")
    s.grid(
        [
            ("参加する", "公開情報の収集と拡散、Slack、今後の案への投票。救命や現地マッチングは担いません。"),
            ("入口はページの下", "被災された方の導線を先に置いているため、支援者向けの入口はページの下にあります。"),
        ]
    )
    s.h2("使うときの約束")
    s.steps(
        [
            "公式が一次情報：このサイトは見出しとリンクです。本文の全文転載はしません。",
            "数値は速報：人的被害や警報の対象は変わります。最新は公式で確認。",
            "申請は窓口へ：対象・期間・金額は各実施機関の判断です。",
        ]
    )
    s.save("info-portal.png")

    s = Sheet(
        "石川・富山・福井にお住まいの方へ",
        "自分の状況から探す",
        "住まい・移動・事業者の3つの扉と、市町村検索から入れます。",
        "anime-guide-map.jpg",
        "住まい・移動・事業者から、いま必要な案内を選びましょう。",
        (0.5, 0.58),
    )
    s.note("最新の避難・支援の有無は、必ずお住まいの市町村公式で確認してください。")
    s.h2("3つの案内")
    s.grid(
        [
            ("住まいが被災した方", "写真を残す。先に契約しない。罹災証明と被災証明の違い。便乗商法に注意。"),
            ("移動と生活", "電車・道路・電気ガス水道・病院・買い物。運行や店の開閉は各公式へ。"),
            ("被災した事業者の方", "店舗・工場の記録と相談窓口。融資・保証は指定や公募があってから。"),
            ("市町村から探す", "51市町村。県ポータルの避難・避難所。公式の罹災・支援リンク。"),
        ]
    )
    s.h2("いま確認してほしい公式")
    s.pills(["各県の防災ポータル", "県の大雨対応ページ", "気象庁の警報", "市町村公式"])
    s.para("このページでは、市町村名で検索して公式の罹災証明・支援案内へ進めます。")
    s.save("info-resident.png")

    s = Sheet(
        "住まいが被災した方へ",
        "記録してから、公式へ",
        "片付けの前に写真。契約の前に市町村の案内。金額はこのサイトに書きません。",
        "anime-guide-map.jpg",
        "片付ける前に写真を。契約前に市町村の案内を確認してください。",
        (0.22, 0.57),
    )
    s.note("先に修理契約すると、後から公費の補助が受けられない場合があります。")
    s.h2("いますぐ")
    s.steps(
        [
            "写真を撮る：四方向の外観。浸水の深さと傷みは、全体と寄りの両方。サイトには送らない。",
            "市町村の案内を見る：罹災証明の受付開始を公式で確認してから動く。",
            "保険・共済へ連絡：提出先ごとに証明書が複数枚必要になることがあります。",
            "ごみと衛生は公式の手順：泥の扱い、仮置き場、収集日は市町村。",
        ]
    )
    s.h2("証明のちがい（呼び方は市町村で違う）")
    s.compare(
        "罹災証明書",
        ["生活の拠点となる住まい", "支援金・応急修理・税の減免などに使うことが多い", "市町村が被害の程度を調査して発行することが多い"],
        "被災証明書など",
        ["事業所・車庫など生活の拠点以外", "被害があったことの証明。保険や取引先へ", "届出中心の市町村もある"],
    )
    s.save("info-housing.png")

    s = Sheet(
        "移動と生活",
        "運行・ライフラインは公式で",
        "お盆明けの移動、停電・断水、病院や買い物。このページに区間名や店名の一覧は載せません。",
        "anime-guide-map.jpg",
        "移動やライフラインは、出発前に最新の公式情報を見ましょう。",
        (0.5, 0.58),
    )
    s.note("通行できた道でも、その後に規制が出ることがあります。現地の誘導に従ってください。")
    s.h2("確認する場所")
    s.grid(
        [
            ("電車・バス", "JR西日本の運行情報、IRいしかわ・のと鉄道・あいの風・富山地鉄・ハピライン・えちぜん・福鉄、各バス会社の公式。"),
            ("車・道路", "通れた道マップ、JARTIC、NEXCO中日本、県の道路、県警。"),
            ("電気・水道・ガス", "北陸電力送配電の停電情報、金沢エナジー・日本海ガス・福井都市ガス、市町村の水道。"),
            ("医療・薬局", "各県の救急医療情報。独自の開閉リストは作りません。"),
            ("スーパー・コンビニ", "各社の店舗検索とお知らせが一次情報。SNSの伝聞は載せません。"),
            ("市町村公式", "水道・ごみ・避難所・粉ミルク等の配布は、発表があれば市町村ページで。"),
        ]
    )
    s.save("info-life.png")

    s = Sheet(
        "被災した事業者の方へ",
        "店舗・工場も、まず記録",
        "飲食店、小売、工場、事務所。個人事業も法人も。融資は借り入れです。金額は書きません。",
        "anime-guide-map.jpg",
        "建物・設備・在庫を撮影し、契約前に相談窓口を確認しましょう。",
        (0.78, 0.57),
    )
    s.note("自宅兼店舗は、住まいのページも見てください。住居と店舗で手続が分かれることがあります。")
    s.h2("いまの流れ")
    s.steps(
        [
            "安全と写真：漏電・ガスに注意。建物・設備・在庫の写真を残す。",
            "保険と市町村：事業用は被災証明になることが多い。先に契約しない。",
            "飲食は保健所：浸水した調理場の再開は、清掃・消毒と食品の廃棄判断が必要。",
            "相談窓口：中部経済産業局（富山・石川）、近畿経済産業局（福井）、公庫、信用保証協会、商工会・会議所、よろず支援拠点。",
        ]
    )
    s.h2("これからあり得ること（指定・公募があってから）")
    s.grid(
        [
            ("資金繰り", "災害復旧貸付、県制度融資、セーフティネット保証4号。認定と審査あり。"),
            ("税・雇用・補助金", "申告期限の延長、雇用の相談。グループ補助金などは公募を待って公式を見る。"),
        ]
    )
    s.save("info-business.png")

    s = Sheet(
        "市町村から探す",
        "51市町村の入口",
        "県防災ポータルの避難・避難所スナップショットと、公式の罹災・支援リンクへつなぎます。",
        "anime-guide-map.jpg",
        "お住まいの市町村を選び、公式の支援案内へ進んでください。",
        (0.5, 0.54),
    )
    s.note("初日対象はレベル5の市町と流山市。他市町村は枠を先に出し、公式リンクから確認します。")
    s.h2("ページの使い方")
    s.steps(
        [
            "市町村名を選ぶ：このサイトの市町村ページが開きます。",
            "公式へ飛ぶ：トップページ、防災ページ、罹災証明・支援案内。",
            "バッジを見る：避難所開設、災害救助法の適用などは速報です。",
            "空欄でも公式優先：中身が薄い市町村は、市町村公式が一次情報です。",
        ]
    )
    s.h2("市町村ページに載っているもの")
    s.pills(["いまの避難・救助法", "被害の報道リンク", "支援策", "行政の記録", "生活再建の段取り"])
    s.save("info-municipalities.png")

    s = Sheet(
        "各市町村ページ",
        "このページの見方",
        "いま → 報道 → 支援策 → 行政の記録 → 生活再建。見出しとリンクのみです。",
        "anime-guide-map.jpg",
        "まず上の公式ボタンを確認し、必要な支援策へ進んでください。",
        (0.5, 0.58),
    )
    s.note("報道は全文転載しません。Yahoo!ニュース等は出典へ。数値は速報です。")
    s.h2("上から読む")
    s.grid(
        [
            ("いま", "県ポータルの避難情報・避難所。レベル5対象だったかのメモ。"),
            ("被害の報道", "市町村名が出る記事、県全体のテレビ・通信社、Yahoo!検索。"),
            ("支援策", "公式の罹災・支援リンク。国と県の案内。救助法の適用状況。"),
            ("行政などの記録", "県ポータルや消防庁など。報道と分けて残しています。"),
            ("生活再建の段取り", "写真 → 調査 → 証明 → 応急修理か応急仮設。開始日は公式。"),
            ("住まい／事業者", "自宅被害と店舗・工場では窓口が違います。該当する案内へ。"),
        ]
    )
    s.save("info-municipality.png")

    s = Sheet(
        "県・国の支援",
        "公式への案内",
        "石川・富山・福井と国の発表、事業者向け相談。本文は転載せず、リンク先で確認します。",
        "anime-guide-map.jpg",
        "制度の対象や受付期間は、県・国・市町村の公式で確認しましょう。",
        (0.78, 0.57),
    )
    s.note("災害救助法は応急の住まい・生活が中心です。店舗の復旧は別制度になることが多いです。")
    s.h2("まず開く公式")
    s.grid(
        [
            ("石川・富山・福井", "防災ポータル。令和8年8月27日からの大雨の対応。救助法の発表。被害情報PDF。"),
            ("国", "内閣府の被災者支援。消防庁の災害情報。気象庁の警報。川の防災情報。"),
            ("事業者", "中部・近畿経済産業局の特別相談。中小企業庁。県の中小企業融資制度。"),
            ("このサイトのログ", "県・国の見出しを時系列で残します。上書きせず履歴にします。"),
        ]
    )
    s.para("市町村ごとの申請案内は「市町村から探す」へ。住まい・事業者の段取りはそれぞれのページへ。")
    s.save("info-prefecture.png")

    s = Sheet(
        "支援・協働する方へ",
        "情報を集め、届ける",
        "CTZC有志の活動。行政・報道の公開情報を集め、県民へ分かりやすく渡すことから着手します。",
        "anime-guide-team.jpg",
        "公開情報を整理し、必要な方へ分かりやすく届けていきます。",
        (0.52, 0.5),
    )
    s.note("救命、現地ボランティアのマッチング、罹災調査そのものは担いません。")
    s.h2("いまやっていること")
    s.steps(
        [
            "公式情報の収集：許可した出典の見出しとURLを、市町村ページに残す。",
            "県民向けに整理：住まい・移動・事業者・市町村の入口を分ける。",
            "Slackで協働：アイデアを流さず、公開サイトと投票に載せる。",
            "今後の案に投票：必要だと思う情報・機能・行動に票を入れる。",
        ]
    )
    s.h2("現地活動を探すとき")
    s.para("県・市町村社協・赤十字などの公式募集を確認。募集対象、事前登録、保険を確認してから参加します。")
    s.pills(["大網白里市災害VC", "石川・富山・福井社協", "赤十字防災ボランティア", "ちばボランティアナビ"])
    s.h2("CTZCへの参加")
    s.pills(["Slack", "今後の案に投票", "CTZCウェブサイト", "Facebookグループ"])
    s.save("info-supporters.png")

    s = Sheet(
        "今後の案への投票",
        "何があるとよいか、票で示す",
        "結果は今後の機能や案内の参考です。個人情報は取りません。申請や被害の申告ではありません。",
        "anime-guide-team.jpg",
        "必要だと思う案を選んでください。投票は今後の活動の参考にします。",
        (0.38, 0.5),
    )
    s.note("1つの案につき、このブラウザで1票（取り消し可）。結果は参考値です。")
    s.h2("投票のルール")
    s.steps(
        [
            "ログイン不要：県民・支援者・一般の方も投票できます。氏名は取りません。",
            "種類で見る：情報・機能・行動。票の多い順にも並べ替えできます。",
            "合算：運用シートの投票用スクリプトが動くと、全員の票が件数に出ます。",
            "対象外：救命、現地マッチング、罹災調査そのものは票の対象にしません。",
        ]
    )
    s.para("別の案は Slack または GitHub の Issue へ。投票は「ほしいもの」の参考であり、実施を約束するものではありません。")
    s.save("info-ideas.png")


if __name__ == "__main__":
    build_all()
