# Data Files Directory

This directory should contain your input data files for model training.

## Required Files

The following files are required for the default configuration:

### Read Count Files
- `NGS-NZ-3454.txt` - Read counts for experiment 3454
- `NGS-NZ-3477.txt` - Read counts for experiment 3477

### Library Sequence Files
- `ORI_A_library_2024-06-13_13_22_23.012484.csv` - ORI A library sequences
- `ORI_C_library_2024-06-13_13_22_23.186347.csv` - ORI C library sequences

## File Format

- **Read count files** (`.txt`): Tab-separated files with columns for sequence identifiers and read counts per sample
- **Library sequence files** (`.csv`): CSV files containing sequence information for the library

## Custom Data Files

If your data files have different names or locations, update the `readcount_file` and `library_seqs_file` paths in `config/training_config.yaml`.

## Note

Data files are not included in the GitHub repository due to their size. You must provide your own data files.

