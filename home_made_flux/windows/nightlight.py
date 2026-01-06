from __future__ import annotations

import logging
import platform
from dataclasses import dataclass


@dataclass
class NightLightState:
    enabled: bool
    strength: int


class NightLightController:
    """
    Safe wrapper around Windows Night Light settings.

    This baseline implementation prioritizes safety: when not running on
    Windows or when dry_run is True, it will log intended actions without
    modifying system settings.
    """

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger.getChild("nightlight")
        self.is_windows = platform.system().lower() == "windows"

    def apply_state(
        self, state: NightLightState, transition_minutes: int, dry_run: bool = True
    ) -> bool:
        """
        Apply the desired Night Light state.

        Returns True if the operation was executed or safely simulated.
        """
        strength = max(0, min(100, state.strength))
        if dry_run or not self.is_windows:
            self.logger.info(
                "[Dry run] Would set Night Light to %s at strength %s (transition %s min)",
                "ON" if state.enabled else "OFF",
                strength,
                transition_minutes,
            )
            return True

        # Placeholder for real Windows integration. Keeping it safe for now.
        self.logger.warning(
            "Attempting to set Night Light to %s at strength %s (transition %s min). "
            "Direct system changes are not implemented in this baseline.",
            "ON" if state.enabled else "OFF",
            strength,
            transition_minutes,
        )
        # Return False to indicate no system change occurred.
        return False
