<script setup lang="ts">
import { defineAsyncComponent } from "vue";
import type { ConfigSummary, ConnectionState } from "@/types";

const SettingsDrawer = defineAsyncComponent({
  loader: () => import("@/components/settings/SettingsDrawer.vue"),
  delay: 200,
  timeout: 30000,
});

defineProps<{
  open: boolean;
  connection: ConnectionState;
  config: ConfigSummary | null;
  apiBase: string;
  language: string;
  permissionMode: string;
  planMode: boolean;
}>();

const emit = defineEmits<{
  "update:open": [value: boolean];
  "update:api-base": [value: string];
  "update:language": [value: string];
  "update:permission-mode": [value: string];
  "update:plan-mode": [value: boolean];
  "refresh-connection": [];
  "datasource-switched": [];
}>();
</script>

<template>
  <SettingsDrawer
    :open="open"
    :connection="connection"
    :config="config"
    :api-base="apiBase"
    :language="language"
    :permission-mode="permissionMode"
    :plan-mode="planMode"
    @update:open="emit('update:open', $event)"
    @update:api-base="emit('update:api-base', $event)"
    @update:language="emit('update:language', $event)"
    @update:permission-mode="emit('update:permission-mode', $event)"
    @update:plan-mode="emit('update:plan-mode', $event)"
    @refresh-connection="emit('refresh-connection')"
    @datasource-switched="emit('datasource-switched')"
  />
</template>
