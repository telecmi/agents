#!/usr/bin/env bash


wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

mv kokoro-v1.0.onnx src/piopiy/services/opensource/kokoro/data/kokoro-v1.0.onnx
mv voices-v1.0.bin src/piopiy/services/opensource/kokoro/data/voices-v1.0.bin

