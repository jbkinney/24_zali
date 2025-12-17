# Quick Start Guide

## Prerequisites Check

Before running, ensure you have:

1. **Python 3.7+** installed
   ```bash
   python --version
   ```

2. **Snakemake** installed
   ```bash
   pip install snakemake
   # or
   conda install -c bioconda snakemake
   ```

3. **MAVE-NN package** accessible
   - The `mavenn` directory should be at `../mavenn` relative to this workflow
   - Or modify the path in `scripts/train_mpos_models.py`

## Installation (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: If you encounter a `pulp.list_solvers` error, run:
   ```bash
   ./fix_pulp.sh
   # or manually:
   pip install --upgrade "pulp==2.7"
   ```

2. **Add your data files to the `data/` directory:**
   
   **Note**: Data files are not included in this repository. You must provide your own data files.
   
   Required files:
   - `NGS-NZ-3454.txt` - Read counts for experiment 3454
   - `NGS-NZ-3477.txt` - Read counts for experiment 3477
   - `ORI_A_library_2024-06-13_13_22_23.012484.csv` - ORI A library sequences
   - `ORI_C_library_2024-06-13_13_22_23.186347.csv` - ORI C library sequences
   
   Place these files in the `data/` directory, then verify:
   ```bash
   ls data/
   ```
   
   If your files have different names, update the paths in `config/training_config.yaml`.

3. **Verify mavenn is accessible:**
   ```bash
   python -c "import sys; sys.path.insert(0, '../mavenn'); import mavenn; print('MAVE-NN found!')"
   ```

## Running the Workflow

### Option 1: Using the wrapper script (Easiest)

```bash
# Run the workflow
./run_workflow.sh

# Dry run to see what will happen
./run_workflow.sh --dry-run

# Run with verbose output
./run_workflow.sh --verbose
```

### Option 2: Using Snakemake directly

```bash
# Run the workflow
# Note: Models are trained one at a time by default to prevent memory issues
snakemake -j 1

# Dry run
snakemake -n

# Verbose output
snakemake -j 1 -v
```

### Option 3: Train a single model directly (Recommended if you get memory errors)

```bash
# Train a specific model by index (easiest way)
bash scripts/train_single_model.sh 0 0

# Or use Python directly
python scripts/train_model_by_index.py \
    --config config/training_config.yaml \
    --model-index 0 \
    --sample-set-index 0 \
    --output-dir output
```

### Option 4: Train all models sequentially (shell script)

```bash
# Train all models one at a time
bash scripts/train_all_models.sh config/training_config.yaml output
```

## Expected Runtime

- **Per model**: ~5-30 minutes (depending on data size and hardware)
- **Full workflow**: ~1-3 hours for all models (models train sequentially)
- **With GPU**: Significantly faster
- **Note**: Models are trained one at a time by default to prevent memory issues

## Output Location

All results will be saved in the `output/` directory:
- Model files: `output/{run_name}_{sample_set}.pickle` and `.weights.h5`
- Plots: `output/*.png`
- Logs: `output/training.log`

## Troubleshooting

### "mavenn not found"
```bash
# Check if mavenn exists
ls ../mavenn

# If not, create a symlink or modify the path in train_mpos_models.py
```

### GPU memory errors
```bash
# Run with fewer parallel jobs
snakemake -j 1

# Or modify batch_size in config/training_config.yaml
```

### File not found errors
```bash
# Verify data files exist
ls -lh data/

# Check paths in config/training_config.yaml
```

## Next Steps

- Review the full [README.md](README.md) for detailed documentation
- Customize `config/training_config.yaml` for your specific needs
- Check `output/` directory for results after completion

