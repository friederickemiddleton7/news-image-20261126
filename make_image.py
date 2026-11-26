#!/usr/bin/env python3
"""Draw the 26 November 2026 world-news poster as a 1024x1024 RGB PNG.

Rendered at 2x supersample and downscaled with LANCZOS. Every text run is
measured with real DejaVu font metrics; all runs must be at least 19 design
pixels tall, fit inside their card and the canvas, and not overlap any other
run. The module is deterministic: no clock, random numbers or wall-clock data.
"""

from PIL import Image, ImageDraw, ImageFont

SS = 2
C = 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

NAVY = (11, 18, 32)
CARD = (21, 31, 51)
HAIR = (42, 58, 87)
BODY = (215, 222, 234)
WHITE = (255, 255, 255)
AMBER = (242, 179, 61)
TEAL = (79, 209, 197)
MUTED = (147, 160, 180)

BOLD = "DejaVuSans-Bold.ttf"
REG = "DejaVuSans.ttf"
MIN_FONT = 19

STORY_COUNT = 38
GRID_COLS = 5
GRID_ROWS = 8
GRID_TOP = 364
GRID_GAP = 4
GRID_COL_W = 194
GRID_ROW_H = 72
GRID_MAX_LINES = 3
GRID_INK_STEP = 19

_fonts = {}
_runs = []
_meas = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def font(name, size):
    key = (name, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_DIR + name, size * SS)
    return _fonts[key]


def width(text, fnt):
    return _meas.textlength(text, font=fnt) / SS


def ink_box(text, name, size):
    bb = font(name, size).getbbox(text)
    return bb[1] / SS, bb[3] / SS


def tracked_width(text, fnt, tracking):
    return width(text, fnt) + tracking * max(0, len(text) - 1)


def rect(d, x0, y0, x1, y1, fill=None, outline=None, lw=1):
    box = tuple(int(round(v * SS)) for v in (x0, y0, x1, y1))
    if fill is not None:
        d.rectangle(box, fill=fill)
    if outline is not None:
        d.rectangle(box, outline=outline, width=max(1, int(round(lw * SS))))


def poly(d, points, fill):
    d.polygon([(int(round(x * SS)), int(round(y * SS))) for x, y in points],
              fill=fill)


def draw_text(d, x, y, text, name, size, fill, tracking=0, clip=None, label=""):
    fnt = font(name, size)
    if size < MIN_FONT:
        raise AssertionError("type below %d px: %r" % (MIN_FONT, text))
    if tracking:
        cx = x
        for ch in text:
            d.text((int(round(cx * SS)), int(round(y * SS))), ch, font=fnt,
                   fill=fill)
            cx += width(ch, fnt) + tracking
    else:
        d.text((int(round(x * SS)), int(round(y * SS))), text, font=fnt,
               fill=fill)
    top, bottom = ink_box(text, name, size)
    box = (x, y + top, x + tracked_width(text, fnt, tracking), y + bottom)
    if box[0] < 0 or box[1] < 0 or box[2] > C or box[3] > C:
        raise AssertionError("text outside canvas: %r %s" % (text, box))
    if clip and (box[0] < clip[0] or box[1] < clip[1] or
                 box[2] > clip[2] or box[3] > clip[3]):
        raise AssertionError("text outside clip %s: %r %s" % (clip, text, box))
    _runs.append((box[0], box[1], box[2], box[3], label or text[:32]))
    return box


