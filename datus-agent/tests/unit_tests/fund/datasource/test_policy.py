"""Tests for downstream fund datasource policy extension."""

from types import SimpleNamespace
from unittest.mock import MagicMock


def test_apply_datasource_policy_wraps_connector_when_allowlist_configured():
    from datus_fund.datasource.policy import apply_datasource_policy
    from datus_fund.datasource.restricted_connector import RestrictedSqlConnector

    connector = MagicMock()
    connector.dialect = "postgresql"
    connector.database_name = "ccks_fund"
    connector.schema_name = "public"
    config = SimpleNamespace(
        extra={
            "allowed_databases": ["ccks_fund"],
            "allowed_schemas": ["public"],
            "allowed_tables": ["public.orders"],
        }
    )

    result = apply_datasource_policy(connector, config)

    assert isinstance(result, RestrictedSqlConnector)
    assert result.raw_connector is connector
    assert result.allowed_databases == ["ccks_fund"]
    assert result.allowed_schemas == ["public"]
    assert result.allowed_tables == ["public.orders"]


def test_apply_datasource_policy_returns_connector_without_allowlist():
    from datus_fund.datasource.policy import apply_datasource_policy

    connector = MagicMock()
    config = SimpleNamespace(extra={})

    assert apply_datasource_policy(connector, config) is connector
