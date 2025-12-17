# GitHub Repository Setup

This document explains how to prepare this repository for GitHub upload.

## Files Excluded from Git

The following files and directories are excluded via `.gitignore`:

### Data Files
- `data/*.txt` - Read count files
- `data/*.csv` - Library sequence files
- `data/*.tsv` - Tab-separated data files

**Note**: The `data/` directory structure is preserved with a `.gitkeep` file.

### Output Files
- `output/` - All training outputs (models, plots, logs)
- `outputbash/` - Alternative output directory
- `*.pickle` - Model pickle files
- `*.h5` - Model weight files
- `*.png` - Plot images
- `*.log` - Log files

### Other Excluded Files
- Python cache files (`__pycache__/`, `*.pyc`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Virtual environments (`venv/`, `env/`)

## What IS Included

The repository includes:
- All Python scripts in `scripts/`
- Configuration files in `config/`
- Documentation (README.md, QUICKSTART.md, etc.)
- Workflow files (Snakefile, shell scripts)
- Requirements file (`requirements.txt`)
- Directory structure (via `.gitkeep` files)

## For Users Cloning the Repository

Users will need to:

1. **Clone the repository**
2. **Add their data files** to the `data/` directory:
   - `NGS-NZ-3454.txt`
   - `NGS-NZ-3477.txt`
   - `ORI_A_library_2024-06-13_13_22_23.012484.csv`
   - `ORI_C_library_2024-06-13_13_22_23.186347.csv`
3. **Update `config/training_config.yaml`** if their files have different names/paths
4. **Install dependencies**: `pip install -r requirements.txt`
5. **Ensure MAVE-NN is available** at `../mavenn` or update the path

See `README.md` and `data/README.md` for more details.

## Repository Size

Without data files, the repository should be small enough for GitHub (typically < 1 MB).

