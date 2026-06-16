<script setup lang="ts">
import { Copy, Pencil, Check, X } from "@lucide/vue";
import Badge from "@/components/ui/Badge.vue";
import Button from "@/components/ui/Button.vue";
import Textarea from "@/components/ui/Textarea.vue";
import type { ReferenceSQLInfo } from "@/types";
import { findCardElement } from "@/lib/utils";

const props = defineProps<{
  sqlDetail: ReferenceSQLInfo;
  editingField: string | null;
  editingValue: string;
  copiedField: string | null;
}>();

const emit = defineEmits<{
  'start-edit': [field: string, value: string | null];
  'save': [field: 'summary' | 'sql' | 'search_text'];
  'cancel': [];
  'update:editingValue': [value: string];
  'copy-card': [el: HTMLElement, fieldId: string];
}>();

function splitSearchText(text: string): string[] {
  return text
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);
}

function isEditing(field: string): boolean {
  return props.editingField === field;
}

function handleEditKeydown(e: KeyboardEvent, saveField: 'summary' | 'sql' | 'search_text') {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    emit('save', saveField);
  }
  if (e.key === "Escape") {
    e.preventDefault();
    emit('cancel');
  }
}
</script>

<template>
  <div class="knowledgeDetailBody">
    <!-- Summary card -->
    <div class="detailCard">
      <div class="detailCardHeader">
        <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Summary</h4></span>
        <template v-if="isEditing('sql-summary')">
          <Button variant="ghost" size="icon" class="cardCopyBtn" title="取消" aria-label="取消" @click="emit('cancel')">
            <X :size="14" />
          </Button>
          <Button variant="ghost" size="icon" class="cardCopyBtn cardSaveBtn" title="保存 (Ctrl+Enter)" aria-label="保存" @click="emit('save', 'summary')">
            <Check :size="14" />
          </Button>
        </template>
        <template v-else>
          <Button variant="ghost" size="icon" class="cardCopyBtn" title="编辑" aria-label="编辑" @click="emit('start-edit', 'sql-summary', sqlDetail.summary ?? '')">
            <Pencil :size="14" />
          </Button>
          <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-card', findCardElement($event), 'sql-summary')">
            <Check v-if="copiedField === 'sql-summary'" :size="14" class="copySuccess" />
            <Copy v-else :size="14" />
          </Button>
        </template>
      </div>
      <div class="detailCardBody" @keydown="handleEditKeydown($event, 'summary')">
        <Textarea v-if="isEditing('sql-summary')" :modelValue="editingValue" @update:modelValue="emit('update:editingValue', $event)" class="cardEditarea" :rows="3" placeholder="SQL 摘要描述" />
        <p v-else class="detailCardText">{{ sqlDetail.summary }}</p>
      </div>
    </div>
    <!-- SQL block with header -->
    <div class="detailCard">
      <div class="detailCardHeader">
        <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">SQL</h4></span>
        <template v-if="isEditing('sql-code')">
          <span class="cardEditMeta">{{ editingValue.split('\n').length }} lines</span>
          <Button variant="ghost" size="icon" class="cardCopyBtn" title="取消" aria-label="取消" @click="emit('cancel')">
            <X :size="14" />
          </Button>
          <Button variant="ghost" size="icon" class="cardCopyBtn cardSaveBtn" title="保存 (Ctrl+Enter)" aria-label="保存" @click="emit('save', 'sql')">
            <Check :size="14" />
          </Button>
        </template>
        <template v-else>
          <Button variant="ghost" size="icon" class="cardCopyBtn" title="编辑" aria-label="编辑" @click="emit('start-edit', 'sql-code', sqlDetail.sql ?? '')">
            <Pencil :size="14" />
          </Button>
          <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-card', findCardElement($event), 'sql-code')">
            <Check v-if="copiedField === 'sql-code'" :size="14" class="copySuccess" />
            <Copy v-else :size="14" />
          </Button>
        </template>
      </div>
      <div @keydown="handleEditKeydown($event, 'sql')">
        <Textarea v-if="isEditing('sql-code')" :modelValue="editingValue" @update:modelValue="emit('update:editingValue', $event)" class="editCodearea" :rows="10" placeholder="SELECT ..." style="margin: 0; border-radius: 0;" />
        <pre v-else class="sqlBlockCode">{{ sqlDetail.sql }}</pre>
      </div>
    </div>
    <!-- Search text card -->
    <div v-if="sqlDetail.search_text || isEditing('sql-search')" class="detailCard">
      <div class="detailCardHeader">
        <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Search Text</h4></span>
        <template v-if="isEditing('sql-search')">
          <Button variant="ghost" size="icon" class="cardCopyBtn" title="取消" aria-label="取消" @click="emit('cancel')">
            <X :size="14" />
          </Button>
          <Button variant="ghost" size="icon" class="cardCopyBtn cardSaveBtn" title="保存 (Ctrl+Enter)" aria-label="保存" @click="emit('save', 'search_text')">
            <Check :size="14" />
          </Button>
        </template>
        <template v-else>
          <Button variant="ghost" size="icon" class="cardCopyBtn" title="编辑" aria-label="编辑" @click="emit('start-edit', 'sql-search', sqlDetail.search_text ?? '')">
            <Pencil :size="14" />
          </Button>
          <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-card', findCardElement($event), 'sql-search')">
            <Check v-if="copiedField === 'sql-search'" :size="14" class="copySuccess" />
            <Copy v-else :size="14" />
          </Button>
        </template>
      </div>
      <div class="detailCardBody" @keydown="handleEditKeydown($event, 'search_text')">
        <Textarea v-if="isEditing('sql-search')" :modelValue="editingValue" @update:modelValue="emit('update:editingValue', $event)" class="cardEditarea" :rows="3" placeholder="用于向量检索的文本" />
        <div v-else class="searchTextSegments">
          <p
            v-for="(seg, i) in splitSearchText(sqlDetail.search_text ?? '')"
            :key="i"
            class="searchTextSegment"
          >
            {{ seg }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
