import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const isDocker = process.env.DOCKER === "true";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3002,
    host: "0.0.0.0",
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://localhost:5000", // 🔹 pour dev local
        changeOrigin: true,
      },
    },
  },
  define: {
    __BACKEND_URL__: JSON.stringify(
      isDocker
        ? "/api" // 🔹 quand le frontend est dans Docker
        : "http://localhost:5000/api" // 🔹 quand tu testes localement
    ),
  },
});
