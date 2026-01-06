from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ScheduleDecision:
    should_enable: bool
    target_strength: int
    next_change: datetime
    reason: str


class FluxLogic:
    """Encapsulates the time-of-day logic for Night Light scheduling."""

    def __init__(self, transition_minutes: int = 10) -> None:
        self.transition_minutes = transition_minutes

    @staticmethod
    def is_night(now: datetime, sunrise: datetime, sunset: datetime) -> bool:
        """
        Determine if current time is considered night.

        Args:
            now: Current datetime (timezone-aware preferred).
            sunrise: Today's sunrise datetime.
            sunset: Today's sunset datetime.
        """
        # Handles cases where sunset is before sunrise (crossing midnight).
        if sunrise <= sunset:
            return now < sunrise or now >= sunset
        return sunset <= now < sunrise

    def next_transition(self, now: datetime, sunrise: datetime, sunset: datetime) -> datetime:
        if self.is_night(now, sunrise, sunset):
            # Next change is sunrise (may be next day)
            if sunrise <= now:
                return sunrise + timedelta(days=1)
            return sunrise
        # Daytime -> next change at sunset
        if sunset <= now:
            return sunset + timedelta(days=1)
        return sunset

    def decide(
        self,
        now: datetime,
        sunrise: datetime,
        sunset: datetime,
        target_strength: int,
        manual_override: bool | None = None,
    ) -> ScheduleDecision:
        if manual_override is not None:
            should_enable = manual_override
            reason = "Manual override"
        else:
            should_enable = self.is_night(now, sunrise, sunset)
            reason = "Based on sun times"

        next_change = self.next_transition(now, sunrise, sunset)
        return ScheduleDecision(
            should_enable=should_enable,
            target_strength=target_strength,
            next_change=next_change,
            reason=reason,
        )
