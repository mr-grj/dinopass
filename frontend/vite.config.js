import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // listen on 0.0.0.0 so the dev server is reachable from Docker
    port: Number(process.env.VITE_PORT) || 3000,
    strictPort: true,
    // File-system polling is needed for hot-reload inside Docker bind mounts.
    watch: process.env.VITE_USE_POLLING ? { usePolling: true } : undefined,
  },
  build: {
    outDir: "dist",
  },
});
