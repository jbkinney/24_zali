#!/bin/bash
# Train a single model by index
# Usage: bash train_single_model.sh <model_index> <sample_set_index> [config_file] [output_dir] [--use-cpu]

MODEL_IDX="${1}"
SAMPLE_SET_IDX="${2}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKFLOW_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$WORKFLOW_DIR"

if [ -z "$MODEL_IDX" ] || [ -z "$SAMPLE_SET_IDX" ]; then
    echo "Usage: $0 <model_index> <sample_set_index> [config_file] [output_dir] [--use-cpu]"
    echo ""
    echo "Example: $0 0 0"
    echo "Example: $0 3 0 --use-cpu"
    echo "Example: $0 3 0 config/training_config.yaml output --use-cpu"
    exit 1
fi

# Parse optional arguments
CONFIG_FILE="config/training_config.yaml"
OUTPUT_DIR="output"
USE_CPU=""

# Check remaining arguments
shift 2  # Remove model_idx and sample_set_idx
while [[ $# -gt 0 ]]; do
    case $1 in
        --use-cpu)
            USE_CPU="--use-cpu"
            shift
            ;;
        *)
            # If it doesn't start with --, it's a positional argument
            if [[ ! "$1" =~ ^-- ]]; then
                if [ -z "$CONFIG_FILE" ] || [ "$CONFIG_FILE" == "config/training_config.yaml" ]; then
                    # First non-flag argument is config file (if not already set to default)
                    if [ -f "$1" ]; then
                        CONFIG_FILE="$1"
                    fi
                else
                    # Second non-flag argument is output dir
                    OUTPUT_DIR="$1"
                fi
            fi
            shift
            ;;
    esac
done

mkdir -p "$OUTPUT_DIR"

echo "Training model $MODEL_IDX, sample set $SAMPLE_SET_IDX"
echo "Config: $CONFIG_FILE"
echo "Output: $OUTPUT_DIR"
if [ -n "$USE_CPU" ]; then
    echo "Using CPU mode (GPU disabled)"
fi
echo ""

python3 "$SCRIPT_DIR/train_model_by_index.py" \
    --config "$CONFIG_FILE" \
    --model-index "$MODEL_IDX" \
    --sample-set-index "$SAMPLE_SET_IDX" \
    --output-dir "$OUTPUT_DIR" \
    $USE_CPU

