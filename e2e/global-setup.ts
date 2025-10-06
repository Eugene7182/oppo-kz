import { execSync } from "node:child_process";
import path from "node:path";

export default async function globalSetup(): Promise<void> {
  const repoRoot = path.resolve(__dirname, "..");
  const env = { ...process.env, PYTHONPATH: "backend" };
  execSync("python backend/scripts/seed_demo_data.py --purge", {
    cwd: repoRoot,
    stdio: "inherit",
    env,
  });
}
