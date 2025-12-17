#!/usr/bin/env python3
"""
Train a single model configuration by index.

This script trains one model from the config file to avoid memory accumulation.
"""

import sys
import os
import yaml
import argparse
import gc

# Parse arguments early to check for --use-cpu flag before importing TensorFlow
# This is important because CUDA_VISIBLE_DEVICES must be set before TensorFlow is imported
parser = argparse.ArgumentParser(description='Train a single model by config index')
parser.add_argument('--config', type=str, required=True)
parser.add_argument('--model-index', type=int, required=True)
parser.add_argument('--sample-set-index', type=int, required=True)
parser.add_argument('--output-dir', type=str, default='output')
parser.add_argument('--use-cpu', action='store_true', 
                   help='Force CPU usage instead of GPU (useful if GPU memory is corrupted)')
args, unknown = parser.parse_known_args()

# Force CPU if requested - MUST be done before importing TensorFlow
if args.use_cpu:
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    # Also disable GPU in TensorFlow config
    os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'false'
    print("Forcing CPU usage (GPU disabled)")

# Add parent directory to path to import main training functions
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import the main training script's functions
# Note: train_mpos_models will import TensorFlow, so CUDA_VISIBLE_DEVICES must be set above
from train_mpos_models import analyze_MPOS, clear_tf_memory

def main():

    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    if args.model_index >= len(config['models']):
        print(f"Error: Model index {args.model_index} out of range")
        sys.exit(1)

    model_config = config['models'][args.model_index]
    fit_samples = model_config.get('fit_samples', [])
    
    if not fit_samples:
        print(f"Error: Model {args.model_index} has no fit_samples defined")
        sys.exit(1)
    
    if args.sample_set_index < 0 or args.sample_set_index >= len(fit_samples):
        print(f"Error: Sample set index {args.sample_set_index} out of range (0-{len(fit_samples)-1})")
        print(f"Available sample sets: {fit_samples}")
        sys.exit(1)

    # Get the specific sample set to train
    sample_set = fit_samples[args.sample_set_index]
    
    # Create a modified config with just this one sample set
    single_model_config = model_config.copy()
    single_model_config['fit_samples'] = [sample_set]
    
    # Clear memory before starting - do this aggressively
    import tensorflow as tf
    try:
        # Reset TensorFlow state completely
        tf.keras.backend.clear_session()
        # Clear any GPU memory
        if tf.config.list_physical_devices('GPU'):
            for gpu in tf.config.list_physical_devices('GPU'):
                try:
                    tf.config.experimental.reset_memory_stats(gpu)
                except:
                    pass
    except:
        pass
    
    # Force garbage collection
    gc.collect()
    clear_tf_memory()
    
    # Train the model with error handling
    try:
        models = analyze_MPOS(
            readcount_file=model_config['readcount_file'],
            library_seqs_file=model_config['library_seqs_file'],
            all_samples=model_config['all_samples'],
            adapter_lengths=tuple(model_config['adapter_lengths']),
            zipf_figure_shape=tuple(model_config['zipf_figure_shape']),
            fit_samples=[sample_set],
            fit_model=True,
            output_dir=args.output_dir
        )
    except Exception as e:
        error_msg = str(e)
        # Check if it's a GPU memory error
        if 'GPU' in error_msg or 'device:GPU' in error_msg or 'InternalError' in error_msg or 'Failed copying input tensor' in error_msg:
            print(f"\n{'='*60}")
            print("ERROR: GPU memory issue detected")
            print(f"{'='*60}")
            print(f"Error details: {error_msg}")
            print("\nThis error typically occurs when GPU memory is corrupted from a previous failed run.")
            print("\nSOLUTION: Retry with CPU mode using the --use-cpu flag:")
            print(f"  bash scripts/train_single_model.sh {args.model_index} {args.sample_set_index} --use-cpu")
            print(f"  or")
            print(f"  python scripts/train_model_by_index.py --config {args.config} \\")
            print(f"      --model-index {args.model_index} --sample-set-index {args.sample_set_index} \\")
            print(f"      --output-dir {args.output_dir} --use-cpu")
            print(f"\n{'='*60}")
            raise
        else:
            # Re-raise if it's not a GPU error
            raise

    # Plot if requested
    if models and 'sign_flips' in model_config:
        sign_flips_list = model_config['sign_flips']
        # Safely get sign_flip, default to False if index out of range
        if args.sample_set_index < len(sign_flips_list):
            sign_flip = sign_flips_list[args.sample_set_index]
        else:
            print(f"Warning: sign_flips list shorter than sample sets, using False")
            sign_flip = False
        
        from train_mpos_models import plot_models
        try:
            plot_models(
                models,
                sign_flips=[sign_flip],
                reverse_complement=model_config.get('reverse_complement', False),
                output_dir=args.output_dir
            )
        except Exception as e:
            print(f"Warning: Could not plot model: {e}")

    # Clear memory aggressively
    if models:
        # Delete each model individually
        for model_name in list(models.keys()):
            del models[model_name]
        del models
    clear_tf_memory()
    
    # Force Python to release memory (gc is already imported at top of file)
    for _ in range(3):
        gc.collect()

    print("Model training completed successfully!")
    print(f"Memory cleared. Process ID: {os.getpid()}")


if __name__ == '__main__':
    # args was already parsed at module level
    main()

