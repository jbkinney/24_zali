# Memory Issue Fix

## Problem

The workflow was getting "Killed: 9" errors, which indicates the process was killed by the operating system due to running out of memory. This happens because:

1. **Memory Accumulation**: Training multiple models in a single Python process causes memory to accumulate, even with cleanup
2. **TensorFlow/Keras**: These frameworks can hold onto memory even after clearing sessions
3. **Large Models**: Each model can use significant GPU/CPU memory during training

## Solution

The workflow has been restructured to train **each model in a separate Python process**. This ensures:

- Complete memory cleanup between models (OS reclaims all memory when process exits)
- No memory accumulation across multiple models
- Better isolation (if one model fails, others can still run)

## How It Works

1. **Shell Script Wrapper** (`scripts/train_all_models.sh`): 
   - Parses the config file to get all model tasks
   - Calls `train_model_by_index.py` once per model
   - Each call runs in a separate Python process

2. **Single Model Script** (`scripts/train_model_by_index.py`):
   - Trains exactly one model configuration
   - Exits after completion, freeing all memory
   - Can be run independently for debugging

3. **Snakemake Workflow**:
   - Calls the shell script which handles sequential training
   - Tracks all output files for dependency management

## Usage

### Option 1: Use Snakemake (Recommended)

```bash
snakemake -j 1
```

### Option 2: Use Shell Script Directly

```bash
bash scripts/train_all_models.sh config/training_config.yaml output
```

### Option 3: Train Individual Models

```bash
# Train model 0, sample set 0
python scripts/train_model_by_index.py \
    --config config/training_config.yaml \
    --model-index 0 \
    --sample-set-index 0 \
    --output-dir output
```

## Memory Management Tips

1. **Monitor Memory**: Use `htop` or `top` to watch memory usage
2. **Reduce Batch Size**: If still having issues, reduce `batch_size` in config
3. **Train Fewer Models**: Comment out models in config file if needed
4. **Use CPU**: If GPU memory is the issue, TensorFlow will fall back to CPU automatically

## Expected Behavior

- Each model trains in ~5-30 minutes
- Memory usage should drop to baseline between models
- Process exits cleanly after each model
- All models are saved even if some fail

## Troubleshooting

### "Killed: 9" Still Happening

1. Check available memory: `free -h` (Linux) or Activity Monitor (Mac)
2. Reduce batch size in config
3. Train models one at a time manually
4. Close other memory-intensive applications

### "ModuleNotFoundError: No module named 'yaml'"

```bash
pip install pyyaml
```

### Models Not Training

Check individual log files in `output/`:
```bash
ls output/*.log
tail output/NGS-NZ-3454_A1-1W_A1-Out.log
```

