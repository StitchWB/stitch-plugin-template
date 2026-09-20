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
pip install pytest pytest-timeout
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
# one-time keypair (keep the private key offline):
python -m stitch_plugin_tools keygen --out keys/
python -m stitch_plugin_tools sign . --key keys/private.key
```

### 6. Dev-install and run

```bash
python -m stitch_plugin_tools dev-install .
STITCH_DEV_MODE=1 python -m stitch_backend
```

The plugin appears as a tab in the AI Hub; commands are callable as
`plugin.my-plugin.<command>`.

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
