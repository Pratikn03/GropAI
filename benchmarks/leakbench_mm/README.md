# LeakBench-MM (Skeleton)
This benchmark compares leaky versus guardrail-enforced splits across modalities.

Folders:
- `splits/`: JSON split definitions (leaky vs safe)
- `run_eval.py`: swaps between splits, runs the tabular HPO script twice, and stores markers in `reports/metrics`.
