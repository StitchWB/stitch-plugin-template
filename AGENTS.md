# AGENTS.md — Stitch Plugin Template

- Lane: **service plugin** (`kind=service`), public repo `StitchWB/stitch-<id>`,
  hub mount `plugins-src/stitch-<id>`. Class/channel is assigned by
  `python -m stitch_plugin_tools classify` — never hand-picked. Provider/autoreg
  plugins are a closed family living in the private hub — not this template.
- Dev loop (needs a python with `stitch_plugin_tools` importable, e.g. the hub venv):
  - `python -m stitch_plugin_tools verify` — runs every gate for this plugin kind
    (ruff, manifest-lint, pytest, classify) and prints the verdict.
  - `python -m stitch_plugin_tools publish --dry-run` — prints channel, submodule
    path, the farm workflow to dispatch and a pre-flight gate checklist. Never
    publishes.
- После verify — commit/push в этот репо. Публикация — CI-ферма StitchWB/stitch-ci,
  manual dispatch:
  `gh workflow run publish-service-plugins.yml --repo StitchWB/stitch-ci -f version=<semver>`.
- Full rules: AGENTS.md + docs/PUBLICATION-POLICY.md of the private hub
  (Stitch-Account-Manager; this machine: `D:\Sources\AI\AI-abusers\IDE-Account-Manager`).
  Protocol: `docs/service-plugins.md` in StitchWB/Stitch-Manager.
