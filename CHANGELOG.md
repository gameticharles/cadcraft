# Changelog

## xs.1 (2026-11-13)

- The recipe: `xpress/transform.py` with `brand.toml` (Xpress Survey's colours, set in CADCraft's
  theme source) and `rename.toml` (CADCraft → CAD Studio in what the app shows; font, plotter and
  settings-folder names kept; About credits CADCraft; no update check against CADCraft's releases).
- `build.yml` builds the web zip and desktop programs for Linux, Windows (x64, arm64) and macOS
  (universal) and publishes `v<CADCraft version>-xs.<n>`; `sync.yml` builds each new CADCraft
  release weekly.
- First build: CADCraft v0.20.1.
