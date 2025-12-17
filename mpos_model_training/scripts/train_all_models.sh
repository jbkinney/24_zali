#!/bin/bash
# Train all models one at a time to avoid memory issues

set -e  # Exit on error

CONFIG_FILE="${1:-config/training_config.yaml}"
OUTPUT_DIR="${2:-output}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKFLOW_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$WORKFLOW_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Get tasks using Python (with yaml)
TASKS=$(python3 << PYTHON_EOF
import sys
import os

try:
    import yaml
except ImportError:
    print("ERROR: yaml module not found. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    config_file = "$CONFIG_FILE"
    if not os.path.exists(config_file):
        print(f"ERROR: Config file not found: {config_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    if not config:
        print("ERROR: Config file is empty or invalid", file=sys.stderr)
        sys.exit(1)
    
    if 'models' not in config:
        print("ERROR: 'models' key not found in config", file=sys.stderr)
        sys.exit(1)
    
    tasks = []
    for model_idx, model_config in enumerate(config['models']):
        if model_config.get('fit_model', True):
            fit_samples = model_config.get('fit_samples', [])
            if not fit_samples:
                print(f"Warning: Model {model_idx} has no fit_samples, skipping", file=sys.stderr)
                continue
            for sample_set_idx in range(len(fit_samples)):
                tasks.append(f"{model_idx},{sample_set_idx}")
    
    print(" ".join(tasks))
except Exception as e:
    print(f"ERROR: Failed to parse config: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
PYTHON_EOF
)

if [ $? -ne 0 ] || [ -z "$TASKS" ]; then
    echo "Error: Failed to parse configuration file or no models to train"
    exit 1
fi

TOTAL_TASKS=$(echo $TASKS | wc -w | tr -d ' ')
echo "Found $TOTAL_TASKS model(s) to train"
echo ""

# Track statistics
SUCCESS_COUNT=0
SKIPPED_COUNT=0
FAILED_COUNT=0
FAILED_MODELS=()

# Train each model separately with complete isolation
# Each model runs in its own process, and we wait for it to complete before starting the next
for task in $TASKS; do
    IFS=',' read -r model_idx sample_set_idx <<< "$task"
    
    # Get the expected output file name to check if already completed
    SAMPLE_SET_NAME=$(python3 << PYTHON_EOF
try:
    import yaml
except ImportError:
    print("ERROR: yaml module not found", file=sys.stderr)
    sys.exit(1)
import sys
with open("$CONFIG_FILE", 'r') as f:
    config = yaml.safe_load(f)
model_config = config['models'][$model_idx]
readcount_file = model_config['readcount_file'].split('/')[-1]
run_name = readcount_file.split(".")[0]
fit_samples = model_config.get('fit_samples', [])
sample_set = fit_samples[$sample_set_idx]
sample_set_name = f"{run_name}_{'_'.join(sample_set)}"
print(sample_set_name)
PYTHON_EOF
)
    
    # Check if model is already completed (has pickle and weights files)
    if [ -f "$OUTPUT_DIR/${SAMPLE_SET_NAME}.pickle" ] && [ -f "$OUTPUT_DIR/${SAMPLE_SET_NAME}.weights.h5" ]; then
        echo "=========================================="
        echo "Skipping model $model_idx, sample set $sample_set_idx (already completed)"
        echo "Output: ${SAMPLE_SET_NAME}"
        echo "=========================================="
        SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
        continue
    fi
    
    echo "=========================================="
    echo "Training model $model_idx, sample set $sample_set_idx"
    echo "Output: ${SAMPLE_SET_NAME}"
    echo "=========================================="
    echo "Starting at: $(date)"
    
    # Create a temporary log file for this model to check for errors
    TEMP_LOG=$(mktemp)
    
    # Run each model in a completely separate process
    # Use 'timeout' if available to prevent hanging, and ensure process isolation
    TRAIN_EXIT_CODE=0
    if command -v timeout >/dev/null 2>&1; then
        # Use timeout as a safety measure (24 hours max per model)
        timeout 86400 python3 "$SCRIPT_DIR/train_model_by_index.py" \
            --config "$CONFIG_FILE" \
            --model-index "$model_idx" \
            --sample-set-index "$sample_set_idx" \
            --output-dir "$OUTPUT_DIR" > "$TEMP_LOG" 2>&1 || {
            TRAIN_EXIT_CODE=$?
        }
    else
        # No timeout command available, run directly
        python3 "$SCRIPT_DIR/train_model_by_index.py" \
            --config "$CONFIG_FILE" \
            --model-index "$model_idx" \
            --sample-set-index "$sample_set_idx" \
            --output-dir "$OUTPUT_DIR" > "$TEMP_LOG" 2>&1 || {
            TRAIN_EXIT_CODE=$?
        }
    fi
    
    # Check if the process was killed due to memory issues
    if [ $TRAIN_EXIT_CODE -ne 0 ]; then
        # Check for "Killed: 9" in the output (exit code 137 = 128 + 9)
        if [ $TRAIN_EXIT_CODE -eq 137 ] || grep -q "Killed: 9" "$TEMP_LOG" 2>/dev/null || grep -q "Killed" "$TEMP_LOG" 2>/dev/null; then
            echo ""
            echo "WARNING: Model $model_idx, sample set $sample_set_idx was killed due to memory issues (Killed: 9)"
            echo "This model will be skipped. You can try training it individually later with:"
            echo "  bash scripts/train_single_model.sh $model_idx $sample_set_idx"
            echo "  or"
            echo "  python scripts/train_model_by_index.py --config $CONFIG_FILE --model-index $model_idx --sample-set-index $sample_set_idx --output-dir $OUTPUT_DIR"
            echo ""
            # Save the log for this failed model
            mkdir -p "$OUTPUT_DIR/log"
            cp "$TEMP_LOG" "$OUTPUT_DIR/log/model_${model_idx}_ss_${sample_set_idx}_FAILED.log"
            echo "Error log saved to: $OUTPUT_DIR/log/model_${model_idx}_ss_${sample_set_idx}_FAILED.log"
            rm -f "$TEMP_LOG"
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_MODELS+=("$model_idx,$sample_set_idx")
            echo "Continuing with next model..."
            echo ""
            continue
        else
            # Other types of errors - still continue but log the error
            echo ""
            echo "ERROR: Failed to train model $model_idx, sample set $sample_set_idx (exit code: $TRAIN_EXIT_CODE)"
            echo "This model will be skipped. You can try training it individually later."
            # Save the log for this failed model
            mkdir -p "$OUTPUT_DIR/log"
            cp "$TEMP_LOG" "$OUTPUT_DIR/log/model_${model_idx}_ss_${sample_set_idx}_FAILED.log"
            echo "Error log saved to: $OUTPUT_DIR/log/model_${model_idx}_ss_${sample_set_idx}_FAILED.log"
            rm -f "$TEMP_LOG"
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_MODELS+=("$model_idx,$sample_set_idx")
            echo "Continuing with next model..."
            echo ""
            continue
        fi
    fi
    
    # Clean up temp log on success
    rm -f "$TEMP_LOG"
    
    # Explicitly wait for the process to complete and release all resources
    wait
    
    # Force garbage collection at shell level (clear any cached Python processes)
    # This ensures the next model starts with a clean slate
    echo "Completed model $model_idx, sample set $sample_set_idx at: $(date)"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    echo "Waiting 5 seconds to ensure memory is fully released..."
    sleep 5
    echo ""
done

echo "=========================================="
echo "Training Summary"
echo "=========================================="
echo "Total models: $TOTAL_TASKS"
echo "Successfully trained: $SUCCESS_COUNT"
echo "Skipped (already completed): $SKIPPED_COUNT"
echo "Failed: $FAILED_COUNT"
echo ""

if [ $FAILED_COUNT -gt 0 ]; then
    echo "Failed models:"
    for failed_model in "${FAILED_MODELS[@]}"; do
        IFS=',' read -r failed_model_idx failed_sample_set_idx <<< "$failed_model"
        echo "  - Model $failed_model_idx, sample set $failed_sample_set_idx"
        echo "    Retry with: bash scripts/train_single_model.sh $failed_model_idx $failed_sample_set_idx"
    done
    echo ""
    echo "You can retry failed models individually or run this script again."
    echo "The script will skip successfully completed models."
    exit 1
else
    echo "All models trained successfully!"
    exit 0
fi
