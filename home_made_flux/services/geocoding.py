from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests


GEOCODE_URL = "https://nominatim.openstreetmap.org/search"


@dataclass
class GeoResult:
    latitude: float
    longitude: float
    display_name: str


class GeocodingService:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger.getChild("geocoding")

    def lookup(self, query: str) -> Optional[GeoResult]:
        if not query.strip():
            return None
        params = {"q": query, "format": "json", "limit": 1}
        headers = {"User-Agent": "home-made-flux/0.1"}
        try:
            response = requests.get(GEOCODE_URL, params=params, headers=headers, timeout=8)
            if response.status_code != 200:
                self.logger.warning("Geocoding failed: status %s", response.status_code)
                return None
            payload = response.json()
            if not payload:
                self.logger.info("No geocoding results for query: %s", query)
                return None
            top = payload[0]
            return GeoResult(
                latitude=float(top.get("lat")),
                longitude=float(top.get("lon")),
                display_name=top.get("display_name", query),
            )
        except Exception as exc:
            self.logger.warning("Geocoding error: %s", exc)
            return None
