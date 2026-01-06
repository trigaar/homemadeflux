from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests


SUN_API_URL = "https://api.sunrise-sunset.org/json"


@dataclass
class SunTimes:
    sunrise: datetime
    sunset: datetime


class SunTimeService:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger.getChild("suntime")

    def fetch(self, latitude: float, longitude: float) -> Optional[SunTimes]:
        params = {"lat": latitude, "lng": longitude, "formatted": 0}
        try:
            response = requests.get(SUN_API_URL, params=params, timeout=8)
            if response.status_code != 200:
                self.logger.warning("Sun time lookup failed: status %s", response.status_code)
                return None
            payload = response.json()
            results = payload.get("results")
            if not results:
                self.logger.warning("Sun time API returned no results")
                return None
            sunrise = datetime.fromisoformat(results["sunrise"])
            sunset = datetime.fromisoformat(results["sunset"])
            # Convert to local time for comparison.
            local_tz = datetime.now().astimezone().tzinfo or timezone.utc
            sunrise_local = sunrise.astimezone(local_tz)
            sunset_local = sunset.astimezone(local_tz)
            return SunTimes(sunrise=sunrise_local, sunset=sunset_local)
        except Exception as exc:
            self.logger.warning("Sun time lookup error: %s", exc)
            return None

    def fallback(self) -> SunTimes:
        """Return a sensible default if network is unavailable."""
        now = datetime.now().astimezone()
        sunrise = now.replace(hour=7, minute=0, second=0, microsecond=0)
        sunset = now.replace(hour=19, minute=0, second=0, microsecond=0)
        if sunrise > sunset:
            sunset -= timedelta(days=1)
        return SunTimes(sunrise=sunrise, sunset=sunset)
