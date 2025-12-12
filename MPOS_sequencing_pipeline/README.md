# Sequencing Data Processing Pipeline

This directory contains scripts and workflows for processing raw sequencing data from FASTQ files into count tables suitable for downstream analysis.

## Important Note on Count Interpretation

**The counts represent whole fragment/molecule counts.** Each R1 read corresponds to one DNA fragment/molecule. Therefore, the final counts in the output tables represent the number of unique fragments matching each library sequence in each condition. This is the appropriate metric for analyzing fragment-level enrichment or depletion across conditions.

## Overview

The pipeline processes paired-end sequencing data (R1 and R2 FASTQ files) through the following steps:

1. **Extract sequences**: Extract sequence lines from FASTQ files
2. **Match barcodes**: Identify sequences matching sample-specific barcodes and extract target sequences
3. **Count sequences**: Count occurrences of each unique sequence within each sample
4. **Merge counts**: Combine all sample count files into a single count table

The workflow can process multiple sequencing runs in parallel (e.g., NGS-NZ-3454 and NGS-NZ-3477).

## Workflow Steps

### Step 1: Extract Sequences
Extracts sequence lines (every 4th line starting at line 2) from FASTQ files. In FASTQ format:
- Line 1: Sequence identifier (starts with `@`)
- Line 2: Sequence
- Line 3: `+` (separator)
- Line 4: Quality scores

This step extracts only the sequence lines (line 2 of each read).

### Step 2: Match Barcodes
For each sample, identifies sequences that start with specific barcode sequences. After matching:
- Skips a fixed number of bases after the barcode (typically 19 or 24 bases)
- Extracts the next 90 bases as the target sequence
- Saves sequences for each sample to separate files

### Step 3: Count Sequences
Counts the number of occurrences of each unique sequence within each sample file. Outputs files with format:
```
<count> <sequence>
```
sorted by count in descending order.

**Note**: Each count represents one DNA fragment/molecule.

### Step 4: Merge Count Files
Merges all sample count files into a single table where:
- First column: Sequence
- Subsequent columns: Count for each sample (0 if sequence not found in that sample)

## Usage

### Option 1: Snakemake Workflow (Recommended)

The Snakemake workflow automates all steps and handles dependencies automatically.

#### Prerequisites
- [Snakemake](https://snakemake.readthedocs.io/) installed
- Python 3.6+
- Standard Unix tools (awk, grep, sed, sort, join)

#### Setup

1. **Configure the workflow**: Edit `config.yaml` to specify your sequencing runs:
   ```yaml
   sequencing_runs:
     - name: "NGS-NZ-3454"
       fastq_r1: "path/to/NGS-NZ-3454_S1_R1_001.fastq"
       fastq_r2: "path/to/NGS-NZ-3454_S1_R2_001.fastq"
       barcode_config: "barcode_config_3454.json"
     
     - name: "NGS-NZ-3477"
       fastq_r1: "path/to/NGS-NZ-3477_S1_R1_001.fastq"
       fastq_r2: "path/to/NGS-NZ-3477_S1_R2_001.fastq"
       barcode_config: "barcode_config_3477.json"
   ```

2. **Configure barcodes**: Edit the appropriate `barcode_config_*.json` file to specify:
   - Sample names
   - Barcode sequences (can be multiple per sample)
   - Skip length (bases to skip after barcode)
   - Extract length (bases to extract)

   Example:
   ```json
   {
     "A1-Out": {
       "barcodes": ["ATACAACAGC", "CGACTAGGT"],
       "skip_length": 24,
       "extract_length": 90
     }
   }
   ```

#### Run

```bash
snakemake --cores 1
```

For cluster execution:
```bash
snakemake --cluster "qsub -l m_mem_free=5G" --jobs 10
```

The final outputs will be in `results/<sequencing_run>.txt` for each run.

### Option 2: Shell Script Workflow

For users who prefer not to use Snakemake, a shell script alternative is provided.

#### Prerequisites
- Python 3.6+ (for JSON and YAML parsing)
- PyYAML: `pip install pyyaml`
- Standard Unix tools (awk, grep, sed, sort, join)

#### Setup

Same as Snakemake workflow - configure `config.yaml` and barcode config JSON files.

#### Run

```bash
./run_pipeline.sh
```

The final outputs will be in `results/<sequencing_run>.txt` for each run.

## Output Format

The final count tables (`results/<sequencing_run>.txt`) have the following format:

```
<sequence1> <count_sample1> <count_sample2> ... <count_sampleN>
<sequence2> <count_sample1> <count_sample2> ... <count_sampleN>
...
```

Where:
- First column: Unique sequence (90bp target sequence)
- Subsequent columns: Read count for each sample (0 if sequence not found)
- **Each count represents one DNA fragment/molecule**

## Directory Structure

After running the pipeline, the following directories will be created:

```
.
├── sequences/              # Extracted sequences from FASTQ files
├── seqs_by_sample/         # Sequences matched to each sample (prefixed with run name)
├── Counts_seqs_by_sample/  # Count files for each sample (prefixed with run name)
└── results/                # Final merged count tables (one per sequencing run)
```

## Configuration Files

### `config.yaml`
Main configuration file specifying:
- List of sequencing runs to process
- For each run: name, FASTQ file paths, and barcode configuration file

### `barcode_config_*.json`
JSON files specifying for each sample:
- `barcodes`: Array of barcode sequences (sequences starting with any of these will match)
- `skip_length`: Number of bases to skip after the barcode
- `extract_length`: Number of bases to extract as the target sequence

## Notes

- The pipeline processes R1 reads for barcode matching. R2 reads are extracted but not currently used in the barcode matching step.
- Barcode matching is case-sensitive and requires exact matches at the start of the sequence.
- The merge step uses `join` which requires sorted input files. Sequences are sorted alphabetically for merging.
- Missing sequences in a sample are represented as 0 in the final count table.
- **Counts represent fragment/molecule counts, not read counts** - each R1 read corresponds to one fragment.

## Troubleshooting

### No sequences matched for a sample
- Verify barcode sequences in the barcode config JSON file are correct
- Check that sequences in your FASTQ files actually start with these barcodes
- Ensure skip_length and extract_length are appropriate for your sequencing design

### Memory issues during counting
- For very large files, consider processing runs separately
- The Snakemake workflow can be run with resource limits: `snakemake --resources mem_mb=10000`

### Join command fails
- Ensure all count files are properly sorted before merging
- Check that count files have the correct format (count in first column, sequence in second)

## Original Scripts

The original cluster scripts are preserved in the parent directory for reference:
- `get_seqs*.sh`: Extract sequences from FASTQ
- `match_illumina_BCs*.sh`: Match barcodes (hardcoded for specific runs)
- `count_seqs*.sh`: Count sequences (uses qsub for cluster)
- `merge_count_files*.sh`: Merge count files (hardcoded sample list)

These scripts are now superseded by the automated workflows but are kept for compatibility and reference.

