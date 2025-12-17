#!/bin/bash
#SBATCH --job-name=mpos_training
#SBATCH --output=logs/slurm_%j.out
#SBATCH --error=logs/slurm_%j.err
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1  # Remove this line if no GPU available

# Print job information
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "Node: $SLURM_NODELIST"
echo "Start Time: $(date)"

# Change to the directory where the script was submitted
cd $SLURM_SUBMIT_DIR

# Load required modules (adjust for your cluster)
# module load python/3.9
# module load cuda/11.0  # If using GPU

# Activate conda environment if using one
# conda activate mpos_env

# Create logs directory if it doesn't exist
mkdir -p logs

# Create output directory if it doesn't exist
mkdir -p output

# Run Snakemake
# Use -j 1 for sequential execution to avoid GPU memory conflicts
snakemake -j 1 --use-conda 2>&1 | tee logs/snakemake_${SLURM_JOB_ID}.log

# Print completion time
echo "End Time: $(date)"
echo "Job completed"

