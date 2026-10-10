# Stitch Plugin Template

A GitHub template for building **Stitch Manager service plugins**
(`kind=service`). Generated from the canonical scaffold — create your
repo with **Use this template**, then follow the quickstart below.

## Quickstart

### 1. Rename

Pick a plugin id (`[A-Za-z0-9_-]`, no dots) and rename the pieces:

- repo / directory name → `my-plugin/`
- `plugin.json` → `id`, `name`, `service` fields → `my-plugin`
- `stitch_plugin_template/` package dir → `my_plugin/` (id with `-` → `_`)
- `plugin.json` → `entry.module` → `my_plugin`
- `tests/test_plugin_protocol.py` → `MODULE` / `PLUGIN_ID` constants

### 2. Implement your handlers

- `stitch_plugin_template/service.py` — domain logic.
- `stitch_plugin_template/__main__.py` — register a handler per command
  (`server.register("my_command", _handle_my_command)`).
- `plugin.json` — declare each command under `contributions.commands`,
  UI nodes under `contributions.ui`, and i18n labels under
  `contributions.i18n` (nested under the plugin id).
- `stitch_plugin_template/storage.py` — SQLite schema, migrated via
  `_migrate_db` (set `contributions.storage.sqlite` to `false` if you
  need no database).

### 3. Test

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q --timeout=60
```

`tests/test_plugin_protocol.py` spawns the plugin and drives the raw
JSON-RPC line protocol (init -> ping -> command -> shutdown) with no host
dependency -- copy the pattern for your own commands.

### 4. Run (local REPL, no host boot)

```bash
python -m stitch_plugin_tools run .
```

Spawns the plugin child, streams stderr live, and drives a line-based
REPL on stdin (`<command> [json-params]` -> pretty-printed result).
Built-ins: `ping`, `init-info`, `logs`, `help`, `exit`.  Reverse-RPC
`engine.oauth.*` requests are stubbed (the plugin gets a clear error
instead of hanging).  Try `health_check` and `echo {"text":"hi"}` first.

### 5. Sign

```bash
# one-time keypair (keep the private key outside the package):
python -m stitch_plugin_tools keygen --out ../my-plugin-keys/
python -m stitch_plugin_tools sign . --key ../my-plugin-keys/private.key
```

Packs exclude `keys/` and `*.key` by default and warn at pack time, but a
sibling directory keeps the source tree clean anyway.

### 6. Dev-install and run

```bash
python -m stitch_plugin_tools dev-install .
STITCH_DEV_MODE=1 python -m stitch_backend
```

The plugin appears as a tab in the AI Hub; commands are callable as
`plugin.my-plugin.<command>`.

## Secrets

Plugins read secrets from the process environment (`os.environ`) —
handlers see whatever the host process has. Document your variables in
`env.example` and set them in the shell (or your service manager) that
launches the host. Files whose names start with `.env` are stripped from
publish packs and refused by the publish gate, so local env files never
ship. A host-side keyring API (encrypted at rest, no master-key exposure
to plugins) is on the roadmap — see the issues in
[StitchWB/Stitch-Manager](https://github.com/StitchWB/Stitch-Manager/issues).

## Dependencies

Runtime: **stdlib + vendoring only.** The plugin runs inside the host
interpreter, so `import` resolves against the host environment — a
third-party package you add locally will be missing for other installs.
Ship pure-Python dependencies by vendoring them next to
`stitch_plugin_template/_vendor/`. A per-plugin venv mechanism is tracked in
the public repo issues; until then, keep runtime imports stdlib-only.
Dev tooling (pytest, pytest-timeout, ruff) lives in
`requirements-dev.txt`.

## Data and storage

The host owns the paths: `plugin.init` receives `db_path` (SQLite
database the plugin may create) and `data_dir` (scratch directory).
Never store state inside the package — pack contents are signed and
treated as read-only. Schema changes go through
`stitch_plugin_template/storage.py: migrate()` — declare it in
`contributions.storage.migrations` and the host invokes it as
`_migrate_db` on install and upgrade. For versioned migrations over
existing tables, extend `migrate()` with the `PRAGMA table_info` +
`ALTER TABLE` pattern (see `stitch-relaycheck` for a worked example).

## Long-running commands

Host RPC calls are capped (~30s; ~5s for community/sandbox plugins).
Anything longer must become a job: a `start_<x>_job` command writes a
row into a jobs table and returns `{"jobId": ...}` immediately, a
background thread does the work and updates progress, and `get_job` /
`list_jobs` commands let the UI poll for status. See `stitch-relaycheck`
(`start_audit_job` / `get_job` / `list_jobs`) for the worked pattern. A
native job model (progress notifications, streamed results) is on the
roadmap.

## Release

1. Bump `version` in `plugin.json` (semver) and update
   `contributions.changelog`.
2. Validate locally — the dry-run runs the same gates as the real
   publish (marketplace metadata, UI contributions, env-file refusal):

   ```bash
   python -m stitch_plugin_tools publish-all --dry-run
   ```

3. Sign the package (keys live outside the repo, see §5).
4. Official publishing runs on the CI farm — pin the version so the
   workflow upserts it instead of creating a CalVer one:

   ```bash
   gh workflow run publish-service-plugins.yml --repo StitchWB/stitch-ci -f version=<semver>
   ```

## Protocol notes

- `plugin.init` params carry `supported` — the optional host features
  available in the session (e.g. `reverse_rpc`, `caller_identity`).
- The init result carries `capabilities` — the plugin's opt-in features
  (e.g. `["reverse_rpc"]` when using `server.call_host`). Keep it `[]`
  until you need one.

## Docs

- [Service plugin authoring guide](https://github.com/StitchWB/Stitch-Manager/blob/main/docs/service-plugins.md)
- [Plugin conventions](https://github.com/StitchWB/Stitch-Manager/blob/main/docs/plugin-authoring.md)

## License

MIT — see [LICENSE](LICENSE).
