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
│   │   ├── sql/            # SQL 控制台组件
│   │   └── ui/             # 通用 UI 组件
│   ├── composables/        # Vue Composables
│   │   ├── useAuth.ts      # 认证逻辑
│   │   ├── useChatWorkspace.ts
│   │   ├── useConnection.ts
│   │   └── ...
│   ├── lib/                # 工具函数
│   ├── App.vue             # 应用入口
│   ├── main.ts             # 主入口文件
│   └── types.ts            # 类型定义
├── .env                    # 环境变量配置
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

## 认证机制

### 认证流程

1. **页面加载**：用户访问应用时，`App.vue` 会调用 `useAuth` composable 进行身份验证
2. **获取 Token**：优先从环境变量 `VITE_DEV_ACCESS_TOKEN` 获取（开发环境），其次从 Cookie 中的 `access_token` 获取
3. **验证身份**：调用用户详情接口验证 Token 有效性
4. **处理结果**：
   - 认证成功：显示主应用界面
   - 认证失败：跳转到登录页

### 环境变量配置

在 `.env` 文件中配置以下变量：

```env
# 获取用户详情接口（自行配置）
VITE_AUTH_API_URL=https://your/userinfo

# 登录页跳转地址（自行配置）
VITE_AUTH_LOGIN_URL=https://your/token

# 开发环境测试用 access_token（优先级高于 cookie）
# 生产环境请留空或删除此项
VITE_DEV_ACCESS_TOKEN=
```

### 认证接口说明

**获取用户详情接口**

- **URL**: `VITE_AUTH_API_URL`
- **Method**: `GET`
- **Headers**:
  - `Authorization`: `Bearer {access_token}`
  - `Content-Type`: `application/x-www-form-urlencoded`

**成功响应示例**:

```json
{
  "userId": 698,
  "username": "x_liuyanping",
  "realname": "刘延平",
  "email": "x_liuyanping@phfund.com.cn",
  "userStatus": "正常",
  "permissionList": []
}
```

**认证失败条件**：

- Cookie 中无 `access_token` 且环境变量中无测试 Token
- 接口返回为空

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

- **对话 (Chat)**: 与 AI Agent 进行自然语言交互
- **知识库 (Knowledge)**: 管理和浏览知识库内容
- **MCP**: Model Context Protocol 工具管理
- **SQL 控制台**: 执行 SQL 查询
- **仪表盘 (Dashboard)**: 数据可视化
- **报告 (Report)**: 生成和查看报告
