#!/bin/bash
# Simple wrapper script to run the MPOS model training workflow

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Default values
JOBS=1
DRY_RUN=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -j|--jobs)
            JOBS="$2"
            shift 2
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -j, --jobs N       Number of parallel jobs (default: 1)"
            echo "  -n, --dry-run      Dry run (show what would be done)"
            echo "  -v, --verbose      Verbose output"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Check if Snakemake is installed
if ! command -v snakemake &> /dev/null; then
    echo "Error: Snakemake is not installed."
    echo "Install it with: pip install snakemake"
    exit 1
fi

# Build Snakemake command
SNAKEMAKE_CMD="snakemake -j $JOBS"

if [ "$DRY_RUN" = true ]; then
    SNAKEMAKE_CMD="$SNAKEMAKE_CMD -n"
fi

if [ "$VERBOSE" = true ]; then
    SNAKEMAKE_CMD="$SNAKEMAKE_CMD -v"
fi

# Create output directory if it doesn't exist
mkdir -p output

# Run Snakemake
echo "Running MPOS model training workflow..."
echo "Command: $SNAKEMAKE_CMD"
echo ""

$SNAKEMAKE_CMD

echo ""
echo "Workflow completed successfully!"

