"""Moon app unit tests, run inside the base image by the app workflow (PYTHONPATH=.:/opt/slowapp)."""
import unittest
from datetime import datetime, timedelta, timezone

from moon import phase


class Phase(unittest.TestCase):
    def test_known_moons(self):
        # 2026-10-26 04:12 UTC full moon; 2026-10-10 15:50 UTC new moon (published tables)
        self.assertGreater(phase.illumination(datetime(2026, 10, 26, 4, 12, tzinfo=timezone.utc)), 0.97)
        self.assertLess(phase.illumination(datetime(2026, 10, 10, 15, 50, tzinfo=timezone.utc)), 0.03)

    def test_next_phase_is_ahead_and_within_a_month(self):
        t = datetime(2026, 10, 7, 16, tzinfo=timezone.utc)
        for f in (0.0, 0.5):
            n = phase.next_phase(t, f)
            self.assertTrue(t <= n < t + timedelta(days=phase.SYNODIC_DAYS))



class KeepClear(unittest.TestCase):
    """On the Slowboard 470 the board draws the app strip over the card, so every full card leaves
    it blank; down the right edge, where the keys are, there's only the card's own key hints."""

    def cards(self):
        from types import SimpleNamespace
        from PIL import Image
        from moon import draw
        t = datetime(2026, 11, 18, 10, tzinfo=timezone(timedelta(hours=-7)))
        ctx = SimpleNamespace(for_=t, now=t, canvas=lambda s, fill: Image.new("RGB", (s.w, s.h), fill))
        surface = SimpleNamespace(w=540, h=960, inks="g16")
        fs = (draw.full, draw.phases, draw.month, draw.year)
        return [(f.__name__, draw.key_hints(f(ctx, surface, False), surface, i).convert("RGB")) for i, f in enumerate(fs)]

    def test_the_full_deck_leaves_the_strip_blank(self):
        from slowapp_kit import grey
        for name, img in self.cards():
            self.assertEqual(img.crop((0, 900, 540, 960)).getcolors(), [(540 * 60, grey(15))], name)

    def test_its_key_hints_and_nothing_else_by_the_keys(self):
        from slowapp_kit import grey
        blank = lambda img, box: img.crop(box).getcolors() == [((box[2] - box[0]) * (box[3] - box[1]), grey(15))]  # noqa: E731
        for name, img in self.cards():
            self.assertFalse(blank(img, (470, 188, 540, 212)), f"{name}: no hint by K1")
            self.assertFalse(blank(img, (470, 298, 540, 322)), f"{name}: no hint by K2")
            for box in ((470, 0, 540, 152), (470, 214, 540, 296), (470, 324, 540, 340)):
                self.assertTrue(blank(img, box), f"{name}: something else by the keys {box}")

if __name__ == "__main__":
    unittest.main()
