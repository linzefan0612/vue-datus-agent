<script setup lang="ts">
import { ref, computed, shallowRef, onMounted, defineAsyncComponent } from "vue";
import { BookOpen, Database, Folder, FolderPlus, Loader2, RotateCw } from "@lucide/vue";
import yaml from "js-yaml";
import { toast } from "vue-sonner";

import Button from "@/components/ui/Button.vue";
import ConfirmDialog from "@/components/ui/ConfirmDialog.vue";
import ScrollArea from "@/components/ui/ScrollArea.vue";
import Input from "@/components/ui/Input.vue";
import Label from "@/components/ui/Label.vue";
import Sheet from "@/components/ui/Sheet.vue";
import SheetContent from "@/components/ui/SheetContent.vue";
import SheetHeader from "@/components/ui/SheetHeader.vue";
import SheetTitle from "@/components/ui/SheetTitle.vue";
import { subjectApi, catalogApi, tableApi } from "@/lib/api";
import { handleError } from "@/lib/utils";
import type { SubjectNode, MetricInfo, ReferenceSQLInfo, SubjectNodeType, DatabaseInfo, TableDetail } from "@/types";
import { useConnection } from "@/composables/useConnection";
import type { ParsedMetric } from "./MetricDetailView.vue";
import type { ParsedSemanticModel } from "./TableDetailView.vue";
import TreeNode from "./TreeNode.vue";

const BootstrapDialog = defineAsyncComponent({
  loader: () => import("./BootstrapDialog.vue"),
  delay: 200,
  timeout: 30000,
});
const CatalogTree = defineAsyncComponent({
  loader: () => import("./CatalogTree.vue"),
  delay: 200,
  timeout: 30000,
});
const MetricDetailView = defineAsyncComponent({
  loader: () => import("./MetricDetailView.vue"),
  delay: 200,
  timeout: 30000,
});
const ReferenceSqlDetailView = defineAsyncComponent({
  loader: () => import("./ReferenceSqlDetailView.vue"),
  delay: 200,
  timeout: 30000,
});
const TableDetailView = defineAsyncComponent({
  loader: () => import("./TableDetailView.vue"),
  delay: 200,
  timeout: 30000,
});

const { effectiveBase } = useConnection();

const parsedMetric = computed<ParsedMetric | null>(() => {
  if (!metricDetail.value?.yaml) return null;
  try {
    const doc = yaml.load(metricDetail.value.yaml) as Record<string, unknown>;
    const m = doc?.metric as Record<string, unknown> | undefined;
    if (!m) return null;
    const locked = m.locked_metadata as Record<string, unknown> | undefined;
    const tags = (locked?.tags as string[]) ?? [];
    const typeParams = (m.type_params as Record<string, unknown>) ?? {};
    const type = String(m.type ?? "");

    // Parse type-specific fields
    let numerator: string | undefined;
    let denominator: string | undefined;
    let expr: string | undefined;
    let measures: string[] = [];

    if (type === "ratio") {
      const num = typeParams.numerator as Record<string, unknown> | undefined;
      const den = typeParams.denominator as Record<string, unknown> | undefined;
      numerator = num?.name ? String(num.name) : undefined;
      denominator = den?.name ? String(den.name) : undefined;
    } else if (type === "derived") {
      measures = ((typeParams.metrics as unknown[]) ?? []).map(String);
      expr = typeParams.expr ? String(typeParams.expr) : undefined;
    } else if (type === "expr" || type === "cumulative") {
      measures = ((typeParams.measures as unknown[]) ?? []).map(String);
      expr = typeParams.expr ? String(typeParams.expr) : undefined;
    } else {
      // simple / measure_proxy / unknown
      const raw = typeParams.measures ?? typeParams.measure;
      if (Array.isArray(raw)) {
        measures = raw.map((v) => (typeof v === "object" && v !== null ? String((v as Record<string, unknown>).name ?? v) : String(v)));
      } else if (raw != null) {
        measures = [typeof raw === "object" ? String((raw as Record<string, unknown>).name ?? raw) : String(raw)];
      }
    }

    return { name: String(m.name ?? ""), description: String(m.description ?? ""), type, typeParams, tags, numerator, denominator, expr, measures };
  } catch {
    return null;
  }
});

