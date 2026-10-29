import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  build: {
    outDir: "../custom_components/eta_heating_technology/frontend/panel",
    emptyOutDir: true,
    target: "es2021",
    modulePreload: false,
    rollupOptions: {
      input: "src/eta-panel.ts",
      output: {
        format: "es",
        entryFileNames: "eta-panel.js",
        inlineDynamicImports: true,
      },
    },
  },
});
