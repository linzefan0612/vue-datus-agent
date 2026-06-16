<script setup lang="ts">
import ConversationToolbar from "@/components/chat/ConversationToolbar.vue";
import MessageList from "@/components/chat/MessageList.vue";
import ChatComposer from "@/components/chat/ChatComposer.vue";
import type { CatalogRecord, ChatMessage, ConnectionState, SelectOption } from "@/types";

defineProps<{
  connection: ConnectionState;
  isStreaming: boolean;
  selectedSession: string | null;
  messages: readonly ChatMessage[];
  agentOptions: readonly SelectOption[];
  modelOptions: readonly SelectOption[];
  isLoadingModels: boolean;
  databaseOptions: readonly SelectOption[];
  catalogEntries: readonly CatalogRecord[];
  isLoadingCatalog: boolean;
  selectedAgent: string;
  model: string;
  database: string;
  schema: string;
  planMode: boolean;
}>();

const emit = defineEmits<{
  "refresh-connection": [];
  "delete-session": [];
  "stop-session": [];
  "resume-session": [];
  "open-artifact": [kind: string, slug: string];
  "update:selected-agent": [value: string];
  "update:model": [value: string];
  "update:database": [value: string];
  "update:schema": [value: string];
  "update:plan-mode": [value: boolean];
  send: [message: string];
  insert: [message: string];
  stop: [];
}>();
</script>

<template>
  <div class="chatView">
    <div class="chatShell">
      <ConversationToolbar
        :selected-session="selectedSession"
        :connection="connection"
        :is-streaming="isStreaming"
        @refresh-connection="emit('refresh-connection')"
        @delete-session="emit('delete-session')"
        @stop-session="emit('stop-session')"
        @resume-session="emit('resume-session')"
      />
      <MessageList
        :messages="messages"
        :is-streaming="isStreaming"
        :session-id="selectedSession"
        @open-artifact="(kind: string, slug: string) => emit('open-artifact', kind, slug)"
      />
    </div>
    <ChatComposer
      :connection="connection"
      :is-streaming="isStreaming"
      :agent-options="agentOptions"
      :model-options="modelOptions"
      :is-loading-models="isLoadingModels"
      :database-options="databaseOptions"
      :catalog-entries="catalogEntries"
      :is-loading-catalog="isLoadingCatalog"
      :selected-agent="selectedAgent"
      :model="model"
      :database="database"
      :schema="schema"
      :plan-mode="planMode"
      @update:selected-agent="emit('update:selected-agent', $event)"
      @update:model="emit('update:model', $event)"
      @update:database="emit('update:database', $event)"
      @update:schema="emit('update:schema', $event)"
      @update:plan-mode="emit('update:plan-mode', $event)"
      @send="emit('send', $event)"
      @insert="emit('insert', $event)"
      @stop="emit('stop')"
    />
  </div>
</template>
