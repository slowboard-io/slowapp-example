"""The moon app's entrypoint: `python3 -m moon job render` (the image's ENTRYPOINT and CMD)."""
from datetime import timedelta

import slowapp_kit as kit
from slowapp_kit import Card

from . import draw, phase


@kit.job("render")
def render(ctx):
    south = bool(ctx.settings.get("south"))
    t = ctx.for_
    peek = f"{phase.illumination(t) * 100:.0f}% lit"
    # The board's slot (k4): the moon and the week ahead.
    surface = ctx.feed("phase")
    if surface is not None:
        ctx.write_feed("phase", [
            Card("home", draw.home(ctx, surface, south), phase.name(t), peek=peek),
            Card("week", draw.week(ctx, surface, south), "The week ahead"),
        ], valid_from=t, valid_until=t + timedelta(hours=6))
    # A whole greyscale screen (contract 5, g16) for a thin board: home is what it shows, and its
    # keys step through the rest (the Slowboard 470 keeps the deck and browses it offline).
    surface = ctx.feed("full")
    if surface is not None:
        ctx.write_feed("full", [
            Card("home", draw.full(ctx, surface, south), phase.name(t), peek=peek),
            Card("phases", draw.phases(ctx, surface, south), "The next four phases"),
            Card("month", draw.month(ctx, surface, south), "The next four weeks"),
            Card("year", draw.year(ctx, surface, south), "Full and new moons ahead"),
        ], valid_from=t, valid_until=t + timedelta(hours=6))


kit.main()