const parsedSemanticModel = computed<ParsedSemanticModel | null>(() => {
  if (!semanticModelYaml.value) return null;
  try {
    const doc = yaml.load(semanticModelYaml.value) as Record<string, unknown>;
    const ds = doc?.data_source as Record<string, unknown> | undefined;
    if (!ds) return null;
    const identifiers = ((ds.identifiers as unknown[]) ?? []).map((i) => {
      const item = i as Record<string, unknown>;
      return { name: String(item.name ?? ""), description: String(item.description ?? ""), type: String(item.type ?? ""), expr: String(item.expr ?? "") };
    });
    const measures = ((ds.measures as unknown[]) ?? []).map((m) => {
      const item = m as Record<string, unknown>;
      return { name: String(item.name ?? ""), description: String(item.description ?? ""), agg: String(item.agg ?? ""), expr: String(item.expr ?? "") };
    });
    const dimensions = ((ds.dimensions as unknown[]) ?? []).map((d) => {
      const item = d as Record<string, unknown>;
      return {
        name: String(item.name ?? ""),
        description: String(item.description ?? ""),
        type: String(item.type ?? ""),
        expr: String(item.expr ?? ""),
        typeParams: item.type_params as Record<string, unknown> | undefined,
      };
    });
    const mut = doc.mutability as Record<string, unknown> | undefined;
    return {
      name: String(ds.name ?? ""),
      description: String(ds.description ?? ""),
      sqlQuery: String(ds.sql_query ?? ""),
      identifiers,
      measures,
      dimensions,
      mutability: String(mut?.type ?? ""),
    };
  } catch {
    return null;
  }
});

const metricTypeColors: Record<string, "default" | "secondary" | "destructive" | "outline" | "success"> = {
  simple: "success",
  measure_proxy: "secondary",
  ratio: "default",
  derived: "outline",
  expr: "destructive",
  cumulative: "secondary",
};

const copiedField = shallowRef<string | null>(null);

async function copyToClipboard(text: string, fieldId: string) {
  try {
    await navigator.clipboard.writeText(text);
    copiedField.value = fieldId;
    setTimeout(() => { copiedField.value = null; }, 1500);
  } catch {
    // fallback
  }
}

function copyCardText(el: HTMLElement, fieldId: string) {
  const clone = el.cloneNode(true) as HTMLElement;
  clone.querySelectorAll("button").forEach((b) => b.remove());
  copyToClipboard(clone.innerText.trim(), fieldId);
}

// ─── State ───────────────────────────────────────────────────────────────────

const subjects = ref<SubjectNode[]>([]);
const loading = shallowRef(false);
const selectedNode = ref<SubjectNode | null>(null);
const detailLoading = shallowRef(false);

// Catalog tree state
const activeTree = shallowRef<"subject" | "catalog">("subject");
const catalogEntries = ref<DatabaseInfo[]>([]);
const catalogLoading = shallowRef(false);
const selectedTable = shallowRef<string>("");
const tableDetail = ref<TableDetail | null>(null);
const semanticModelYaml = shallowRef<string | null>(null);

// Bootstrap
const showBootstrap = shallowRef(false);

// Detail data
const metricDetail = ref<MetricInfo | null>(null);
const sqlDetail = ref<ReferenceSQLInfo | null>(null);
const deleteTarget = ref<SubjectNode | null>(null);
const deletingPath = shallowRef("");

// Create/rename dialog
const showCreateDialog = shallowRef(false);
const createType = shallowRef<SubjectNodeType>("directory");
const createName = shallowRef("");
const createParentPath = ref<string[]>([]);
const creating = shallowRef(false);

// ─── Load tree ───────────────────────────────────────────────────────────────

async function loadSubjects() {
  loading.value = true;
  try {
    const result = await subjectApi.list(effectiveBase());
    if (result) subjects.value = result.subjects ?? [];
  } catch (e) {
    handleError("加载 Subject 失败", e);
  } finally {
    loading.value = false;
  }
}

async function loadCatalog() {
  catalogLoading.value = true;
  try {
    const result = await catalogApi.list(effectiveBase());
    if (result) catalogEntries.value = result.databases ?? [];
  } catch (e) {
    handleError("加载 Catalog 失败", e);
  } finally {
    catalogLoading.value = false;
  }
}

