[![DOI](https://zenodo.org/badge/1114583370.svg)](https://doi.org/10.5281/zenodo.18989567)
# MPOS Analysis Code

Computational analysis code for the Massively Parallel Origin Selection (MPOS) experiments in:

> **Bauer\*, Zali\* et al.** "Evolution of Origin Sequence and Recognition for Licensing of Eukaryotic DNA Replication." *bioRxiv* (2026).
> [doi: 10.64898/2026.03.10.710760](https://doi.org/10.64898/2026.03.10.710760)

This repository covers the MPOS sequencing, model training, and figure generation pipeline. Cryo-EM structural analysis and EdU-seq genome-wide origin mapping are described in the paper but are not included here.

## Pipeline Overview

```
Raw FASTQs ──> Count Tables ──> MAVE-NN Models ──> Paper Figures
                │                    │                    │
   MPOS_sequencing_pipeline/  mpos_model_training/  generate_mpos_figs.ipynb
```

**Stage 1 — Sequencing processing** (`MPOS_sequencing_pipeline/`): Demultiplexes paired-end FASTQ files by barcode, extracts 90 bp target sequences, and produces per-sequence count tables.

**Stage 2 — Model training** (`mpos_model_training/`): Trains MAVE-NN additive models on count data to infer sequence determinants of origin activity.

**Stage 3 — Figure generation** (`generate_mpos_figs.ipynb`): Loads trained models and generates Figures 6A, 6C, and S6A for the paper.

## Repository Structure

```
├── MPOS_sequencing_pipeline/   # Stage 1: FASTQ → count tables (Snakemake)
├── mpos_model_training/        # Stage 2: count tables → MAVE-NN models (Snakemake)
├── generate_mpos_figs.ipynb    # Stage 3: models → paper figures
├── data/                       # Trained models, libraries, and genomic sequence sets
├── figures/                    # Output figures (PDF + PNG)
├── misc/                       # Exploratory notebooks (not used for final figures)
└── preprint/                   # Paper and supplement PDFs
```

## Data Files

| File | Description |
|------|-------------|
| `NGS-NZ-3477_A1before_yl_A1_plate_yl-0n.pickle` / `.weights.h5` | MAVE-NN trained model for OriA-006 |
| `NGS-NZ-3477_C2-out_c2-P.pickle` / `.weights.h5` | MAVE-NN trained model for OriC-061 |
| `ORI_A_library_*.csv` | OriA-006 MPOS variant library (7,000 sequences) |
| `ORI_C_library_*.csv` | OriC-061 MPOS variant library (7,000 sequences) |
| `NGS-NZ_read_counts.csv` | Summary of sequencing read counts per sample/run |
| `peakset3_sequence_matches.csv` | *Y. lipolytica* EdU-seq peak regions (positive set, 623 regions) |
| `peakset3_sequence_controls.csv` | *Y. lipolytica* random genomic regions (negative set, 623 regions) |
| `oriDB_confirmed_ARSs_1000bp.csv` | *S. cerevisiae* confirmed origins from OriDB (1 kb regions) |
| `saccharomyces_control_seqs_1000bp.csv` | *S. cerevisiae* random genomic regions (1 kb, negative set) |
| `saccharomyces_control_seqs_10000bp.csv` | *S. cerevisiae* random genomic regions (10 kb, negative set) |
| `model.mi.exp8_ars416_wt.txt` | *S. cerevisiae* ARS1 origin motif (PWM from [Hu et al.](https://doi.org/10.1038/s41586-022-05484-3)) |
| `24_zali.mplstyle` | Matplotlib style file for publication figures |

## Figures

| Output file | Paper figure |
|-------------|--------------|
| `figures/fig6A_OriA_model.pdf` | Figure 6A — OriA-006 MPOS additive model (sequence logo) |
| `figures/figS6C_OriC_model.pdf` | Figure S6A — OriC-061 MPOS additive model (sequence logo) |
| `figures/fig6C_ROC_curves.pdf` | Figure 6C — ROC curves for motif-based origin prediction |

## Reproducing Figures

To regenerate Figures 6A, 6C, and S6A from the pre-trained models:

```bash
pip install -r requirements.txt
jupyter notebook generate_mpos_figs.ipynb
```

Run all cells. Outputs are saved to `figures/`.

To reproduce the full pipeline from raw sequencing data, see the READMEs in `MPOS_sequencing_pipeline/` (Stage 1) and `mpos_model_training/` (Stage 2).

## Dependencies

Core dependencies for figure generation (see `requirements.txt`):

- Python 3.8+
- [MAVE-NN](https://github.com/jbkinney/mavenn) (mavenn)
- [Logomaker](https://github.com/jbkinney/logomaker) (logomaker)
- NumPy, Pandas, Matplotlib, SciPy

Each pipeline stage has its own `requirements.txt` with additional dependencies (Snakemake, TensorFlow, etc.).

## License

This work is released under a [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) license, consistent with the preprint.

## Contact

- Bruce Stillman: stillman@cshl.edu
- Leemor Joshua-Tor: leemor@cshl.edu
- Justin Kinney (for questions about this repo): jkinney@cshl.edu
