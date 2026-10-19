# slowapp-example

A minimal [slowapp](https://github.com/mike-anderson/slowapp-base): the moon's phase for one third of
a Slowboard e-paper dashboard. It needs Pillow only, so it builds on the slim `slowapp-python`
base (1.4.1, contract 4). It has no network, secrets or data: everything comes from the time, so
its fixture is an empty directory. **Use this repo as a template** for a new app.

| File | What it is |
|---|---|
| `slowapp.toml` | The manifest: `network = "none"`, 48 MB, one `render` job, one slot-sized feed `phase`, one setting, two examples, and the catalog page's words (`blurb`, `about`, `ink`, `repo`) ([reference](https://github.com/mike-anderson/slowapp-base/blob/main/MANIFEST.md)) |
| `moon/__main__.py` | The job: `@kit.job("render")` writes a deck of two cards, *home* and *the week ahead* |
| `moon/draw.py` | Drawing in the panel's four inks. Text uses `fontmode = "1"`, because antialiased pixels would fall outside the palette |
| `moon/phase.py` | The arithmetic |
| `Dockerfile` | `FROM` the base, pinned by tag and digest |
| `.github/dependabot.yml` | One weekly PR that bumps the base pin and the workflow ref together, with a three-day cooldown |
| `.github/workflows/app.yml` | Calls slowapp-base's reusable workflow (`@v1.4.1`, the same release as the base): validate, test, render the examples twice, build the catalog bundle, build for armv7, and publish on a `vX.Y.Z` tag with the bundle attached |

## Making your own

1. Click **Use this template**, then rename the module and set `[app] id`, `title`, `image`, the
   catalog words (`blurb`, `about`, `ink`, `repo`) and a `license` (an SPDX expression).
2. Pick the base: `slowapp-python`, or `slowapp-python-sci` if you need numpy or SciPy. Copy the
   pinned `FROM` line from the [latest release](https://github.com/mike-anderson/slowapp-base/releases),
   and set `app.yml`'s workflow ref to the same tag.
3. Set the grants your app needs (`network = "egress"`, `secrets`, `data`, `memory`) and add a
   fixture under `fixtures/` for each example, so CI can render it offline.
4. Push. The workflow's summary shows the rendered cards and their blob ids, and the `catalog`
   artifact holds every example at every slot size.
5. Tag `v0.1.0` to publish. The release notes give the `image@sha256:…` line for `slowhub.toml`.

To run it locally, see the base repo's README.
