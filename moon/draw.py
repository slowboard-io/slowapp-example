"""Moon cards. The board's slot (`phase`, k4) is in the panel's four inks, with text drawn without
antialiasing (fontmode "1") because every pixel must be one of them. The full screen (`full`,
g16) is drawn in greys and snapped to the sixteen levels at the end."""
import math

from PIL import ImageDraw

import slowapp_kit as kit
from slowapp_kit import BLACK, RED, WHITE, YELLOW

from . import phase


def disc(d, cx, cy, r, t, south=False, lit=YELLOW, dark=BLACK, rim=BLACK, rim_w=2):
    """The moon at time t: the lit part in `lit`, the dark part in `dark`, outlined in `rim`."""
    a = phase.age(t) / phase.SYNODIC_DAYS            # 0 new, 0.5 full
    waxing = a < 0.5
    k = math.cos(2 * math.pi * a)                    # terminator: x = k * half-width, 1 new .. -1 full
    lit_right = waxing != south                      # northern sky: waxing is lit on the right
    for dy in range(-r, r + 1):
        half = int(math.sqrt(max(r * r - dy * dy, 0)))
        if half == 0:
            continue
        term = int(round(k * half))
        x0, x1 = cx - half, cx + half
        # Lit span: from the terminator to the lit limb.
        if lit_right:
            lx0, lx1 = cx + term, x1
        else:
            lx0, lx1 = x0, cx - term
        d.line((x0, cy + dy, x1, cy + dy), fill=dark)
        if lx1 > lx0:
            d.line((lx0, cy + dy, lx1, cy + dy), fill=lit)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=rim, width=rim_w)


