<script setup lang="ts">
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { BarChart, LineChart, PieChart, ScatterChart } from "echarts/charts";
import { DataZoomComponent, GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

use([BarChart, LineChart, PieChart, ScatterChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent, CanvasRenderer]);

defineProps<{
  option: Record<string, unknown>;
}>();
</script>

<template>
  <VChart :option="option" autoresize style="width: 100%; height: 260px;" />
</template>
