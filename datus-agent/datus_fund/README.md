# datus_fund 下游扩展模块

datus_fund 是 datus-agent 的下游扩展模块，提供 API 接口扩展和数据源访问控制功能。

## 目录结构

```
datus_fund/
├── __init__.py
├── api/                      # API 扩展
│   ├── __init__.py
│   ├── routes.py             # 扩展路由定义
│   └── artifact_service.py   # Dashboard/Report 服务
└── datasource/               # 数据源扩展
    ├── __init__.py
    ├── policy.py             # 数据源访问策略
    └── restricted_connector.py # 受限连接器
```

---

## API 接口

datus_fund 注册了以下 API 接口：

### 1. 切换数据源

```http
POST /api/v1/config/datasources/switch
```

**请求体：**
```json
{
  "name": "datasource_name"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "current_datasource": "datasource_name"
  }
}
```

**功能说明：** 切换当前项目的默认数据源，并刷新服务缓存。

---

### 2. 列出 Dashboard

```http
GET /api/v1/dashboard/list
```

**响应：**
```json
[
  {
    "slug": "sales_overview",
    "name": "销售概览仪表板",
    "description": "展示销售数据的关键指标",
    "kind": "dashboard",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T15:00:00Z",
    "datasources": ["mysql_prod"],
    "key_tables": ["orders", "customers"]
  }
]
```

**功能说明：** 返回项目中所有 Dashboard 的元信息列表。

---

### 3. 获取 Dashboard HTML

```http
GET /api/v1/dashboard/html?slug={dashboard_slug}&query_endpoint={url}
```

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| slug | 是 | Dashboard 的唯一标识 |
| query_endpoint | 否 | SQL 查询端点 URL，默认自动检测 |

**响应：** 返回渲染后的 HTML 页面，可直接嵌入 iframe。

---

### 4. 列出 Report

```http
GET /api/v1/report/list
```

**响应格式同 Dashboard 列表**，`kind` 字段为 `"report"`。

---

### 5. 获取 Report HTML

```http
GET /api/v1/report/html?slug={report_slug}
```

**参数：**
| 参数 | 必填 | 说明 |
|------|------|------|
| slug | 是 | Report 的唯一标识 |

**响应：** 返回渲染后的 HTML 页面。

---

## 数据源访问控制

datus_fund 提供数据源级别的访问控制，支持数据库/Schema/表级别的白名单限制。

### 配置方式

在 `agent.yml` 的数据源配置中添加以下字段：

```yaml
services:
  datasources:
    mysql_prod:
      type: mysql
      host: localhost
      port: 3306
      database: production
      # 访问控制配置
      allowed_databases:
        - "sales_db"
        - "inventory_db"
      allowed_schemas:
        - "public"
        - "analytics"
      allowed_tables:
        - "sales_db.*.orders"
        - "sales_db.*.customers"
        - "inventory_db.public.products"
```

**控制规则：**
- `allowed_databases`: 允许访问的数据库列表
- `allowed_schemas`: 允许访问的 Schema 列表
- `allowed_tables`: 允许访问的表，支持通配符格式 `{database}.{schema}.{table}`

**示例：**
```yaml
services:
  datasources:
    ccks_pg:
      type: postgresql
      host: 127.0.0.1
      port: 5433
      username: datus
      password: datus
      database: ccks_fund
      schema: public
      allowed_databases:
        - ccks_fund
      allowed_schemas:
        - public
      allowed_tables:
        - public.mf_fundarchives
        - public.mf_netvalue
        - public.mf_fundmanagernew
```

当配置了访问控制后，SQL 执行会被拒绝如果引用了白名单之外的表。元数据 Schema（如 `information_schema` 和 `pg_catalog`）的直查也会被阻止。

---

## 接入指南

### 步骤 1：确保 datus_fund 包含在打包配置中

在 `datus-agent/pyproject.toml` 中确认 `datus_fund*` 已包含：

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["datus*", "datus_fund*"]
exclude = ["benchmark*", "docs*"]
```

### 步骤 2：注册路由模块

在 `datus-agent/datus/api/service.py` 的 `_route_modules` 列表中添加 datus_fund 路由：

```python
# datus/api/service.py (约第 482 行)
_route_modules = [
    ("datus.api.routes.chat_routes", "chat"),
    ("datus.api.routes.cli_routes", "cli"),
    # ... 其他路由模块
    ("datus_fund.api.routes", "fund"),  # 添加这一行
]
```

路由会通过动态导入自动注册：

```python
import importlib

for module_path, name in _route_modules:
    try:
        mod = importlib.import_module(module_path)
        app.include_router(mod.router)
    except ImportError:
        logger.info(f"{name} routes not available (module not found)")
```

### 步骤 3：注入数据源策略

在 `datus-agent/datus/tools/db_tools/db_manager.py` 中添加策略导入和应用：

```python
# datus/tools/db_tools/db_manager.py (文件开头)
try:
    from datus_fund.datasource.policy import apply_datasource_policy, filter_adapter_extra_fields
except ImportError:  # datus_fund 未安装时使用默认实现
    def apply_datasource_policy(connector, db_config):
        return connector
    def filter_adapter_extra_fields(extra):
        return dict(extra)


# 在 _build_conn() 方法中应用策略
def _build_conn(self, db_config: DbConfig) -> BaseSqlConnector:
    # ... 创建 connector 的代码
    conn = connector_registry.create_connector(db_config.type, connection_config)
    return apply_datasource_policy(conn, db_config)  # 应用数据源策略
```

### 步骤 4：重新安装包

```bash
cd datus-agent
pip install -e .
```

### 步骤 5：启动服务验证

```bash
# 启动服务
datus-api --config ./conf/agent.yml --host 0.0.0.0 --port 8001

# 验证接口
curl http://localhost:8001/api/v1/dashboard/list
```

---

## 开发注意事项

### 循环导入问题

由于 `datus/api/__init__.py` 会导入 `service` 模块，而 `service.py` 在模块顶层执行 `create_app()`，会导致循环导入。

**解决方案：** 在 `datus_fund/api/routes.py` 中，**禁止在模块顶层导入任何 `datus.api.*` 模块**，所有相关导入必须在函数内部延迟执行。

```python
# ❌ 错误：顶层导入
from datus.api.deps import ServiceDep

# ✅ 正确：函数内延迟导入
async def list_dashboards(request: Request):
    from datus.api.deps import get_datus_service
    svc = await get_datus_service(request)
```

### 清除缓存

部署更新后，建议清除 Python 缓存：

```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
```

---

## 扩展开发

如需添加新的扩展接口：

1. 在 `datus_fund/api/routes.py` 中添加新的路由处理函数
2. 在 `datus_fund/api/artifact_service.py` 中实现业务逻辑
3. 确保所有 `datus.*` 模块导入都在函数内部

**示例：**

```python
@router.get("/custom/endpoint", summary="Custom Endpoint")
async def custom_endpoint(request: Request):
    from datus.api.deps import get_datus_service

    svc = await get_datus_service(request)
    # 业务逻辑
    return {"status": "ok"}
```

---

## 版本兼容性

- datus_fund 与 datus-agent 版本紧密耦合
- 升级 datus-agent 时需同步更新 datus_fund
- 内部 API 可能随 datus-agent 版本变化
