# Vue Datus Agent

智能数据分析助手全栈项目，由前端 Vue 3 应用和后端 Datus Agent 服务组成。

## 项目概览

本项目为数据分析场景提供完整的 AI Agent 解决方案：

- **前端 (frontend)**: 基于 Vue 3 + TypeScript 构建的现代化 Web 界面
- **后端 (datus-agent)**: 基于 Python 的 AI 数据工程 Agent 服务
- **扩展模块 (datus_fund)**: 面向基金行业的下游扩展，提供 API 接口增强和数据源访问控制

---

## 技术架构

```
vue-datus-agent/
├── frontend/              # Vue 3 前端应用
│   ├── src/
│   │   ├── components/    # UI 组件
│   │   ├── composables/   # 业务逻辑
│   │   └── lib/           # 工具函数
│   └── README.md
│
├── datus-agent/           # Python 后端服务
│   ├── datus/             # 核心模块
│   ├── datus_fund/        # 下游扩展模块
│   └── README.md
│
└── README.md              # 本文件
```

---

## 前端 (frontend)

基于 Vue 3 生态构建的智能数据分析界面。

**技术栈：**
- Vue 3.5 + TypeScript 5.8
- Vite 7 构建工具
- Tailwind CSS 4 样式框架
- ECharts 数据可视化

**核心功能：**
- 对话交互：与 AI Agent 自然语言对话
- 知识库管理：语义模型、指标、参考 SQL
- SQL 控制台：执行查询和数据分析
- 仪表盘/报告：数据可视化展示
- Agent 管理：创建和配置 AI Agent
- MCP 管理：Model Context Protocol 工具配置

**快速开始：**

```bash
cd frontend
npm install
npm run dev
```

📖 **详细文档**: [frontend/README.md](frontend/README.md)

---

## 后端 (datus-agent)

**Datus** 是一个开源的数据工程 Agent，通过领域感知推理、语义搜索和持续学习，将自然语言转换为准确的 SQL。

**当前版本：`0.3.4`**

**核心能力：**
- 构建可演进的上下文：将 Schema、参考 SQL、语义模型、指标等统一为知识库
- 从探索到领域 Agent：支持 CLI 交互、Plan Mode、Subagent 打包
- 指标与语义层：集成 MetricFlow，支持业务指标定义
- 评估框架：内置 BIRD 和 Spider 2.0-Snow 数据集评测

**支持的 LLM 提供商：**
OpenAI、Claude、Gemini、DeepSeek、Qwen、Kimi、OpenRouter 等 10+

**支持的数据库：**
SQLite、DuckDB、PostgreSQL、MySQL、Snowflake、StarRocks、ClickHouse 等 11 种

**使用方式：**

| 接口 | 命令 | 场景 |
|------|------|------|
| CLI | `datus-cli --datasource demo` | 数据工程师探索数据、构建上下文 |
| Web | `datus-cli --web --datasource demo` | 分析师通过浏览器对话 |
| API | `datus-api --datasource demo` | 应用通过 REST 调用 |
| MCP | `datus-mcp --datasource demo` | Claude Desktop、Cursor 等客户端 |

📖 **官方文档**: [Datus Documentation](https://docs.datus.ai/)

---

## 扩展模块 (datus_fund)

`datus_fund` 是 datus-agent 的下游扩展模块，面向特定业务场景提供定制化功能。

**当前实现的功能：**

### API 接口扩展

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/v1/config/datasources/switch` | POST | 切换当前数据源 |
| `/api/v1/dashboard/list` | GET | 列出所有 Dashboard |
| `/api/v1/dashboard/html` | GET | 获取 Dashboard HTML |
| `/api/v1/report/list` | GET | 列出所有 Report |
| `/api/v1/report/html` | GET | 获取 Report HTML |

### 数据源访问控制

支持数据库/Schema/表级别的白名单限制：

```yaml
# agent.yml 配置示例
services:
  datasources:
    mysql_prod:
      type: mysql
      host: localhost
      port: 3306
      database: production
      allowed_databases:
        - "sales_db"
        - "inventory_db"
      allowed_tables:
        - "sales_db.*.orders"
        - "sales_db.public.customers"
```

📖 **详细文档**: [datus-agent/datus_fund/README.md](datus-agent/datus_fund/README.md)

---

## 文档导航

| 模块 | 文档链接 |
|------|----------|
| 前端应用 | [frontend/README.md](frontend/README.md) |
| 后端核心 | [datus-agent/README.md](datus-agent/README.md) |
| 扩展模块 | [datus-agent/datus_fund/README.md](datus-agent/datus_fund/README.md) |

---

## 快速开始

### 1. 初始化项目

```bash
# 克隆仓库
git clone https://github.com/linzefan0612/vue-datus-agent.git
cd vue-datus-agent

# 安装前端依赖
cd frontend && npm install && cd ..

# 安装后端依赖
cd datus-agent && python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -e . && cd ..
```

### 2. 配置环境

```bash
# 前端环境变量
cp frontend/.env.example frontend/.env
# 编辑 .env 文件配置认证和 API 地址

# 后端配置
# 编辑 datus-agent/conf/agent.yml 配置数据源和模型
```

### 3. 启动服务

```bash
# 启动后端 API
cd datus-agent && source .venv/Scripts/activate
datus-api --config ./conf/agent.yml --host 0.0.0.0 --port 8000

# 启动前端（新终端）
cd frontend
npm run dev
```

访问 http://localhost:5173 即可使用。

---

## License

[Apache 2.0](datus-agent/LICENSE)
