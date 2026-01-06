from __future__ import annotations

import logging
import queue
import tkinter as tk
from dataclasses import asdict
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Optional

from home_made_flux.core.logic import FluxLogic, ScheduleDecision
from home_made_flux.core.scheduler import Scheduler, SchedulerResult
from home_made_flux.services.geocoding import GeocodingService
from home_made_flux.services.geolocation import GeolocationService, Location
from home_made_flux.services.suntime import SunTimeService, SunTimes
from home_made_flux.util.config import AppConfig, save_config, update_config
from home_made_flux.windows.nightlight import NightLightController, NightLightState


class MainWindow:
    def __init__(
        self,
        root: tk.Tk,
        config: AppConfig,
        geolocation: GeolocationService,
        geocoding: GeocodingService,
        suntime: SunTimeService,
        nightlight: NightLightController,
        logger: logging.Logger,
    ) -> None:
        self.root = root
        self.config = config
        self.geolocation = geolocation
        self.geocoding = geocoding
        self.suntime = suntime
        self.nightlight = nightlight
        self.logger = logger.getChild("ui")
        self.logic = FluxLogic(transition_minutes=config.transition_minutes)
        self.status_queue: queue.Queue[SchedulerResult] = queue.Queue()

        self.location: Optional[Location] = None
        self.sun_times: Optional[SunTimes] = None

        self._build_ui()
        self.scheduler = Scheduler(
            interval_minutes=self.config.schedule_interval_minutes,
            tick=self._tick,
            callback=self.status_queue.put,
        )
        self.scheduler.start()
        self.root.after(1000, self._process_queue)

    def _build_ui(self) -> None:
        self.root.title("home made flux")
        self.root.geometry("520x420")

        self.location_mode = tk.StringVar(value=self.config.location_mode)
        self.manual_location_var = tk.StringVar(value=self.config.manual_location)
        self.strength_var = tk.IntVar(value=self.config.night_light_strength)
        self.transition_var = tk.IntVar(value=self.config.transition_minutes)
        self.start_login_var = tk.BooleanVar(value=self.config.start_at_login)
        self.dry_run_var = tk.BooleanVar(value=self.config.dry_run)
        self.override_var = tk.StringVar(
            value="auto"
            if self.config.manual_override is None
            else ("on" if self.config.manual_override else "off")
        )

        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        status_frame = ttk.LabelFrame(frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=8)
        self.status_label = ttk.Label(status_frame, text="Night Light: Unknown")
        self.status_label.pack(anchor=tk.W)
        self.next_change_label = ttk.Label(status_frame, text="Next change: --")
        self.next_change_label.pack(anchor=tk.W)
        self.location_label = ttk.Label(status_frame, text="Location: resolving...")
        self.location_label.pack(anchor=tk.W)

        location_frame = ttk.LabelFrame(frame, text="Location", padding=10)
        location_frame.pack(fill=tk.X, pady=8)
        ttk.Radiobutton(
            location_frame, text="Auto (IP-based)", variable=self.location_mode, value="auto"
        ).pack(anchor=tk.W)
        manual_row = ttk.Frame(location_frame)
        manual_row.pack(fill=tk.X, pady=4)
        ttk.Radiobutton(
            manual_row, text="Manual:", variable=self.location_mode, value="manual"
        ).pack(side=tk.LEFT)
        ttk.Entry(manual_row, textvariable=self.manual_location_var, width=35).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Label(manual_row, text="(lat,long or City, Country)").pack(side=tk.LEFT)

        controls_frame = ttk.LabelFrame(frame, text="Controls", padding=10)
        controls_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        strength_row = ttk.Frame(controls_frame)
        strength_row.pack(fill=tk.X, pady=4)
        ttk.Label(strength_row, text="Night Light strength").pack(anchor=tk.W)
        ttk.Scale(
            strength_row,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.strength_var,
        ).pack(fill=tk.X)

        transition_row = ttk.Frame(controls_frame)
        transition_row.pack(fill=tk.X, pady=4)
        ttk.Label(transition_row, text="Transition (minutes)").pack(anchor=tk.W)
        ttk.Scale(
            transition_row,
            from_=0,
            to=60,
            orient=tk.HORIZONTAL,
            variable=self.transition_var,
        ).pack(fill=tk.X)

        override_row = ttk.Frame(controls_frame)
        override_row.pack(fill=tk.X, pady=4)
        ttk.Label(override_row, text="Manual override (resets after next tick)").pack(anchor=tk.W)
        override_options = ttk.Frame(override_row)
        override_options.pack(anchor=tk.W)
        for label, value in [("Follow schedule", "auto"), ("Force On", "on"), ("Force Off", "off")]:
            ttk.Radiobutton(
                override_options,
                text=label,
                value=value,
                variable=self.override_var,
            ).pack(side=tk.LEFT, padx=4)

        toggles_row = ttk.Frame(controls_frame)
        toggles_row.pack(fill=tk.X, pady=4)
        ttk.Checkbutton(toggles_row, text="Start at login (placeholder)", variable=self.start_login_var).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Checkbutton(toggles_row, text="Dry run (recommended)", variable=self.dry_run_var).pack(
            side=tk.LEFT, padx=4
        )

        buttons_row = ttk.Frame(frame)
        buttons_row.pack(fill=tk.X, pady=10)
        ttk.Button(buttons_row, text="Apply now", command=self.apply_now).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons_row, text="Save settings", command=self.save_settings).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(buttons_row, text="Exit", command=self._on_close).pack(side=tk.RIGHT, padx=4)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _parse_override(self) -> Optional[bool]:
        value = self.override_var.get()
        if value == "on":
            return True
        if value == "off":
            return False
        return None

    def _resolve_manual_location(self, text: str) -> Optional[Location]:
        if "," in text:
            try:
                lat_str, lon_str = [piece.strip() for piece in text.split(",", maxsplit=1)]
                return Location(latitude=float(lat_str), longitude=float(lon_str), city=None, country=None)
            except ValueError:
                return None
        geo = self.geocoding.lookup(text)
        if not geo:
            return None
        return Location(latitude=geo.latitude, longitude=geo.longitude, city=geo.display_name, country=None)

    def _resolve_location(self) -> Location:
        if self.location_mode.get() == "manual":
            manual = self._resolve_manual_location(self.manual_location_var.get())
            if manual:
                return manual
        found = self.geolocation.fetch()
        if found:
            return found
        self.logger.info("Falling back to default location (0,0)")
        return Location(latitude=0.0, longitude=0.0, city="Unknown", country=None)

    def _fetch_sun_times(self, location: Location) -> SunTimes:
        sun = self.suntime.fetch(location.latitude, location.longitude)
        if sun:
            return sun
        return self.suntime.fallback()

    def _tick(self) -> SchedulerResult:
        self.location = self._resolve_location()
        self.sun_times = self._fetch_sun_times(self.location)

        now = datetime.now().astimezone()
        manual_override = self._parse_override()
        decision = self.logic.decide(
            now=now,
            sunrise=self.sun_times.sunrise,
            sunset=self.sun_times.sunset,
            target_strength=int(self.strength_var.get()),
            manual_override=manual_override,
        )
        applied = self.nightlight.apply_state(
            NightLightState(enabled=decision.should_enable, strength=decision.target_strength),
            transition_minutes=int(self.transition_var.get()),
            dry_run=self.dry_run_var.get(),
        )
        # Reset override after single use.
        if manual_override is not None:
            self.override_var.set("auto")
        message = f"{decision.reason}; applied={applied}"
        return SchedulerResult(decision=decision, applied=applied, timestamp=now, message=message)

    def _process_queue(self) -> None:
        while not self.status_queue.empty():
            result = self.status_queue.get()
            self._update_status(result.decision, result)
        self.root.after(1000, self._process_queue)

    def _update_status(self, decision: ScheduleDecision, result: SchedulerResult) -> None:
        status_text = f"Night Light: {'ON' if decision.should_enable else 'OFF'} | Strength: {decision.target_strength}"
        self.status_label.config(text=status_text)
        next_change_text = decision.next_change.strftime("%Y-%m-%d %H:%M")
        self.next_change_label.config(text=f"Next change: {next_change_text}")
        location_text = "Unknown"
        if self.location:
            parts = [self.location.city or "Unknown"]
            if self.location.country:
                parts.append(self.location.country)
            location_text = ", ".join([p for p in parts if p])
            location_text += f" ({self.location.latitude:.2f}, {self.location.longitude:.2f})"
        self.location_label.config(text=f"Location: {location_text}")
        self.logger.info("Scheduler tick: %s", result.message)

    def apply_now(self) -> None:
        result = self.scheduler.trigger_once()
        messagebox.showinfo(
            "Applied",
            f"Night Light set to {'ON' if result.decision.should_enable else 'OFF'} "
            f"at strength {result.decision.target_strength}\nReason: {result.decision.reason}",
        )

    def save_settings(self) -> None:
        updates = {
            "location_mode": self.location_mode.get(),
            "manual_location": self.manual_location_var.get(),
            "night_light_strength": int(self.strength_var.get()),
            "transition_minutes": int(self.transition_var.get()),
            "schedule_interval_minutes": self.config.schedule_interval_minutes,
            "start_at_login": self.start_login_var.get(),
            "dry_run": self.dry_run_var.get(),
        }
        self.config = update_config(self.config, updates)
        save_config(self.config)
        messagebox.showinfo("Settings", "Settings saved to config.json")
        self.logger.info("Settings saved: %s", asdict(self.config))

    def _on_close(self) -> None:
        self.scheduler.stop()
        self.root.destroy()
