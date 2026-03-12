# MPOS Sequencing Pipeline

Snakemake workflow that processes paired-end FASTQ files into per-sequence count tables for MPOS analysis. Demultiplexes reads by sample-specific barcodes, extracts 90 bp target sequences, and counts unique sequences per sample. Counts represent whole fragment/molecule counts (one R1 read = one fragment).

## Prerequisites

- Python 3.6+
- [Snakemake](https://snakemake.readthedocs.io/) (or PyYAML for the shell script alternative)
- Standard Unix tools: `awk`, `grep`, `sed`, `sort`, `join`

```bash
pip install -r requirements.txt
```

## Input

- Paired-end FASTQ files (R1 and R2) for each sequencing run
- Barcode configuration JSON files specifying per-sample barcodes and extraction parameters

## Configuration

**`config.yaml`** — lists sequencing runs with paths to FASTQ files and barcode configs:

```yaml
sequencing_runs:
  - name: "NGS-NZ-3454"
    fastq_r1: "path/to/NGS-NZ-3454_S1_R1_001.fastq"
    fastq_r2: "path/to/NGS-NZ-3454_S1_R2_001.fastq"
    barcode_config: "barcode_config_3454.json"
```

**`barcode_config_*.json`** — per-sample barcode sequences and extraction parameters:

```json
{
  "A1-Out": {
    "barcodes": ["ATACAACAGC", "CGACTAGGT"],
    "skip_length": 24,
    "extract_length": 90
  }
}
```

## Running

```bash
# Snakemake (recommended)
snakemake --cores 1

# Shell script alternative
./run_pipeline.sh
```

## Pipeline Steps

1. **Extract sequences** — pull sequence lines from R1/R2 FASTQs
2. **Match barcodes** — select reads by barcode prefix, skip adapter bases, extract 90 bp target
3. **Count sequences** — count unique sequences per sample
4. **Merge counts** — combine sample counts into one table per run

## Output

Final count tables are written to `results/<run_name>.txt`:

```
<sequence>  <count_sample1>  <count_sample2>  ...
```

Intermediate files are stored in `sequences/`, `seqs_by_sample/`, and `Counts_seqs_by_sample/`.

## Notes

- Barcode matching is case-sensitive and requires exact matches at the start of R1 reads.
- R2 reads are extracted but not used in barcode matching.
- Missing sequences in a sample are represented as 0 in the merged table.