// ─── Select node ─────────────────────────────────────────────────────────────

async function selectNode(node: SubjectNode) {
  selectedNode.value = node;
  selectedTable.value = "";
  tableDetail.value = null;
  semanticModelYaml.value = null;
  metricDetail.value = null;
  sqlDetail.value = null;
  if (!node.type || node.type === "directory") return;

  detailLoading.value = true;
  const base = effectiveBase();
  try {
    if (node.type === "metric") {
      metricDetail.value = await subjectApi.getMetric(base, node.subject_path);
    } else if (node.type === "reference_sql") {
      sqlDetail.value = await subjectApi.getReferenceSql(base, node.subject_path);
    }
  } catch (e) {
    handleError("加载详情失败", e);
  } finally {
    detailLoading.value = false;
  }
}

async function selectTable(tableName: string) {
  selectedTable.value = tableName;
  selectedNode.value = null;
  metricDetail.value = null;
  sqlDetail.value = null;
  tableDetail.value = null;
  semanticModelYaml.value = null;

  detailLoading.value = true;
  const base = effectiveBase();
  try {
    const [detailResult, smResult] = await Promise.all([
      tableApi.detail(base, tableName),
      tableApi.getSemanticModel(base, tableName),
    ]);
    if (detailResult) tableDetail.value = detailResult.table;
    semanticModelYaml.value = smResult?.yaml ?? null;
  } catch (e) {
    handleError("加载表详情失败", e);
  } finally {
    detailLoading.value = false;
  }
}

function switchTree(tree: "subject" | "catalog") {
  activeTree.value = tree;
  if (tree === "catalog" && catalogEntries.value.length === 0) {
    loadCatalog();
  }
}

// ─── CRUD operations ─────────────────────────────────────────────────────────

function openCreate(parentPath: string[], type: SubjectNodeType) {
  createParentPath.value = parentPath;
  createType.value = type;
  createName.value = "";
  showCreateDialog.value = true;
}

async function handleCreate() {
  if (!createName.value.trim()) return;
  const base = effectiveBase();
  const path = [...createParentPath.value, createName.value.trim()];
  creating.value = true;
  try {
    if (createType.value === "directory") {
      await subjectApi.create(base, path);
    } else if (createType.value === "metric") {
      await subjectApi.createMetric(base, path, createName.value.trim());
    }
    showCreateDialog.value = false;
    await loadSubjects();
  } catch (e) {
    handleError("创建失败", e);
  } finally {
    creating.value = false;
  }
}

function requestDelete(node: SubjectNode) {
  deleteTarget.value = node;
}

async function confirmDelete() {
  if (!deleteTarget.value) return;
  const node = deleteTarget.value;
  deletingPath.value = node.subject_path.join("/");
  try {
    await subjectApi.delete(effectiveBase(), node.type || "directory", node.subject_path);
    if (selectedNode.value?.subject_path.join("/") === node.subject_path.join("/")) {
      selectedNode.value = null;
    }
    deleteTarget.value = null;
    toast.success(`已删除：${node.name}`);
    await loadSubjects();
  } catch (e) {
    handleError("删除失败", e);
  } finally {
    deletingPath.value = "";
  }
}

// ─── Edit handlers ───────────────────────────────────────────────────────────

// Per-card editing state: tracks which card is being edited
const editingField = shallowRef<string | null>(null);
const editingValue = shallowRef("");

function startEdit(field: string, value?: string | null) {
  editingField.value = field;
  editingValue.value = value ?? "";
}

function cancelEdit() {
  editingField.value = null;
  editingValue.value = "";
}

// ── Metric (YAML) ─────────────────────────────────────────────────────────

const editingMetric = shallowRef(false);
const editingMetricYaml = shallowRef("");

function startEditMetric() {
  if (!metricDetail.value) return;
  editingMetricYaml.value = metricDetail.value.yaml;
  editingMetric.value = true;
}

async function saveMetric() {
  if (!selectedNode.value) return;
  try {
    await subjectApi.editMetric(effectiveBase(), selectedNode.value.subject_path, editingMetricYaml.value);
    metricDetail.value = { ...metricDetail.value!, yaml: editingMetricYaml.value };
    editingMetric.value = false;
  } catch (e) {
    handleError("保存指标失败", e);
  }
}

