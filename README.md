# slowapp-example

A minimal [slowapp](https://github.com/mike-anderson/slowapp-base): the moon's phase for one third of
a Slowboard e-paper dashboard. It needs Pillow only, so it builds on the slim `slowapp-python`
base. It has no network, secrets or data: everything comes from the time, so its fixture is an
empty directory. **Use this repo as a template** for a new app.

| File | What it is |
|---|---|
| `slowapp.toml` | The manifest: `network = "none"`, 48 MB, one `render` job, one slot-sized feed `phase`, one setting, two examples ([reference](https://github.com/mike-anderson/slowapp-base/blob/main/MANIFEST.md)) |
| `moon/__main__.py` | The job: `@kit.job("render")` writes a deck of two cards, *home* and *the week ahead* |
| `moon/draw.py` | Drawing in the panel's four inks. Text uses `fontmode = "1"`, because antialiased pixels would fall outside the palette |
| `moon/phase.py` | The arithmetic |
| `Dockerfile` | `FROM` the base, pinned by tag and digest |
| `.github/workflows/app.yml` | Calls slowapp-base's reusable workflow: validate, test, render the examples twice, build for armv7, and publish on a `vX.Y.Z` tag |

## Making your own

1. Click **Use this template**, then rename the module and set `[app] id`, `title` and `image`.
2. Pick the base: `slowapp-python`, or `slowapp-python-sci` if you need numpy or SciPy. Copy the
   pinned `FROM` line from the [latest release](https://github.com/mike-anderson/slowapp-base/releases).
3. Set the grants your app needs (`network = "egress"`, `secrets`, `data`, `memory`) and add a
   fixture under `fixtures/` for each example, so CI can render it offline.
4. Push. The workflow's summary shows the rendered cards and their blob ids.
5. Tag `v0.1.0` to publish. The release notes give the `image@sha256:…` line for `slowbhub.toml`.

To run it locally, see the base repo's README.
