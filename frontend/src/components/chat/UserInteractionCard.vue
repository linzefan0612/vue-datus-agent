<script setup lang="ts">
import { computed, ref, shallowRef } from "vue";
import { md } from "@/lib/markdown";
import Button from "@/components/ui/Button.vue";
import { useChatState } from "@/composables/useChatState";
import type { UserInteractionRequest } from "@/types";

const props = defineProps<{
  sessionId: string;
  interactionKey: string;
  actionType: string;
  requests: ReadonlyArray<UserInteractionRequest>;
  isStreaming?: boolean;
}>();

const loading = shallowRef(false);
const error = shallowRef<string | null>(null);
const succeeded = shallowRef(false);

const { sendInteraction } = useChatState();

// ── Permission content parsing ────────────────────────────────────────────

const TOOL_FRIENDLY_NAMES: Record<string, string> = {
  "filesystem_tools.write_file": "写入文件",
  "filesystem_tools.read_file": "读取文件",
  "filesystem_tools.edit_file": "编辑文件",
  "filesystem_tools.list_directory": "列出目录内容",
  "filesystem_tools.create_directory": "创建目录",
  "filesystem_tools.move_file": "移动文件",
  "filesystem_tools.search_files": "搜索文件",
  "filesystem_tools.get_file_info": "获取文件信息",
  "db_tools.execute_sql": "执行 SQL 查询",
  "db_tools.list_tables": "列出数据表",
  "db_tools.describe_table": "查看表结构",
  "context_search_tools.search_context": "搜索上下文",
};

function friendlyToolName(raw: string): string {
  if (TOOL_FRIENDLY_NAMES[raw]) return TOOL_FRIENDLY_NAMES[raw];
  // mcp.{server}.{tool}
  const mcpMatch = raw.match(/^mcp\.(\w+)\.(.+)$/);
  if (mcpMatch) return `MCP 工具 (${mcpMatch[1]}: ${mcpMatch[2]})`;
  // skills.{name}
  const skillMatch = raw.match(/^skills?\.(.+)$/);
  if (skillMatch) return `技能: ${skillMatch[1]}`;
  // Fallback: replace underscores with spaces, strip category prefix
  const dotIdx = raw.lastIndexOf(".");
  const name = dotIdx >= 0 ? raw.slice(dotIdx + 1) : raw;
  return name.replace(/_/g, " ");
}

interface ParsedPermission {
  isPermission: boolean;
  header: string; // "Permission Request" or "External Filesystem Access"
  toolRaw: string;
  toolFriendly: string;
  argsRaw: string | null;
  pathValue: string | null;
  extraNote: string | null;
}

