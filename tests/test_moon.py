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
    """On the Slowboard 470 the board draws its key labels, their lane and the app strip over the
    card: every full card leaves them blank."""
    AREAS = [(336, 16, 144, 120), (480, 0, 60, 340), (0, 900, 540, 60)]

    def test_the_full_deck_leaves_the_boards_areas_blank(self):
        from types import SimpleNamespace
        from PIL import Image
        from slowapp_kit import grey
        from moon import draw
        t = datetime(2026, 11, 18, 10, tzinfo=timezone(timedelta(hours=-7)))
        ctx = SimpleNamespace(for_=t, now=t, canvas=lambda s, fill: Image.new("RGB", (s.w, s.h), fill))
        surface = SimpleNamespace(w=540, h=960, inks="g16")
        for f in (draw.full, draw.phases, draw.month, draw.year):
            img = f(ctx, surface, False).convert("RGB")
            for x, y, w, h in self.AREAS:
                colours = img.crop((x, y, x + w, y + h)).getcolors()
                self.assertEqual(colours, [(w * h, grey(15))], f"{f.__name__}: something in {(x, y, w, h)}")


if __name__ == "__main__":
    unittest.main()
