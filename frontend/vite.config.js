import { defineConfig } from "vite";
import { resolve } from "path";

export default defineConfig({
  base: "/static/dist/",
  build: {
    manifest: true,
    outDir: "../static/dist",
    emptyOutDir: true,
    rollupOptions: {
      input: resolve(__dirname, "src/main.js"),
    },
  },
});
