<script setup lang="ts">
import { computed } from "vue";
import { chatApi } from "@/lib/api";
import { md } from "@/lib/markdown";
import { useConnection } from "@/composables/useConnection";

import type { ChatMessage } from "@/types";

const { effectiveBase } = useConnection();
import ToolCard from "./ToolCard.vue";
import UserInteractionCard from "./UserInteractionCard.vue";
import ArtifactCard from "./ArtifactCard.vue";
import FeedbackButtons from "./FeedbackButtons.vue";
import SuccessStoryButton from "./SuccessStoryButton.vue";

const props = defineProps<{
  message: ChatMessage;
  sessionId?: string;
  isStreaming?: boolean;
}>();

const emit = defineEmits<{
  stop: [];
  "open-artifact": [kind: string, slug: string];
}>();

const blocks = computed(() =>
  props.message.blocks?.length
    ? props.message.blocks
    : [{ type: "markdown" as const, content: props.message.content }]
);

// When the last block is a user-interaction, the backend is waiting for input — not streaming
const awaitingInteraction = computed(() => {
  const last = blocks.value[blocks.value.length - 1];
  return last?.type === "user-interaction";
});

function renderMarkdown(content: string): string {
  return md.render(content);
}

const renderedBlocks = computed(() =>
  blocks.value.map((block, i) => {
    if (block.type === 'markdown') {
      return { ...block, html: md.render(block.content), _key: `md-${i}-${block.content.length}` };
    }
    return { ...block, _key: `${block.type}-${i}` };
  })
);

async function handleFeedback(emoji: string) {
  if (!props.sessionId) return;
  const base = effectiveBase();
  try {
    await chatApi.feedback(base, {
      source_session_id: props.sessionId,
      reaction_emoji: emoji,
      reference_msg: props.message.content.slice(0, 2000),
    });
  } catch (error) {
    console.error("Feedback failed:", error);
  }
}
</script>

<template>
  <div class="messageBlocks">
    <template v-for="block in renderedBlocks" :key="block._key">
      <ToolCard
        v-if="block.type === 'tool-call'"
        mode="call"
        :tool-name="block.toolName"
        :value="block.params"
      />
      <ToolCard
        v-else-if="block.type === 'tool-result'"
        mode="result"
        :tool-name="block.toolName"
        :value="block.result"
        :duration="block.duration"
        :short-desc="block.shortDesc"
      />
      <UserInteractionCard
        v-else-if="block.type === 'user-interaction'"
        :session-id="sessionId ?? ''"
        :interaction-key="block.interactionKey"
        :action-type="block.actionType"
        :requests="block.requests"
        :is-streaming="isStreaming && !awaitingInteraction"
      />
      <ArtifactCard
        v-else-if="block.type === 'artifact'"
        :kind="block.kind"
        :slug="block.slug"
        :name="block.name"
        :description="block.description"
        @open-artifact="(kind, slug) => emit('open-artifact', kind, slug)"
      />
      <div v-else class="markdownBody" v-html="block.html" />
    </template>
    <div v-if="message.role === 'assistant' && sessionId" class="messageActions">
      <FeedbackButtons
        @feedback="handleFeedback"
      />
      <SuccessStoryButton
        :session-id="sessionId"
        :message-content="message.content"
      />
    </div>
  </div>
</template>
