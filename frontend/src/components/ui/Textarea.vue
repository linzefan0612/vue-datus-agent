<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import { cn } from "@/lib/utils";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  placeholder?: string;
  rows?: number;
}>();

const modelValue = defineModel<string>({ default: "" });
</script>

<template>
  <textarea
    :placeholder="props.placeholder"
    v-model="modelValue"
    :rows="props.rows ?? 3"
    :class="cn(
      'flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-base shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm',
      props.class
    )"
  />
</template>
