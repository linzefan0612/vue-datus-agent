# Datus Agent Frontend

基于 Vue 3 + TypeScript + Tailwind CSS 构建的智能数据分析助手前端应用。

## 技术栈

- **框架**: Vue 3.5 (Composition API + `<script setup>`)
- **语言**: TypeScript 5.8
- **构建工具**: Vite 7
- **样式**: Tailwind CSS 4
- **UI 组件**: reka-ui (基于 Radix UI 的 Vue 组件库)
- **图表**: ECharts + vue-echarts
- **Markdown 渲染**: markdown-it
- **图标**: Lucide Vue
- **通知**: vue-sonner

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 组件目录
│   │   ├── agent/          # Agent 管理相关组件
│   │   ├── chat/           # 聊天相关组件
│   │   ├── dashboard/      # 仪表盘组件
│   │   ├── knowledge/      # 知识库组件
│   │   ├── layout/         # 布局组件
│   │   ├── mcp/            # MCP 管理组件
│   │   ├── report/         # 报告组件
│   │   ├── settings/       # 设置组件
│   │   ├── sql/            # SQL 控制台组件
│   │   ├── visualization/  # 数据可视化组件
│   │   └── ui/             # 通用 UI 组件
│   ├── composables/        # Vue Composables
│   ├── lib/                # 工具函数和 API
│   ├── types/              # TypeScript 类型定义
│   ├── styles/             # 全局样式
│   ├── App.vue             # 应用入口
│   ├── main.ts             # 主入口文件
│   └── types.ts            # 核心类型定义
├── .env                    # 环境变量配置
├── vite.config.ts          # Vite 配置
└── package.json
```

## 开发命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm run test

# 预览构建结果
npm run preview
```

## 环境变量配置

在 `.env` 文件中配置以下变量：

```env
# ==================== 认证相关配置 ====================

# 是否启用登录认证（生产环境生效）
# false: 不启用登录认证（默认）
# true: 启用登录认证
VITE_AUTH_ENABLED=false

# 获取用户详情接口（自行配置）
VITE_AUTH_API_URL=https://your/userinfo

# 登录页跳转地址（自行配置）
VITE_AUTH_LOGIN_URL=https://your/token

# 开发环境测试用 access_token（优先级高于 cookie）
# 生产环境请留空或删除此项
VITE_DEV_ACCESS_TOKEN=

# ==================== API 配置 ====================

# 后端 API 目标地址（用于开发环境代理）
VITE_DATUS_API_TARGET=http://localhost:8000
```

## 认证机制

### 认证开关

通过 `VITE_AUTH_ENABLED` 环境变量控制是否启用认证：

- `false`（默认）：不启用认证，使用默认用户身份访问
- `true`：启用认证，需要通过登录验证才能访问

### 认证流程

1. **页面加载**：用户访问应用时，`App.vue` 会调用 `useAuth` composable 进行身份验证
2. **检查开关**：如果 `VITE_AUTH_ENABLED=false`，直接使用默认用户，跳过认证
3. **获取 Token**：优先从环境变量 `VITE_DEV_ACCESS_TOKEN` 获取（开发环境），其次从 Cookie 中的 `access_token` 获取
4. **验证身份**：调用用户详情接口验证 Token 有效性
5. **处理结果**：
   - 认证成功：显示主应用界面
   - 认证失败：跳转到登录页

### useAuth Composable

```typescript
import { useAuth } from "@/composables/useAuth";

const { state, checkAuth } = useAuth();

// state 包含:
// - loading: boolean - 加载状态
// - authenticated: boolean - 是否已认证
// - user: UserInfo | null - 用户信息

// 执行认证校验
checkAuth();
```

## 主要功能模块

### 1. 对话 (Chat)

与 AI Agent 进行自然语言交互，支持多种消息类型和交互方式。

