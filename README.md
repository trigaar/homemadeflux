# home made flux

A lightweight Windows desktop helper that schedules Night Light based on your location and local sunrise/sunset times. It uses a simple Tkinter UI, runs locally, and defaults to a safe **dry-run** mode so it won't modify system settings unless you turn it off on Windows.

## Features
- Auto location via IP lookup or manual city/coordinate input.
- Computes sunrise/sunset and toggles Night Light accordingly (with manual override that resets after the next tick).
- Adjustable strength (0-100) and transition minutes.
- Scheduler runs every few minutes (default 5) and supports an "Apply now" action.
- Persists settings to `config.json`.
- Logging to `./logs/app.log`.

## Quick start
1. Install Python 3.11+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python -m home_made_flux.app
   ```

## Building the Windows executable
From the repository root on Windows:
```bash
pyinstaller --onefile --noconsole --name "home made flux" home_made_flux/app.py
```
The resulting executable will be placed under `dist/`.

## Configuration
The app reads and writes `config.json` in the repository directory. Key options include:
- `location_mode`: `auto` or `manual`
- `manual_location`: either `"lat,long"` or `"City, Country"`
- `night_light_strength`: 0-100
- `transition_minutes`: 0-60
- `schedule_interval_minutes`: scheduler tick interval (minutes)
- `dry_run`: keep enabled for a safe simulation
- `start_at_login`: placeholder toggle for future startup integration

## Known limitations
- Direct Night Light integration is left as a safe placeholder; dry-run logging is the default.
- Network calls (geolocation, geocoding, sunrise/sunset) may fall back to defaults if offline.
- Start-at-login is not yet wired into OS settings.

## Development
- Unit tests:
  ```bash
  python -m unittest
  ```
- Logs live under `./logs/app.log`.

## Repository layout
- `home_made_flux/app.py` – entry point
- `home_made_flux/ui/main_window.py` – Tkinter UI + scheduling glue
- `home_made_flux/core/logic.py` – day/night decision logic
- `home_made_flux/core/scheduler.py` – background scheduler
- `home_made_flux/services/*` – network services (geolocation, geocoding, sun times)
- `home_made_flux/windows/nightlight.py` – safe Night Light controller
- `home_made_flux/util/*` – config and logging helpers
- `build/README.md` – build notes
