"""Tests for fund datasource restricted connector."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from datus_db_core import BaseSqlConnector

from datus.tools.db_tools.db_manager import get_connection
from datus.utils.exceptions import DatusException
from datus_fund.datasource.restricted_connector import RestrictedSqlConnector


def _connector():
    connector = MagicMock()
    connector.dialect = "postgresql"
    connector.schema_name = "public"
    connector.database_name = "ccks_fund"
    connector.catalog_name = ""
    connector.get_databases.return_value = ["ccks_fund", "other_db"]
    connector.get_schemas.return_value = ["public", "private"]
    connector.get_tables.return_value = ["mf_fundarchives", "mf_netvalue", "mf_awards"]
    connector.get_views.return_value = ["mf_visible_view", "mf_hidden_view"]
    connector.execute_query.return_value = SimpleNamespace(success=True, sql_return=[{"ok": 1}])
    connector.execute.return_value = SimpleNamespace(success=True, sql_return=[{"ok": 1}])
    return connector


def test_get_connection_returns_restricted_single_connector():
    mock_conn = MagicMock(spec=BaseSqlConnector)
    mock_conn.dialect = "postgresql"
    restricted = RestrictedSqlConnector(mock_conn, ["public.orders"])

    result = get_connection(restricted)

    assert result is restricted


def test_filters_table_listing():
    connector = _connector()
    restricted = RestrictedSqlConnector(connector, ["public.mf_fundarchives", "public.mf_netvalue"])

    assert restricted.get_tables(schema_name="public") == ["mf_fundarchives", "mf_netvalue"]


def test_filters_database_listing():
    connector = _connector()
    restricted = RestrictedSqlConnector(connector, allowed_databases=["ccks_fund"])

    assert restricted.get_databases() == ["ccks_fund"]


def test_filters_schema_listing():
    connector = _connector()
    restricted = RestrictedSqlConnector(connector, allowed_schemas=["public"])

    assert restricted.get_schemas(database_name="ccks_fund") == ["public"]


def test_schema_restriction_filters_tables():
    connector = _connector()
    restricted = RestrictedSqlConnector(connector, allowed_schemas=["public"])

    assert restricted.get_tables(schema_name="private") == []
    connector.get_tables.assert_not_called()


def test_allows_query_for_allowed_table():
    connector = _connector()
    restricted = RestrictedSqlConnector(connector, ["public.mf_fundarchives"])

    result = restricted.execute_query("select * from mf_fundarchives", result_format="list")

    assert result.success is True
    connector.execute_query.assert_called_once_with("select * from mf_fundarchives", result_format="list")


def test_rejects_query_for_out_of_scope_table():
    connector = _connector()
    restricted = RestrictedSqlConnector(connector, ["public.mf_fundarchives"])

    result = restricted.execute_query("select * from mf_awards", result_format="list")

    assert result.success is False
    assert "outside datasource allowlist" in result.error
    connector.execute_query.assert_not_called()


def test_rejects_query_for_out_of_scope_schema():
    connector = _connector()
    restricted = RestrictedSqlConnector(connector, allowed_schemas=["private"])

    result = restricted.execute_query("select * from public.mf_fundarchives", result_format="list")

    assert result.success is False
    assert "outside datasource allowlist" in result.error
    connector.execute_query.assert_not_called()


def test_rejects_metadata_schema_query():
    connector = _connector()
    restricted = RestrictedSqlConnector(connector, ["public.mf_fundarchives"])

    result = restricted.execute(
        {"sql_query": "select table_name from information_schema.tables"},
        result_format="list",
    )

    assert result.success is False
    assert "metadata schemas" in result.error
    connector.execute.assert_not_called()


def test_blocks_schema_for_out_of_scope_table():
    connector = _connector()
    restricted = RestrictedSqlConnector(connector, ["public.mf_fundarchives"])

    with pytest.raises(PermissionError):
        restricted.get_schema(schema_name="public", table_name="mf_awards")


def test_get_connection_raises_for_missing_name():
    c1 = MagicMock()

    with pytest.raises(DatusException):
        get_connection({"a": c1, "b": MagicMock()}, "c")
