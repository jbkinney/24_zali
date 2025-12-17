# Package Information

## What This Package Contains

This package converts the Jupyter notebook `Train_models.ipynb` into an automated, cluster-ready workflow using Snakemake. It includes:

1. **Automated Workflow**: Snakemake-based pipeline for reproducible model training
2. **Standalone Scripts**: Python scripts that can run independently
3. **Configuration Management**: YAML-based configuration for easy customization
4. **Cluster Support**: Example submission scripts for SLURM, PBS, and SGE
5. **Data Files**: All required input data files packaged together

## Key Features

- ✅ **Reproducible**: Snakemake ensures consistent execution
- ✅ **Parallelizable**: Can run multiple models in parallel (with caution for GPU memory)
- ✅ **Cluster-Ready**: Includes submission scripts for common HPC systems
- ✅ **Configurable**: Easy to modify via YAML configuration
- ✅ **Memory-Managed**: Automatic GPU memory cleanup between models
- ✅ **Self-Contained**: All data files included

## Files Created

### Core Workflow Files
- `Snakefile`: Main Snakemake workflow definition
- `scripts/train_mpos_models.py`: Main training script (extracted from notebook)
- `config/training_config.yaml`: Configuration file with all model parameters

### Data Files
- `data/NGS-NZ-3454.txt`: Read count data for run 3454
- `data/NGS-NZ-3477.txt`: Read count data for run 3477
- `data/ORI_A_library_*.csv`: ORI A library sequences
- `data/ORI_C_library_*.csv`: ORI C library sequences

### Documentation
- `README.md`: Comprehensive documentation
- `QUICKSTART.md`: Quick start guide
- `PACKAGE_INFO.md`: This file

### Helper Scripts
- `run_workflow.sh`: Simple wrapper for local execution
- `submit_slurm.sh`: SLURM cluster submission script
- `requirements.txt`: Python dependencies

### Other
- `.gitignore`: Git ignore patterns for output files

## Differences from Original Notebook

1. **Automated Execution**: No manual cell execution needed
2. **Batch Processing**: All models trained in one run
3. **Error Handling**: Better error handling and logging
4. **Memory Management**: Improved GPU memory cleanup
5. **Non-Interactive**: Uses non-interactive matplotlib backend
6. **Configurable**: Easy to modify without editing code

## Migration Notes

If you were using the original notebook:

1. **Configuration**: Model parameters are now in `config/training_config.yaml`
2. **Output**: All outputs go to `output/` directory
3. **Execution**: Run `./run_workflow.sh` or `snakemake -j 1` instead of running notebook cells
4. **Plots**: All plots are saved automatically (no `plt.show()`)

## Dependencies

The workflow requires:
- Python 3.7+
- Snakemake
- MAVE-NN package (at `../mavenn` or configured path)
- All packages listed in `requirements.txt`

## Usage Summary

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
./run_workflow.sh

# Or with Snakemake
snakemake -j 1

# On cluster (SLURM example)
sbatch submit_slurm.sh
```

## Output Structure

```
output/
├── {run_name}_read_counts.png
├── {run_name}_{library}_counts.png
├── {run_name}_{library}_match_rates.png
├── {run_name}_{library}_zipf_plots.png
├── {run_name}_{sample_set}.pickle
├── {run_name}_{sample_set}.weights.h5
├── {run_name}_{sample_set}_logo.png
├── {run_name}_{sample_set}_training_history.png
├── {run_name}_{sample_set}_measurement_process.png
└── {run_name}_{sample_set}_zipf_plots.png
```

## Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Check `QUICKSTART.md` for common issues
3. Review logs in `output/training.log`

