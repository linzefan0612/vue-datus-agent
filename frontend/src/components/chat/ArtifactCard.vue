<script setup lang="ts">
import { BarChart3, ChevronDown, ExternalLink, FileText } from "@lucide/vue";
import { CollapsibleRoot, CollapsibleTrigger, CollapsibleContent } from "reka-ui";
import { computed, shallowRef } from "vue";

const props = defineProps<{
  kind: string;
  slug: string;
  name: string;
  description?: string;
}>();

const emit = defineEmits<{
  "open-artifact": [kind: string, slug: string];
}>();

const isOpen = shallowRef(true);

const kindLabel = computed(() => (props.kind === "report" ? "报告" : "仪表盘"));
const kindIcon = computed(() => (props.kind === "report" ? FileText : BarChart3));
</script>

<template>
  <CollapsibleRoot :open="isOpen" :data-state="isOpen ? 'open' : 'closed'" class="artifactCard">
    <CollapsibleTrigger as-child>
      <button type="button" class="artifactHeader" @click="isOpen = !isOpen">
        <span class="artifactChevron" aria-hidden="true">
          <ChevronDown :size="16" />
        </span>
        <span class="artifactStatusIcon" aria-hidden="true">
          <component :is="kindIcon" :size="15" />
        </span>
        <span class="artifactHeading">
          <span class="artifactBadge">{{ kindLabel }}</span>
          <span class="artifactName">{{ name }}</span>
        </span>
      </button>
    </CollapsibleTrigger>
    <CollapsibleContent force-mount>
      <div class="artifactBody">
        <p v-if="description" class="artifactDesc">{{ description }}</p>
        <div class="artifactActions">
          <button class="artifactOpenBtn" type="button" @click="emit('open-artifact', kind, slug)">
            <ExternalLink :size="14" />
            在{{ kindLabel }}中打开
          </button>
        </div>
      </div>
    </CollapsibleContent>
  </CollapsibleRoot>
</template>
