#!/bin/bash

echo "🎯 Downloading Kokoro model files..."

# Get script directory (where this script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Target directory relative to script location
TARGET_DIR="$SCRIPT_DIR/src/piopiy/services/opensource/kokoro/data"

# Create target directory
mkdir -p "$TARGET_DIR"

# Check if files already exist
if [ -f "$TARGET_DIR/kokoro-v1.0.onnx" ] && [ -f "$TARGET_DIR/voices-v1.0.bin" ]; then
    echo "✅ Kokoro files already exist, skipping download"
    exit 0
fi

# URLs
MODEL_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

# Download directly to target directory
echo "📥 Downloading kokoro-v1.0.onnx..."
if wget -q --show-progress -O "$TARGET_DIR/kokoro-v1.0.onnx" "$MODEL_URL"; then
    echo "✅ Downloaded kokoro-v1.0.onnx"
else
    echo "❌ Failed to download kokoro-v1.0.onnx"
    exit 1
fi

echo "📥 Downloading voices-v1.0.bin..."
if wget -q --show-progress -O "$TARGET_DIR/voices-v1.0.bin" "$VOICES_URL"; then
    echo "✅ Downloaded voices-v1.0.bin"
else
    echo "❌ Failed to download voices-v1.0.bin"
    exit 1
fi

echo "🎉 Kokoro model files downloaded successfully!"
echo "📁 Files saved to: $TARGET_DIR"
ls -lh "$TARGET_DIR/"