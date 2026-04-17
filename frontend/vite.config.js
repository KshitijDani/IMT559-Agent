import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, "..", "");

  return {
    envDir: "..",
    define: {
      "import.meta.env.VITE_BASE_URL": JSON.stringify(env.BASE_URL || "")
    },
    plugins: [react()]
  };
});
