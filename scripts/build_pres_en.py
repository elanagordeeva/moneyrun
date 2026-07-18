#!/usr/bin/env python3
"""English version of Moneyrun_new.pdf — simplified rebuild via reportlab.
Original design is a Keynote export with rich graphics; this script reproduces
the slide structure, palette and brand markers (Moneyrun mark, "Empower your life")
in English. The final slide replaces author contacts with a neutral closing."""

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

# Register Inter-like sans (Arial Unicode covers Latin); fallback to Helvetica TTC via mac path
def _register_fonts():
    candidates = [
        ("/Library/Fonts/Arial Unicode.ttf", "Arial Unicode.ttf"),
    ]
    for path,_ in candidates:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont("Brand", path))
            pdfmetrics.registerFont(TTFont("BrandBold", path))
            return True
    return False
_register_fonts()

OUT = Path(__file__).resolve().parent.parent / "art" / "Moneyrun_en.pdf"
PAGE_W, PAGE_H = 1280, 720           # 16:9

DARK   = HexColor("#0a0a0a")
LIGHT  = HexColor("#fafafa")
LIME   = HexColor("#BDFF76")         # brand canon
LIME_INK = HexColor("#1f2a05")
WHITE  = white
MUTED  = HexColor("#888888")
SOFT   = HexColor("#dddddd")
INK    = HexColor("#0e120e")

FONT_BOLD   = "BrandBold" if "BrandBold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
FONT_REG    = "Brand"     if "Brand"     in pdfmetrics.getRegisteredFontNames() else "Helvetica"
FONT_OBLIQUE= "Brand"     if "Brand"     in pdfmetrics.getRegisteredFontNames() else "Helvetica-Oblique"

# ──────────────────────────────────────────────────────────────────
# Helpers
def wrap(text, font, size, max_width):
    return simpleSplit(text, font, size, max_width)

def draw_mark(c, x, y, size, fill=LIME, mark_only=False):
    """Moneyrun mark — simplified (rounded blob)."""
    c.saveState()
    c.setFillColor(fill)
    # Stylized blob: oval + tail
    c.ellipse(x, y, x+size*1.0, y+size*0.78, fill=1, stroke=0)
    # tail
    p = c.beginPath()
    p.moveTo(x+size*0.55, y+size*0.18)
    p.curveTo(x+size*0.75, y-size*0.05, x+size*0.95, y+size*0.05, x+size*1.05, y+size*0.30)
    p.curveTo(x+size*0.95, y+size*0.15, x+size*0.75, y+size*0.10, x+size*0.65, y+size*0.20)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def footer(c, page_num, section=None, light=False):
    c.saveState()
    fg = INK if light else WHITE
    mut = HexColor("#666666") if light else MUTED
    # logo + name
    draw_mark(c, 50, 30, 18, fill=fg)
    c.setFillColor(fg)
    c.setFont(FONT_BOLD, 13)
    c.drawString(78, 33, "Moneyrun")
    # section text
    if section:
        c.setFillColor(mut)
        c.setFont(FONT_OBLIQUE, 11)
        c.drawString(220, 35, section)
    # center: Empower your life
    c.setFillColor(mut)
    c.setFont(FONT_OBLIQUE, 11)
    c.drawCentredString(PAGE_W/2, 35, "Empower your life")
    # right: © Moneyrun 2026  · page
    c.setFillColor(mut)
    c.setFont(FONT_REG, 10)
    c.drawString(PAGE_W-220, 35, "© Moneyrun, 2026")
    c.setFont(FONT_BOLD, 11)
    c.setFillColor(fg)
    c.drawRightString(PAGE_W-50, 33, str(page_num))
    c.restoreState()

def bg(c, color=DARK):
    c.setFillColor(color)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

def title_lime(c, x, y, text, size=48, max_width=600, leading=1.05, align="left"):
    c.setFillColor(LIME)
    c.setFont(FONT_BOLD, size)
    lines = wrap(text, FONT_BOLD, size, max_width)
    for line in lines:
        if align == "center":
            c.drawCentredString(x+max_width/2, y, line)
        elif align == "right":
            c.drawRightString(x+max_width, y, line)
        else:
            c.drawString(x, y, line)
        y -= size*leading

def title_ink(c, x, y, text, size=48, max_width=600, leading=1.05, color=INK, align="left", font=FONT_BOLD):
    c.setFillColor(color)
    c.setFont(font, size)
    lines = wrap(text, font, size, max_width)
    for line in lines:
        if align == "center":
            c.drawCentredString(x+max_width/2, y, line)
        elif align == "right":
            c.drawRightString(x+max_width, y, line)
        else:
            c.drawString(x, y, line)
        y -= size*leading
    return y

