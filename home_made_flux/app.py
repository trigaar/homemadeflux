from __future__ import annotations

import sys
import tkinter as tk

from home_made_flux.ui.main_window import MainWindow
from home_made_flux.services.geolocation import GeolocationService
from home_made_flux.services.geocoding import GeocodingService
from home_made_flux.services.suntime import SunTimeService
from home_made_flux.util.config import AppConfig, load_config
from home_made_flux.util.logging_setup import setup_logging
from home_made_flux.windows.nightlight import NightLightController


def main() -> int:
    logger = setup_logging()
    config = load_config()
    logger.info("Loaded configuration")

    root = tk.Tk()
    MainWindow(
        root=root,
        config=config,
        geolocation=GeolocationService(logger),
        geocoding=GeocodingService(logger),
        suntime=SunTimeService(logger),
        nightlight=NightLightController(logger),
        logger=logger,
    )
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
