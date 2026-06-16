"""Fund artifact extension routes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 所有 datus.* 模块的导入都延迟到函数内部
# 避免任何可能的循环导入问题

if TYPE_CHECKING:
    from pathlib import Path

router = APIRouter(prefix="/api/v1", tags=["fund-artifacts"])


class SwitchDatasourceRequest(BaseModel):
    """Request body for switching the active datasource."""

    name: str


def _get_logger():
    """延迟获取 logger 实例。"""
    from datus.utils.loggings import get_logger

    return get_logger(__name__)


def _project_files_root(svc) -> "Path":
    from pathlib import Path

    return Path(svc.agent_config.project_root)


async def _evict_current_project(project_id: str) -> None:
    from datus.api import deps

    cache = deps._service_cache
    if cache is None:
        return
    try:
        await cache.evict(project_id)
    except Exception:
        _get_logger().exception("Failed to evict service cache for project %s", project_id)


@router.post(
    "/config/datasources/switch",
    response_model=dict,
    summary="Switch Active Datasource",
)
async def switch_datasource(
    body: SwitchDatasourceRequest,
    request: Request,
):
    from datus.api.deps import get_datus_service, get_app_context
    from datus.api.models.base_models import Result
    from datus.utils.exceptions import DatusException, ErrorCode

    svc = await get_datus_service(request)
    ctx = await get_app_context(request)

    config = svc.agent_config
    if body.name not in config.services.datasources:
        raise DatusException(
            ErrorCode.COMMON_FIELD_INVALID,
            message=f"Datasource '{body.name}' not found in services.datasources.",
        )

    from datus.configuration.project_config import ProjectOverride, load_project_override, save_project_override

    current = load_project_override() or ProjectOverride()
    current.default_datasource = body.name
    save_project_override(current)

    await _evict_current_project(ctx.project_id or "default")

    return Result(success=True, data={"current_datasource": body.name}).model_dump()


@router.get("/dashboard/list", summary="List Dashboard Artifacts")
async def list_dashboards(request: Request):
    from datus.api.deps import get_datus_service
    from datus.schemas.artifact_manifest import ArtifactManifest
    from datus_fund.api import artifact_service

    svc = await get_datus_service(request)
    result = await artifact_service.list_dashboards(project_files_root=_project_files_root(svc))
    return result.data or []


@router.get("/dashboard/html", response_class=HTMLResponse, summary="Get Dashboard HTML")
async def get_dashboard_html(
    request: Request,
    slug: str = Query(..., description="Dashboard slug"),
    query_endpoint: str = Query(default="", description="Override query endpoint URL (empty = auto-detect)"),
) -> Response:
    from datus.api.deps import get_datus_service
    from datus_fund.api import artifact_service

    svc = await get_datus_service(request)

    if not query_endpoint:
        base = str(request.base_url).rstrip("/")
        query_endpoint = f"{base}/api/v1/dashboard/query"

    result = await artifact_service.render_dashboard_html(
        project_files_root=_project_files_root(svc),
        dashboard_slug=slug,
        query_endpoint=query_endpoint,
    )
    if not result.success or result.data is None:
        error_html = (
            "<!doctype html><html><body style='font-family:sans-serif;padding:40px;text-align:center'>"
            f"<h2>Dashboard not found</h2><p>{result.errorMessage or 'Unknown error'}</p>"
            "</body></html>"
        )
        return HTMLResponse(content=error_html, status_code=404)
    return HTMLResponse(content=result.data)


@router.get("/report/list", summary="List Report Artifacts")
async def list_reports(request: Request):
    from datus.api.deps import get_datus_service
    from datus.schemas.artifact_manifest import ArtifactManifest
    from datus_fund.api import artifact_service

    svc = await get_datus_service(request)
    result = await artifact_service.list_reports(project_files_root=_project_files_root(svc))
    return result.data or []


@router.get("/report/html", response_class=HTMLResponse, summary="Get Report HTML")
async def get_report_html(
    request: Request,
    slug: str = Query(..., description="Report slug"),
) -> Response:
    from datus.api.deps import get_datus_service
    from datus_fund.api import artifact_service

    svc = await get_datus_service(request)

    result = await artifact_service.render_report_html(
        project_files_root=_project_files_root(svc),
        report_slug=slug,
    )
    if not result.success or result.data is None:
        error_html = (
            "<!doctype html><html><body style='font-family:sans-serif;padding:40px;text-align:center'>"
            f"<h2>Report not found</h2><p>{result.errorMessage or 'Unknown error'}</p>"
            "</body></html>"
        )
        return HTMLResponse(content=error_html, status_code=404)
    return HTMLResponse(content=result.data)
