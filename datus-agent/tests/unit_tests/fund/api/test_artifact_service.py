"""Tests for fund artifact service helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from datus_fund.api import artifact_service

_SAMPLE_APP_JSX = "import React from 'react';\nexport default function App() { return null; }\n"


def _write_manifest(root: Path, slug: str, manifest: dict) -> Path:
    artifact_dir = root / "dashboards" / slug
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return artifact_dir


@pytest.mark.asyncio
async def test_list_dashboards_empty_when_no_dashboards_dir(tmp_path: Path):
    result = await artifact_service.list_dashboards(project_files_root=tmp_path)

    assert result.success is True
    assert result.data == []


@pytest.mark.asyncio
async def test_list_dashboards_returns_single_dashboard(tmp_path: Path):
    _write_manifest(
        tmp_path,
        "demo",
        {
            "slug": "demo",
            "name": "Demo Dashboard",
            "description": "Just a demo",
            "kind": "dashboard",
            "created_at": "2026-05-20T00:00:00Z",
        },
    )

    result = await artifact_service.list_dashboards(project_files_root=tmp_path)

    assert result.success is True
    assert len(result.data) == 1
    assert result.data[0].slug == "demo"
    assert result.data[0].name == "Demo Dashboard"
    assert result.data[0].kind == "dashboard"


@pytest.mark.asyncio
async def test_list_dashboards_returns_multiple_sorted_by_recency(tmp_path: Path):
    _write_manifest(
        tmp_path,
        "old",
        {
            "slug": "old",
            "name": "Old Dashboard",
            "description": "An older dashboard",
            "kind": "dashboard",
            "created_at": "2026-01-01T00:00:00Z",
        },
    )
    _write_manifest(
        tmp_path,
        "newer",
        {
            "slug": "newer",
            "name": "Newer Dashboard",
            "description": "More recent",
            "kind": "dashboard",
            "created_at": "2026-06-01T00:00:00Z",
            "updated_at": "2026-06-01T12:00:00Z",
        },
    )

    result = await artifact_service.list_dashboards(project_files_root=tmp_path)

    assert result.success is True
    assert [manifest.slug for manifest in result.data] == ["newer", "old"]


@pytest.mark.asyncio
async def test_list_dashboards_skips_corrupt_manifest(tmp_path: Path):
    _write_manifest(
        tmp_path,
        "good",
        {
            "slug": "good",
            "name": "Good Dashboard",
            "description": "Valid manifest",
            "kind": "dashboard",
            "created_at": "2026-05-20T00:00:00Z",
        },
    )
    bad_dir = tmp_path / "dashboards" / "bad"
    bad_dir.mkdir(parents=True, exist_ok=True)
    (bad_dir / "manifest.json").write_text("{not-json", encoding="utf-8")

    result = await artifact_service.list_dashboards(project_files_root=tmp_path)

    assert result.success is True
    assert [manifest.slug for manifest in result.data] == ["good"]


@pytest.mark.asyncio
async def test_list_dashboards_skips_dir_without_manifest(tmp_path: Path):
    _write_manifest(
        tmp_path,
        "good",
        {
            "slug": "good",
            "name": "Good Dashboard",
            "description": "Valid manifest",
            "kind": "dashboard",
            "created_at": "2026-05-20T00:00:00Z",
        },
    )
    orphan = tmp_path / "dashboards" / "orphan"
    orphan.mkdir(parents=True, exist_ok=True)
    (orphan / "render").mkdir(exist_ok=True)
    (orphan / "render" / "app.jsx").write_text(_SAMPLE_APP_JSX, encoding="utf-8")

    result = await artifact_service.list_dashboards(project_files_root=tmp_path)

    assert result.success is True
    assert [manifest.slug for manifest in result.data] == ["good"]
