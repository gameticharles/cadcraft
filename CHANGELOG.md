# Changelog

## xs.3 (2026-11-14)

- `fonts.toml`: the web build redraws with newly arrived fonts only when a drawing is open. Xpress
  Survey sends its fonts as CAD Studio starts, and the command line said "command `regenall` is not
  available right now: no drawing open".

## xs.2 (2026-11-14)

- `fonts.toml`: the web build takes TrueType and OpenType font files (from its own Open too, and as
  Xpress Survey's page sends its stand-ins for Windows fonts) and registers them under their file
  names; the desktop build reads the folders named in `CADCRAFT_BUNDLED_FONTS`, after every
  installed font.
- The web zip carries `XPRESS-MODIFICATIONS.txt` too (`v0.20.1-xs.1` has it only in the desktop archives).

## xs.1 (2026-11-13)

- The recipe: `xpress/transform.py` with `brand.toml` (Xpress Survey's colours, set in CADCraft's
  theme source) and `rename.toml` (CADCraft → CAD Studio in what the app shows; font, plotter and
  settings-folder names kept; About credits CADCraft; no update check against CADCraft's releases).
- `build.yml` builds the web zip and desktop programs for Linux, Windows (x64, arm64) and macOS
  (universal) and publishes `v<CADCraft version>-xs.<n>`; `sync.yml` builds each new CADCraft
  release weekly.
- First build: CADCraft v0.20.1.
