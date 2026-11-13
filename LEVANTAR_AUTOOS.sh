#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/web"
if ! command -v node >/dev/null; then echo 'Instala Node.js 20+ para ejecutar AutoOS.'; exit 1; fi
if [[ ! -d node_modules/vite ]]; then npm install; fi
echo 'AutoOS en http://localhost:3000'
npm run dev
