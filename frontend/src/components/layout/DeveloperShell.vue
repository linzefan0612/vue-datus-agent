<script setup lang="ts">
import { computed, defineAsyncComponent, ref, shallowRef, watch } from "vue";
import { Splitpanes, Pane } from "splitpanes";
import "splitpanes/dist/splitpanes.css";

import ChatView from "@/components/chat/ChatView.vue";
import AppSettingsDrawer from "@/components/layout/AppSettingsDrawer.vue";
import Sidebar from "@/components/layout/Sidebar.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import Sheet from "@/components/ui/Sheet.vue";
import SheetContent from "@/components/ui/SheetContent.vue";
import type { ChatWorkspace } from "@/composables/useChatWorkspace";
import type { DeveloperViewType } from "@/types";

const AgentManager = defineAsyncComponent({
  loader: () => import("@/components/agent/AgentManager.vue"),
  delay: 200,
  timeout: 30000,
});
const KnowledgeExplorer = defineAsyncComponent({
  loader: () => import("@/components/knowledge/KnowledgeExplorer.vue"),
  delay: 200,
  timeout: 30000,
});
const SqlConsole = defineAsyncComponent({
  loader: () => import("@/components/sql/SqlConsole.vue"),
  delay: 200,
  timeout: 30000,
});
const McpManager = defineAsyncComponent({
  loader: () => import("@/components/mcp/McpManager.vue"),
  delay: 200,
  timeout: 30000,
});
const DashboardView = defineAsyncComponent({
  loader: () => import("@/components/dashboard/DashboardView.vue"),
  delay: 200,
  timeout: 30000,
});
const ReportView = defineAsyncComponent({
  loader: () => import("@/components/report/ReportView.vue"),
  delay: 200,
  timeout: 30000,
});

const { workspace } = defineProps<{
  workspace: ChatWorkspace;
}>();

const {
  language,
  permissionMode,
  planMode,
  apiBase,
  connection,
  config,
  setApiBase,
  messages,
  sessions,
  selectedSession,
  isStreaming,
  isLoadingSessions,
  selectSession,
  stopSession,
  deleteSession,
  compactSession,
  resumeSession,
  clearMessages,
  agentOptions,
  modelOptions,
  isLoadingModels,
  databaseOptions,
  catalogEntries,
  isLoadingCatalog,
  selectedAgent,
  selectedModel,
  database,
  schema,
  handleSend,
  handleInsert,
  handleRefreshConnection,
  handleDatasourceSwitched,
  setLanguage,
  setPermissionMode,
  setPlanMode,
  setDatabase,
  setSchema,
} = workspace;

const activeView = shallowRef<DeveloperViewType>("chat");

const settingsOpen = shallowRef(false);
const agentManagerOpen = shallowRef(false);

function openSettings() {
  settingsOpen.value = true;
}

// 选择会话时，若当前不在对话模块，自动切换到对话
function handleSelectSession(sessionId: string) {
  selectSession(sessionId);
  if (activeView.value !== "chat") {
    activeView.value = "chat";
  }
}

function openAgentManager() {
  agentManagerOpen.value = true;
}

const sidebarCollapsed = shallowRef(false);
const splitpanesRef = ref<InstanceType<typeof Splitpanes> | null>(null);

const collapsedMinPanePercent = computed(() => Math.ceil((64 / window.innerWidth) * 100));

function onSidebarToggle() {
  sidebarCollapsed.value = !sidebarCollapsed.value;
}

watch(sidebarCollapsed, (collapsed) => {
  const el = splitpanesRef.value?.$el as HTMLElement | null;
  if (!el) return;
  const splitter = el.querySelector(".splitpanes__splitter") as HTMLElement | null;
  if (splitter) {
    splitter.style.pointerEvents = collapsed ? "none" : "";
    splitter.style.cursor = collapsed ? "default" : "";
  }
});

function onPaneResized(payload: { panes: Array<{ size: number }> }) {
  if (payload.panes.length > 0) {
    sidebarCollapsed.value = payload.panes[0].size < 10;
  }
}

function openArtifact(kind: string) {
  activeView.value = kind === "report" ? "report" : "dashboard";
}

const deleteTarget = shallowRef<string | null>(null);
const deletingSession = shallowRef(false);

