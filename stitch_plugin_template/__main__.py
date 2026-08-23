"""RPC entry point for the stitch-plugin-template service plugin.

Spawned by ``ServicePluginHost`` as ``python -m stitch_plugin_template``.
Implements the JSON-RPC 2.0 line protocol via ``RpcPluginServer``.

Protocol methods handled automatically by ``RpcPluginServer``:
  - ``plugin.init``    -> stores handshake params via ``_Ctx``.
  - ``plugin.ping``    -> returns ``"pong"``.
  - ``plugin.shutdown``-> returns ``None`` and exits.

``plugin.call`` dispatches to registered handlers.  ``_migrate_db``
is a reserved call name used by the host after init to create SQLite
tables (when ``contributions.storage.migrations`` is set).

Standalone: tries to import ``RpcPluginServer`` from
``autoreg.plugin.rpc`` (available when ``autoreg`` is on ``sys.path``).
If the import fails (standalone plugin without the host's python tree),
a vendored equivalent is loaded from ``._vendor.rpc_server`` — same
protocol, no external dependency.  The vendored module is regenerated
by ``stitch_plugin_tools dev-install`` / ``vendor``.
"""

# _generated_by: stitch_plugin_tools scaffold v3

from __future__ import annotations

from typing import Any

from . import service, storage

try:
    from autoreg.plugin.rpc import RpcPluginServer
except ImportError:
    from ._vendor.rpc_server import RpcPluginServer


# ── State received in plugin.init handshake ───────────────────────────────


class _Ctx:
    """Mutable container for plugin.init handshake state."""

    db_path: str = ""
    data_dir: str = ""
    supported: list[str] = []


ctx = _Ctx()


def _uid(params: dict[str, Any]) -> int | None:
    """Caller user id forwarded by the dual-format router (None = guest)."""
    uid = params.get("caller_user_id")
    return int(uid) if uid is not None else None


def _handle_init(params: dict[str, Any]) -> dict[str, Any]:
    """Store handshake params and return them as the init result.

    ``supported`` lists the optional host features available in this
    session (e.g. ``reverse_rpc``, ``caller_identity``).  Declare the
    plugin's own opt-in features in the ``capabilities`` result field
    (e.g. ``["reverse_rpc"]`` when using ``server.call_host``).
    """
    ctx.db_path = str(params.get("db_path", ""))
    ctx.data_dir = str(params.get("data_dir", ""))
    supported = params.get("supported")
    ctx.supported = list(supported) if isinstance(supported, list) else []
    return {
        "plugin_id": params.get("plugin_id", ""),
        "db_path": ctx.db_path,
        "data_dir": ctx.data_dir,
        "capabilities": [],
    }


def _handle_migrate_db(params: dict[str, Any]) -> dict[str, Any]:
    """Create SQLite tables (raw_sql migration).

    For plugins with ``contributions.storage.sqlite = false`` (e.g.
    cards/opencode/radar), use the no-op variant that returns the
    version ack without touching the database::

        return {
            "from_version": params.get("from_version", 0),
            "to_version": params.get("to_version", 1),
        }
    """
    if ctx.db_path:
        storage.migrate(ctx.db_path)
    return {
        "from_version": params.get("from_version", 0),
        "to_version": params.get("to_version", 1),
    }


def _handle_health_check(params: dict[str, Any]) -> dict[str, Any]:
    """Health-check command — returns pong."""
    return service.health_check()


def _handle_echo(params: dict[str, Any]) -> dict[str, Any]:
    """Echo the ``text`` param back to the caller."""
    _uid(params)  # caller identity available for per-user logic
    return service.echo(str(params.get("text", "")))


# ── Server entry point ────────────────────────────────────────────────────

def main() -> None:
    """Register handlers and serve the JSON-RPC loop."""
    server = RpcPluginServer()
    server.set_init_handler(_handle_init)
    server.register("_migrate_db", _handle_migrate_db)
    server.register("health_check", _handle_health_check)
    server.register("echo", _handle_echo)
    server.serve()


if __name__ == "__main__":
    main()
