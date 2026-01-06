# Build & packaging

Baseline PyInstaller command (run on Windows with Python 3.11+):

```bash
pyinstaller --onefile --noconsole --name "home made flux" home_made_flux/app.py
```

Notes:
- Ensure dependencies are installed: `pip install -r requirements.txt`.
- The build produces a standalone `home made flux.exe` under `dist/`.
- The application is designed to run without administrator privileges; when in doubt, keep **dry run** enabled to avoid touching system settings.

Troubleshooting:
- If geolocation or sunrise/sunset lookups fail, the app falls back to default coordinates and times.
- For logging during build, check `./logs/app.log`.
