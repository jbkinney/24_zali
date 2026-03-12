# MPOS Model Training

Trains [MAVE-NN](https://github.com/jbkinney/mavenn) additive models on MPOS count data to infer sequence determinants of replication origin activity in *Y. lipolytica*. Uses Snakemake for workflow management and supports both local and cluster (SLURM) execution.

## Prerequisites

- Python 3.7+
- [Snakemake](https://snakemake.readthedocs.io/)
- [MAVE-NN](https://github.com/jbkinney/mavenn) — expected at `../mavenn` (or modify path in `scripts/train_mpos_models.py`)
- TensorFlow 2.5+

```bash
pip install -r requirements.txt
```

If you encounter a `pulp.list_solvers` error with Snakemake, pin pulp: `pip install pulp==2.7`

## Input Data

Place the following in `data/` (not included in repo due to size):

| File | Description |
|------|-------------|
| `NGS-NZ-3454.txt` | Count table from sequencing run 3454 (output of `MPOS_sequencing_pipeline/`) |
| `NGS-NZ-3477.txt` | Count table from sequencing run 3477 |
| `ORI_A_library_*.csv` | OriA-006 library sequences |
| `ORI_C_library_*.csv` | OriC-061 library sequences |

## Configuration

Edit `config/training_config.yaml` to set:

- **`models`**: list of model configs (readcount file, library file, sample names, adapter lengths, sample pairs to fit)
- **`training_params`**: learning rate (1e-3), epochs (500), batch size (1), early stopping patience (2)

## Running

### Local

```bash
# Full workflow (models train sequentially to avoid memory issues)
snakemake -j 1

# Or use the wrapper script
./run_workflow.sh

# Train a single model by index
python scripts/train_model_by_index.py \
    --config config/training_config.yaml \
    --model-index 0 --sample-set-index 0 --output-dir output
```

### SLURM Cluster

```bash
sbatch submit_slurm.sh
```

Edit `submit_slurm.sh` to match your cluster's module and resource configuration.

## Output

All results are saved to `output/`:

- `{name}_{samples}.pickle` / `.weights.h5` — trained model and weights
- `{name}_{samples}_logo.png` — sequence logo
- `{name}_*_training_history.png`, `*_measurement_process.png`, `*_zipf_plots.png` — diagnostics

## Memory Notes

Models are trained in separate Python processes to avoid TensorFlow memory accumulation. If you still encounter "Killed: 9" errors:

1. Reduce `batch_size` in config
2. Limit dataset size: `export MPOS_MAX_SEQUENCES=10000`
3. Force CPU: `export CUDA_VISIBLE_DEVICES=-1`
4. Train models individually via `scripts/train_model_by_index.py`

Minimum 8 GB RAM recommended (16 GB preferred). GPU optional.

## Directory Structure

```
├── Snakefile                       # Workflow definition
├── config/training_config.yaml     # Model and training configuration
├── scripts/
│   ├── train_mpos_models.py        # Main training script
│   ├── train_model_by_index.py     # Single-model trainer (for memory isolation)
│   ├── train_all_models.sh         # Sequential training with auto-resume
│   └── ...
├── data/                           # Input data (user-provided)
└── output/                         # Results (created at runtime)
```
