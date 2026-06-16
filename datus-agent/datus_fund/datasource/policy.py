"""Datasource policy hook for the fund downstream build."""

from __future__ import annotations

from typing import Any, List, Tuple

from datus_db_core import BaseSqlConnector

from datus_fund.datasource.restricted_connector import RestrictedSqlConnector, _normalize_allowed_tables

_DATUS_DATASOURCE_EXTRA_FIELDS = {"allowed_databases", "allowed_schemas", "allowed_tables"}


def resolve_allowed_context(db_config: Any) -> Tuple[List[str], List[str], List[str]]:
    """Return datasource-level database/schema/table allowlists from config."""
    extra = getattr(db_config, "extra", None) or {}
    return (
        _normalize_allowed_tables(extra.get("allowed_databases")),
        _normalize_allowed_tables(extra.get("allowed_schemas")),
        _normalize_allowed_tables(extra.get("allowed_tables")),
    )


def apply_datasource_policy(connector: BaseSqlConnector, db_config: Any) -> BaseSqlConnector | RestrictedSqlConnector:
    """Apply downstream datasource restrictions, returning the original connector when unrestricted."""
    allowed_databases, allowed_schemas, allowed_tables = resolve_allowed_context(db_config)
    if not (allowed_databases or allowed_schemas or allowed_tables):
        return connector
    return RestrictedSqlConnector(
        connector,
        allowed_tables=allowed_tables,
        allowed_databases=allowed_databases,
        allowed_schemas=allowed_schemas,
    )


def filter_adapter_extra_fields(extra: dict[str, Any]) -> dict[str, Any]:
    """Remove Datus-only datasource policy fields before creating adapter configs."""
    return {key: value for key, value in extra.items() if key not in _DATUS_DATASOURCE_EXTRA_FIELDS}
