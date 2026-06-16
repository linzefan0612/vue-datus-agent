"""Fund artifact listing and HTML rendering helpers."""

from __future__ import annotations

import asyncio
import datetime as _dt
import html
import json
from pathlib import Path
from typing import List, Optional

from datus.agent.node.visual_artifact._artifact_html_renderer import (
    CDN_BUNDLE_CSS,
    CDN_BUNDLE_JS,
    ArtifactHtmlSpec,
    _copy_offline_assets,
    _escape_for_script_tag,
    _extract_title,
    _read_artifact_files,
    _resolve_dist,
)
from datus.agent.node.visual_artifact.dashboard_html_renderer import (
    _DASHBOARD_SPEC,
    DEFAULT_QUERY_ENDPOINT,
    _escape_js_single_quoted,
)
from datus.agent.node.visual_artifact.report_html_renderer import _REPORT_SPEC
from datus.api.models.base_models import Result
from datus.api.services.dashboard_service import _resolve_dashboard_dir
from datus.api.services.report_service import REPORT_SLUG_RE, _resolve_report_dir
from datus.schemas.artifact_manifest import ArtifactManifest
from datus.schemas.gen_visual_dashboard_models import DASHBOARD_SLUG_RE
from datus.utils.loggings import get_logger

logger = get_logger(__name__)


def _render_artifact_html_str(
    *,
    spec: ArtifactHtmlSpec,
    project_root: Path,
    slug: str,
    dist: Optional[Path] = None,
) -> str:
    """Compile an artifact HTML string without writing ``index.html``."""
    if not spec.slug_regex.fullmatch(slug):
        raise ValueError(f"invalid {spec.kind}_slug {slug!r}; expected to match {spec.slug_regex.pattern}")
    project_root = project_root.resolve()
    artifact_dir = project_root / spec.root_dir_name / slug
    app_jsx_path = artifact_dir / "render" / "app.jsx"
    if not app_jsx_path.is_file():
        raise FileNotFoundError(f"render/app.jsx not found under {artifact_dir}")

    app_jsx = app_jsx_path.read_text(encoding="utf-8")
    files = _read_artifact_files(artifact_dir, spec.artifact_dirs)

    dist_dir = _resolve_dist(dist)
    if dist_dir is not None:
        css_url, js_url = _copy_offline_assets(artifact_dir, dist_dir)
        logger.info("Offline mode: copied web-artifact-render assets from %s", dist_dir)
    else:
        css_url, js_url = CDN_BUNDLE_CSS, CDN_BUNDLE_JS

    template_html = spec.template_path.read_text(encoding="utf-8")
    created_at = _dt.datetime.fromtimestamp(app_jsx_path.stat().st_mtime, tz=_dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    title = _extract_title(app_jsx, slug)
    payload = {
        "slug": slug,
        "title": title,
        "created_at": created_at,
        "files": files,
    }
    payload_json = _escape_for_script_tag(json.dumps(payload, ensure_ascii=False))

    rendered = (
        template_html.replace(spec.data_placeholder, payload_json)
        .replace(spec.title_placeholder, html.escape(title))
        .replace(spec.css_url_placeholder, css_url)
        .replace(spec.js_url_placeholder, js_url)
    )
    for placeholder, value in spec.extra_placeholders.items():
        rendered = rendered.replace(placeholder, value)
    return rendered


async def _list_artifacts(root: Path, kind: str) -> Result[List[ArtifactManifest]]:
    if not await asyncio.to_thread(root.is_dir):
        return Result(success=True, data=[])

    def _scan() -> List[Path]:
        return sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name)

    subdirs = await asyncio.to_thread(_scan)

    manifests: List[ArtifactManifest] = []
    for subdir in subdirs:
        manifest_path = subdir / "manifest.json"
        if not await asyncio.to_thread(manifest_path.is_file):
            continue
        try:
            text = await asyncio.to_thread(manifest_path.read_text, "utf-8")
            manifests.append(ArtifactManifest.model_validate(json.loads(text)))
        except Exception as exc:
            logger.warning("Skipping %s %s: corrupt manifest.json (%s)", kind, subdir.name, exc)

    manifests.sort(key=lambda manifest: manifest.updated_at or manifest.created_at or "", reverse=True)
    return Result(success=True, data=manifests)