def body(c, x, y, text, size=15, max_width=420, leading=1.45, color=WHITE, font=FONT_REG):
    c.setFillColor(color)
    c.setFont(font, size)
    paragraphs = text.split("\n")
    for para in paragraphs:
        if not para.strip():
            y -= size*leading*.6
            continue
        for line in wrap(para, font, size, max_width):
            c.drawString(x, y, line)
            y -= size*leading
    return y

def num_marker(c, x, y, n, size=22, fg=LIME, bg_col=None):
    if bg_col:
        c.setFillColor(bg_col)
        c.circle(x+size/2, y+size/2, size/1.6, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont(FONT_BOLD, size)
    c.drawString(x, y, n)

# ──────────────────────────────────────────────────────────────────
# Slides

def slide_cover(c, page):
    bg(c, DARK)
    # mark
    cx, cy = PAGE_W/2, PAGE_H/2 + 70
    c.saveState()
    c.setFillColor(LIME)
    sz = 130
    c.ellipse(cx-sz*.45, cy-sz*.18, cx+sz*.45, cy+sz*.65, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(cx+sz*.10, cy-sz*.10)
    p.curveTo(cx+sz*.40, cy-sz*.35, cx+sz*.70, cy-sz*.25, cx+sz*.78, cy+sz*.05)
    p.curveTo(cx+sz*.65, cy-sz*.12, cx+sz*.45, cy-sz*.18, cx+sz*.30, cy-sz*.08)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    # title
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 96)
    c.drawCentredString(PAGE_W/2, PAGE_H/2-90, "Moneyrun")
    # tagline
    c.setFillColor(LIME)
    c.setFont(FONT_OBLIQUE, 22)
    c.drawCentredString(PAGE_W/2, 60, "Empower your life")

def slide_split_title_body(c, page, title, bodies, section=None):
    """Dark slide: big lime title right, body paragraphs left columns."""
    bg(c, DARK)
    title_lime(c, 620, PAGE_H-100, title, size=46, max_width=600, leading=1.1)
    # two body columns left
    col_w = 260
    for i, txt in enumerate(bodies):
        body(c, 60 + i*(col_w+30), PAGE_H/2+40, txt, size=15, max_width=col_w, color=WHITE)
    footer(c, page, section=section)

def slide_section(c, page, label):
    """Big lime title centered on dark."""
    bg(c, DARK)
    title_lime(c, 60, PAGE_H/2+60, label, size=72, max_width=PAGE_W-120, leading=1.05)
    footer(c, page)

def slide_text_left(c, page, title, body_text, section=None, light=False):
    bg(c, LIGHT if light else DARK)
    color_title = INK if light else LIME
    color_body  = INK if light else WHITE
    c.setFillColor(color_title)
    c.setFont(FONT_BOLD, 36)
    y = PAGE_H-130
    for line in wrap(title, FONT_BOLD, 36, 620):
        c.drawString(60, y, line); y -= 38
    body(c, 60, y-30, body_text, size=16, max_width=620, color=color_body)
    footer(c, page, section=section, light=light)

def slide_three_columns(c, page, header, cols, section=None, light=True):
    """Three columns with #1/#2/#3 markers."""
    bg(c, LIGHT if light else DARK)
    ink = INK if light else WHITE
    if header:
        c.setFillColor(ink)
        c.setFont(FONT_BOLD, 28)
        c.drawString(60, PAGE_H-110, header)
    col_w = (PAGE_W - 120 - 60) / 3
    for i, col in enumerate(cols):
        x = 60 + i*(col_w+30)
        c.setFillColor(LIME)
        c.setFont(FONT_BOLD, 44)
        c.drawString(x, PAGE_H/2+90, f"#{i+1}")
        c.setFillColor(ink)
        c.setFont(FONT_BOLD, 17)
        y=PAGE_H/2+30
        for line in wrap(col["title"], FONT_BOLD, 17, col_w-10):
            c.drawString(x, y, line); y-=20
        c.setFillColor(HexColor("#444444") if light else SOFT)
        c.setFont(FONT_REG, 13)
        for line in wrap(col["text"], FONT_REG, 13, col_w-10):
            c.drawString(x, y-20, line); y-=18
    footer(c, page, section=section, light=light)

def slide_numbered_list(c, page, title, items, section=None, light=False):
    bg(c, LIGHT if light else DARK)
    ink = INK if light else WHITE
    accent = LIME
    c.setFillColor(accent if not light else ink)
    c.setFont(FONT_BOLD, 32)
    y = PAGE_H-130
    for line in wrap(title, FONT_BOLD, 32, PAGE_W-120):
        c.drawString(80, y, line); y -= 36
    y -= 30
    for i, it in enumerate(items, 1):
        c.setFillColor(accent)
        c.setFont(FONT_BOLD, 22)
        c.drawString(80, y, f"{i}.")
        c.setFillColor(ink)
        c.setFont(FONT_REG, 16)
        for line in wrap(it, FONT_REG, 16, PAGE_W-220):
            c.drawString(130, y, line); y -= 22
        y -= 14
    footer(c, page, section=section, light=light)

def slide_two_col(c, page, title, left, right, section=None, light=False):
    bg(c, LIGHT if light else DARK)
    ink = INK if light else WHITE
    accent = LIME
    c.setFillColor(accent)
    c.setFont(FONT_BOLD, 32)
    y = PAGE_H-130
    for line in wrap(title, FONT_BOLD, 32, PAGE_W-120):
        c.drawString(60, y, line); y -= 36
    y_start = y - 30
    col_w = (PAGE_W-120)/2 - 30
    for col_idx, col in enumerate([left, right]):
        x = 60 + col_idx*(col_w+60)
        y = y_start
        c.setFillColor(accent)
        c.setFont(FONT_BOLD, 18)
        c.drawString(x, y, col["title"]); y -= 26
        c.setFillColor(ink)
        c.setFont(FONT_REG, 14)
        for line in wrap(col["text"], FONT_REG, 14, col_w):
            c.drawString(x, y, line); y -= 19
    footer(c, page, section=section, light=light)

def slide_quad(c, page, title, quads, section=None, light=False):
    """2x2 grid of card-like items."""
    bg(c, LIGHT if light else DARK)
    ink = INK if light else WHITE
    accent = LIME
    c.setFillColor(accent)
    c.setFont(FONT_BOLD, 30)
    y = PAGE_H-110
    for line in wrap(title, FONT_BOLD, 30, PAGE_W-120):
        c.drawString(60, y, line); y -= 34
    cell_w = (PAGE_W-120-40)/2
    cell_h = 170
    for i, q in enumerate(quads):
        col = i%2; row = i//2
        x = 60 + col*(cell_w+40)
        cy_top = y-30 - row*(cell_h+30)
        c.setFillColor(accent)
        c.setFont(FONT_BOLD, 20)
        c.drawString(x, cy_top, q["title"])
        c.setFillColor(ink)
        c.setFont(FONT_REG, 14)
        sub_y = cy_top - 28
        for line in wrap(q["text"], FONT_REG, 14, cell_w):
            c.drawString(x, sub_y, line); sub_y -= 19
    footer(c, page, section=section, light=light)

def slide_venn(c, page, body_text, labels, section=None):
    bg(c, LIGHT)
    body(c, 70, PAGE_H-120, body_text, size=16, max_width=460, color=INK)
    # venn circles
    cx, cy = PAGE_W-340, PAGE_H/2 + 20
    r = 130
    coords = [(cx-r*0.5, cy+r*0.4), (cx+r*0.5, cy+r*0.4), (cx-r*0.5, cy-r*0.4), (cx+r*0.5, cy-r*0.4)]
    c.setDash(3,3)
    c.setStrokeColor(HexColor("#888888"))
    for x,y in coords:
        c.circle(x, y, r, stroke=1, fill=0)
    c.setDash()
    # central lime circle
    c.setFillColor(LIME)
    c.circle(cx, cy, r*0.55, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 16)
    c.drawCentredString(cx, cy-5, "Moneyrun")
    # labels around
    label_positions = [
        (cx, cy+r+30, labels[0]),     # top
        (cx+r*1.7, cy, labels[1]),    # right
        (cx, cy-r-30, labels[2]),     # bottom
        (cx-r*1.7, cy, labels[3]),    # left
    ]
    c.setFillColor(INK)
    c.setFont(FONT_REG, 13)
    for (x,y,t) in label_positions:
        c.drawCentredString(x, y, t)
    footer(c, page, section=section, light=True)

def slide_closing(c, page):
    """Neutral final slide — no contacts."""
    bg(c, DARK)
    # central mark
    cx, cy = PAGE_W/2, PAGE_H/2+50
    c.saveState()
    c.setFillColor(LIME)
    sz = 90
    c.ellipse(cx-sz*.45, cy-sz*.18, cx+sz*.45, cy+sz*.65, fill=1, stroke=0)
    p = c.beginPath()
    p.moveTo(cx+sz*.10, cy-sz*.10)
    p.curveTo(cx+sz*.40, cy-sz*.35, cx+sz*.70, cy-sz*.25, cx+sz*.78, cy+sz*.05)
    p.curveTo(cx+sz*.65, cy-sz*.12, cx+sz*.45, cy-sz*.18, cx+sz*.30, cy-sz*.08)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    c.setFillColor(WHITE)
    c.setFont(FONT_BOLD, 72)
    c.drawCentredString(PAGE_W/2, PAGE_H/2-60, "Thank you")
    c.setFillColor(LIME)
    c.setFont(FONT_OBLIQUE, 24)
    c.drawCentredString(PAGE_W/2, PAGE_H/2-120, "Empower your life")

# ──────────────────────────────────────────────────────────────────
# Build
def build():
    c = canvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H))
    pg = 0

    # 1 — Cover
    pg += 1; slide_cover(c, pg); c.showPage()

    # 2 — Running is not just sport
    pg += 1
    slide_split_title_body(c, pg,
        "Running is not just sport — it's the path of consciousness development",
        [
            "For our ancestors, the ability to remember routes during running — for example, the way from home to the hunting grounds — was vital.",
            "Over hundreds of thousands of years of evolution, running has become an important factor in brain development. That is why we believe that, above all, running is the development of consciousness.",
        ])
    c.showPage()

    # 3 — Venn
    pg += 1
    slide_venn(c, pg,
        "We have united every form of running motivation in a single app that captures all the analytics and statistics — completely free, so that anyone can easily start the path of self-improvement.",
        ["Health", "Mind-building", "Money", "Strength"],
        section="The problem we solve")
    c.showPage()

    # 4 — Section
    pg += 1
    slide_section(c, pg, "Moneyrun service capabilities for athletes")
    c.showPage()

    # 5 — How it works (3 columns)
    pg += 1
    slide_three_columns(c, pg, "How it works",
        [
            {"title":"Athlete",
             "text":"Registers in the app. Joins clubs. Logs workouts. Builds up Experience (XP)."},
            {"title":"Moneyrun",
             "text":"Connects athletes with clubs. Handles billing and all platform calculations. Monitors fraud. Continuously improves the platform with new features."},
            {"title":"Clubs",
             "text":"Corporations and social organisations create clubs on the platform to motivate employees and communities. Set the exchange rate based on each athlete's XP level."},
        ],
        section="How it works", light=True)
    c.showPage()

    # 6 — Section
    pg += 1; slide_section(c, pg, "Experience"); c.showPage()

    # 7 — XP details
    pg += 1
    slide_numbered_list(c, pg,
        "XP (Experience) — points an athlete earns for activity. The XP amount depends mainly on:",
        [
            "Heart-rate data submitted by the athlete (including HR-max).",
            "Intensity and duration of the training load (eTRIMP).",
            "Training-load balance (Ch72 and ChT).",
            "Amateur performance metrics (RL and RQ).",
        ],
        section="Experience")
    c.showPage()

    # 8 — EF Moneyrun
    pg += 1
    slide_text_left(c, pg,
        "EF Moneyrun (Endowment Fund)",
        "The fund collects voluntary contributions, invests them and channels the monthly income to support athletes through clubs and to reward Grade progression.",
        section="EF Moneyrun")
    c.showPage()

    # 9 — Who can contribute
    pg += 1
    slide_text_left(c, pg,
        "Who can contribute to EF Moneyrun",
        "Patrons: founders and employees, private investors, corporations and the athletes themselves (reinvesting their earned-by-running funds).\n\nContributions grow the investment portfolio → percentage income rises → more is distributed among the athletes.",
        section="EF Moneyrun")
    c.showPage()

    # 10 — News feed
    pg += 1
    slide_text_left(c, pg,
        "A news feed that motivates and inspires runners",
        "Showing the achievements of other athletes. All community activity is reflected in the feed — available to subscribers and other athletes.",
        section="Athlete social network")
    c.showPage()

    # 11 — Social #1 #2 #3
    pg += 1
    slide_three_columns(c, pg, "",
        [
            {"title":"Athletes publish workouts and photos",
             "text":"Subscribers see workouts in the feed, leaving likes and comments."},
            {"title":"Regular Moneyrun events in the feed",
             "text":"Community members keep up with everything interesting, including challenges."},
            {"title":"Athletes contribute to running's growth",
             "text":"Money earned can be invested in EF Moneyrun to support running — this action is reflected in the shared feed."},
        ],
        section="Athlete social network", light=True)
    c.showPage()

    # 12 — Section Clubs
    pg += 1; slide_section(c, pg, "Clubs"); c.showPage()

    # 13 — Communities
    pg += 1
    slide_text_left(c, pg,
        "Interest-based communities can create their own clubs",
        "Communities set their own membership rules. Clubs unite like-minded people around common goals for joint training. A club can include gamified elements and competitions within the training process.",
        section="Clubs")
    c.showPage()

    # 14 — Club balance
    pg += 1
    slide_text_left(c, pg,
        "Club balance is built from EF Moneyrun and member contributions",
        "These funds can be used at the club's own discretion — to donate on behalf of the club, or to sponsor events.",
        section="Clubs")
    c.showPage()

    # 15 — Section Statistics
    pg += 1; slide_section(c, pg, "Statistics and analytics"); c.showPage()

    # 16 — Free analytics
    pg += 1
    slide_text_left(c, pg,
        "Athletes analyse workouts and improve their results for free",
        "For every workout you can view detailed statistics and track progress over time.",
        section="Statistics and analytics")
    c.showPage()

    # 17 — Section PRO
    pg += 1; slide_section(c, pg, "PRO division"); c.showPage()

    # 18 — PRO list
    pg += 1
    slide_numbered_list(c, pg,
        "For those ready to take on a challenge and train professionally:",
        [
            "Training diary with advanced analytics.",
            "Choice of coach from Moneyrun-authorised specialists.",
            "Personalised training plan.",
        ],
        section="PRO division")
    c.showPage()

    # 19 — Section Races
    pg += 1; slide_section(c, pg, "Races"); c.showPage()

    # 20 — Races list
    pg += 1
    slide_numbered_list(c, pg,
        "«Races» — your achievements in one place",
        [
            "Automatic personal records over classic distances.",
            "Smart search — convenient filters and sorting to find the race you need among many.",
            "Linking to workouts — attach a Race to a previously uploaded Workout on our platform.",
        ],
        section="Races")
    c.showPage()

    # 21 — Section Withdraw
    pg += 1; slide_section(c, pg, "Money withdrawal"); c.showPage()

    # 22 — Withdrawal description
    pg += 1
    slide_text_left(c, pg,
        "Withdraw money to your personal card in three clicks",
        "After a workout the athlete exchanges XP for rubles. They can then withdraw funds from their virtual account by phone number.",
        section="Withdrawal")
    c.showPage()

    # 23 — Integrations
    pg += 1
    slide_text_left(c, pg,
        "Moneyrun integrates with every popular sports watch and running app",
        "Strava, Garmin, Apple Watch, Suunto, Polar, Coros — and more.",
        section="Integrations")
    c.showPage()

    # 24 — Future steps
    pg += 1
    slide_two_col(c, pg,
        "The product evolves quickly — new capabilities arrive regularly",
        {"title":"Today",
         "text":"Workouts, social network, funds, clubs, statistics and analytics, PRO division, marketplace, money withdrawal."},
        {"title":"Coming next",
         "text":"Coach profiles. Workout and goal pages with personalised training plans. Geolocation services."},
        section="Future steps")
    c.showPage()

    # 25 — Section Corporate club
    pg += 1; slide_section(c, pg, "Create your own club on Moneyrun"); c.showPage()

    # 26 — Corporate club, 2 cols + side cluster
    pg += 1
    slide_two_col(c, pg,
        "Create a corporate club for free",
        {"title":"Hosting a club — free, no commissions",
         "text":"The platform takes no money for hosting — no fees or transaction payments."},
        {"title":"Contribution to EF Moneyrun",
         "text":"A voluntary donation to support running — not an obligatory payment."},
        section="Corporate club")
    c.showPage()

    # 27 — Employee motivation 2x2
    pg += 1
    slide_quad(c, pg, "Employee motivation",
        [
            {"title":"Fair",
             "text":"Every athlete is paid for the work they actually did."},
            {"title":"Transparent",
             "text":"Every athlete sees the exchange rate and the XP earning rules right in the app, in real time."},
            {"title":"Material",
             "text":"No bonuses, tokens or coins — only rubles."},
            {"title":"Non-material",
             "text":"A sense of belonging to the development of the running community."},
        ],
        section="Corporate club")
    c.showPage()

    # 28 — Corporate club list
    pg += 1
    slide_numbered_list(c, pg,
        "A corporate club for your employees on Moneyrun",
        [
            "Additional material and non-material motivation.",
            "More productive employees.",
            "Even, instant motivation grounded in personal achievements.",
            "In-company challenges with stakes and bets.",
        ],
        section="Corporate club")
    c.showPage()

    # 29 — Neutral closing (no contacts)
    pg += 1; slide_closing(c, pg); c.showPage()

    c.save()
    print(f"Built {OUT} ({pg} slides)")

if __name__ == "__main__":
    build()
