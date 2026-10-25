# -*- coding: utf-8 -*-
"""Generate ten English A4 portrait infographics for the public site."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

import site_config

ROOT = Path(__file__).resolve().parents[1]
# 脚注に出すサイトの URL。scheme を落として短く見せる
SITE_LABEL = site_config.base_url().split("://", 1)[-1]
# 引数にファイル名を渡すと、その分だけ描き直す（例: info-portal-en.png）。無指定なら全部。
ONLY = set(sys.argv[1:])
OUT = ROOT / "site" / "img"
# 描画に使う欧文フォント。上から順に、最初に見つかったものを使う。
# Windows・macOS・Linux のどこで実行しても描けるようにするため。書体は環境で変わる。
FONT_CANDIDATES = {
    "r": [
        r"C:\Windows\Fonts\segoeui.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "m": [
        r"C:\Windows\Fonts\seguisb.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "b": [
        r"C:\Windows\Fonts\segoeuib.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}

# A4 portrait at 150 dpi (210 mm x 297 mm)
W, H = 1240, 1754
M = 64
ACCENT = (11, 92, 171)
ACCENT_DK = (8, 62, 118)
INK = (26, 26, 26)
MUTED = (82, 82, 82)
LINE = (216, 220, 227)
CARD = (255, 255, 255)
PAGE = (244, 245, 247)
PRESS = (138, 90, 0)
OK = (27, 107, 42)
WARN_BG = (255, 248, 230)
WARN_BD = (234, 217, 168)
BLUE_BG = (231, 241, 251)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


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


def wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    fnt: ImageFont.FreeTypeFont,
    max_w: int,
) -> list[str]:
    """Wrap English at spaces, with a character fallback for long tokens."""
    lines: list[str] = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        current = ""
        for word in para.split():
            trial = word if not current else f"{current} {word}"
            if draw.textlength(trial, font=fnt) <= max_w:
                current = trial
                continue
            if current:
                lines.append(current)
                current = ""
            if draw.textlength(word, font=fnt) <= max_w:
                current = word
                continue
            part = ""
            for ch in word:
                if part and draw.textlength(part + ch, font=fnt) > max_w:
                    lines.append(part)
                    part = ch
                else:
                    part += ch
            current = part
        lines.append(current)
    return lines


def round_rect(draw, box, fill, outline=None, width=1, radius=18):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_block(draw, xy, text, fnt, fill, max_w, leading=None):
    x, y = xy
    line_h = leading or int(fnt.size * 1.35)
    lines = wrap(draw, text, fnt, max_w)
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_h), line, font=fnt, fill=fill)
    return y + len(lines) * line_h


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
        guide = ImageOps.fit(
            guide,
            (310, 212),
            method=Image.Resampling.LANCZOS,
            centering=self.guide_center,
        )
        mask = Image.new("L", guide.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 309, 211), radius=20, fill=255)
        self.im.paste(guide, (866, 12), mask)
        self.d.rounded_rectangle(
            (864, 10, 1178, 226), radius=22, outline=(255, 255, 255), width=4
        )
        self.d.text((M, 25), self.kicker, font=self.f("m", 25), fill=(210, 228, 248))
        title_font = self.f("b", 49)
        while self.d.textlength(self.title, font=title_font) > 760 and title_font.size > 35:
            title_font = self.f("b", title_font.size - 1)
        self.d.text((M, 62), self.title, font=title_font, fill=(255, 255, 255))
        text_block(
            self.d,
            (M, 126),
            self.subtitle,
            self.f("r", 23),
            (230, 240, 250),
            760,
            30,
        )
        self.d.rectangle((0, 236, W, 318), fill=WARN_BG)
        self.d.rectangle((0, 318, W, 322), fill=WARN_BD)
        self.d.text(
            (M, 253),
            "Guide: “" + self.guide_message + "”",
            font=self.f("b", 23),
            fill=PRESS,
        )

    def _footer(self):
        y = H - 148
        self.d.rectangle((0, y, W, H), fill=ACCENT_DK)
        self.d.text(
            (M, y + 16),
            "This graphic is not clickable. The actual buttons are above it on the page.",
            font=self.f("b", 21),
            fill=(255, 232, 170),
        )
        self.d.text(
            (M, y + 54),
            "Run by CTZC (CivicTechZenChiba) volunteers — not an official government source",
            font=self.f("r", 20),
            fill=(230, 240, 250),
        )
        self.d.text(
            (M, y + 91),
            "Confirm eligibility, deadlines and applications with official municipal, prefectural or national offices",
            font=self.f("r", 19),
            fill=(180, 206, 232),
        )
        self.d.text(
            (916, y + 118),
            SITE_LABEL,
            font=self.f("r", 15),
            fill=(180, 206, 232),
        )

    def h2(self, text: str):
        self.d.text((M, self.y), text, font=self.f("b", 29), fill=ACCENT)
        self.y += 46

    def note(self, text: str):
        fnt = self.f("r", 23)
        lines = wrap(self.d, text, fnt, W - M * 2 - 40)
        height = 26 + len(lines) * 31 + 14
        round_rect(
            self.d,
            (M, self.y, W - M, self.y + height),
            WARN_BG,
            WARN_BD,
            2,
            14,
        )
        text_block(
            self.d,
            (M + 20, self.y + 14),
            text,
            fnt,
            PRESS,
            W - M * 2 - 40,
            31,
        )
        self.y += height + 18

    def para(self, text: str):
        self.y = text_block(
            self.d, (M, self.y), text, self.f("r", 24), INK, W - M * 2, 34
        ) + 10

    def steps(self, items: list[str]):
        for i, item in enumerate(items, 1):
            head, sep, rest = item.partition(":")
            f_head, f_body = self.f("m", 24), self.f("r", 22)
            head_lines = wrap(self.d, head.strip(), f_head, W - M * 2 - 100)
            body_lines = wrap(self.d, rest.strip(), f_body, W - M * 2 - 100) if sep else []
            head_h = max(38, len(head_lines) * 30)
            height = 28 + head_h + (len(body_lines) * 29 + 7 if body_lines else 0) + 14
            top = self.y
            round_rect(self.d, (M, top, W - M, top + height), CARD, LINE, 2, 16)
            self.d.ellipse((M + 18, top + 16, M + 62, top + 60), fill=ACCENT)
            number = str(i)
            tw = self.d.textlength(number, font=self.f("b", 27))
            self.d.text(
                (M + 40 - tw / 2, top + 20),
                number,
                font=self.f("b", 27),
                fill=(255, 255, 255),
            )
            text_block(
                self.d, (M + 78, top + 16), head.strip(), f_head, INK, W - M * 2 - 100, 30
            )
            if body_lines:
                text_block(
                    self.d,
                    (M + 78, top + 20 + head_h),
                    rest.strip(),
                    f_body,
                    MUTED,
                    W - M * 2 - 100,
                    29,
                )
            self.y = top + height + 11

    def grid(self, cells: list[tuple[str, str]], cols=2):
        f_head, f_body = self.f("b", 24), self.f("r", 21)
        gap = 16
        inner = W - M * 2
        cell_w = (inner - gap * (cols - 1)) // cols
        for start in range(0, len(cells), cols):
            row = cells[start : start + cols]
            heights = []
            for title, body in row:
                title_lines = wrap(self.d, title, f_head, cell_w - 40)
                body_lines = wrap(self.d, body, f_body, cell_w - 40)
                heights.append(24 + len(title_lines) * 30 + 8 + len(body_lines) * 28 + 18)
            row_h = max(heights)
            for col, (title, body) in enumerate(row):
                x0 = M + col * (cell_w + gap)
                round_rect(
                    self.d, (x0, self.y, x0 + cell_w, self.y + row_h), CARD, LINE, 2, 16
                )
                self.d.rectangle((x0, self.y, x0 + 10, self.y + row_h), fill=ACCENT)
                title_lines = wrap(self.d, title, f_head, cell_w - 40)
                text_block(
                    self.d, (x0 + 24, self.y + 14), title, f_head, ACCENT, cell_w - 40, 30
                )
                text_block(
                    self.d,
                    (x0 + 24, self.y + 20 + len(title_lines) * 30),
                    body,
                    f_body,
                    INK,
                    cell_w - 40,
                    28,
                )
            self.y += row_h + gap

    def compare(
        self, left_title: str, left: list[str], right_title: str, right: list[str]
    ):
        gap = 16
        cell_w = (W - M * 2 - gap) // 2
        f_head, f_body = self.f("b", 22), self.f("r", 20)

        def column_height(title, items):
            title_n = len(wrap(self.d, title, f_head, cell_w - 36))
            item_n = sum(len(wrap(self.d, "• " + t, f_body, cell_w - 36)) for t in items)
            return 22 + title_n * 28 + 14 + item_n * 27 + 18

        row_h = max(column_height(left_title, left), column_height(right_title, right))
        for x0, title, items, color in (
            (M, left_title, left, ACCENT),
            (M + cell_w + gap, right_title, right, OK),
        ):
            round_rect(
                self.d, (x0, self.y, x0 + cell_w, self.y + row_h), CARD, LINE, 2, 16
            )
            title_lines = wrap(self.d, title, f_head, cell_w - 36)
            title_h = 18 + len(title_lines) * 28 + 10
            self.d.rectangle((x0, self.y, x0 + cell_w, self.y + title_h), fill=color)
            text_block(
                self.d, (x0 + 18, self.y + 10), title, f_head, (255, 255, 255), cell_w - 36, 28
            )
            yy = self.y + title_h + 12
            for item in items:
                yy = text_block(
                    self.d, (x0 + 18, yy), "• " + item, f_body, INK, cell_w - 36, 27
                )
        self.y += row_h + 17

    def pills(self, labels: list[str]):
        fnt = self.f("m", 20)
        x, y = M, self.y
        for label in labels:
            pill_w = self.d.textlength(label, font=fnt) + 28
            if x + pill_w > W - M:
                x, y = M, y + 50
            round_rect(self.d, (x, y, x + pill_w, y + 40), BLUE_BG, ACCENT, 2, 20)
            self.d.text((x + 14, y + 6), label, font=fnt, fill=ACCENT)
            x += pill_w + 10
        self.y = y + 54

    def save(self, name: str):
        if ONLY and name not in ONLY:
            return
        if self.y > H - 160:
            raise RuntimeError(f"Content overflow in {name}: y={self.y}")
        path = OUT / name
        self.im.save(path, "PNG", optimize=True, dpi=(150, 150))
        print(f"wrote {path} (content bottom: {self.y})")


def build_all() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    s = Sheet(
        "August 2026 Ishikawa, Toyama & Fukui Heavy Rain Portal",
        "Start Here",
        "A page that helps affected residents reach official information, starting from their municipality and their situation.",
        "anime-guide-map.jpg",
        "Work down the page: choose your municipality, then your situation.",
        (0.5, 0.55),
    )
    s.note("This site is volunteer-run, not an official government source. Apply through official prefectural or municipal offices.")
    s.h2("Three steps (buttons are above this graphic)")
    s.steps([
        "Choose your municipality: official notices, support programs and damage timelines are shown per municipality. Your choice stays on your device.",
        "Choose what you are dealing with: flooding above floor level, a flooded car, rented housing, medication and more lead straight to that guidance.",
        "Three things to do right now: photos before you clean up, keep every receipt, check with your municipality before repairs.",
    ])
    s.h2("For supporters and collaborators")
    s.grid([
        ("Take part", "Collecting and sharing public information, Slack, and voting on future ideas. We do not handle rescue or on-site matching."),
        ("Entrance is lower down", "The route for affected residents comes first, so the supporter entrance sits at the bottom of the page."),
    ])
    s.h2("Three rules for using this site")
    s.steps([
        "Official sources come first: This site provides headlines and links. It does not reproduce full articles.",
        "Figures are preliminary: Casualty figures and areas covered by warnings may change. Check the latest official information.",
        "Apply at the responsible office: Eligibility, deadlines and amounts are decided by each administering authority.",
    ])
    s.save("info-portal-en.png")

    s = Sheet(
        "For Ishikawa, Toyama and Fukui Residents",
        "Find Help for Your Situation",
        "Enter through one of three routes—housing, transport and daily life, or business—or search by municipality.",
        "anime-guide-map.jpg",
        "Choose housing, transport and daily life, or business guidance.",
        (0.5, 0.58),
    )
    s.note("Always check your municipality's official website for the latest evacuation information and available support.")
    s.h2("Three guidance routes")
    s.grid([
        ("If Your Home Was Damaged", "Take photos. Do not sign a contract first. Know the difference between damage certificates. Beware of disaster-related scams."),
        ("Transport & Daily Life", "Trains, roads, electricity, gas, water, hospitals and shopping. Check each operator's official service or opening information."),
        ("If Your Business Was Damaged", "Document shops and factories and find consultation desks. Loans and guarantees require an official designation or application call."),
        ("Search by Municipality", "All 51 municipalities. Prefectural evacuation and shelter information, plus official damage-certificate and support links."),
    ])
    s.h2("Official sources to check now")
    s.pills(["Prefectural disaster portals", "Prefecture: Heavy Rain Response", "JMA Warnings", "Your Municipality"])
    s.para("Search by municipality name on this page, then follow the official links for damage certificates and support.")
    s.save("info-resident-en.png")

    s = Sheet(
        "If Your Home Was Damaged",
        "Document First, Then Check Official Guidance",
        "Take photos before cleanup. Check municipal guidance before signing a contract. This site does not list benefit amounts.",
        "anime-guide-map.jpg",
        "Take photos before cleanup and check municipal guidance before contracting.",
        (0.22, 0.57),
    )
    s.note("If you sign a repair contract first, you may become ineligible for publicly funded assistance.")
    s.h2("Do this now")
    s.steps([
        "Take photos: Photograph the exterior from four directions. Capture flood depth and damage in both wide and close-up shots. Do not send photos to this site.",
        "Check municipal guidance: Wait for the municipality's official announcement that damage-certificate applications are open.",
        "Contact your insurer or mutual aid provider: You may need several certificate copies for different recipients.",
        "Follow official waste and sanitation procedures: Your municipality sets rules for mud, temporary collection sites and pickup dates.",
    ])
    s.h2("Certificate types (names vary by municipality)")
    s.compare(
        "Disaster Damage Certificate (Risai Shomeisho)",
        ["For your primary residence", "Often used for support payments, emergency repairs and tax reductions", "Usually issued after the municipality assesses the severity of damage"],
        "Other Damage Certificate (Hisai Shomeisho, etc.)",
        ["For workplaces, garages and property other than your primary residence", "Confirms that damage occurred; may be used for insurers or business partners", "Some municipalities mainly use a self-report process"],
    )
    s.save("info-housing-en.png")

    s = Sheet(
        "Transport & Daily Life",
        "Check Official Service Updates",
        "Post-holiday travel, outages, water cuts, hospitals and shopping. This page does not maintain lists of routes or stores.",
        "anime-guide-map.jpg",
        "Check the latest official transport and utility updates before leaving.",
        (0.5, 0.58),
    )
    s.note("A road that was passable may later be restricted. Follow directions at the scene.")
    s.h2("Where to check")
    s.grid([
        ("Trains & Buses", "Official service information from JR West, IR Ishikawa, Noto, Ainokaze, Toyama Chiho, Hapi-Line, Echizen and Fukui railways, and each bus operator."),
        ("Cars & Roads", "Passable-road maps, JARTIC, NEXCO Central, prefectural road information and prefectural police."),
        ("Electricity, Water & Gas", "Hokuriku Electric Power T&D outage information; Kanazawa Energy, Nihonkai Gas and Fukui City Gas; and municipal water services."),
        ("Medical Care & Pharmacies", "Prefectural emergency medical networks. We do not create an independent open/closed list."),
        ("Supermarkets & Convenience Stores", "Company store locators and notices are primary sources. We do not post social-media hearsay."),
        ("Municipal Information", "If announced, municipalities post water, waste, shelter and infant-formula distribution information."),
    ])
    s.save("info-life-en.png")

    s = Sheet(
        "If Your Business Was Damaged",
        "Document Shops and Factories First",
        "For restaurants, retailers, factories, offices, sole traders and companies. Loans must be repaid. Amounts are not listed here.",
        "anime-guide-map.jpg",
        "Photograph buildings, equipment and stock; check consultation desks before contracting.",
        (0.78, 0.57),
    )
    s.note("For a home-based business, also see the housing page. Home and business procedures may be separate.")
    s.h2("What to do now")
    s.steps([
        "Safety and photos: Beware of electrical leakage and gas. Photograph buildings, equipment and inventory.",
        "Insurance and municipality: Business property often uses a non-residential damage certificate. Do not sign a contract first.",
        "Restaurants—contact the public health center: Reopening a flooded kitchen requires cleaning, disinfection and decisions on discarding food.",
        "Consultation desks: Chubu METI (Toyama, Ishikawa), Kansai METI (Fukui), Japan Finance Corporation, the Credit Guarantee Association, chambers and societies of commerce, and Yorozu Support Centers.",
    ])
    s.h2("Possible later support (only after official designation or calls)")
    s.grid([
        ("Financing", "Disaster recovery loans, prefectural loans and Safety Net Guarantee No. 4. Certification and screening apply."),
        ("Tax, Employment & Grants", "Possible filing extensions and employment consultation. Wait for official calls before relying on group subsidies or similar grants."),
    ])
    s.save("info-business-en.png")

    s = Sheet(
        "Search by Municipality",
        "Gateway to All 54 Municipalities",
        "Connects prefectural evacuation and shelter snapshots with official damage-certificate and support links.",
        "anime-guide-map.jpg",
        "Choose your municipality, then continue to its official support information.",
        (0.5, 0.54),
    )
    s.note("The initial focus is municipalities formerly under Level 5 alerts, plus Nagareyama. Others are listed early; use their official links.")
    s.h2("How to use the page")
    s.steps([
        "Choose a municipality: Its page on this site will open.",
        "Continue to official sources: Open its home page, disaster-prevention page, and damage-certificate or support guidance.",
        "Read the badges: Open shelters and Disaster Relief Act coverage are preliminary information.",
        "Official sources still come first: If a municipal page here has little content, rely on that municipality's official website.",
    ])
    s.h2("What each municipal page includes")
    s.pills(["Current Evacuation & Relief Act", "Damage News Links", "Support Measures", "Government Records", "Recovery Steps"])
    s.save("info-municipalities-en.png")

    s = Sheet(
        "Individual Municipality Pages",
        "How to Read This Page",
        "Current status → news → support → government records → recovery. Only headlines and links are provided.",
        "anime-guide-map.jpg",
        "Start with the official button above, then proceed to the support you need.",
        (0.5, 0.58),
    )
    s.note("News articles are not reproduced in full. Yahoo! News and similar links lead to the source. Figures are preliminary.")
    s.h2("Read from top to bottom")
    s.grid([
        ("Current Status", "Prefectural evacuation and shelter information, plus a note on whether the area was under a Level 5 alert."),
        ("Damage News", "Articles naming the municipality, prefecture-wide TV and news-agency coverage, and Yahoo! searches."),
        ("Support Measures", "Official damage-certificate and support links, national and prefectural guidance, and Disaster Relief Act coverage."),
        ("Government & Other Records", "Prefectural portal and Fire and Disaster Management Agency records, kept separate from news coverage."),
        ("Steps to Rebuild Daily Life", "Photos → assessment → certificate → emergency repair or temporary housing. Check official start dates."),
        ("Housing / Business", "Homes and shops or factories use different service desks. Continue to the relevant guidance."),
    ])
    s.save("info-municipality-en.png")

    s = Sheet(
        "Prefectural & National Support",
        "Guide to Official Sources",
        "Prefectural and national announcements and business consultations. We link to the source rather than reproducing full text.",
        "anime-guide-map.jpg",
        "Confirm eligibility and application periods with official prefectural, national or municipal sources.",
        (0.78, 0.57),
    )
    s.note("The Disaster Relief Act mainly covers emergency housing and daily life. Business recovery often uses separate programs.")
    s.h2("Official sources to open first")
    s.grid([
        ("Ishikawa, Toyama and Fukui", "Disaster Prevention Portal; response to heavy rain from 27 August 2026; Relief Act announcements; and damage-information PDFs."),
        ("National Government", "Cabinet Office victim support, FDMA disaster information, JMA warnings, and river-disaster information."),
        ("For Businesses", "Chubu and Kansai METI special consultation, the Small and Medium Enterprise Agency, and prefectural SME loan programs."),
        ("This Site's Log", "A chronological record of prefectural and national headlines. History is preserved rather than overwritten."),
    ])
    s.para("For local application guidance, use “Search by Municipality.” For procedures, see the housing or business page.")
    s.save("info-prefecture-en.png")

    s = Sheet(
        "For Supporters & Collaborators",
        "Collect and Share Information",
        "A CTZC volunteer effort, starting with public government and news information made easier for residents to use.",
        "anime-guide-team.jpg",
        "We organize public information and make it easier to reach people who need it.",
        (0.52, 0.5),
    )
    s.note("We do not provide rescue, match on-site volunteers, or conduct damage assessments.")
    s.h2("What we are doing now")
    s.steps([
        "Collect official information: Save headlines and URLs from approved sources on municipal pages.",
        "Organize it for residents: Separate entry points for housing, transport, businesses and municipalities.",
        "Collaborate in Slack: Keep ideas from disappearing by publishing them on the site and putting them to a vote.",
        "Vote on future ideas: Support information, features or actions you believe are needed.",
    ])
    s.h2("When looking for on-site activities")
    s.para("Check official recruitment by prefectural or municipal social welfare councils and the Red Cross. Confirm eligibility, advance registration and insurance before joining.")
    s.pills(["Municipal disaster VCs", "Prefectural social welfare councils", "Red Cross Disaster Volunteers", "Prefectural volunteer information"])
    s.h2("Join CTZC")
    s.pills(["Slack", "Vote on Future Ideas", "CTZC Website", "Facebook Group"])
    s.save("info-supporters-en.png")

    s = Sheet(
        "Vote on Future Ideas",
        "Show What Is Needed with Your Vote",
        "Results guide future features and information. We collect no personal data. This is not an aid application or damage report.",
        "anime-guide-team.jpg",
        "Choose ideas you need. Votes will guide future activities.",
        (0.38, 0.5),
    )
    s.note("One vote per idea in this browser; you can withdraw it. Results are indicative only.")
    s.h2("Voting rules")
    s.steps([
        "No login required: Residents, supporters and the general public may vote. We do not collect names.",
        "Browse by type: Information, feature or action. You can also sort by vote count.",
        "Combined totals: When the voting script in the operations sheet runs, everyone's votes appear in the count.",
        "Out of scope: Rescue, on-site matching and damage assessment are not voting topics.",
    ])
    s.para("Suggest other ideas in Slack or a GitHub Issue. A vote indicates demand; it is not a promise that the idea will be implemented.")
    s.save("info-ideas-en.png")


if __name__ == "__main__":
    build_all()
