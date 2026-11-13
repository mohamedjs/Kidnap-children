import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// The web app talks to the API only. In dev, /api is proxied to the FastAPI process.
// Photos never go through here: the browser PUTs/GETs them on presigned bucket URLs.
const api = process.env.API_URL ?? "http://127.0.0.1:4100";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: "localhost",
    port: 3100,
    strictPort: true,
    proxy: { "/api": { target: api, changeOrigin: false } },
  },
  preview: { port: 3100, strictPort: true, proxy: { "/api": { target: api } } },
});
