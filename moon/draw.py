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
    """The whole screen in greys (a thin battery board, e.g. the Slowboard 470 at 960x540): the moon
    large on a night panel, the facts beside it, the week below them, and when it was drawn, so a
    device that holds it for hours still says how old it is."""
    from datetime import timedelta
    from slowapp_kit import grey, snap_g16
    t = ctx.for_
    w, h = surface.w, surface.h
    img = ctx.canvas(surface, fill=grey(15))
    d = ImageDraw.Draw(img)
    s = min(w / 960, h / 540)                     # drawn for 960x540; scales with the surface

    # The night panel on the left, the moon in it.
    side = int(w * 0.46)
    d.rectangle((0, 0, side - 1, h - 1), fill=grey(1))
    r = int(min(side, h) * 0.40)
    disc(d, side // 2, h // 2, r, t, south, lit=grey(14), dark=grey(3), rim=grey(7), rim_w=max(2, int(3 * s)))

    # The facts, each line shrunk to fit the column.
    x, right = side + int(36 * s), w - int(28 * s)

    def line(y, text, name, size, fill):
        while size > 12 and d.textlength(text, font=kit.font(name, size)) > right - x:
            size -= 1
        d.text((x, y), text, font=kit.font(name, size), fill=fill, anchor="lt")

    line(int(36 * s), phase.name(t), "DejaVuSans-Bold.ttf", int(44 * s), grey(0))
    line(int(98 * s), f"{phase.illumination(t) * 100:.0f}% lit · day {phase.age(t):.1f} of 29.5",
         "DejaVuSans.ttf", int(26 * s), grey(4))
    full_at, new_at = phase.next_phase(t, 0.5), phase.next_phase(t, 0.0)
    for i, (label, when) in enumerate(sorted([("Full", full_at), ("New", new_at)], key=lambda p: p[1])):
        days = round((when - t) / timedelta(days=1))
        line(int((156 + 38 * i) * s), f"{label} moon {when:%a %-d %b} · {days} d", "DejaVuSans.ttf",
             int(26 * s), grey(0))

    # The week ahead: seven small moons.
    small = kit.font("DejaVuSans.ttf", int(20 * s))
    y = int(290 * s)
    d.line((x, y - int(18 * s), right, y - int(18 * s)), fill=grey(10), width=max(1, int(2 * s)))
    cw = (right - x) / 7
    rr = int(min(cw * 0.38, 26 * s))
    for i in range(7):
        ti = t + timedelta(days=i + 1)
        cx = int(x + cw * i + cw / 2)
        disc(d, cx, y + int(32 * s), rr, ti, south, lit=grey(15), dark=grey(3), rim=grey(3))
        d.text((cx, y + int(70 * s)), f"{ti:%a}", font=small, fill=grey(0), anchor="mt")
        d.text((cx, y + int(96 * s)), f"{ti:%-d}", font=small, fill=grey(5), anchor="mt")

    # When it was drawn: the full-cycle check reads this off the glass.
    d.text((right, h - int(20 * s)), f"drawn {ctx.now:%a %-d %b %H:%M} · for {t:%H:%M}",
           font=small, fill=grey(6), anchor="rb")
    return snap_g16(img)