def fit_lines(text, name, size, max_width, max_lines):
    """Greedy word wrap; every line must fit max_width by real metrics."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if width(trial, font(name, size)) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
                cur = word
            else:
                raise AssertionError("word too wide at %d px: %r" % (size, word))
            if width(cur, font(name, size)) > max_width:
                raise AssertionError("word too wide at %d px: %r" % (size, word))
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        raise AssertionError("wrap needs %d lines (>%d): %r" %
                             (len(lines), max_lines, text))
    return lines


def header(d):
    d.rectangle((0, 0, C * SS, 152 * SS), fill=NAVY)
    draw_text(d, 22, 10, "WORLD NEWS", BOLD, 23, AMBER, tracking=9,
              clip=(0, 0, C, 46), label="kicker")
    draw_text(d, 20, 41, "26 NOVEMBER 2026", BOLD, 72, WHITE,
              clip=(0, 36, C, 119), label="date")
    rect(d, 20, 119, 1004, 122, fill=AMBER)
    draw_text(d, 22, 127, "THURSDAY  \u00b7  38 STORIES ACROSS SIX CONTINENTS",
              REG, 20, BODY, clip=(0, 122, C, 152), label="subhead")


def lead(d):
    x0, y0, x1, y1 = 12, 158, 1012, 357
    clip = (x0 + 6, y0 + 4, x1 - 6, y1 - 4)
    rect(d, x0, y0, x1, y1, fill=CARD)
    rect(d, x0, y0, x1, y1, outline=HAIR, lw=1)
    rect(d, x0, y0, x0 + 4, y1, fill=AMBER)

    draw_text(d, 26, y0 + 10, "LEAD  \u00b7  AMERICAS  \u00b7  WASHINGTON",
              BOLD, 21, AMBER, tracking=1, clip=clip, label="lead-chip")

    title = ["TRUMP SLAPS NEW TARIFFS", "ON 14 TRADING PARTNERS"]
    for i, s in enumerate(title):
        draw_text(d, 26, y0 + 46 + i * 52, s, BOLD, 45, WHITE,
                  clip=clip, label="lead-head-%d" % i)
    body = ("SECTION 301 OVERCAPACITY DUTIES: CHINA 20% ON TOP OF EXISTING "
            "LEVIES, INDIA 17\u201325%, EU, JAPAN AND KOREA 15%.")
    lines = fit_lines(body, REG, 19, 690, 2)
    for i, s in enumerate(lines):
        draw_text(d, 26, y0 + 146 + i * 22, s, REG, 19, BODY,
                  clip=clip, label="lead-body-%d" % i)

    # Flat container ship pictogram, rectangles and triangles only.
    ox, oy = 762, 205
    rect(d, ox, oy + 70, ox + 180, oy + 80, fill=TEAL)          # water
    rect(d, ox + 10, oy + 56, ox + 170, oy + 70, fill=HAIR)     # deck
    poly(d, [(ox + 6, oy + 80), (ox + 174, oy + 80),
             (ox + 160, oy + 106), (ox + 20, oy + 106)], fill=HAIR)  # hull
    rect(d, ox + 106, oy + 34, ox + 158, oy + 56, fill=AMBER)   # cabin
    rect(d, ox + 114, oy + 40, ox + 126, oy + 50, fill=NAVY)    # cabin window
    rect(d, ox + 134, oy + 40, ox + 146, oy + 50, fill=NAVY)
    rect(d, ox + 70, oy + 10, ox + 78, oy + 46, fill=HAIR)      # mast
    poly(d, [(ox + 74, oy - 4), (ox + 90, oy + 20),
             (ox + 58, oy + 20)], fill=AMBER)                    # arrow
    for col in range(4):                                        # containers
        for row in range(2):
            xx = ox + 14 + col * 34
            yy = oy + 14 + row * 26
            fill = AMBER if (col + row) % 3 == 0 else TEAL
            rect(d, xx, yy, xx + 30, yy + 22, fill=fill)
    draw_text(d, ox + 10, oy + 112, "TARIFF", BOLD, 19, AMBER,
              clip=clip, label="pictogram-tariff")


GRID = [
    ("EUR \u00b7 KYIV", "RUSSIAN STRIKE HITS KYIV MALL"),
    ("AMR \u00b7 NEW YORK", "NASDAQ SLIDES 4%; TECH FALLS"),
    ("ME \u00b7 GAZA CITY", "ISRAEL KILLS HAMAS CHIEF"),
    ("ME \u00b7 JAZAN", "HOUTHI HITS JAZAN PORT"),
    ("AFR \u00b7 CAIRO", "FUEL TANKER CRASH KILLS 30"),
    ("APAC \u00b7 JIUQUAN", "FIRST PAKISTANI IN SPACE"),
    ("APAC \u00b7 CANBERRA", "AUSTRALIA INFLATION 4.9%"),
    ("EUR \u00b7 SAMARA", "RUSSIAN REFINERIES HIT"),
    ("EUR \u00b7 WARSAW", "POLAND PLANS NO-FLY ZONE"),
    ("EUR \u00b7 TALLINN", "ESTONIA CLOSES BORDER"),
    ("EU \u00b7 BRUSSELS", "EU SUMMIT ON UKRAINE FUNDS"),
    ("EUR \u00b7 LONDON", "UK ENERGY BILLS +25%"),
    ("US \u00b7 WASHINGTON", "THANKSGIVING DINNER UP 6%"),
    ("US \u00b7 S.F.", "KING TIDES FLOOD BAY"),
    ("US \u00b7 WASHINGTON", "US DEBT NEARS $41.1 TRILLION"),
    ("AMR \u00b7 ARGENTINA", "PESO FALLS TO 1,592"),
    ("US \u00b7 WASHINGTON", "HUAWEI TRADE SECRETS GUILTY"),
    ("APAC \u00b7 BEIJING", "XI PROBES SHANGHAI"),
    ("APAC \u00b7 PYONGYANG", "N.KOREA EXPELS ENVOY"),
    ("APAC \u00b7 SEOUL", "KOREA TARIFF CAP 15%"),
    ("APAC \u00b7 TOKYO", "JAPAN AI POWER BID"),
    ("APAC \u00b7 HOBART", "TASMANIA FIRE EVACUATES"),
    ("APAC \u00b7 HONIARA", "SOLOMONS SIGN SECURITY PACT"),
    ("APAC \u00b7 BANDUNG", "JAVA MINE TRAPS 30"),
    ("APAC \u00b7 CAMBODIA", "CHINA JOINS GOLDEN DRILLS"),
    ("ASIA \u00b7 HONG KONG", "ANIMAL IMPORTS SOAR"),
    ("ME \u00b7 HORMUZ", "TANKER MINED IN HORMUZ"),
    ("ME \u00b7 GENEVA", "UN ATROCITY WARNING"),
    ("ME \u00b7 JERUSALEM", "NETANYAHU CASE DROPPED"),
    ("AFR \u00b7 KHARTOUM", "DRONE DEATHS TOP SUDAN"),
    ("AFR \u00b7 OYO", "KENYA-CONGO PEACE TALKS"),
    ("AFR \u00b7 PRETORIA", "PHALA PHALA CASE AXED"),
    ("AFR \u00b7 LAGOS", "NOLLYWOOD LEGEND DIES"),
    ("AFR \u00b7 BENGHAZI", "LIBYAN OFFICERS DEAD"),
    ("GLB \u00b7 SAN JUAN", "PUERTO RICO MISS UNIVERSE"),
    ("GLB \u00b7 NEW YORK", "UN CHIEF RACE STALLS"),
    ("GLB \u00b7 TOKYO", "ASIA STOCKS SLIDE ON AI"),
]
assert len(GRID) + 1 == STORY_COUNT, "expected 38 stories"


def grid(d):
    left = 12
    cw, ch, gap = GRID_COL_W, GRID_ROW_H, GRID_GAP
    rendered = 0
    for idx, (chip, head) in enumerate(GRID):
        col, row = idx % GRID_COLS, idx // GRID_COLS
        x0 = left + col * (cw + gap)
        y0 = GRID_TOP + row * (ch + gap)
        x1, y1 = x0 + cw, y0 + ch
        if x1 > 1012 or y1 > 969:
            raise AssertionError("grid cell %d outside grid area" % idx)
        rect(d, x0, y0, x1, y1, fill=CARD)
        rect(d, x0, y0, x1, y1, outline=HAIR, lw=1)
        clip = (x0 + 4, y0 + 2, x1 - 4, y1 - 2)
        chip_lines = fit_lines(chip, REG, 19, cw - 10, 2)
        head_max = 5 - len(chip_lines)
        for j, s in enumerate(chip_lines):
            draw_text(d, x0 + 4, y0 + 1 + j * GRID_INK_STEP, s, REG, 19, TEAL,
                      clip=clip, label="chip-%d-%d" % (idx, j))
        head_y = y0 + 1 + len(chip_lines) * GRID_INK_STEP + 1
        head_lines = fit_lines(head, BOLD, 19, cw - 12, head_max)
        total_lines = len(chip_lines) + len(head_lines)
        if total_lines > GRID_MAX_LINES:
            raise AssertionError("card %d needs %d lines" % (idx, total_lines))
        for j, s in enumerate(head_lines):
            draw_text(d, x0 + 4, head_y + j * GRID_INK_STEP, s, BOLD, 19, WHITE,
                      clip=clip, label="head-%d-%d" % (idx, j))
        rendered += 1
    if rendered != 37:
        raise AssertionError("rendered %d grid cards, expected 37" % rendered)
    return rendered


def footer(d):
    rect(d, 12, 973, 1012, 976, fill=HAIR)
    draw_text(d, 16, 984, "SOURCES", BOLD, 19, AMBER, tracking=1,
              clip=(0, 978, C, C), label="sources-label")
    sources = ("AP \u00b7 REUTERS \u00b7 AFP \u00b7 KYIV INDEP \u00b7 TAIPEI TIMES \u00b7 "
               "ABC \u00b7 BBC \u00b7 AL JAZEERA \u00b7 SBS \u00b7 CNBC")
    draw_text(d, 130, 984, sources, REG, 19, MUTED,
              clip=(124, 978, C, C), label="sources")


def verify_runs():
    for i in range(len(_runs)):
        a = _runs[i]
        for j in range(i + 1, len(_runs)):
            b = _runs[j]
            if a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]:
                raise AssertionError("text overlap: %r / %r" % (a[4], b[4]))


def build(path):
    _runs.clear()
    img = Image.new("RGB", (C * SS, C * SS), NAVY)
    d = ImageDraw.Draw(img)
    header(d)
    lead(d)
    cards = grid(d)
    footer(d)
    verify_runs()
    out = img.resize((C, C), Image.LANCZOS)
    out.save(path, "PNG", optimize=True)
    print("stories: %d (1 lead + %d grid cards), text runs: %d" %
          (1 + cards, cards, len(_runs)))
    print("ALL LAYOUT CHECKS PASSED")
    return 1 + cards


if __name__ == "__main__":
    build("entry.png")
