# Workflow Summary

This directory contains a complete, automated workflow for processing sequencing data from FASTQ files to count tables.

## Key Features

1. **Fragment-level counts**: The pipeline counts whole fragments/molecules. Each R1 read represents one DNA fragment, so the output counts represent the number of unique fragments matching each library sequence in each condition.

2. **Multiple sequencing runs**: The workflow can process multiple sequencing runs (e.g., NGS-NZ-3454 and NGS-NZ-3477) in a single execution.

3. **Fully automated**: No manual file moving or renaming required - all steps are automated.

4. **Reproducible**: Configuration files ensure reproducible results across runs.

## Files in This Directory

- **`Snakefile`**: Snakemake workflow (recommended for automated execution)
- **`run_pipeline.sh`**: Shell script alternative (doesn't require Snakemake)
- **`config.yaml`**: Main configuration file specifying sequencing runs and file paths
- **`barcode_config_3454.json`**: Barcode configuration for NGS-NZ-3454
- **`barcode_config_3477.json`**: Barcode configuration for NGS-NZ-3477
- **`README.md`**: Comprehensive documentation
- **`QUICKSTART.md`**: Quick start guide
- **`requirements.txt`**: Python dependencies
- **`.gitignore`**: Git ignore rules for intermediate files

## Quick Start

1. Edit `config.yaml` with your FASTQ file paths
2. Edit barcode config JSON files if needed
3. Run: `snakemake --cores 1` or `./run_pipeline.sh`
4. Find results in `results/<sequencing_run>.txt`

## Addressing Your Questions

### 1. Fragment Counts
**Yes, the counts represent whole fragment counts.** Each R1 read corresponds to one DNA fragment/molecule. The pipeline extracts sequences from R1 reads, matches barcodes, and counts unique sequences. Therefore, each count in the final table represents one fragment matching that library sequence in that condition.

### 2. Multiple Sequencing Runs
**Both NGS-NZ-3454 and NGS-NZ-3477 are now supported.** The workflow processes both runs in parallel:
- Separate barcode configs: `barcode_config_3454.json` and `barcode_config_3477.json`
- Both runs specified in `config.yaml`
- Output files: `results/NGS-NZ-3454.txt` and `results/NGS-NZ-3477.txt`

### 3. Subdirectory Organization
**All workflow files are in the `sequencing_pipeline/` subdirectory** for easy GitHub upload. This directory is self-contained and ready to share.

## Original Scripts

The original cluster scripts (`get_seqs*.sh`, `match_illumina_BCs*.sh`, etc.) remain in the parent directory for reference but are superseded by this automated workflow.

