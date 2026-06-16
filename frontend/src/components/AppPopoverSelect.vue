<script setup lang="ts">
import { computed, shallowRef, watch } from "vue";
import { ChevronDown, Loader2 } from "@lucide/vue";

import Popover from "@/components/ui/Popover.vue";
import PopoverTrigger from "@/components/ui/PopoverTrigger.vue";
import PopoverContent from "@/components/ui/PopoverContent.vue";
import Command from "@/components/ui/Command.vue";
import CommandEmpty from "@/components/ui/CommandEmpty.vue";
import CommandGroup from "@/components/ui/CommandGroup.vue";
import CommandInput from "@/components/ui/CommandInput.vue";
import CommandItem from "@/components/ui/CommandItem.vue";
import CommandList from "@/components/ui/CommandList.vue";
import { filterSelectOptions } from "@/lib/select-options";
import type { SelectOption } from "@/types";

const props = withDefaults(defineProps<{
  value: string;
  options: readonly SelectOption[];
  disabled?: boolean;
  loading?: boolean;
  placeholder?: string;
  narrow?: boolean;
}>(), {
  placeholder: "请选择",
  narrow: false,
  loading: false
});

const emit = defineEmits<{
  "update:value": [value: string];
}>();

const open = defineModel<boolean>("open", { default: false });
const query = shallowRef("");
const selectedOption = computed(() => props.options.find((o) => o.value === props.value));
const filteredOptions = computed(() => filterSelectOptions(props.options, query.value));

watch(open, (next) => {
  if (!next) query.value = "";
});

const selectOption = (option: SelectOption) => {
  emit("update:value", option.value);
  open.value = false;
};

const clearSelection = () => {
  emit("update:value", "");
  open.value = false;
};
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger>
      <button
        :class="`dbPickerButton ${open ? 'open' : ''}`"
        type="button"
        :disabled="disabled || loading"
        :title="selectedOption?.label ?? placeholder"
        :aria-label="`${placeholder}，当前为 ${selectedOption?.label ?? placeholder}`"
      >
        <Loader2 v-if="loading" class="spin" :size="14" />
        <span :class="{ placeholder: !selectedOption }">{{ loading ? '加载中...' : (selectedOption?.label ?? placeholder) }}</span>
        <ChevronDown v-if="!loading" :size="14" />
      </button>
    </PopoverTrigger>
    <PopoverContent :class="`dbPickerMenu ${narrow ? 'narrow' : ''}`" align="start" side="top" :side-offset="8">
      <Command>
        <CommandInput v-model="query" :placeholder="`搜索${placeholder}`" />
        <CommandList>
          <CommandEmpty v-if="filteredOptions.length === 0">没有匹配项</CommandEmpty>
          <CommandGroup>
            <CommandItem
              v-if="value"
              class="selectCommandItem"
              @select="clearSelection"
            >
              <span>{{ placeholder }}</span>
            </CommandItem>
            <CommandItem
              v-for="option in filteredOptions"
              :key="option.value"
              class="selectCommandItem"
              :class="{ selected: value === option.value }"
              :value="option.value"
              @select="selectOption(option)"
            >
              <span>{{ option.label }}</span>
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>

<style scoped>
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
