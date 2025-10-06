import { defineConfig } from "@playwright/test";
import path from "node:path";

const baseURL = process.env.API_BASE_URL ?? "http://localhost:8000/api/v1";

export default defineConfig({
  testDir: path.join(__dirname, "tests"),
  globalSetup: path.join(__dirname, "global-setup.ts"),
  fullyParallel: false,
  use: {
    baseURL,
    extraHTTPHeaders: {
      "content-type": "application/json",
    },
  },
  reporter: [["list"]],
});
