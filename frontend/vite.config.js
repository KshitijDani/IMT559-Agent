import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, "..", "");

  return {
    envDir: "..",
    define: {
      "import.meta.env.ALLOW_DEV_AUTH": JSON.stringify(env.ALLOW_DEV_AUTH || "false"),
      "import.meta.env.VITE_GOOGLE_CLIENT_ID": JSON.stringify(env.GOOGLE_CLIENT_ID || "")
    },
    plugins: [react()]
  };
});