function parsePermissionContent(content: string): ParsedPermission {
  const notPermission: ParsedPermission = {
    isPermission: false,
    header: "",
    toolRaw: "",
    toolFriendly: "",
    argsRaw: null,
    pathValue: null,
    extraNote: null,
  };

  // Match permission request or external filesystem access
  const headerMatch = content.match(/^###\s*(Permission Request|External Filesystem Access)/m);
  if (!headerMatch) return notPermission;

  const header = headerMatch[1];
  const toolMatch = content.match(/\*\*Tool:\*\*\s*`([^`]+)`/);
  const toolRaw = toolMatch ? toolMatch[1] : "";
  const toolFriendly = friendlyToolName(toolRaw);

  const pathMatch = content.match(/\*\*Path:\*\*\s*`([^`]+)`/);
  const pathValue = pathMatch ? pathMatch[1] : null;

  const argsMatch = content.match(/\*\*Args:\*\*\s*`([^`]*)`/);
  const argsRaw = argsMatch ? argsMatch[1] : null;

  // Extract note like "(outside project root)"
  const noteMatch = content.match(/_\(([^)]+)\)_/);
  const extraNote = noteMatch ? noteMatch[1] : null;

  return { isPermission: true, header, toolRaw, toolFriendly, argsRaw, pathValue, extraNote };
}

/** Extract a meaningful preview from args JSON string. */
function extractArgsPreview(argsRaw: string | null): { key: string; value: string } | null {
  if (!argsRaw) return null;
  try {
    const obj = JSON.parse(argsRaw);
    // Priority: path > file_path > skill_name > query > sql
    for (const key of ["path", "file_path", "skill_name", "query", "sql", "command"]) {
      if (typeof obj[key] === "string" && obj[key].trim()) {
        const val = obj[key];
        return { key, value: val.length > 120 ? val.slice(0, 117) + "..." : val };
      }
    }
  } catch {
    // Not valid JSON, show raw if short enough
    if (argsRaw.length <= 120) return { key: "args", value: argsRaw };
  }
  return null;
}

interface FriendlyRequest {
  parsed: ParsedPermission;
  argsPreview: { key: string; value: string } | null;
  markdownHtml: string | null; // for non-permission content
}

const friendlyRequests = computed<FriendlyRequest[]>(() =>
  props.requests.map((req) => {
    const parsed = parsePermissionContent(req.content);
    if (parsed.isPermission) {
      return { parsed, argsPreview: extractArgsPreview(parsed.argsRaw), markdownHtml: null };
    }
    // Non-permission: render as markdown
    return { parsed, argsPreview: null, markdownHtml: md.render(req.content) };
  })
);

// ── Interaction handling ──────────────────────────────────────────────────

// Per-request selection tracking: { requestIndex: selectedKey }
const selectedKeys = ref<Record<number, string>>({});
// Per-request free text values: { requestIndex: text }
const freeTextValues = ref<Record<number, string>>({});

/** Check if a request should use free text input (no options, allowFreeText). */
function isFreeTextRequest(req: { options: ReadonlyArray<{ key: string; title: string }>; allowFreeText?: boolean }) {
  return req.allowFreeText && req.options.length === 0;
}

// All requests have a selection (either option selected or free text filled)
const allSelected = computed(() => {
  if (props.requests.length === 0) return false;
  return props.requests.every((req, i) => {
    if (isFreeTextRequest(req)) {
      return !!freeTextValues.value[i]?.trim();
    }
    return selectedKeys.value[i] !== undefined;
  });
});

// Disabled when: already loading, already succeeded, or no sessionId
const buttonsDisabled = computed(
  () => loading.value || succeeded.value || !props.sessionId || !props.interactionKey
);

/** Select an option for a specific request. */
function handleSelect(requestIndex: number, key: string) {
  if (buttonsDisabled.value) return;
  selectedKeys.value = { ...selectedKeys.value, [requestIndex]: key };
}

/** Submit all selected answers to the backend. */
async function handleSubmit() {
  if (buttonsDisabled.value || !allSelected.value) return;

  // Build answers array in request order
  const answers: string[][] = props.requests.map((req, i) => {
    if (isFreeTextRequest(req)) {
      const text = freeTextValues.value[i]?.trim() || "";
      return [text];
    }
    const key = selectedKeys.value[i];
    return key ? [key] : [""];
  });

  loading.value = true;
  error.value = null;

  try {
    await sendInteraction(props.interactionKey, answers);
    succeeded.value = true;
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    error.value = msg.includes("task is already running")
      ? "任务仍在运行，请点击停止按钮后重试，或新建会话"
      : `提交失败: ${msg}`;
  } finally {
    loading.value = false;
  }
}

function retry() {
  error.value = null;
  selectedKeys.value = {};
  freeTextValues.value = {};
  succeeded.value = false;
}

const ARG_LABELS: Record<string, string> = {
  path: "路径",
  file_path: "路径",
  skill_name: "技能",
  query: "查询",
  sql: "SQL",
  command: "命令",
  args: "参数",
};
</script>

<template>
  <div class="userInteractionCard">
    <p v-if="actionType === 'confirm'" class="userInteractionLabel">需要确认</p>
    <p v-else class="userInteractionLabel">请选择</p>

    <div v-for="(freq, idx) in friendlyRequests" :key="idx" class="userInteractionRequest">
      <!-- Permission content: structured friendly view -->
      <template v-if="freq.parsed.isPermission">
        <p class="userInteractionContent">
          请求使用工具：<strong>{{ freq.parsed.toolFriendly }}</strong>
          <template v-if="freq.parsed.pathValue">
            <br /><span class="permDetail">{{ freq.parsed.pathValue }}</span>
            <template v-if="freq.parsed.extraNote">
              <span class="permNote">（{{ freq.parsed.extraNote }}）</span>
            </template>
          </template>
          <template v-else-if="freq.argsPreview">
            <br /><span class="permDetail">{{ ARG_LABELS[freq.argsPreview.key] || freq.argsPreview.key }}：{{ freq.argsPreview.value }}</span>
          </template>
        </p>
        <details v-if="freq.parsed.argsRaw" class="permRawDetails">
          <summary>查看原始参数</summary>
          <pre class="permRawArgs">{{ freq.parsed.argsRaw }}</pre>
        </details>
      </template>

      <!-- Non-permission content: render as markdown -->
      <div v-else-if="freq.markdownHtml" class="userInteractionContent markdownBody" v-html="freq.markdownHtml" />

      <div class="userInteractionOptions">
        <button
          v-for="opt in requests[idx].options"
          :key="opt.key"
          class="userInteractionBtn"
          :class="{ selected: selectedKeys[idx] === opt.key }"
          :disabled="buttonsDisabled"
          @click="handleSelect(idx, opt.key)"
        >
          <span v-if="selectedKeys[idx] === opt.key && succeeded" class="checkIcon">✓</span>
          {{ opt.title }}
        </button>
        <!-- Free text input when no options but allowFreeText -->
        <input
          v-if="isFreeTextRequest(requests[idx])"
          v-model="freeTextValues[idx]"
          class="userInteractionInput"
          type="text"
          placeholder="请输入..."
          aria-label="自由文本输入"
          :disabled="buttonsDisabled"
          @keydown.enter="handleSubmit"
        />
      </div>
    </div>

    <!-- Submit button -->
    <div v-if="!succeeded" class="userInteractionSubmit">
      <button
        class="userInteractionBtn submitBtn"
        :disabled="buttonsDisabled || !allSelected"
        @click="handleSubmit"
      >
        提交
      </button>
    </div>

    <p v-if="!sessionId || !interactionKey" class="userInteractionStatus">等待会话信息...</p>
    <p v-else-if="loading" class="userInteractionStatus">提交中...</p>
    <p v-else-if="succeeded" class="userInteractionStatus done">已提交，等待回复...</p>

    <div v-if="error" class="userInteractionError">
      <p>{{ error }}</p>
      <Button variant="outline" size="sm" @click="retry">重试</Button>
    </div>
  </div>
</template>
