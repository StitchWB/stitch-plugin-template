---
name: stitch-plugin
description: Authoring Stitch Manager SERVICE plugins (public repos stitch-*, plugins-src mount, kind=service stdio JSON-RPC subprocess, declarative UI v2 + i18n). Use when creating or extending a service plugin from this template: scaffold, manifest contributions, declarative UI, i18n bundles, storage, gates, publishing. The other family (provider/autoreg plugins, closed zone) is authored inside the private Stitch hub - if the task is account farming or autoreg, this is the wrong repo.
---

# Stitch Service Plugin (template)

This template seeds PUBLIC service plugins. Protocol depth lives in
`docs/service-plugins.md` of StitchWB/Stitch-Manager (RPC §2, declarative UI §4,
i18n §5, storage §6, entitlements §7, dev loop §8) - link it, never restate the
manifest schema here: `manifest-lint` is the schema authority.

## Cycle

1. Scaffold (this repo is itself scaffold output; for a fresh plugin elsewhere):
   `$env:PYTHONIOENCODING='utf-8'` first on Windows (cp1251 crashes on CLI emoji),
   then `python -m stitch_plugin_tools new <dir> --id stitch-<id> --kind service`.
2. Implement: `__main__.py` handlers stay thin, `service.py` owns logic,
   `storage.py` owns the plugin sqlite (`contributions.storage` + `_migrate_db`).
   Secrets at rest: Fernet `crypto.py` pattern (reference: stitch-relaycheck).
   Never hand-edit `_vendor/rpc_server.py` - `dev-install`/`vendor` regenerate it.
3. Gates, in this order, red blocks green:
   - `python -m stitch_plugin_tools test <dir>` (or pytest) - green
   - `ruff check` + `ruff format` - clean
   - `python -m stitch_plugin_tools manifest-lint <dir>/plugin.json` - clean:
     every i18n key resolves in BOTH ru and en, every command referenced by a
     UI node is declared, `paramsFrom` targets exist, no dead keys
   - `dev-install` + smoke under `STITCH_DEV_MODE=1`
4. Publish: official publishing runs ONLY via the StitchWB/stitch-ci farm
   workflow "Publish service plugins" with a pinned `-f version=<semver from
   manifest>` (the CalVer default creates a NEW version instead of upserting).
   Locally `publish` is `--dry-run` only. Community submission: signed package
   to `/plugins/submit`, then admin review.

## Gotchas (symptom -> fix)

| Symptom | Fix |
|---|---|
| `UnicodeEncodeError` cp1251 on CLI help | set `PYTHONIOENCODING=utf-8` before any stitch_plugin_tools call |
| manifest-lint: i18n key missing | flat keys never resolve - nest bundles: `{"my": {"key": ...}}` |
| manifest-lint: dead key | wire the key into a node/tab label or drop it |
| unsigned package refused from cache | dev loop uses plugins-local + `STITCH_DEV_MODE=1`; cache needs ed25519 signature |
| UI button/table command does nothing | command missing from `contributions.commands` |
| publish created a new version | pin `-f version=<semver>` on farm dispatch |

## Machine-local

Resolve per machine: a python with `stitch_plugin_tools` importable
(`pip install -e python/` from a Stitch-Manager clone, or run from its
`python/` dir); a hub clone path for docs and dev-install smoke.
