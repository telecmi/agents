# Installation Guide

```bash
pip install numpy loguru onnxruntime transformers
```

**For GPU support (recommended for better performance):**

```bash
pip install numpy loguru onnxruntime-gpu transformers
```

## Download Model File

Download the Smart Turn V3 ONNX model from Hugging Face:

```bash
# Create directory structure
mkdir -p piopiy/audio/turn/smart_turn/data

# Download the model file
wget https://huggingface.co/pipecat-ai/smart-turn-v3/tree/main -O piopiy/audio/turn/smart_turn/data/smart-turn-v3.0.onnx
```

**Or download manually:**

1. Go to: https://huggingface.co/pipecat-ai/smart-turn-v3/blob/main/smart-turn-v3.0.onnx
2. Click the download button
3. Place the file in: `piopiy/audio/vad/data/smart-turn-v3.0.onnx`
