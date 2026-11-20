// news-image-20261120 entrypoint (round 2).
// Copies the pre-rendered infographic to /output/entry.png.
// Node 22, standard library only, no network, deterministic.
import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = join(here, "entry.png");
const outDir = "/output";
const dst = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(src, dst);

const bytes = statSync(dst).size;
if (bytes === 0 || bytes > 1024 * 1024) {
  throw new Error(`entry.png size ${bytes} outside 1..1048576 bytes`);
}
console.log(`entry.png -> ${dst} (${bytes} bytes)`);
