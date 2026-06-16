"""Tests for downstream fund artifact API extension routes."""

import argparse

from datus.api.service import create_app


def test_fund_artifact_routes_live_in_extension_module():
    from datus_fund.api.routes import router

    route_paths = {route.path for route in router.routes}

    assert "/api/v1/dashboard/list" in route_paths
    assert "/api/v1/dashboard/html" in route_paths
    assert "/api/v1/report/list" in route_paths
    assert "/api/v1/report/html" in route_paths
    assert "/api/v1/config/datasources/switch" in route_paths


def test_create_app_registers_fund_artifact_routes():
    args = argparse.Namespace(config="", datasource="default", output_dir="./output", log_level="INFO")

    app = create_app(args)
    route_paths = {route.path for route in app.routes}

    assert "/api/v1/dashboard/list" in route_paths
    assert "/api/v1/dashboard/html" in route_paths
    assert "/api/v1/report/list" in route_paths
    assert "/api/v1/report/html" in route_paths
    assert "/api/v1/config/datasources/switch" in route_paths
