# Memory Troubleshooting Guide

If you encounter "Killed: 9" errors during model training, this indicates the process is running out of memory. Here are several solutions:

## Quick Fixes

### 1. Use CPU Instead of GPU
If GPU memory is the issue, force CPU usage:

```bash
export CUDA_VISIBLE_DEVICES=-1
bash scripts/train_all_models.sh config/training_config.yaml output
```

Or use the provided script:
```bash
bash scripts/train_with_cpu.sh config/training_config.yaml output
```

### 2. Reduce Dataset Size
Limit the number of sequences used for training:

```bash
export MPOS_MAX_SEQUENCES=10000  # Use only 10k sequences
bash scripts/train_all_models.sh config/training_config.yaml output
```

### 3. Train One Model at a Time
Instead of running all models, train them individually:

```bash
python3 scripts/train_model_by_index.py \
    --config config/training_config.yaml \
    --model-index 0 \
    --sample-set-index 0 \
    --output-dir output
```

## Memory Optimizations Already Applied

The training script includes several memory optimizations:

1. **Dataset Size Limiting**: Automatically limits to 30,000 sequences by default
2. **Adaptive Batch Size**: Uses smaller batches for large datasets
3. **Memory Clearing**: Aggressively clears TensorFlow sessions between models
4. **GPU Memory Growth**: Prevents TensorFlow from allocating all GPU memory at once

## Additional Options

### Reduce Training Epochs
Edit `config/training_config.yaml` to reduce `epochs` (currently 500):

```yaml
training_params:
  epochs: 100  # Reduce from 500
```

### Increase Early Stopping Patience
This will stop training earlier if validation loss doesn't improve:

```yaml
training_params:
  early_stopping_patience: 5  # Increase from 2
```

### Use a Smaller Subset of Data
You can pre-filter your data files to include only a subset of sequences before running the workflow.

## System Requirements

- **Minimum RAM**: 8GB (16GB recommended)
- **GPU Memory**: 4GB+ if using GPU (or use CPU mode)
- **Disk Space**: ~1GB per model for outputs

## Monitoring Memory Usage

On macOS/Linux, you can monitor memory usage:

```bash
# In another terminal, watch memory usage
watch -n 1 'ps aux | grep python | grep -v grep'
```

Or use `htop` or `top` to monitor system memory.

