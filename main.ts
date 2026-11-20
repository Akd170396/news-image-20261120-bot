// Entry program for make.fun news-image-20261120.
// Copies the pre-rendered entry.png (drawn by render.py) to /output/entry.png.
// Node 22, standard library only, no network. Deterministic: same bytes every run.

import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

if (!existsSync(source)) {
  console.error("entry.png not found next to main.ts");
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

// Guard against a truncated copy: the output must be byte-identical in size.
const sourceSize = statSync(source).size;
const targetSize = statSync(target).size;
if (sourceSize !== targetSize) {
  console.error(`copy mismatch: source ${sourceSize} bytes, target ${targetSize} bytes`);
  process.exit(1);
}

console.log(`entry.png written to ${target} (${targetSize} bytes)`);
