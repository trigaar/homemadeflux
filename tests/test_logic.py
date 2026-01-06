import unittest
from datetime import datetime, timezone

from home_made_flux.core.logic import FluxLogic


class FluxLogicTests(unittest.TestCase):
    def setUp(self) -> None:
        self.logic = FluxLogic()
        self.tz = timezone.utc

    def test_is_night_crosses_midnight(self) -> None:
        sunrise = datetime(2024, 1, 1, 7, 0, tzinfo=self.tz)
        sunset = datetime(2023, 12, 31, 18, 0, tzinfo=self.tz)
        self.assertTrue(self.logic.is_night(datetime(2023, 12, 31, 20, 0, tzinfo=self.tz), sunrise, sunset))
        self.assertFalse(self.logic.is_night(datetime(2024, 1, 1, 8, 0, tzinfo=self.tz), sunrise, sunset))

    def test_next_transition_day_to_night(self) -> None:
        now = datetime(2024, 6, 1, 12, 0, tzinfo=self.tz)
        sunrise = datetime(2024, 6, 1, 6, 0, tzinfo=self.tz)
        sunset = datetime(2024, 6, 1, 20, 0, tzinfo=self.tz)
        next_change = self.logic.next_transition(now, sunrise, sunset)
        self.assertEqual(next_change, sunset)

    def test_decide_manual_override(self) -> None:
        now = datetime(2024, 6, 1, 10, 0, tzinfo=self.tz)
        sunrise = datetime(2024, 6, 1, 6, 0, tzinfo=self.tz)
        sunset = datetime(2024, 6, 1, 20, 0, tzinfo=self.tz)
        decision = self.logic.decide(now, sunrise, sunset, target_strength=60, manual_override=True)
        self.assertTrue(decision.should_enable)
        self.assertEqual(decision.target_strength, 60)
        self.assertEqual(decision.reason, "Manual override")


if __name__ == "__main__":
    unittest.main()
