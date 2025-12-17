# MPOS Model Training Workflow

This package contains a Snakemake workflow for training MAVE-NN models on MPOS (Multiplexed Origin of Replication Sequencing) data. The workflow trains models to classify DNA sequences into different samples based on their sequence content.

## Directory Structure

```
mpos_model_training/
├── README.md                 # This file
├── Snakefile                 # Snakemake workflow definition
├── requirements.txt          # Python dependencies
├── config/
│   └── training_config.yaml  # Configuration file for model training
├── data/                     # Input data files (not included in repo - see Data Files section)
│   └── .gitkeep             # Placeholder to maintain directory structure
├── scripts/
│   └── train_mpos_models.py  # Main training script
└── output/                   # Output directory (created at runtime)
    ├── *.pickle              # Trained model files
    ├── *.weights.h5          # Model weights
    └── *.png                 # Plots and visualizations
```

## Prerequisites

1. **Python 3.7+** with pip
2. **Snakemake** (install via `pip install snakemake` or `conda install -c bioconda snakemake`)
3. **MAVE-NN package** - The `mavenn` directory should be located at the same level as this workflow directory (i.e., `../mavenn`)

## Installation

1. Clone or copy this directory to your desired location
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **Add your data files** (see [Data Files](#data-files) section below)
4. Ensure the MAVE-NN package is available. The script expects it at `../mavenn` relative to this directory. If it's located elsewhere, you can:
   - Create a symlink: `ln -s /path/to/mavenn ../mavenn`
   - Or modify the path in `scripts/train_mpos_models.py` (line 18)

## Data Files

**Important**: Data files are not included in this repository due to their size. You must provide your own data files.

### Required Data Files

Place the following data files in the `data/` directory:

1. **Read count files** (`.txt` format):
   - `NGS-NZ-3454.txt` - Read counts for experiment 3454
   - `NGS-NZ-3477.txt` - Read counts for experiment 3477

2. **Library sequence files** (`.csv` format):
   - `ORI_A_library_2024-06-13_13_22_23.012484.csv` - ORI A library sequences
   - `ORI_C_library_2024-06-13_13_22_23.186347.csv` - ORI C library sequences

### Data File Format

- **Read count files** (`.txt`): Tab-separated files with columns for sequence identifiers and read counts per sample
- **Library sequence files** (`.csv`): CSV files containing sequence information for the library

### Updating Configuration

After adding your data files, update `config/training_config.yaml` to point to the correct file paths. The default configuration expects files in the `data/` directory with the names listed above.

If your files have different names or locations, update the `readcount_file` and `library_seqs_file` paths in the `models` section of `config/training_config.yaml`.

## Configuration

Edit `config/training_config.yaml` to configure:
- Which models to train
- Input data files (paths to your data files)
- Sample names and groupings
- Training parameters
- Output settings

### Key Configuration Parameters

- `output_dir`: Directory where results will be saved
- `data_dir`: Directory containing input data files
- `models`: List of model configurations, each with:
  - `readcount_file`: Path to read count data
  - `library_seqs_file`: Path to library sequences
  - `all_samples`: List of all sample names
  - `adapter_lengths`: [front_adapter, back_adapter] lengths
  - `fit_samples`: List of sample pairs to train models for
  - `fit_model`: Whether to train models (true/false)
  - `sign_flips`: List of booleans for sign flipping per model
  - `reverse_complement`: Whether to reverse complement sequences

## Usage

### Running Locally

#### Option 1: Using Snakemake (Recommended)

```bash
# Run the entire workflow
# Note: Models are trained one at a time by default to prevent memory issues
snakemake -j 1

# Dry run to see what will be executed
snakemake -n

# Run with verbose output
snakemake -j 1 -v
```

#### Option 2: Train a Single Model

If you encounter memory issues, you can train models one at a time:

```bash
# Train model 0, sample set 0
bash scripts/train_single_model.sh 0 0

# Train model 1, sample set 0
bash scripts/train_single_model.sh 1 0
```

Or use Python directly:

```bash
python scripts/train_model_by_index.py \
    --config config/training_config.yaml \
    --model-index 0 \
    --sample-set-index 0 \
    --output-dir output
```

#### Option 3: Resume Training

The `train_all_models.sh` script automatically skips models that are already completed.
If training fails partway through, simply run it again:

```bash
bash scripts/train_all_models.sh config/training_config.yaml output
```

It will resume from where it left off.

### Running on a Compute Cluster

#### SLURM Example

Create a file `submit_slurm.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=mpos_training
#SBATCH --output=logs/slurm_%j.out
#SBATCH --error=logs/slurm_%j.err
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1  # If GPU available

# Load required modules (adjust for your cluster)
module load python/3.9
module load cuda/11.0  # If using GPU

# Activate conda environment if using one
# conda activate mpos_env

# Run Snakemake
snakemake -j 1 --use-conda
```

Submit with:
```bash
mkdir -p logs
sbatch submit_slurm.sh
```

#### PBS/Torque Example

Create a file `submit_pbs.sh`:

```bash
#!/bin/bash
#PBS -N mpos_training
#PBS -o logs/pbs_${PBS_JOBID}.out
#PBS -e logs/pbs_${PBS_JOBID}.err
#PBS -l walltime=24:00:00
#PBS -l nodes=1:ppn=4
#PBS -l mem=16gb
#PBS -l gpus=1  # If GPU available

cd $PBS_O_WORKDIR

# Load modules and run
module load python/3.9
snakemake -j 1
```

Submit with:
```bash
mkdir -p logs
qsub submit_pbs.sh
```

#### SGE Example

Create a file `submit_sge.sh`:

```bash
#!/bin/bash
#$ -N mpos_training
#$ -o logs/sge_$JOB_ID.out
#$ -e logs/sge_$JOB_ID.err
#$ -l h_rt=24:00:00
#$ -pe smp 4
#$ -l mem_free=16G
#$ -l gpu=1  # If GPU available

cd $SGE_O_WORKDIR
snakemake -j 1
```

Submit with:
```bash
mkdir -p logs
qsub submit_sge.sh
```

## Output Files

After running the workflow, the `output/` directory will contain:

### Model Files
- `{run_name}_{sample_set}.pickle`: Saved model object
- `{run_name}_{sample_set}.weights.h5`: Model weights in HDF5 format

### Visualization Files
- `{run_name}_read_counts.png`: Bar plot of total read counts per sample
- `{run_name}_{library}_counts.png`: Matched read counts
- `{run_name}_{library}_match_rates.png`: Fraction of reads matching library
- `{run_name}_{library}_zipf_plots.png`: Zipf plots for all samples
- `{run_name}_{sample_set}_zipf_plots.png`: Overlayed Zipf plots for training samples
- `{run_name}_{sample_set}_training_history.png`: Training/validation information over epochs
- `{run_name}_{sample_set}_measurement_process.png`: Probability distributions
- `{run_name}_{sample_set}_logo.png`: Sequence logo plot

## Memory Management

The workflow includes automatic GPU memory management:
- GPU memory growth is enabled to prevent TensorFlow from allocating all memory at once
- TensorFlow sessions are cleared after each model training
- Garbage collection is run to free Python objects

If you encounter GPU memory issues:
1. Reduce `batch_size` in the configuration
2. Train models one at a time (set `-j 1` in Snakemake)
3. Use CPU instead of GPU (TensorFlow will automatically fall back)

## Troubleshooting

### Issue: "Killed: 9" or Out of Memory Errors

**Solution**: The workflow has been designed to train each model in a separate process to avoid memory accumulation. If you still encounter memory issues:

1. **Check available memory**:
   ```bash
   # Linux
   free -h
   # Mac
   vm_stat
   ```

2. **Reduce batch size** in `config/training_config.yaml`:
   ```yaml
   training_params:
     batch_size: 1  # Reduce from default if needed
   ```

3. **Train models manually one at a time**:
   ```bash
   python scripts/train_model_by_index.py \
       --config config/training_config.yaml \
       --model-index 0 \
       --sample-set-index 0 \
       --output-dir output
   ```

4. **Close other applications** to free up memory

See `MEMORY_FIX.md` for more details on the memory management approach.

### Issue: "ModuleNotFoundError: No module named 'mavenn'"

**Solution**: Ensure the mavenn package is accessible. Check that:
- The `mavenn` directory exists at `../mavenn` relative to this workflow
- Or modify the path in `scripts/train_mpos_models.py` line 18

### Issue: GPU memory errors

**Solution**: 
- Reduce batch size in configuration
- Train models sequentially (`-j 1`)
- Check GPU memory: `nvidia-smi` (for NVIDIA GPUs)

### Issue: File not found errors

**Solution**: 
- Verify all data files are in the `data/` directory
- Check file paths in `config/training_config.yaml`
- Use absolute paths if relative paths don't work

### Issue: Snakemake not found

**Solution**: Install Snakemake:
```bash
pip install snakemake
# or
conda install -c bioconda snakemake
```

### Issue: "AttributeError: module 'pulp' has no attribute 'list_solvers'"

**Solution**: This is a version incompatibility between `pulp` and `snakemake`. Fix it by:
```bash
# Run the fix script
./fix_pulp.sh

# Or manually downgrade pulp
pip install --upgrade "pulp==2.7"
```

The issue occurs because newer versions of `pulp` (2.8+) changed the method name from `list_solvers` to `listSolvers`, but Snakemake still expects the old name. Pinning `pulp` to version 2.7 resolves this.

### Issue: "ModuleNotFoundError: No module named 'yaml'"

**Solution**: Install PyYAML:
```bash
pip install pyyaml
```

Note: `pyyaml` provides the `yaml` module, so installing `pyyaml` is sufficient.

## Customization

### Adding New Models

Edit `config/training_config.yaml` and add a new entry to the `models` list:

```yaml
- name: "MyNewModel"
  readcount_file: "data/my_data.txt"
  library_seqs_file: "data/my_library.csv"
  all_samples: ["sample1", "sample2", ...]
  adapter_lengths: [21, 19]
  zipf_figure_shape: [2, 2]
  fit_samples:
    - ["sample1", "sample2"]
  fit_model: true
  sign_flips: [false]
  reverse_complement: false
```

### Modifying Training Parameters

Edit the `training_params` section in `config/training_config.yaml`:

```yaml
training_params:
  learning_rate: 1e-3      # Learning rate
  epochs: 500              # Maximum epochs
  batch_size: 1            # Batch size (reduce if memory issues)
  early_stopping: true     # Enable early stopping
  early_stopping_patience: 2  # Patience for early stopping
```

## Citation

If you use this workflow, please cite:
- MAVE-NN: [Kinney & Atwal (2019) bioRxiv](https://www.biorxiv.org/content/10.1101/253211v1)
- Your MPOS publication (if applicable)

## License

[Specify your license here]

## Contact

[Your contact information]

