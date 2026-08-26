import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// TODO: point the /api proxy at the backend host once deployment domains are known.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