async def list_dashboards(*, project_files_root: Path) -> Result[List[ArtifactManifest]]:
    """Enumerate dashboard manifests under ``<project_files_root>/dashboards``."""
    return await _list_artifacts(project_files_root / "dashboards", "dashboard")


async def list_reports(*, project_files_root: Path) -> Result[List[ArtifactManifest]]:
    """Enumerate report manifests under ``<project_files_root>/reports``."""
    return await _list_artifacts(project_files_root / "reports", "report")


async def render_dashboard_html(
    *,
    project_files_root: Path,
    dashboard_slug: str,
    query_endpoint: str,
) -> Result[str]:
    """Compile a dashboard artifact to an HTML string for iframe rendering."""
    dashboard_dir = _resolve_dashboard_dir(project_files_root, dashboard_slug)
    if dashboard_dir is None:
        return Result(
            success=False,
            errorCode="INVALID_DASHBOARD_SLUG",
            errorMessage=f"dashboard_slug must match {DASHBOARD_SLUG_RE.pattern}",
        )

    try:
        spec = ArtifactHtmlSpec(
            kind=_DASHBOARD_SPEC.kind,
            root_dir_name=_DASHBOARD_SPEC.root_dir_name,
            slug_regex=_DASHBOARD_SPEC.slug_regex,
            artifact_dirs=_DASHBOARD_SPEC.artifact_dirs,
            template_path=_DASHBOARD_SPEC.template_path,
            data_placeholder=_DASHBOARD_SPEC.data_placeholder,
            title_placeholder=_DASHBOARD_SPEC.title_placeholder,
            css_url_placeholder=_DASHBOARD_SPEC.css_url_placeholder,
            js_url_placeholder=_DASHBOARD_SPEC.js_url_placeholder,
            extra_placeholders={
                "__DATUS_QUERY_ENDPOINT__": _escape_js_single_quoted(query_endpoint or DEFAULT_QUERY_ENDPOINT),
            },
        )
        html_str = await asyncio.to_thread(
            _render_artifact_html_str,
            spec=spec,
            project_root=project_files_root,
            slug=dashboard_slug,
        )
    except FileNotFoundError:
        return Result(
            success=False,
            errorCode="DASHBOARD_NOT_FOUND",
            errorMessage=f"dashboard {dashboard_slug!r} not found or missing render/app.jsx",
        )
    except ValueError as exc:
        return Result(success=False, errorCode="INVALID_DASHBOARD_SLUG", errorMessage=str(exc))
    except Exception as exc:
        logger.exception("Failed to render HTML for %s: %s", dashboard_slug, exc)
        return Result(success=False, errorCode="DASHBOARD_NOT_FOUND", errorMessage=str(exc))

    return Result(success=True, data=html_str)


async def render_report_html(*, project_files_root: Path, report_slug: str) -> Result[str]:
    """Compile a report artifact to an HTML string for iframe rendering."""
    report_dir = _resolve_report_dir(project_files_root, report_slug)
    if report_dir is None:
        return Result(
            success=False,
            errorCode="INVALID_REPORT_SLUG",
            errorMessage=f"report_slug must match {REPORT_SLUG_RE.pattern}",
        )

    try:
        html_str = await asyncio.to_thread(
            _render_artifact_html_str,
            spec=_REPORT_SPEC,
            project_root=project_files_root,
            slug=report_slug,
        )
    except FileNotFoundError:
        return Result(
            success=False,
            errorCode="REPORT_NOT_FOUND",
            errorMessage=f"report {report_slug!r} not found or missing render/app.jsx",
        )
    except ValueError as exc:
        return Result(success=False, errorCode="INVALID_REPORT_SLUG", errorMessage=str(exc))
    except Exception as exc:
        logger.exception("Failed to render HTML for %s: %s", report_slug, exc)
        return Result(success=False, errorCode="REPORT_NOT_FOUND", errorMessage=str(exc))

    return Result(success=True, data=html_str)
