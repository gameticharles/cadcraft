# CAD Studio

CAD Studio is the CAD program in [Xpress Survey](https://xpresssurveygh.com). It is
[CADCraft](https://github.com/storytold/cadcraft) (MIT OR Apache-2.0, by the ArtCraft team and the
CADCraft contributors) with three changes:

- Xpress Survey's colours: deep green surfaces, an emerald accent, amber points and warnings.
- The name "CAD Studio" wherever the app shows a name. The About window credits CADCraft.
- No update check against CADCraft's releases. CAD Studio's updates come with Xpress Survey.

This branch (`xpress`) holds only the recipe. CADCraft's source is not copied or changed here: each
build checks out a CADCraft release tag and changes it as the recipe says, so following CADCraft
never needs a rebase. CADCraft's own branches are kept as forked and are not built.

| Path | What it does |
| --- | --- |
| `xpress/brand.toml` | Theme token fields, painted colour literals and egui widget colours to set |
| `xpress/rename.toml` | The name change: where it applies, the names kept (fonts, plotters), the About text |
| `xpress/fonts.toml` | Fonts supplied by Xpress Survey (web: font files it sends; desktop: `CADCRAFT_BUNDLED_FONTS`) |
| `xpress/jobs.toml` | SAVEJOB and `xpress.state`, for drawings opened from Xpress Survey's jobs |
| `xpress/embed.toml` | `?embed`: CAD Studio inside a job's page (no menus, SAVE to the job), and xdata in queries |
| `xpress/devices.toml` | No larger textures than the device has, so phones that report less still start |
| `xpress/transform.py` | Applies them all to a CADCraft checkout; fails when any rule finds nothing to change |
| `.github/workflows/build.yml` | Builds the web zip and the desktop programs, and publishes a release |
| `.github/workflows/sync.yml` | Each Monday, builds CADCraft's latest release if it has no CAD Studio build yet |

## Releases

Tags are `v<CADCraft version>-xs.<n>`, as in `v0.20.1-xs.1`; `n` counts CAD Studio builds of that
CADCraft release. Each release has:

- `cadcraft-web-<version>.zip`: the browser build. Xpress Survey pins it in
  `cadcraft/cadcraft.lock.json` and serves it at `/cadcraft/`.
- `cad-studio-<version>-<target>.tar.gz` (`.zip` on Windows): the desktop program for
  `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`, `x86_64-pc-windows-msvc`,
  `aarch64-pc-windows-msvc` and `universal-apple-darwin`, with the licences and a list of the files
  the transform changed. The programs are not signed.
- `SHA256SUMS.txt`.

The desktop programs are built for speed: fat LTO, one codegen unit, and x86-64-v2 on x86_64.

## Trying the recipe locally

```sh
git clone https://github.com/storytold/cadcraft cadcraft-src
git -C cadcraft-src checkout v0.20.1
python3 xpress/transform.py cadcraft-src --check   # what would change
python3 xpress/transform.py cadcraft-src           # change it
cd cadcraft-src && cargo run --release -p cadcraft
```

Python 3.11 or newer. When a new CADCraft release moves something the recipe changes, the
transform names each rule it could not place and changes nothing; update the rule in
`brand.toml` or `rename.toml`.

## Licence

As CADCraft: MIT OR Apache-2.0, at your option (`LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE`).
CAD Studio is not affiliated with the ArtCraft team or with Autodesk, Inc.
