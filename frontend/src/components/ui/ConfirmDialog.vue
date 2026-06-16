<script setup lang="ts">
import {
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogOverlay,
  AlertDialogPortal,
  AlertDialogRoot,
  AlertDialogTitle,
} from "reka-ui";
import { Loader2 } from "@lucide/vue";

import Button from "@/components/ui/Button.vue";

const props = withDefaults(
  defineProps<{
    open: boolean;
    title: string;
    description?: string;
    confirmLabel?: string;
    cancelLabel?: string;
    loading?: boolean;
    destructive?: boolean;
  }>(),
  {
    confirmLabel: "确认",
    cancelLabel: "取消",
    loading: false,
    destructive: false,
  },
);

const emit = defineEmits<{
  "update:open": [value: boolean];
  confirm: [];
}>();
</script>

<template>
  <AlertDialogRoot :open="props.open" @update:open="emit('update:open', $event)">
    <AlertDialogPortal>
      <AlertDialogOverlay class="confirmDialogOverlay" />
      <AlertDialogContent class="confirmDialogContent">
        <AlertDialogTitle class="confirmDialogTitle">{{ title }}</AlertDialogTitle>
        <AlertDialogDescription v-if="description" class="confirmDialogDescription">
          {{ description }}
        </AlertDialogDescription>
        <div class="confirmDialogActions">
          <AlertDialogCancel as-child>
            <Button variant="outline" :disabled="loading">{{ cancelLabel }}</Button>
          </AlertDialogCancel>
          <Button
            :variant="destructive ? 'destructive' : 'default'"
            :disabled="loading"
            @click="emit('confirm')"
          >
            <Loader2 v-if="loading" class="spin" :size="15" />
            {{ confirmLabel }}
          </Button>
        </div>
      </AlertDialogContent>
    </AlertDialogPortal>
  </AlertDialogRoot>
</template>
