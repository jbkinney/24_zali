#!/usr/bin/env python3
"""
Train a single MAVE-NN model for MPOS data.

This script trains one model configuration to avoid memory accumulation.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import random
import scipy.stats
import logomaker
from scipy.signal import correlate
import pickle
import gc
import sys
import os
import argparse
import yaml

# Insert local path to MAVE-NN at beginning of Python's path
script_dir = os.path.dirname(os.path.abspath(__file__))
workflow_dir = os.path.dirname(script_dir)
possible_mavenn_paths = [
    os.path.join(workflow_dir, '..', 'mavenn'),  # ../mavenn from workflow
    os.path.join(workflow_dir, 'mavenn'),         # ./mavenn in workflow
    'mavenn',                                      # Current directory
]

mavenn_found = False
for mavenn_path in possible_mavenn_paths:
    abs_path = os.path.abspath(mavenn_path)
    if os.path.exists(abs_path) and os.path.isdir(abs_path):
        sys.path.insert(0, abs_path)
        mavenn_found = True
        print(f"Found mavenn at: {abs_path}")
        break

if not mavenn_found:
    print("Warning: mavenn directory not found. Trying default path...")
    sys.path.insert(0, os.path.join(workflow_dir, '..', 'mavenn'))

# Import MAVE-NN
import mavenn
import tensorflow as tf

# Configure GPU memory growth to prevent memory issues
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"GPU memory growth enabled for {len(gpus)} GPU(s)")
    except RuntimeError as e:
        print(f"Could not set GPU memory growth: {e}")
else:
    print("No GPU devices found, using CPU")


def clear_tf_memory():
    """Clear TensorFlow/Keras memory to prevent GPU memory issues"""
    import tensorflow.keras.backend as K
    K.clear_session()
    gc.collect()


# Import the analyze_MPOS function from the main script
# We'll define a simplified version here
def analyze_MPOS_single_model(readcount_file, library_seqs_file, all_samples, 
                               adapter_lengths, zipf_figure_shape, sample_set,
                               fit_model=True, output_dir="."):
    """
    Analyze MPOS data and train a single model.
    """
    # Load counts table
    read_counts = pd.read_table(readcount_file, sep=" ", header=None)
    columns_dict = {0: "var_seq"}
    for i, sample in enumerate(all_samples):
        columns_dict[i + 1] = sample
    read_counts = read_counts.rename(columns_dict, axis=1)

    # Extract names
    run_name = os.path.basename(readcount_file).split(".")[0]
    library_name = os.path.basename(library_seqs_file).split(".")[0]
    sample_set_name = run_name + "_" + "_".join(sample_set)

    # Load library sequences
    library = pd.read_csv(library_seqs_file)
    if 'Unnamed: 0' in library.columns:
        library.drop('Unnamed: 0', axis=1, inplace=True)
    library["var_seq"] = [seq[adapter_lengths[0]:(len(seq) - adapter_lengths[1])] 
                          for seq in library["var_seq"]]
    library = library.merge(read_counts, on="var_seq")
    library = library[library[all_samples].sum(axis=1) > 0]

    if fit_model:
        # Get sequences with reads in target samples
        nonzero_library = library[library[sample_set].sum(axis=1) > 0]
        min_read_threshold = 10
        nonzero_library = nonzero_library[nonzero_library[sample_set].min(axis=1) > min_read_threshold]
        nonzero_library["set"] = random.choices(
            ["training", "validation", "test"], 
            weights=[0.5, 0.2, 0.3],
            k=len(nonzero_library)
        )

        L = len(nonzero_library.loc[nonzero_library.index[0], 'var_seq'])
        print(f'Sequence length: {L:d} DNA nucleotides')

        trainval_df, test_df = mavenn.split_dataset(nonzero_library)

        model = mavenn.Model(
            L=L,
            alphabet='dna',
            gpmap_type='additive',
            regression_type='MPA',
            theta_regularization=0.1,
            eta_regularization=0.001,
            Y=len(sample_set)
        )

        model.set_data(
            x=trainval_df['var_seq'],
            y=trainval_df[sample_set],
            validation_flags=trainval_df['validation']
        )

        print(f"Training on {len(nonzero_library)} sequences")
        model.fit(
            learning_rate=1e-3,
            epochs=500,
            batch_size=1,
            early_stopping=True,
            early_stopping_patience=2,
            verbose=True
        )

        # Save model
        model_path = os.path.join(output_dir, sample_set_name)
        model.save(model_path)
        print(f"Model saved to {model_path}")
        
        clear_tf_memory()
        return model
    
    return None


def main():
    parser = argparse.ArgumentParser(description='Train a single MAVE-NN model')
    parser.add_argument('--readcount-file', type=str, required=True)
    parser.add_argument('--library-seqs-file', type=str, required=True)
    parser.add_argument('--all-samples', type=str, nargs='+', required=True)
    parser.add_argument('--adapter-lengths', type=int, nargs=2, required=True)
    parser.add_argument('--sample-set', type=str, nargs='+', required=True)
    parser.add_argument('--output-dir', type=str, default='output')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    clear_tf_memory()

    model = analyze_MPOS_single_model(
        readcount_file=args.readcount_file,
        library_seqs_file=args.library_seqs_file,
        all_samples=args.all_samples,
        adapter_lengths=tuple(args.adapter_lengths),
        zipf_figure_shape=(1, 1),  # Not used for single model
        sample_set=args.sample_set,
        fit_model=True,
        output_dir=args.output_dir
    )

    if model:
        del model
        clear_tf_memory()

    print("Model training completed successfully!")


if __name__ == '__main__':
    main()

