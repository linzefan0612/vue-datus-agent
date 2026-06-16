<script setup lang="ts">
import { Copy, Pencil, Check, X } from "@lucide/vue";
import Badge from "@/components/ui/Badge.vue";
import Button from "@/components/ui/Button.vue";
import Textarea from "@/components/ui/Textarea.vue";
import type { TableDetail } from "@/types";
import { findCardElement } from "@/lib/utils";

export interface SmIdentifier { name: string; description: string; type: string; expr: string; }
export interface SmMeasure { name: string; description: string; agg: string; expr: string; }
export interface SmDimension { name: string; description: string; type: string; expr: string; typeParams?: Record<string, unknown>; }
export interface ParsedSemanticModel {
  name: string;
  description: string;
  sqlQuery: string;
  identifiers: SmIdentifier[];
  measures: SmMeasure[];
  dimensions: SmDimension[];
  mutability: string;
}

const props = defineProps<{
  tableDetail: TableDetail;
  selectedTable: string;
  semanticModelYaml: string | null;
  parsedSemanticModel: ParsedSemanticModel | null;
  editingSm: boolean;
  editingSmYaml: string;
  copiedField: string | null;
}>();

const emit = defineEmits<{
  'start-edit-sm': [];
  'save-sm': [];
  'cancel-sm': [];
  'update:editingSmYaml': [value: string];
  'copy-to-clipboard': [text: string, fieldId: string];
  'copy-card': [el: HTMLElement, fieldId: string];
}>();

function handleEditKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    emit('save-sm');
  }
  if (e.key === "Escape") {
    e.preventDefault();
    emit('cancel-sm');
  }
}
</script>

