<script setup lang="ts">
import { Copy, Pencil, Check, X } from "@lucide/vue";
import Badge from "@/components/ui/Badge.vue";
import Button from "@/components/ui/Button.vue";
import Textarea from "@/components/ui/Textarea.vue";
import type { MetricInfo } from "@/types";
import { findCardElement } from "@/lib/utils";

export interface ParsedMetric {
  name: string;
  description: string;
  type: string;
  typeParams: Record<string, unknown>;
  tags: string[];
  numerator?: string;
  denominator?: string;
  expr?: string;
  measures: string[];
}

defineProps<{
  parsedMetric: ParsedMetric | null;
  metricDetail: MetricInfo;
  editingMetric: boolean;
  editingMetricYaml: string;
  copiedField: string | null;
  metricTypeColors: Record<string, "default" | "secondary" | "destructive" | "outline" | "success">;
}>();

const emit = defineEmits<{
  'start-edit': [];
  'save': [];
  'cancel': [];
  'update:editingMetricYaml': [value: string];
  'copy-card': [el: HTMLElement, fieldId: string];
}>();

function formatParamValue(val: unknown): string {
  if (Array.isArray(val)) return val.join(", ");
  if (typeof val === "object" && val !== null) return JSON.stringify(val);
  return String(val ?? "");
}

function handleEditKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    emit('save');
  }
  if (e.key === "Escape") {
    e.preventDefault();
    emit('cancel');
  }
}
</script>

