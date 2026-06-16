import path from "node:path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";

const apiTarget = process.env.VITE_DATUS_API_TARGET ?? "http://localhost:8000";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return undefined;
          if (id.includes("markdown-it") || id.includes("@mdit")) return "vendor-markdown";
          if (id.includes("@lucide/vue")) return "vendor-icons";
          if (id.includes("echarts") || id.includes("vue-echarts")) return "vendor-charts";
          if (id.includes("reka-ui")) return "vendor-ui";
          if (id.includes("js-yaml")) return "vendor-utils";
          if (id.includes("vue")) return "vendor-vue";
          return undefined;
        },
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  optimizeDeps: {
    include: [
      "vue",
      "@lucide/vue",
      "echarts",
      "echarts/core",
      "echarts/charts",
      "echarts/components",
      "echarts/renderers",
      "vue-echarts",
    ],
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: apiTarget,
        changeOrigin: true,
      },
      "/health": {
        target: apiTarget,
        changeOrigin: true,
      },
    },
  },
});