def home(ctx, surface, south):
    t = ctx.for_
    img = ctx.canvas(surface)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    w, h = img.size
    d.text((w // 2, 18), phase.name(t), font=kit.font("DejaVuSans-Bold.ttf", 34), fill=BLACK, anchor="mt")
    disc(d, w // 2, 200, 120, t, south)
    small = kit.font("DejaVuSans.ttf", 22)
    d.text((w // 2, 338), f"{phase.illumination(t) * 100:.0f}% lit, day {phase.age(t):.1f}",
           font=small, fill=BLACK, anchor="mt")
    full, new = phase.next_phase(t, 0.5), phase.next_phase(t, 0.0)
    d.text((w // 2, 374), f"Full {full:%a %d %b}", font=small, fill=RED, anchor="mt")
    d.text((w // 2, 404), f"New {new:%a %d %b}", font=small, fill=BLACK, anchor="mt")
    return img


def week(ctx, surface, south):
    """The next eight days, two rows of four."""
    from datetime import timedelta
    img = ctx.canvas(surface)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    w, h = img.size
    d.text((w // 2, 14), "The week ahead", font=kit.font("DejaVuSans-Bold.ttf", 28), fill=BLACK, anchor="mt")
    label = kit.font("DejaVuSans.ttf", 18)
    cw = w // 4
    for i in range(8):
        t = ctx.for_ + timedelta(days=i)
        cx, cy = cw * (i % 4) + cw // 2, 140 + (i // 4) * 180
        disc(d, cx, cy, 44, t, south)
        d.text((cx, cy + 56), f"{t:%a %d}", font=label, fill=RED if i == 0 else BLACK, anchor="mt")
    return img


def full(ctx, surface, south):
    """The whole screen in greys for a thin battery board standing tall (the Slowboard 470 at
    540x960): the phase and how lit at the top, the moon large on a night panel, the next full and
    new moons, the week below them, and when it was drawn, so a device that holds it for hours
    still says how old it is."""
    from datetime import timedelta
    from slowapp_kit import grey, snap_g16
    t = ctx.for_
    img = ctx.canvas(surface, fill=grey(15))
    d = ImageDraw.Draw(img)
    b = box(surface)
    s, x, right = b.s, b.left, b.right

    def line(xy, text, name, size, fill, width):
        while size > 12 and d.textlength(text, font=kit.font(name, size)) > width:
            size -= 1
        d.text(xy, text, font=kit.font(name, size), fill=fill, anchor="lt")

    # The head: the phase, and how lit.
    line((x, b.head_top), phase.name(t), "DejaVuSans-Bold.ttf", int(40 * s), grey(0), b.head_right - x)
    line((x, b.head_top + int(56 * s)), f"{phase.illumination(t) * 100:.0f}% lit · day {phase.age(t):.1f}",
         "DejaVuSans.ttf", int(24 * s), grey(4), b.head_right - x)

    # The night panel, the moon in it.
    top, bottom = b.top, b.top + int(410 * s)
    d.rounded_rectangle((x - int(12 * s), top, right + int(12 * s) if not b.board else right, bottom),
                        radius=int(16 * s), fill=grey(1))
    r = int((bottom - top) * 0.42)
    disc(d, (x + right) // 2, (top + bottom) // 2, r, t, south, lit=grey(14), dark=grey(3), rim=grey(7),
         rim_w=max(2, int(3 * s)))

    # The next full and new moons.
    full_at, new_at = phase.next_phase(t, 0.5), phase.next_phase(t, 0.0)
    for i, (label, when) in enumerate(sorted([("Full", full_at), ("New", new_at)], key=lambda p: p[1])):
        days = round((when - t) / timedelta(days=1))
        line((x, bottom + int((30 + 40 * i) * s)), f"{label} moon {when:%a %-d %b} · {days} d", "DejaVuSans.ttf",
             int(26 * s), grey(0), right - x)

    # The week ahead: seven small moons.
    small = kit.font("DejaVuSans.ttf", int(20 * s))
    y = bottom + int(150 * s)
    d.line((x, y - int(18 * s), right, y - int(18 * s)), fill=grey(10), width=max(1, int(2 * s)))
    cw = (right - x) / 7
    rr = int(min(cw * 0.38, 26 * s))
    for i in range(7):
        ti = t + timedelta(days=i + 1)
        cx = int(x + cw * i + cw / 2)
        disc(d, cx, y + int(32 * s), rr, ti, south, lit=grey(15), dark=grey(3), rim=grey(3))
        d.text((cx, y + int(70 * s)), f"{ti:%a}", font=small, fill=grey(0), anchor="mt")
        d.text((cx, y + int(96 * s)), f"{ti:%-d}", font=small, fill=grey(5), anchor="mt")

    drawn(ctx, d, b, f"drawn {ctx.now:%a %-d %b %H:%M} · for {t:%H:%M}")
    return snap_g16(img)


# ---- the rest of the full-screen deck (g16): a thin board's keys step through these ----------------

QUARTERS = [(0.0, "New moon"), (0.25, "First quarter"), (0.5, "Full moon"), (0.75, "Last quarter")]


class Box:
    """Where a full-screen card draws. On the Slowboard 470 (540x960) the board owns its key
    labels (x 336-480, y 16-136), their lane down the right edge (x 480-540, y 0-340) and the app
    strip (y 900-960), so the head stops short of the labels, the body short of the lane, and the
    footer sits above the strip. Elsewhere, plain margins."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.s = s = min(w / 540, h / 960)
        self.board = (w, h) == (540, 960)
        self.left = int(36 * s)
        self.right = 468 if self.board else w - int(36 * s)
        self.head_top = int(28 * s)
        self.head_right = 324 if self.board else self.right
        self.top = int(152 * s) if self.board else int(116 * s)
        self.foot = 888 if self.board else h - int(30 * s)
        self.foot_right = w - 24 if self.board else self.right
        self.bottom = self.foot - int(36 * s)


def box(surface):
    return Box(surface.w, surface.h)


def drawn(ctx, d, b, text):
    from slowapp_kit import grey
    d.text((b.foot_right, b.foot), text, font=kit.font("DejaVuSans.ttf", int(18 * b.s)), fill=grey(6), anchor="rb")


def _g16_page(ctx, surface, title):
    """A light page with a title in the head (two lines if it needs them), a rule under it, and the
    drawn-at line: the shared frame. Returns (image, draw, box)."""
    from slowapp_kit import grey
    img = ctx.canvas(surface, fill=grey(15))
    d = ImageDraw.Draw(img)
    b = box(surface)
    width = b.head_right - b.left
    words = title.split()
    size = int(34 * b.s)
    while True:
        f = kit.font("DejaVuSans-Bold.ttf", size)
        lines, cur = [], ""
        for wd in words:
            if cur and d.textlength(f"{cur} {wd}", font=f) > width:
                lines.append(cur)
                cur = wd
            else:
                cur = f"{cur} {wd}".strip()
        lines.append(cur)
        if (len(lines) <= 2 and all(d.textlength(ln, font=f) <= width for ln in lines)) or size <= 16:
            break
        size -= 1
    d.multiline_text((b.left, b.head_top), "\n".join(lines), font=f, fill=grey(0), spacing=int(6 * b.s))
    y = b.top - int(16 * b.s)
    d.line((b.left, y, b.right, y), fill=grey(10), width=max(1, int(2 * b.s)))
    drawn(ctx, d, b, f"drawn {ctx.now:%a %-d %b %H:%M}")
    return img, d, b


def phases(ctx, surface, south):
    """The next four quarters (new, first quarter, full, last quarter, in the order they come): a
    row each, a big moon beside the day, the time and how many days off."""
    from datetime import timedelta
    from slowapp_kit import grey, snap_g16
    t = ctx.for_
    img, d, b = _g16_page(ctx, surface, "The next four phases")
    s = b.s
    ahead = sorted((phase.next_phase(t, f), label) for f, label in QUARTERS)
    y0, rh = b.top, (b.bottom - b.top) // 4
    r = int(72 * s)
    big, small = kit.font("DejaVuSans-Bold.ttf", int(30 * s)), kit.font("DejaVuSans.ttf", int(24 * s))
    for i, (when, label) in enumerate(ahead):
        cy = y0 + rh * i + rh // 2
        cx = b.left + r
        # A hair past the moment, so a quarter that is exactly now draws as itself.
        disc(d, cx, cy, r, when + timedelta(minutes=1), south, lit=grey(15), dark=grey(2), rim=grey(2),
             rim_w=max(2, int(3 * s)))
        x = cx + r + int(32 * s)
        days = (when - t) / timedelta(days=1)
        d.text((x, cy - int(44 * s)), label, font=big, fill=grey(0), anchor="lt")
        d.text((x, cy - int(2 * s)), f"{when:%a %-d %b}", font=small, fill=grey(0), anchor="lt")
        d.text((x, cy + int(32 * s)), f"{when:%H:%M} · in {days:.0f} d" if days >= 1 else f"{when:%H:%M} · today",
               font=small, fill=grey(5), anchor="lt")
    return snap_g16(img)


def month(ctx, surface, south):
    """The next four weeks, a row a week: 28 small moons, full and new marked."""
    from datetime import timedelta
    from slowapp_kit import grey, snap_g16
    t = ctx.for_
    img, d, b = _g16_page(ctx, surface, "The next four weeks")
    s = b.s
    x0, x1, y0 = b.left - int(12 * s), b.right if b.board else b.right + int(12 * s), b.top
    cw, rh = (x1 - x0) / 7, (b.bottom - y0) / 4
    r = int(cw * 0.36)
    label, note = kit.font("DejaVuSans.ttf", int(17 * s)), kit.font("DejaVuSans-Bold.ttf", int(15 * s))
    full_at, new_at = phase.next_phase(t, 0.5), phase.next_phase(t, 0.0)
    marks = {}
    for when, word in ((full_at, "FULL"), (new_at, "NEW"), (full_at + timedelta(days=phase.SYNODIC_DAYS), "FULL"),
                       (new_at + timedelta(days=phase.SYNODIC_DAYS), "NEW")):
        marks.setdefault(when.date(), word)
    for i in range(28):
        ti = t + timedelta(days=i)
        cx, top = int(x0 + cw * (i % 7) + cw / 2), int(y0 + rh * (i // 7))
        cy = top + r + int(30 * s)
        if i == 0:   # today, boxed
            d.rounded_rectangle((int(cx - cw / 2) + 2, top + int(4 * s), int(cx + cw / 2) - 2, cy + r + int(40 * s)),
                                radius=int(10 * s), outline=grey(4), width=max(2, int(2 * s)))
        d.text((cx, top + int(10 * s)), f"{ti:%a}", font=label, fill=grey(5), anchor="mt")
        disc(d, cx, cy, r, ti, south, lit=grey(15), dark=grey(3), rim=grey(3))
        d.text((cx, cy + r + int(10 * s)), f"{ti:%-d}", font=label, fill=grey(0), anchor="mt")
        if ti.date() in marks:
            d.text((cx, cy + r + int(34 * s)), marks[ti.date()], font=note, fill=grey(4), anchor="mt")
    return snap_g16(img)


def year(ctx, surface, south):
    """The full and new moons of the next twelve months, as a table."""
    from datetime import timedelta
    from slowapp_kit import grey, snap_g16
    t = ctx.for_
    img, d, b = _g16_page(ctx, surface, "Full and new moons ahead")
    s = b.s
    row, head = kit.font("DejaVuSans.ttf", int(22 * s)), kit.font("DejaVuSans-Bold.ttf", int(20 * s))
    full_at, new_at = phase.next_phase(t, 0.5), phase.next_phase(t, 0.0)
    month = timedelta(days=phase.SYNODIC_DAYS)
    x, xn = b.left, b.left + int(256 * s)
    d.text((x + int(44 * s), b.top), "Full moon", font=head, fill=grey(0), anchor="lt")
    d.text((xn, b.top), "New moon", font=head, fill=grey(0), anchor="lt")
    first = b.top + int(48 * s)
    rh, rr = (b.bottom - first) // 12, int(14 * s)
    for k in range(12):
        f, n = full_at + month * k, new_at + month * k
        y = first + k * rh
        disc(d, x + int(16 * s), y + int(13 * s), rr, f + timedelta(minutes=1), south, lit=grey(15), dark=grey(3),
             rim=grey(3), rim_w=1)
        d.text((x + int(44 * s), y), f"{f:%a %-d %b %y}", font=row, fill=grey(0), anchor="lt")
        d.text((xn, y), f"{n:%a %-d %b %y}", font=row, fill=grey(4), anchor="lt")
    return snap_g16(img)
