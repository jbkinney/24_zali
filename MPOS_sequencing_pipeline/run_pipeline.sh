#!/bin/bash
# Automated pipeline script for processing sequencing data
# This script provides an alternative to Snakemake for users who prefer shell scripts
# Handles multiple sequencing runs as specified in config.yaml

set -e  # Exit on error

# Load configuration
if [ ! -f "config.yaml" ]; then
    echo "Error: config.yaml not found. Please create it first."
    exit 1
fi

echo "Starting pipeline for all sequencing runs specified in config.yaml"

# Use Python to parse config and process each run
python3 << 'PYTHON_SCRIPT'
import json
import os
import subprocess
import sys
import yaml

# Try to import yaml, provide helpful error if not available
try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

sequencing_runs = config['sequencing_runs']

for run in sequencing_runs:
    run_name = run['name']
    fastq_r1 = run['fastq_r1']
    fastq_r2 = run['fastq_r2']
    barcode_config_file = run['barcode_config']
    
    print(f"\n{'='*60}")
    print(f"Processing sequencing run: {run_name}")
    print(f"{'='*60}")
    
    # Check if required files exist
    if not os.path.exists(fastq_r1):
        print(f"Error: FASTQ R1 file not found: {fastq_r1}", file=sys.stderr)
        continue
    
    if not os.path.exists(fastq_r2):
        print(f"Error: FASTQ R2 file not found: {fastq_r2}", file=sys.stderr)
        continue
    
    if not os.path.exists(barcode_config_file):
        print(f"Error: Barcode config file not found: {barcode_config_file}", file=sys.stderr)
        continue
    
    # Step 1: Extract sequences from FASTQ files
    print(f"Step 1: Extracting sequences from FASTQ files...")
    os.makedirs('sequences', exist_ok=True)
    subprocess.run(['awk', 'NR % 4 == 2', fastq_r1], stdout=open(f'sequences/{run_name}_R1.txt', 'w'), check=True)
    subprocess.run(['awk', 'NR % 4 == 2', fastq_r2], stdout=open(f'sequences/{run_name}_R2.txt', 'w'), check=True)
    print(f"  ✓ Sequences extracted")
    
    # Step 2: Match barcodes and extract sequences
    print(f"Step 2: Matching barcodes and extracting sequences...")
    os.makedirs('seqs_by_sample', exist_ok=True)
    
    with open(barcode_config_file, 'r') as f:
        barcode_config = json.load(f)
    
    for sample, config_data in barcode_config.items():
        barcodes = config_data['barcodes']
        skip_length = config_data['skip_length']
        extract_length = config_data['extract_length']
        
        # Build grep pattern
        barcode_pattern = '|'.join(barcodes)
        
        # Extract sequences matching barcodes
        seq_file = f'sequences/{run_name}_R1.txt'
        output_file = f'seqs_by_sample/{run_name}_{sample}.txt'
        
        cmd = f"grep -E '^({barcode_pattern})' {seq_file} | sed -E 's/^({barcode_pattern}).{{{skip_length}}}(.{{{extract_length}}}).*/\\2/' > {output_file}"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: No matches found for sample {sample}", file=sys.stderr)
        else:
            print(f"  ✓ Processed {sample}")
    
    # Step 3: Count sequences for each sample
    print(f"Step 3: Counting sequences per sample...")
    os.makedirs('Counts_seqs_by_sample', exist_ok=True)
    
    for sample in barcode_config.keys():
        sample_file = f'seqs_by_sample/{run_name}_{sample}.txt'
        if os.path.exists(sample_file):
            count_file = f'Counts_seqs_by_sample/Counts_{run_name}_{sample}.txt'
            cmd = f"awk '{{ count[$0]++ }} END {{ for (line in count) print count[line], line }}' {sample_file} | sort -nr > {count_file}"
            subprocess.run(cmd, shell=True, check=True)
            print(f"  ✓ Counted {sample}")
    
    # Step 4: Merge count files
    print(f"Step 4: Merging count files...")
    os.makedirs('results', exist_ok=True)
    
    # Get list of count files
    count_files = [f'Counts_seqs_by_sample/Counts_{run_name}_{sample}.txt' for sample in barcode_config.keys()]
    count_files = [f for f in count_files if os.path.exists(f)]
    
    if not count_files:
        print(f"Error: No count files found for {run_name}", file=sys.stderr)
        continue
    
    # Start with first file
    first_file = count_files[0]
    subprocess.run(['sort', '-k2', first_file], stdout=open('results/temp_sorted.txt', 'w'), check=True)
    
    # Merge remaining files
    for count_file in count_files[1:]:
        subprocess.run(['sort', '-k2', count_file], stdout=open('results/temp_current.txt', 'w'), check=True)
        subprocess.run(['join', '-a1', '-a2', '-e', '0', '-o', 'auto', '-1', '1', '-2', '2', 
                       'results/temp_sorted.txt', 'results/temp_current.txt'], 
                      stdout=open('results/temp_merged.txt', 'w'), check=True)
        os.rename('results/temp_merged.txt', 'results/temp_sorted.txt')
    
    # Rename final file
    final_file = f'results/{run_name}.txt'
    os.rename('results/temp_sorted.txt', final_file)
    if os.path.exists('results/temp_current.txt'):
        os.remove('results/temp_current.txt')
    
    print(f"  ✓ Merged count table: {final_file}")

print("\n" + "="*60)
print("Pipeline complete!")
print("="*60)
PYTHON_SCRIPT

