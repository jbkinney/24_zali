#!/usr/bin/env python3
"""
Train MAVE-NN models for MPOS data analysis.

This script trains models to classify reads into different samples based on sequence.
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
# Try multiple possible locations for mavenn
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

# Check if CPU mode is forced via environment variable
force_cpu = os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'

# Configure GPU memory growth to prevent memory issues
# Only configure GPU if not forcing CPU
if not force_cpu:
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            # Enable memory growth to prevent TensorFlow from allocating all GPU memory at once
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"GPU memory growth enabled for {len(gpus)} GPU(s)")
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            print(f"Could not set GPU memory growth: {e}")
    else:
        print("No GPU devices found, using CPU")
else:
    # Force CPU usage - explicitly disable GPU
    try:
        # Hide GPUs from TensorFlow
        tf.config.set_visible_devices([], 'GPU')
        print("CPU mode: GPU devices explicitly disabled")
    except Exception as e:
        print(f"Warning: Could not disable GPU: {e}")
        print("Continuing with CPU mode...")


def clear_tf_memory():
    """Clear TensorFlow/Keras memory to prevent GPU memory issues"""
    import tensorflow as tf
    import tensorflow.keras.backend as K
    try:
        K.clear_session()
        # Try to reset GPU memory if available
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.reset_memory_stats(gpu)
            except:
                pass
    except:
        pass
    gc.collect()
    # Force garbage collection multiple times to ensure memory is freed
    for _ in range(3):
        gc.collect()


def analyze_MPOS(readcount_file, library_seqs_file, all_samples, adapter_lengths, 
                 zipf_figure_shape, fit_samples=None, fit_model=False, sign_flip=False, 
                 read_count_cutoff=1000, output_dir="."):
    """
    Analyze MPOS data and optionally train models.
    
    Parameters:
    -----------
    readcount_file : str
        Path to read count file
    library_seqs_file : str
        Path to library sequences file
    all_samples : list
        List of all sample names
    adapter_lengths : tuple
        (front_adapter_length, back_adapter_length)
    zipf_figure_shape : tuple
        (rows, cols) for Zipf plot layout
    fit_samples : list of lists, optional
        List of sample sets to fit models for
    fit_model : bool
        Whether to fit models
    sign_flip : bool
        Whether to flip signs (not used in current implementation)
    read_count_cutoff : int
        Minimum read count to include sample
    output_dir : str
        Directory to save outputs
    """
    # Load counts table
    read_counts = pd.read_table(readcount_file, sep=" ", header=None)
    columns_dict = {0: "var_seq"}
    for i, sample in enumerate(all_samples):
        columns_dict[i + 1] = sample
    read_counts = read_counts.rename(columns_dict, axis=1)

    # Extract names of sequencing run and library
    run_name = os.path.basename(readcount_file).split(".")[0]
    library_name = os.path.basename(library_seqs_file).split(".")[0]

    # Plot total read counts
    total_read_counts = read_counts[all_samples].sum().to_dict()
    fig = plt.figure(figsize=(15, 5))
    for sample, read_count in total_read_counts.items():
        print(sample, read_count)
    plt.bar(total_read_counts.keys(), total_read_counts.values())
    plt.xlabel("Sample")
    plt.ylabel("Total reads")
    plt.title(run_name)
    plt.savefig(os.path.join(output_dir, f"{run_name}_read_counts.png"))
    plt.close()

    # Load list of library sequences and merge with counts
    library = pd.read_csv(library_seqs_file)
    if 'Unnamed: 0' in library.columns:
        library.drop('Unnamed: 0', axis=1, inplace=True)
    library["var_seq"] = [seq[adapter_lengths[0]:(len(seq) - adapter_lengths[1])] 
                          for seq in library["var_seq"]]
    library = library.merge(read_counts, on="var_seq")
    library = library[library[all_samples].sum(axis=1) > 0]

    # Plot matched read counts
    fig = plt.figure(figsize=(15, 5))
    for sample, read_count in zip(total_read_counts.keys(), library[all_samples].sum()):
        print(sample, read_count)
    plt.bar(total_read_counts.keys(), library[all_samples].sum())
    plt.xlabel("Sample")
    plt.ylabel("Total reads")
    plt.title(run_name + " " + library_name + " sequences")
    plt.savefig(os.path.join(output_dir, f"{run_name}_{library_name}_counts.png"))
    plt.close()

    # Plot fraction of read counts matching library members
    fig = plt.figure(figsize=(15, 5))
    plt.bar(total_read_counts.keys(), library[all_samples].sum()/read_counts[all_samples].sum())
    plt.xlabel("Sample")
    plt.ylabel("Fraction of reads matching library members")
    plt.title(run_name + " " + library_name + " sequences")
    plt.savefig(os.path.join(output_dir, f"{run_name}_{library_name}_match_rates.png"))
    plt.close()

    # Get samples with reads matching library members
    nonzero_samples = []
    for sample in all_samples:
        if sum(library[sample]) > read_count_cutoff:
            nonzero_samples.append(sample)
    
    # Make Zipf plots
    plt.rc('axes', labelsize=20)
    plt.rc('xtick', labelsize=16) 
    plt.rc('ytick', labelsize=16)
    fig, axs = plt.subplots(zipf_figure_shape[0], zipf_figure_shape[1], 
                           figsize=(8*zipf_figure_shape[1], 8*zipf_figure_shape[0]))
    if zipf_figure_shape[0] == 1 and zipf_figure_shape[1] == 1:
        axs = [axs]
    else:
        axs = axs.flatten()
    for i, sample in enumerate(nonzero_samples):
        axs[i].plot(np.linspace(1, len(library), len(library)), 
                   library[sample].sort_values(ascending=False))
        axs[i].set(xlabel="Rank", ylabel="Count in " + sample, xscale='log', yscale='log')
    plt.savefig(os.path.join(output_dir, f"{run_name}_{library_name}_zipf_plots.png"))
    plt.close()

    if not (fit_samples is None):
        model = {}
        for sample_set in fit_samples:
            sample_set_name = run_name + "_" + "_".join(sample_set)
            # Make overlayed Zipf plots of samples used for fitting
            fig, ax = plt.subplots(1, 1, figsize=[5, 5])
            for i, sample in enumerate(sample_set):
                y = library[sample].sort_values(ascending=False)
                y_normalizer = 1/y.sum()
                plt.plot(np.linspace(1, len(library), len(library)), y*y_normalizer, 
                        label=sample)
            plt.xlabel("Rank")
            plt.ylabel("Normalized abundance") 
            plt.xscale('log')
            plt.yscale('log')
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"{sample_set_name}_zipf_plots.png"))
            plt.close()
            
            if fit_model:
                # Get sequences with reads in target samples
                nonzero_library = library[library[sample_set].sum(axis=1) > 0]
                # Before splitting, add a stricter filter
                min_read_threshold = 10  # adjust as needed
                nonzero_library = nonzero_library[nonzero_library[sample_set].min(axis=1) > min_read_threshold]
                
                # Limit dataset size to prevent memory issues
                # Reduce this if you still get "Killed: 9" errors
                max_sequences = int(os.environ.get('MPOS_MAX_SEQUENCES', '30000'))  # Default 30k, can be overridden
                if len(nonzero_library) > max_sequences:
                    print(f"Warning: Dataset has {len(nonzero_library)} sequences, limiting to {max_sequences}")
                    # Sample randomly to reduce size while preserving distribution
                    nonzero_library = nonzero_library.sample(n=max_sequences, random_state=42)
                    print(f"Reduced dataset to {len(nonzero_library)} sequences")
                
                # Reduce training set size
                nonzero_library["set"] = random.choices(
                    ["training", "validation", "test"], 
                    weights=[0.5, 0.2, 0.3],  # Use less training data
                    k=len(nonzero_library)
                )

                # Get and report sequence length
                L = len(nonzero_library.loc[nonzero_library.index[0], 'var_seq'])
                print(f'Sequence length: {L:d} DNA nucleotides')

                # Split dataset
                trainval_df, test_df = mavenn.split_dataset(nonzero_library)

                # Define model
                model[sample_set_name] = mavenn.Model(
                    L=L,
                    alphabet='dna',
                    gpmap_type='additive',
                    regression_type='MPA',
                    theta_regularization=0.1,
                    eta_regularization=0.001,
                    Y=len(sample_set)
                )

                # Set training data
                model[sample_set_name].set_data(
                    x=trainval_df['var_seq'],
                    y=trainval_df[sample_set],
                    validation_flags=trainval_df['validation']
                )

                # Add this print statement before model training
                print(f"Training on {len(nonzero_library)} sequences")
                print(f"Sequence length: {L}")

                # Train model with memory-efficient settings
                # Use adaptive batch size: smaller for large datasets to reduce memory
                # For very large datasets, use batch_size=1 to minimize memory
                if len(trainval_df) > 20000:
                    batch_size = 1  # Use batch_size=1 for large datasets
                else:
                    batch_size = min(16, max(1, len(trainval_df) // 500))  # Adaptive batch size
                print(f"Using batch size: {batch_size} for {len(trainval_df)} training sequences")
                
                model[sample_set_name].fit(
                    learning_rate=1e-3,
                    epochs=500,
                    batch_size=batch_size,
                    early_stopping=True,
                    early_stopping_patience=2,
                    verbose=True
                )
                
                # Clear memory immediately after training
                clear_tf_memory()

                print("Create figure and axes for plotting")
                fig, ax = plt.subplots(1, 1, figsize=[5, 5])

                print("Plot I_var_train, the variational information on training data as a function of epoch")
                ax.plot(model[sample_set_name].history['I_var'], label=r'I_var_train')

                print("Plot I_var_val, the variational information on validation data as a function of epoch")
                ax.plot(model[sample_set_name].history['val_I_var'], label=r'val_I_var')

                print("Style plot")
                ax.set_xlabel('epochs')
                ax.set_ylabel('bits')
                ax.set_title('Training history: variational information')
                ax.legend()

                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, f"{sample_set_name}_training_history.png"))
                plt.close()

                print("Compute phi on test data")
                phi_test = model[sample_set_name].x_to_phi(test_df['var_seq'])

                phi_lim = [min(phi_test)-.5, max(phi_test)+.5]
                phi_grid = np.linspace(phi_lim[0], phi_lim[1], 1000)

                print("Plot probabilities output by measurement process")
                bin_probabilities = model[sample_set_name].p_of_y_given_phi(
                    [i for i in range(len(sample_set))], phi_grid)
                fig, axs = plt.subplots(1, 1, figsize=(16, 8))
                for i, bin in enumerate(bin_probabilities):
                    print(i, sample_set[i])
                    axs.plot(phi_grid, bin, label="Probability of being in \n" + sample_set[i])
                axs.legend()
                plt.savefig(os.path.join(output_dir, f"{sample_set_name}_measurement_process.png"))
                plt.close()

                # Save model
                model_path = os.path.join(output_dir, sample_set_name)
                model[sample_set_name].save(model_path)
                print(f"Model saved to {model_path}")
                
                # Clear TensorFlow session after each model to free GPU memory
                clear_tf_memory()
                
                # Note: Keep model in dictionary for return, but clear TF session
                # The model object is lightweight after saving

    if fit_model:
        return model
    return None


def plot_models(model, sign_flips, reverse_complement=False, output_dir="."):
    """Plot sequence logos for trained models."""
    for sample_set_name, sign_flip in zip(model.keys(), sign_flips):
        try:
            # Retrieve G-P map parameter dict and view dict keys
            theta_dict = model[sample_set_name].get_theta(gauge='uniform')
            
            # Get the additive weights
            lc_weights = theta_dict['theta_lc']
            # Convert them to pandas dataframe
            lc_df = pd.DataFrame(lc_weights, columns=model[sample_set_name].alphabet)

            # Replace NaN and Inf values with 0
            lc_df = lc_df.replace([np.inf, -np.inf], np.nan)
            lc_df = lc_df.fillna(0)

            # Correct sign flips
            if sign_flip:
                lc_df = -1*lc_df

            # Reverse complement
            if reverse_complement:
                lc_df = lc_df.rename(
                    index=dict(zip(lc_df.index, len(lc_df) - lc_df.index)), 
                    columns={"A": "T", "C": "G", "G": "C", "T": "A"}
                )

            # plot logos
            fig, axs = plt.subplots(1, 1, figsize=[12, 3])

            # sequence logo for the CRP-DNA binding energy matrix
            # Create logo (logomaker doesn't support allow_nan parameter in all versions)
            try:
                logo = logomaker.Logo(lc_df, ax=axs, center_values=True)
            except TypeError:
                # Fallback for older logomaker versions
                logo = logomaker.Logo(lc_df, ax=axs, center_values=True)
            axs.set_title(sample_set_name)
            logo.style_spines(visible=False)

            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"{sample_set_name}_logo.png"))
            plt.close()
        except Exception as e:
            print(f"Warning: Could not plot logo for {sample_set_name}: {e}")
            print("Skipping logo plot for this model.")
            continue


def main():
    parser = argparse.ArgumentParser(description='Train MAVE-NN models for MPOS data')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to configuration YAML file')
    parser.add_argument('--output-dir', type=str, default='output',
                       help='Output directory for results')
    args = parser.parse_args()

    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Clear any existing TensorFlow sessions before training
    clear_tf_memory()

    # Train models for each configuration
    for model_config in config['models']:
        readcount_file = model_config['readcount_file']
        library_seqs_file = model_config['library_seqs_file']
        all_samples = model_config['all_samples']
        adapter_lengths = tuple(model_config['adapter_lengths'])
        zipf_figure_shape = tuple(model_config['zipf_figure_shape'])
        fit_samples = model_config.get('fit_samples', None)
        fit_model = model_config.get('fit_model', True)

        print(f"\n{'='*60}")
        print(f"Training models for {readcount_file}")
        print(f"{'='*60}\n")

        models = analyze_MPOS(
            readcount_file=readcount_file,
            library_seqs_file=library_seqs_file,
            all_samples=all_samples,
            adapter_lengths=adapter_lengths,
            zipf_figure_shape=zipf_figure_shape,
            fit_samples=fit_samples,
            fit_model=fit_model,
            output_dir=args.output_dir
        )

        # Plot models if requested
        if models and 'sign_flips' in model_config:
            plot_models(
                models,
                sign_flips=model_config['sign_flips'],
                reverse_complement=model_config.get('reverse_complement', False),
                output_dir=args.output_dir
            )

        # Clear memory after saving models
        if models:
            del models
            clear_tf_memory()

    print("\nAll models trained successfully!")


if __name__ == '__main__':
    main()