<template>
  <div class="knowledgeDetailBody">
    <!-- Row count -->
    <div v-if="tableDetail.rows != null" class="detailCard">
      <div class="detailCardHeader detailCardHeader--table">
        <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Rows</h4></span>
        <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-card', findCardElement($event), 'table-rows')">
          <Check v-if="copiedField === 'table-rows'" :size="14" class="copySuccess" />
          <Copy v-else :size="14" />
        </Button>
      </div>
      <div class="detailCardBody">
        <p class="detailCardText">{{ tableDetail.rows.toLocaleString() }}</p>
      </div>
    </div>
    <!-- Columns table -->
    <div class="detailCard">
      <div class="detailCardHeader detailCardHeader--table">
        <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Columns ({{ tableDetail.columns.length }})</h4></span>
        <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-card', findCardElement($event), 'table-columns')">
          <Check v-if="copiedField === 'table-columns'" :size="14" class="copySuccess" />
          <Copy v-else :size="14" />
        </Button>
      </div>
      <div class="detailCardBody">
        <table class="tableDetailTable">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Nullable</th>
              <th>PK</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="col in tableDetail.columns" :key="col.name">
              <td>{{ col.name }}</td>
              <td><code>{{ col.type }}</code></td>
              <td>{{ col.nullable ? '✓' : '' }}</td>
              <td>{{ col.pk ? '✓' : '' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- Indexes -->
    <div v-if="tableDetail.indexes.length" class="detailCard">
      <div class="detailCardHeader detailCardHeader--table">
        <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Indexes ({{ tableDetail.indexes.length }})</h4></span>
        <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-card', findCardElement($event), 'table-indexes')">
          <Check v-if="copiedField === 'table-indexes'" :size="14" class="copySuccess" />
          <Copy v-else :size="14" />
        </Button>
      </div>
      <div class="detailCardBody">
        <div class="indexList">
          <div v-for="idx in tableDetail.indexes" :key="idx.name" class="indexItem">
            <span class="indexName">{{ idx.name }}</span>
            <Badge variant="secondary">{{ idx.type }}</Badge>
            <span class="indexColumns">{{ idx.columns.join(', ') }}</span>
          </div>
        </div>
      </div>
    </div>
    <!-- Semantic Model -->
    <template v-if="selectedTable && semanticModelYaml !== null">
      <!-- Edit mode -->
      <div v-if="editingSm" class="detailCard" @keydown="handleEditKeydown">
        <div class="detailCardHeader detailCardHeader--table">
          <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Semantic Model — YAML</h4></span>
          <span class="cardEditMeta">{{ editingSmYaml.split('\n').length }} lines</span>
          <Button variant="ghost" size="icon" class="cardCopyBtn" title="取消" aria-label="取消" @click="emit('cancel-sm')">
            <X :size="14" />
          </Button>
          <Button variant="ghost" size="icon" class="cardCopyBtn cardSaveBtn" title="保存 (Ctrl+Enter)" aria-label="保存" @click="emit('save-sm')">
            <Check :size="14" />
          </Button>
        </div>
        <div class="detailCardBody">
          <Textarea :modelValue="editingSmYaml" @update:modelValue="emit('update:editingSmYaml', $event)" class="editCodearea" :rows="18" />
        </div>
      </div>

      <!-- Structured view -->
      <template v-else-if="parsedSemanticModel">
        <!-- Data Source -->
        <div class="detailCard">
          <div class="detailCardHeader detailCardHeader--table">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Data Source</h4></span>
            <Button variant="ghost" size="icon" class="cardCopyBtn" title="编辑" aria-label="编辑" @click="emit('start-edit-sm')">
              <Pencil :size="14" />
            </Button>
            <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-to-clipboard', semanticModelYaml ?? '', 'sm-yaml')">
              <Check v-if="copiedField === 'sm-yaml'" :size="14" class="copySuccess" />
              <Copy v-else :size="14" />
            </Button>
          </div>
          <div class="detailCardBody">
            <div class="smFieldGrid">
              <span class="smFieldKey">Name</span>
              <span class="smFieldValue">{{ parsedSemanticModel.name }}</span>
              <span class="smFieldKey">Description</span>
              <span class="smFieldValue">{{ parsedSemanticModel.description }}</span>
              <span class="smFieldKey">SQL</span>
              <code class="smFieldValue smFieldSql">{{ parsedSemanticModel.sqlQuery }}</code>
              <span v-if="parsedSemanticModel.mutability" class="smFieldKey">Mutability</span>
              <Badge v-if="parsedSemanticModel.mutability" variant="secondary">{{ parsedSemanticModel.mutability }}</Badge>
            </div>
          </div>
        </div>

        <!-- Identifiers -->
        <div v-if="parsedSemanticModel.identifiers.length" class="detailCard">
          <div class="detailCardHeader detailCardHeader--table">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Identifiers ({{ parsedSemanticModel.identifiers.length }})</h4></span>
          </div>
          <div class="detailCardBody">
            <table class="tableDetailTable">
              <thead>
                <tr><th>Name</th><th>Description</th><th>Type</th><th>Expr</th></tr>
              </thead>
              <tbody>
                <tr v-for="id in parsedSemanticModel.identifiers" :key="id.name">
                  <td>{{ id.name }}</td>
                  <td>{{ id.description }}</td>
                  <td><Badge variant="outline">{{ id.type }}</Badge></td>
                  <td><code>{{ id.expr }}</code></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Measures -->
        <div v-if="parsedSemanticModel.measures.length" class="detailCard">
          <div class="detailCardHeader detailCardHeader--table">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Measures ({{ parsedSemanticModel.measures.length }})</h4></span>
          </div>
          <div class="detailCardBody">
            <table class="tableDetailTable">
              <thead>
                <tr><th>Name</th><th>Description</th><th>Agg</th><th>Expr</th></tr>
              </thead>
              <tbody>
                <tr v-for="m in parsedSemanticModel.measures" :key="m.name">
                  <td>{{ m.name }}</td>
                  <td>{{ m.description }}</td>
                  <td><Badge variant="secondary">{{ m.agg }}</Badge></td>
                  <td><code>{{ m.expr }}</code></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Dimensions -->
        <div v-if="parsedSemanticModel.dimensions.length" class="detailCard">
          <div class="detailCardHeader detailCardHeader--table">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Dimensions ({{ parsedSemanticModel.dimensions.length }})</h4></span>
          </div>
          <div class="detailCardBody">
            <table class="tableDetailTable">
              <thead>
                <tr><th>Name</th><th>Description</th><th>Type</th><th>Expr</th></tr>
              </thead>
              <tbody>
                <tr v-for="d in parsedSemanticModel.dimensions" :key="d.name">
                  <td>{{ d.name }}</td>
                  <td>{{ d.description }}</td>
                  <td><Badge :variant="d.type === 'TIME' ? 'default' : 'outline'">{{ d.type }}</Badge></td>
                  <td><code>{{ d.expr }}</code></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Raw YAML (collapsible) -->
        <details class="detailCollapsible">
          <summary>Raw YAML</summary>
          <pre class="knowledgeYaml">{{ semanticModelYaml }}</pre>
        </details>
      </template>

      <!-- Fallback: raw YAML if parse fails -->
      <template v-else>
        <div class="detailCard">
          <div class="detailCardHeader detailCardHeader--table">
            <span class="detailCardHeaderTitle"><h4 class="detailCardTitle">Semantic Model</h4></span>
            <Button variant="ghost" size="icon" class="cardCopyBtn" title="编辑" aria-label="编辑" @click="emit('start-edit-sm')">
              <Pencil :size="14" />
            </Button>
            <Button variant="ghost" size="icon" class="cardCopyBtn" aria-label="复制" @click="emit('copy-to-clipboard', semanticModelYaml ?? '', 'sm-yaml')">
              <Check v-if="copiedField === 'sm-yaml'" :size="14" class="copySuccess" />
              <Copy v-else :size="14" />
            </Button>
          </div>
          <div class="detailCardBody">
            <pre class="knowledgeYaml">{{ semanticModelYaml }}</pre>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>