**核心组件：**
- `ChatView` - 聊天主视图
- `ChatComposer` - 消息输入框，支持多行输入和快捷操作
- `MessageList` - 消息列表展示
- `MessageContent` - 消息内容渲染（支持 Markdown）
- `ToolCard` - 工具调用卡片展示
- `UserInteractionCard` - 用户交互卡片（选择题、多选题等）
- `ArtifactCard` - 产物卡片（图表、报告等）
- `DatabasePicker` - 数据库选择器
- `FeedbackButtons` - 反馈按钮
- `SuccessStoryButton` - 成功案例保存按钮

**核心功能：**
- 实时 SSE 消息推送
- 工具调用状态展示
- 用户交互式问答
- 会话管理（创建、切换、压缩）
- 多数据库切换

### 2. Agent 管理

创建和管理 AI Agent 配置。

**核心组件：**
- `AgentManager` - Agent 列表管理
- `AgentForm` - Agent 创建/编辑表单

**核心功能：**
- Agent 创建、编辑、删除
- 配置 Agent 工具、MCP、技能
- 设置 Agent 权限和规则
- 配置提示词模板

### 3. 知识库 (Knowledge)

管理和浏览知识库内容，支持语义模型和元数据管理。

**核心组件：**
- `KnowledgeExplorer` - 知识库浏览器主视图
- `CatalogTree` - 目录树
- `TreeNode` - 树节点
- `TableDetailView` - 表详情视图
- `MetricDetailView` - 指标详情视图
- `ReferenceSqlDetailView` - 参考 SQL 详情视图
- `BootstrapDialog` - 知识库引导对话框

**核心功能：**
- 语义模型浏览（表、列、索引）
- 指标管理
- 参考 SQL 管理
- 知识库初始化引导
- 平台文档导入

### 4. SQL 控制台

执行 SQL 查询和管理数据库连接。

**核心组件：**
- `SqlConsole` - SQL 控制台主视图

**核心功能：**
- SQL 查询执行
- 查询结果展示
- 上下文命令支持
- 多数据库切换
- 查询历史记录

### 5. 仪表盘 (Dashboard)

数据可视化展示。

**核心组件：**
- `DashboardView` - 仪表盘视图

**核心功能：**
- 图表展示（柱状图、折线图、饼图、散点图）
- 数据洞察展示
- 仪表盘管理（创建、编辑、删除）

### 6. 报告 (Report)

生成和查看数据分析报告。

**核心功能：**
- 报告生成
- 报告查看和编辑
- 报告导出

### 7. MCP 管理

Model Context Protocol 工具管理。

**核心组件：**
- `McpManager` - MCP 管理器

**核心功能：**
- MCP 服务器配置
- 工具列表展示
- 工具过滤（启用/禁用、白名单/黑名单）

### 8. 设置 (Settings)

应用配置管理。

**核心功能：**
- 数据源配置
- 模型配置
- 连接状态检测
- 主题切换

## 核心 Composables

| Composable | 功能说明 |
|------------|----------|
| `useAuth` | 认证状态管理、登录校验 |
| `useChatWorkspace` | 聊天工作区状态管理 |
| `useChatState` | 聊天消息状态管理 |
| `useChatSettings` | 聊天设置（Agent、数据源选择） |
| `useConnection` | 后端连接状态检测 |
| `useModels` | AI 模型列表管理 |
| `useCatalog` | 数据目录管理 |
| `useAgents` | Agent 列表管理 |
| `useTheme` | 主题切换（亮色/暗色） |

## 类型系统

项目使用 TypeScript 严格类型，核心类型定义在 `src/types.ts` 中：

- `ChatMessage` - 聊天消息
- `MessageBlock` - 消息块（Markdown、工具调用、用户交互等）
- `AgentInfo` / `AgentDetail` - Agent 信息
- `TableDetail` - 表详情
- `SqlExecuteResult` - SQL 执行结果
- `McpServerInfo` / `McpToolInfo` - MCP 相关类型
- `DashboardDetail` / `ReportDetail` - 仪表盘和报告类型

## 开发规范

- 使用 Composition API + `<script setup>` 语法
- 组件命名采用 PascalCase
- Composables 命名采用 `use` 前缀
- 样式使用 Tailwind CSS 工具类
- 类型定义优先使用 `type` 而非 `interface`
