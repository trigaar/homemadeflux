from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests


IP_API_URL = "http://ip-api.com/json/"


@dataclass
class Location:
    latitude: float
    longitude: float
    city: str | None = None
    country: str | None = None


class GeolocationService:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger.getChild("geolocation")

    def fetch(self) -> Optional[Location]:
        try:
            response = requests.get(IP_API_URL, timeout=5)
            if response.status_code != 200:
                self.logger.warning("Geolocation failed: status %s", response.status_code)
                return None
            payload = response.json()
            if payload.get("status") != "success":
                self.logger.warning("Geolocation API error: %s", payload.get("message"))
                return None
            return Location(
                latitude=float(payload.get("lat")),
                longitude=float(payload.get("lon")),
                city=payload.get("city"),
                country=payload.get("country"),
            )
        except Exception as exc:  # Network errors are expected; keep it safe.
            self.logger.warning("Geolocation lookup failed: %s", exc)
            return None
