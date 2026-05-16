#!/usr/bin/env bash
set -euo pipefail

# Downloads Supertonic 3 ONNX models from Hugging Face
# Usage: ./scripts/download-v3-models.sh [target_dir]
# Default target: ~/.cache/supertonic3

TARGET="${1:-$HOME/.cache/supertonic3}"

if [ -d "$TARGET/onnx" ] && [ -f "$TARGET/onnx/vector_estimator.onnx" ]; then
    echo "✓ Models already exist at $TARGET"
    du -sh "$TARGET/onnx"
    exit 0
fi

echo "→ Downloading Supertonic 3 models to $TARGET ..."

if ! command -v git-lfs &>/dev/null; then
    echo "Installing git-lfs..."
    sudo apt-get update -qq && sudo apt-get install -y -qq git-lfs
    git lfs install
fi

mkdir -p "$(dirname "$TARGET")"
git clone https://huggingface.co/Supertone/supertonic-3 "$TARGET"

echo ""
echo "✓ Done! Models downloaded to $TARGET"
du -sh "$TARGET/onnx"