// ── Reference SQL (per-card) ───────────────────────────────────────────────

async function saveSqlField(field: "summary" | "sql" | "search_text") {
  if (!selectedNode.value || !sqlDetail.value) return;
  const updated = { ...sqlDetail.value, [field]: editingValue.value };
  try {
    await subjectApi.editReferenceSql(effectiveBase(), {
      name: updated.name,
      sql: updated.sql,
      summary: updated.summary,
      search_text: updated.search_text,
      subject_path: selectedNode.value.subject_path,
    });
    sqlDetail.value = updated;
    cancelEdit();
  } catch (e) {
    handleError("保存 SQL 字段失败", e);
  }
}

// ── Semantic Model (per-card) ──────────────────────────────────────────────

const editingSm = shallowRef(false);
const editingSmYaml = shallowRef("");

function startEditSm() {
  editingSmYaml.value = semanticModelYaml.value ?? "";
  editingSm.value = true;
}

async function saveSm() {
  if (!selectedTable.value) return;
  try {
    await tableApi.saveSemanticModel(effectiveBase(), selectedTable.value, editingSmYaml.value);
    semanticModelYaml.value = editingSmYaml.value;
    editingSm.value = false;
  } catch (e) {
    handleError("保存语义模型失败", e);
  }
}

// ─── Init ────────────────────────────────────────────────────────────────────

onMounted(loadSubjects);
</script>