function requestDeleteSession(sessionId: string) {
  deleteTarget.value = sessionId;
}

async function confirmDeleteSession() {
  if (!deleteTarget.value) return;
  deletingSession.value = true;
  try {
    await deleteSession(deleteTarget.value);
  } finally {
    deletingSession.value = false;
    deleteTarget.value = null;
  }
}
</script>

<template>
  <div class="workspace">
    <Splitpanes vertical ref="splitpanesRef" :style="{ height: '100%' }" @resized="onPaneResized">
      <Pane
        :size="sidebarCollapsed ? collapsedMinPanePercent : 20"
        :min-size="sidebarCollapsed ? collapsedMinPanePercent : 14"
        max-size="34"
      >
        <Sidebar
          :connection="connection"
          :sessions="sessions"
          :selected-session="selectedSession"
          :active-view="activeView"
          :collapsed="sidebarCollapsed"
          :is-loading-sessions="isLoadingSessions"
          :compact-session="compactSession"
          @toggle="onSidebarToggle"
          @refresh-connection="handleRefreshConnection"
          @select-session="handleSelectSession"
          @new-session="clearMessages"
          @open-settings="openSettings"
          @open-agent-manager="openAgentManager"
          @update:active-view="activeView = $event"
          @delete-session="requestDeleteSession"
        />
      </Pane>

      <Pane id="main-content" :size="sidebarCollapsed ? 96 : 80" :min-size="42">
        <ChatView
          v-show="activeView === 'chat'"
          :connection="connection"
          :is-streaming="isStreaming"
          :selected-session="selectedSession"
          :messages="messages"
          :agent-options="agentOptions"
          :model-options="modelOptions"
          :is-loading-models="isLoadingModels"
          :database-options="databaseOptions"
          :catalog-entries="catalogEntries"
          :is-loading-catalog="isLoadingCatalog"
          :selected-agent="selectedAgent"
          :model="selectedModel"
          :database="database"
          :schema="schema"
          :plan-mode="planMode"
          @refresh-connection="handleRefreshConnection"
          @delete-session="selectedSession && requestDeleteSession(selectedSession)"
          @stop-session="stopSession"
          @resume-session="resumeSession()"
          @open-artifact="openArtifact"
          @update:selected-agent="selectedAgent = $event"
          @update:model="selectedModel = $event"
          @update:database="setDatabase($event)"
          @update:schema="setSchema($event)"
          @update:plan-mode="setPlanMode($event)"
          @send="handleSend"
          @insert="handleInsert"
          @stop="stopSession"
        />

        <div v-show="activeView === 'knowledge'" class="knowledgeView">
          <KnowledgeExplorer />
        </div>

        <div v-show="activeView === 'mcp'" class="mcpView">
          <McpManager />
        </div>

        <div v-show="activeView === 'sql'" class="sqlView">
          <SqlConsole />
        </div>

        <div v-show="activeView === 'dashboard'" class="dashboardView">
          <DashboardView />
        </div>

        <div v-show="activeView === 'report'" class="reportView">
          <ReportView />
        </div>
      </Pane>
    </Splitpanes>
  </div>

  <AppSettingsDrawer
    :open="settingsOpen"
    :connection="connection"
    :config="config"
    :api-base="apiBase"
    :language="language"
    :permission-mode="permissionMode"
    :plan-mode="planMode"
    @update:open="settingsOpen = $event"
    @update:api-base="setApiBase"
    @update:language="setLanguage($event)"
    @update:permission-mode="setPermissionMode($event)"
    @update:plan-mode="setPlanMode($event)"
    @refresh-connection="handleRefreshConnection"
    @datasource-switched="handleDatasourceSwitched"
  />

  <Sheet :open="agentManagerOpen" @update:open="agentManagerOpen = $event">
    <SheetContent class="settingsDrawer" side="right" aria-label="Agent 管理">
      <AgentManager />
    </SheetContent>
  </Sheet>

  <ConfirmDialog
    :open="!!deleteTarget"
    title="删除会话"
    :description="deleteTarget ? '确定删除该会话？此操作不可撤销。' : ''"
    confirm-label="删除"
    destructive
    :loading="deletingSession"
    @update:open="deleteTarget = $event ? deleteTarget : null"
    @confirm="confirmDeleteSession"
  />
</template>
