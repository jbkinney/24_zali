#!/bin/bash
# Train models using CPU instead of GPU to avoid memory issues
# Usage: bash train_with_cpu.sh [config_file] [output_dir]

CONFIG_FILE="${1:-config/training_config.yaml}"
OUTPUT_DIR="${2:-output}"

# Force CPU usage
export CUDA_VISIBLE_DEVICES=-1

# Run the training script
bash scripts/train_all_models.sh "$CONFIG_FILE" "$OUTPUT_DIR"