<template>
  <div class="knowledgeExplorer">
    <!-- Left: tree -->
    <div class="knowledgeTree">
      <!-- Tab bar -->
      <div class="treeTabBar">
        <button
          :class="['treeTab', { active: activeTree === 'subject' }]"
          @click="switchTree('subject')"
        >
          <BookOpen :size="14" />
          Subject
        </button>
        <button
          :class="['treeTab', { active: activeTree === 'catalog' }]"
          @click="switchTree('catalog')"
        >
          <Database :size="14" />
          Catalog
        </button>
      </div>

      <!-- Subject tree header -->
      <div v-if="activeTree === 'subject'" class="knowledgeTreeHeader">
        <div class="knowledgeTreeActions">
          <Button variant="ghost" size="icon" aria-label="Bootstrap" title="知识库构建" @click="showBootstrap = true">
            <Database :size="16" />
          </Button>
          <Button variant="ghost" size="icon" aria-label="新建目录" @click="openCreate([], 'directory')">
            <FolderPlus :size="16" />
          </Button>
          <Button variant="ghost" size="icon" :disabled="loading" aria-label="刷新" @click="loadSubjects">
            <Loader2 v-if="loading" class="spin" :size="16" />
            <RotateCw v-else :size="16" />
          </Button>
        </div>
      </div>

      <!-- Catalog tree header -->
      <div v-if="activeTree === 'catalog'" class="knowledgeTreeHeader">
        <div class="knowledgeTreeActions">
          <Button variant="ghost" size="icon" :disabled="catalogLoading" aria-label="刷新" @click="loadCatalog">
            <Loader2 v-if="catalogLoading" class="spin" :size="16" />
            <RotateCw v-else :size="16" />
          </Button>
        </div>
      </div>

      <!-- Subject tree content -->
      <ScrollArea v-if="activeTree === 'subject'" class="knowledgeTreeContent">
        <div v-if="loading" class="knowledgeTreeLoading">
          <Loader2 class="spin" :size="20" />
        </div>
        <div v-else-if="subjects.length === 0" class="knowledgeTreeEmpty">
          <Folder :size="24" />
          <p>暂无 Subject</p>
        </div>
        <template v-else>
          <TreeNode
            v-for="node in subjects"
            :key="node.subject_path.join('/')"
            :node="node"
            :selected-path="selectedNode?.subject_path.join('/') ?? ''"
            :depth="0"
            @select="selectNode"
            @create="openCreate"
            @delete="requestDelete"
          />
        </template>
      </ScrollArea>

      <!-- Catalog tree content -->
      <ScrollArea v-if="activeTree === 'catalog'" class="knowledgeTreeContent">
        <div v-if="catalogLoading" class="knowledgeTreeLoading">
          <Loader2 class="spin" :size="20" />
        </div>
        <CatalogTree
          v-else
          :entries="catalogEntries"
          :selected-table="selectedTable"
          @select="selectTable"
        />
      </ScrollArea>
    </div>

    <!-- Right: detail -->
    <div class="knowledgeDetail">
      <div v-if="!selectedNode && !selectedTable" class="knowledgeDetailEmpty">
        <BookOpen :size="32" />
        <p>选择左侧节点查看详情</p>
      </div>
      <div v-else-if="detailLoading" class="knowledgeDetailLoading">
        <Loader2 class="spin" :size="24" />
      </div>
      <div v-else class="knowledgeDetailContent">
        <!-- Header for subject node -->
        <div v-if="selectedNode" class="knowledgeDetailHeader">
          <h3>{{ selectedNode.name }}</h3>
          <span class="knowledgeDetailType">{{ selectedNode.type || 'directory' }}</span>
        </div>
        <!-- Header for catalog table -->
        <div v-else-if="selectedTable && tableDetail" class="knowledgeDetailHeader">
          <h3>{{ tableDetail.name }}</h3>
          <span class="knowledgeDetailType">table</span>
        </div>

        <!-- Metric detail -->
        <MetricDetailView
          v-if="selectedNode?.type === 'metric' && metricDetail"
          :parsed-metric="parsedMetric"
          :metric-detail="metricDetail"
          :editing-metric="editingMetric"
          :editing-metric-yaml="editingMetricYaml"
          :copied-field="copiedField"
          :metric-type-colors="metricTypeColors"
          @start-edit="startEditMetric"
          @save="saveMetric"
          @cancel="editingMetric = false"
          @update:editing-metric-yaml="editingMetricYaml = $event"
          @copy-card="copyCardText"
        />

        <!-- Reference SQL detail -->
        <ReferenceSqlDetailView
          v-if="selectedNode?.type === 'reference_sql' && sqlDetail"
          :sql-detail="sqlDetail"
          :editing-field="editingField"
          :editing-value="editingValue"
          :copied-field="copiedField"
          @start-edit="startEdit"
          @save="saveSqlField"
          @cancel="cancelEdit"
          @update:editing-value="editingValue = $event"
          @copy-card="copyCardText"
        />

        <!-- Table detail (Catalog) -->
        <TableDetailView
          v-if="selectedTable && tableDetail"
          :table-detail="tableDetail"
          :selected-table="selectedTable"
          :semantic-model-yaml="semanticModelYaml"
          :parsed-semantic-model="parsedSemanticModel"
          :editing-sm="editingSm"
          :editing-sm-yaml="editingSmYaml"
          :copied-field="copiedField"
          @start-edit-sm="startEditSm"
          @save-sm="saveSm"
          @cancel-sm="editingSm = false"
          @update:editing-sm-yaml="editingSmYaml = $event"
          @copy-to-clipboard="copyToClipboard"
          @copy-card="copyCardText"
        />
      </div>
    </div>

    <!-- Create dialog -->
    <Sheet :open="showCreateDialog" @update:open="showCreateDialog = $event">
      <SheetContent class="settingsDrawer" side="right" aria-label="新建">
        <SheetHeader class="settingsHeader">
          <SheetTitle>新建 {{ createType }}</SheetTitle>
        </SheetHeader>
        <form class="agentForm" @submit.prevent="handleCreate">
          <Label>
            名称
            <Input v-model="createName" placeholder="名称" />
          </Label>
          <Button type="submit" :disabled="creating || !createName.trim()">
            <Loader2 v-if="creating" class="spin" :size="14" />
            {{ creating ? '创建中...' : '创建' }}
          </Button>
        </form>
      </SheetContent>
    </Sheet>

    <BootstrapDialog :open="showBootstrap" @update:open="showBootstrap = $event" />

    <ConfirmDialog
      :open="!!deleteTarget"
      title="删除知识节点"
      :description="deleteTarget ? `确定删除 “${deleteTarget.name}”？该节点下的内容将不可用。` : ''"
      confirm-label="删除"
      destructive
      :loading="!!deletingPath"
      @update:open="deleteTarget = $event ? deleteTarget : null"
      @confirm="confirmDelete"
    />
  </div>
</template>
