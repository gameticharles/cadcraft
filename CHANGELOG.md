# Changelog

## xs.5 (2026-11-14)

- `devices.toml`: the web build asks the graphics device for no larger textures than it has. eframe asked for
  8192 pixels a side, and a device reporting 4096 for WebGL2 (some phones' browsers) refused it, so CAD Studio
  didn't start there ("Limit 'max_texture_dimension_2d' value 8192 is better than allowed 4096").
- `embed.toml` (not used by Xpress Survey yet): `?embed` in the web build's URL, for CAD Studio inside a job's
  page: no menu bar, Tool Bar, file tabs or Start page, and its panel layout isn't saved. Typed SAVE and QSAVE
  (Ctrl+S) run SAVEJOB; NEW, OPEN, CLOSE, SAVEAS, EXPORT, PLOT, PUBLISH, WBLOCK and the like say they aren't in
  the job's drawing. The page's own calls (`window.cadcraft.execute`) are unchanged.
- `embed.toml`: the `entities` and `drawing.inspect` queries give each entity's xdata (`xdata`: DXF groups), so
  Xpress Survey's page finds the ids it wrote (`1001 XPRESS`).

## xs.4 (2026-11-14)

- `jobs.toml` (applied by `transform.py` after `fonts.toml`): `SAVEJOB`, typed in CAD Studio, asks Xpress
  Survey's page to save the drawing's boundary to the job it was opened from; `xpress.state` tells the page how
  many SAVEJOBs there have been and gives a mark of the active drawing that changes with each edit, undo and
  redo, for the page's running summary of what would change. Both names in the Chinese catalog.

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
