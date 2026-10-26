# Mandragora H6H Analysis

Data and Python code supporting the study **"Comparative sequence analysis of hyoscyamine 6β-hydroxylase in Mandragora officinarum"**.

## Protein Sequences

- Mandragora officinarum — A0A6M6R352
- Hyoscyamus niger — P24397
- Atropa belladonna — Q9XJ43
- Anisodus tanguticus — Q6V0J1
- Anisodus acutangulus — A2IBI0

## Contents

- Protein sequences and MAFFT alignment
- Python analysis scripts
- Pairwise sequence identity and amino-acid substitution tables
- Exploratory mutation ranking and figures
- Leave-One-Out robustness analysis
- BLOSUM62 substitution scores

## Main Results

- 40 consensus-based amino-acid differences
- 27 unanimous comparator differences
- 35/40 differences supported in all Leave-One-Out comparisons
- G220C identified as the highest-ranked candidate

## Reproducibility

The `12_extended_analysis` folder contains the updated Python script and CSV results.

## Note

All analyses are computational and exploratory. The results do not establish functional effects of amino-acid substitutions.
