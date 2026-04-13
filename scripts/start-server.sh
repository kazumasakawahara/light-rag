#!/bin/bash
# LightRAG Server Launcher
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Load .env
set -a
source .env
set +a

echo "================================"
echo "  LightRAG Server Starting..."
echo "  http://${HOST:-0.0.0.0}:${PORT:-9621}"
echo "================================"
echo ""

# Start server
exec lightrag-server