<template>
  <div class="knowledgeDetailBody">
    <div v-if="!editingMetric">
      <!-- Structured view -->
      <template v-if="parsedMetric">
        <div class="detailCard">
          <div class="detailCardHeader detailCardHeader--metric">
            <span class="detailCardHeaderTitle">
              <span class="metricCardName">{{ parsedMetric.name }}</span>
              <Badge :variant="metricTypeColors[parsedMetric.type] ?? 'secondary'" style="margin-left: 6px;">
                {{ parsedMetric.type }}
              </Badge>
            </span>
            <Button variant="ghost" size="icon" class="cardCopyBtn" title="编辑" aria-label="编辑" @click="emit('start-edit')">
              <Pencil :size="14" />
            </Button>
            <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-card', findCardElement($event), 'metric-info')">
              <Check v-if="copiedField === 'metric-info'" :size="14" class="copySuccess" />
              <Copy v-else :size="14" />
            </Button>
          </div>
          <div class="detailCardBody">
            <p v-if="parsedMetric.description" class="metricDescription">{{ parsedMetric.description }}</p>
            <div v-if="parsedMetric.tags.length" class="metricTags">
              <span v-for="tag in parsedMetric.tags" :key="tag" class="metricTag">{{ tag }}</span>
            </div>
          </div>
        </div>

        <!-- Ratio: numerator / denominator -->
        <div v-if="parsedMetric.type === 'ratio' && (parsedMetric.numerator || parsedMetric.denominator)" class="detailCard">
          <div class="detailCardHeader detailCardHeader--metric">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Ratio</h4></span>
          </div>
          <div class="detailCardBody">
            <div class="metricParamsGrid">
              <div v-if="parsedMetric.numerator" class="metricParamItem">
                <span class="metricParamKey">Numerator</span>
                <code class="metricParamVal">{{ parsedMetric.numerator }}</code>
              </div>
              <div v-if="parsedMetric.denominator" class="metricParamItem">
                <span class="metricParamKey">Denominator</span>
                <code class="metricParamVal">{{ parsedMetric.denominator }}</code>
              </div>
            </div>
          </div>
        </div>

        <!-- Derived / Expr / Cumulative: expression + measures/metrics -->
        <div v-if="(parsedMetric.type === 'derived' || parsedMetric.type === 'expr' || parsedMetric.type === 'cumulative') && (parsedMetric.expr || parsedMetric.measures.length)" class="detailCard">
          <div class="detailCardHeader detailCardHeader--metric">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">{{ parsedMetric.type === 'derived' ? 'Derived From' : 'Expression' }}</h4></span>
          </div>
          <div class="detailCardBody">
            <div class="metricParamsGrid">
              <div v-if="parsedMetric.expr" class="metricParamItem">
                <span class="metricParamKey">Formula</span>
                <code class="metricParamVal">{{ parsedMetric.expr }}</code>
              </div>
              <div v-if="parsedMetric.measures.length" class="metricParamItem">
                <span class="metricParamKey">{{ parsedMetric.type === 'derived' ? 'Metrics' : 'Measures' }}</span>
                <span class="metricParamVal">
                  <span v-for="(m, i) in parsedMetric.measures" :key="m">
                    <code>{{ m }}</code><span v-if="i < parsedMetric.measures.length - 1">, </span>
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Simple / Measure Proxy: measure name(s) -->
        <div v-if="(parsedMetric.type === 'simple' || parsedMetric.type === 'measure_proxy') && parsedMetric.measures.length" class="detailCard">
          <div class="detailCardHeader detailCardHeader--metric">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">{{ parsedMetric.type === 'measure_proxy' ? 'Proxy Measure' : 'Measure' }}</h4></span>
          </div>
          <div class="detailCardBody">
            <div class="metricParamsGrid">
              <div class="metricParamItem">
                <span class="metricParamKey">Name</span>
                <span class="metricParamVal">
                  <span v-for="(m, i) in parsedMetric.measures" :key="m">
                    <code>{{ m }}</code><span v-if="i < parsedMetric.measures.length - 1">, </span>
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Fallback: generic type_params for unknown types -->
        <div v-if="!['ratio','derived','expr','cumulative','simple','measure_proxy'].includes(parsedMetric.type) && Object.keys(parsedMetric.typeParams).length" class="detailCard">
          <div class="detailCardHeader detailCardHeader--metric">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Type Parameters</h4></span>
          </div>
          <div class="detailCardBody">
            <div class="metricParamsGrid">
              <template v-for="(val, key) in parsedMetric.typeParams" :key="key">
                <div class="metricParamItem">
                  <span class="metricParamKey">{{ key }}</span>
                  <span class="metricParamVal">{{ formatParamValue(val) }}</span>
                </div>
              </template>
            </div>
          </div>
        </div>
        <details class="detailCollapsible">
          <summary>Raw YAML</summary>
          <pre class="knowledgeYaml">{{ metricDetail.yaml }}</pre>
        </details>
      </template>
      <!-- Fallback: raw YAML if parse fails -->
      <template v-else>
        <div class="detailCard">
          <div class="detailCardHeader detailCardHeader--metric">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Raw YAML</h4></span>
            <Button variant="ghost" size="icon" class="cardCopyBtn" title="编辑" aria-label="编辑" @click="emit('start-edit')">
              <Pencil :size="14" />
            </Button>
            <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-card', findCardElement($event), 'metric-yaml')">
              <Check v-if="copiedField === 'metric-yaml'" :size="14" class="copySuccess" />
              <Copy v-else :size="14" />
            </Button>
          </div>
          <div class="detailCardBody">
            <pre class="knowledgeYaml">{{ metricDetail.yaml }}</pre>
          </div>
        </div>
      </template>
    </div>
    <div v-else class="knowledgeEditForm" @keydown="handleEditKeydown">
      <div class="detailCard">
        <div class="detailCardHeader detailCardHeader--metric">
          <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">YAML</h4></span>
          <span class="cardEditMeta">{{ editingMetricYaml.split('\n').length }} lines</span>
          <Button variant="ghost" size="icon" class="cardCopyBtn" title="取消" aria-label="取消" @click="emit('cancel')">
            <X :size="14" />
          </Button>
          <Button variant="ghost" size="icon" class="cardCopyBtn cardSaveBtn" title="保存 (Ctrl+Enter)" aria-label="保存" @click="emit('save')">
            <Check :size="14" />
          </Button>
        </div>
        <div class="detailCardBody">
          <Textarea :modelValue="editingMetricYaml" @update:modelValue="emit('update:editingMetricYaml', $event)" class="editCodearea" :rows="14" placeholder="metric:\n  name: ...\n  description: ..." />
        </div>
      </div>
    </div>
  </div>
</template>
