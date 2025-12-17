#!/bin/bash
# Quick fix script for pulp version incompatibility

echo "Fixing pulp version incompatibility..."
echo ""

# Check if pulp is installed
if python -c "import pulp" 2>/dev/null; then
    CURRENT_VERSION=$(python -c "import pulp; print(pulp.__version__)" 2>/dev/null)
    echo "Current pulp version: $CURRENT_VERSION"
    
    # Downgrade to compatible version
    echo "Downgrading pulp to version 2.7..."
    pip install --upgrade "pulp==2.7"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Successfully fixed pulp version!"
        echo "You can now run the workflow with: ./run_workflow.sh"
    else
        echo ""
        echo "✗ Failed to install pulp 2.7"
        echo "Try running: pip install --upgrade 'pulp==2.7'"
    fi
else
    echo "pulp is not installed. Installing compatible version..."
    pip install "pulp==2.7"
fi

