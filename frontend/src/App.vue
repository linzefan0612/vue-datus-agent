<script setup lang="ts">
import { defineAsyncComponent, onMounted } from "vue";

import ToastContainer from "@/components/ui/ToastContainer.vue";
import TooltipProvider from "@/components/ui/TooltipProvider.vue";
import { useAuth } from "@/composables/useAuth";
import { useChatWorkspace } from "@/composables/useChatWorkspace";

const DeveloperShell = defineAsyncComponent({
  loader: () => import("@/components/layout/DeveloperShell.vue"),
  delay: 200,
  timeout: 30000,
});

const workspace = useChatWorkspace();
const { state: authState, checkAuth } = useAuth();

// 页面加载时执行认证校验
onMounted(() => {
  checkAuth();
});
</script>

<template>
  <!-- 全屏 Loading -->
  <div v-if="authState.loading" class="authLoading">
    <div class="authLoadingContent">
      <div class="authLoadingSpinner"></div>
      <span>正在验证身份...</span>
    </div>
  </div>

  <!-- 主应用 -->
  <TooltipProvider v-else-if="authState.authenticated">
    <div class="shell">
      <DeveloperShell :workspace="workspace" />
    </div>
    <ToastContainer />
  </TooltipProvider>
</template>

<style scoped>
.authLoading {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-color, #0f172a);
  z-index: 9999;
}

.authLoadingContent {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-color, #e2e8f0);
  font-size: 14px;
}

.authLoadingSpinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color, #334155);
  border-top-color: var(--primary-color, #3b82f6);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
