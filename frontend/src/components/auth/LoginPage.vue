<script setup lang="ts">
import { Loader2, LogIn } from "@lucide/vue";
import Button from "@/components/ui/Button.vue";

defineProps<{
  loading?: boolean;
}>();

const emit = defineEmits<{
  login: [];
}>();
</script>

<template>
  <div class="loginPage">
    <div class="loginCard">
      <div class="loginLogo">
        <h1>Datus</h1>
      </div>
      <p class="loginSubtitle">AI-powered data engineering platform</p>
      <Button
        class="loginButton"
        :disabled="loading"
        @click="emit('login')"
      >
        <Loader2 v-if="loading" class="spin" :size="16" />
        <LogIn v-else :size="16" />
        <span>{{ loading ? "Connecting..." : "SSO Login" }}</span>
      </Button>
    </div>
  </div>
</template>

<style scoped>
.loginPage {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg-primary);
}

.loginCard {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 48px 40px;
  border-radius: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  min-width: 320px;
}

.loginLogo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.loginLogo h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.loginSubtitle {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.loginButton {
  width: 100%;
  justify-content: center;
  gap: 8px;
  height: 44px;
  font-size: 15px;
}
</style>
