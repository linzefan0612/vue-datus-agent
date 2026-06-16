<script setup lang="ts">
import { ref, shallowRef, computed, onMounted } from "vue";
import { ArrowLeft, BarChart3, Clock, Database, Loader2, RefreshCw, Table2 } from "@lucide/vue";

import Badge from "@/components/ui/Badge.vue";
import Button from "@/components/ui/Button.vue";
import ScrollArea from "@/components/ui/ScrollArea.vue";
import { dashboardApi } from "@/lib/api";
import { useConnection } from "@/composables/useConnection";
import { formatDate } from "@/lib/utils";
import type { ArtifactManifest } from "@/types";

const { effectiveBase } = useConnection();

// ─── State ───────────────────────────────────────────────────────────────────

const dashboards = ref<ArtifactManifest[]>([]);
const loading = shallowRef(false);
const selectedSlug = shallowRef<string | null>(null);
const iframeLoading = shallowRef(false);

// ─── Load list ───────────────────────────────────────────────────────────────

async function loadDashboards() {
  loading.value = true;
  try {
    const result = await dashboardApi.list(effectiveBase());
    if (result) dashboards.value = result;
  } catch (e) {
    console.error("Failed to load dashboards:", e);
  } finally {
    loading.value = false;
  }
}

// ─── Select dashboard ────────────────────────────────────────────────────────

function selectDashboard(slug: string) {
  selectedSlug.value = slug;
  iframeLoading.value = true;
}

function goBack() {
  selectedSlug.value = null;
}

// ─── Derived ─────────────────────────────────────────────────────────────────

const iframeSrc = computed(() => {
  if (!selectedSlug.value) return "";
  return dashboardApi.htmlUrl(effectiveBase(), selectedSlug.value);
});

const selectedManifest = computed(() =>
  dashboards.value.find((d) => d.slug === selectedSlug.value) ?? null
);

// ─── Init ────────────────────────────────────────────────────────────────────

onMounted(loadDashboards);
</script>

<template>
  <div class="dashboardView">
    <!-- List view -->
    <template v-if="!selectedSlug">
      <div class="dashboardHeader">
        <h2>仪表盘</h2>
        <div class="dashboardHeaderActions">
          <Button variant="ghost" size="icon" :disabled="loading" aria-label="刷新" @click="loadDashboards">
            <Loader2 v-if="loading" class="spin" :size="16" />
            <RefreshCw v-else :size="16" />
          </Button>
        </div>
      </div>

      <ScrollArea class="dashboardList">
        <div v-if="loading && dashboards.length === 0" class="dashboardEmpty">
          <Loader2 class="spin" :size="24" />
          <p>加载中...</p>
        </div>
        <div v-else-if="dashboards.length === 0" class="dashboardEmpty">
          <BarChart3 :size="32" />
          <p>暂无仪表盘</p>
          <p class="dashboardEmptyHint">在对话中让 Agent 生成仪表盘</p>
        </div>
        <div v-else class="dashboardGrid">
          <button
            v-for="d in dashboards"
            :key="d.slug"
            class="dashboardCard"
            type="button"
            @click="selectDashboard(d.slug)"
          >
            <div class="dashboardCardHeader">
              <BarChart3 :size="16" />
              <strong>{{ d.name }}</strong>
            </div>
            <p class="dashboardCardDesc">{{ d.description }}</p>
            <div class="dashboardCardMeta">
              <span v-if="d.created_at" class="dashboardCardDate">
                <Clock :size="12" />
                {{ formatDate(d.updated_at || d.created_at) }}
              </span>
              <Badge v-if="d.datasources && d.datasources.length > 0" variant="secondary">
                <Database :size="10" />
                {{ d.datasources.length }}
              </Badge>
              <Badge v-if="d.key_tables && d.key_tables.length > 0" variant="outline">
                <Table2 :size="10" />
                {{ d.key_tables.length }}
              </Badge>
            </div>
          </button>
        </div>
      </ScrollArea>
    </template>

    <!-- Detail view: iframe-rendered dashboard -->
    <template v-else>
      <div class="dashboardHeader">
        <Button variant="ghost" size="icon" aria-label="返回" @click="goBack">
          <ArrowLeft :size="16" />
        </Button>
        <h2>{{ selectedManifest?.name ?? selectedSlug }}</h2>
        <div class="dashboardHeaderActions">
          <Badge v-if="selectedManifest?.datasources?.length" variant="secondary">
            <Database :size="10" />
            {{ selectedManifest.datasources.join(", ") }}
          </Badge>
          <span v-if="selectedManifest?.created_at" class="dashboardCardDate">
            <Clock :size="12" />
            {{ formatDate(selectedManifest.updated_at || selectedManifest.created_at) }}
          </span>
        </div>
      </div>

      <div class="dashboardIframeWrap">
        <div v-if="iframeLoading" class="dashboardIframeLoading">
          <Loader2 class="spin" :size="24" />
          <p>加载仪表盘...</p>
        </div>
        <iframe
          v-if="iframeSrc"
          :src="iframeSrc"
          class="dashboardIframe"
          sandbox="allow-scripts allow-same-origin allow-forms"
          frameborder="0"
          @load="iframeLoading = false"
        />
      </div>
    </template>
  </div>
</template>
