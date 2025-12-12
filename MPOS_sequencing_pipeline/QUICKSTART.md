# Quick Start Guide

## Prerequisites

- Python 3.6+ (for shell script workflow)
- Snakemake (optional, for automated workflow)
- Standard Unix tools: `awk`, `grep`, `sed`, `sort`, `join`
- PyYAML (for shell script workflow): `pip install pyyaml`

## Installation

### For Snakemake workflow:
```bash
pip install snakemake
# or
conda install -c bioconda snakemake
```

### For shell script workflow:
```bash
pip install pyyaml
```

## Quick Start (5 minutes)

### 1. Configure your runs

Edit `config.yaml` to specify your sequencing runs:
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

### 2. Configure barcodes

Edit the appropriate `barcode_config_*.json` file to match your samples. Example:
```json
{
  "Sample1": {
    "barcodes": ["ATACAACAGC", "CGACTAGGT"],
    "skip_length": 24,
    "extract_length": 90
  },
  "Sample2": {
    "barcodes": ["ACATATCGAC"],
    "skip_length": 24,
    "extract_length": 90
  }
}
```

### 3. Run the pipeline

**Option A: Snakemake (recommended)**
```bash
snakemake --cores 1
```

**Option B: Shell script**
```bash
./run_pipeline.sh
```

### 4. Find your results

The final count tables will be at:
```
results/<sequencing_run>.txt
```

One file per sequencing run specified in `config.yaml`.

## Understanding the Output

The output files are tab-separated tables:
```
<sequence1>    <count_sample1>    <count_sample2>    ...
<sequence2>    <count_sample1>    <count_sample2>    ...
```

Where:
- First column: Unique sequence (90bp target sequence)
- Subsequent columns: Fragment count for each sample

**Important**: Each count represents one DNA fragment/molecule. The counts are fragment-level counts, not read-level counts.

## Troubleshooting

**"No sequences matched for sample X"**
- Check barcode sequences in the appropriate `barcode_config_*.json` file
- Verify sequences in FASTQ actually start with these barcodes

**"File not found" errors**
- Check paths in `config.yaml` are correct
- Ensure FASTQ files exist at specified paths

**Memory issues**
- Process runs separately by editing `config.yaml` to include only one run
- Use Snakemake with resource limits: `snakemake --resources mem_mb=10000`

**"No module named 'yaml'"**
- Install PyYAML: `pip install pyyaml`

## Next Steps

See `README.md` for detailed documentation.

