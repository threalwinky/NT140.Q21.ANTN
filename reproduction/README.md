# Reduced SISTAR Reproduction

This directory contains the active reproduction workflow for the project.

## What is included

- baseline `DT`
- baseline `RF`
- repo-native `DT-CTS` from [DT-CTS.py](/home/team/NT140.Q21.ANTN/Final/SISTAR/model/DT-CTS.py)
- threshold-count comparison as a deployment-efficiency proxy
- reduced pushback simulation with three policies:
  - `no_pushback`
  - `immediate_pushback`
  - `hierarchical_confidence_pushback`

The previous fixed-gate pushback idea has been replaced by a hierarchical confidence-aware design.

## Mitigation Improvement

`Hierarchical Confidence-Aware Pushback` works in four levels:

1. `monitor`
2. `local_rate_limit`
3. `upstream_pushback`
4. `hard_block`

The simulation uses:

- an `edge DT-CTS` detector with a lightweight feature set
- a `core DT-CTS` detector with a fuller feature set
- a per-source `suspicion score` that increases when both detectors agree or traffic spikes strongly

This is meant to better match the distributed defense idea of SISTAR than a simple fixed gate.

## Main Commands

Run the reduced reproduction:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_reproduction.py
```

Run the paper-style benchmark:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/paper_benchmark_3models.py
```

Run the full demo:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_full_demo.py
```

That full demo now:

- refreshes `output/`
- reruns the reduced reproduction
- reruns the paper-style benchmark
- reruns the improvement comparison in `improvement/output/`

## Current Outputs

Core reproduction outputs:

- `output/classification_metrics.csv`
- `output/threshold_metrics.csv`
- `output/benchmark_metrics.csv`
- `output/pushback_metrics.csv`
- `output/pushback_detail.csv`
- `output/summary.md`

Paper-style benchmark outputs:

- `output/benchmark_cicids2017_dt_rf_dtcts.csv`
- `output/benchmark_accuracy.png`
- `output/benchmark_f1_scores.png`
- `output/benchmark_accept_deny_f3.png`
- `output/benchmark_accept_deny_f5.png`
- `output/benchmark_accept_deny_f7.png`

Improvement outputs:

- `improvement/output/TEACHER_SUMMARY.md`
- `improvement/output/teacher_comparison_table.csv`
- `improvement/output/hierarchical_improvement_dashboard.png`

## Current Results Snapshot

From the latest `run_reproduction.py` run:

- `DT` F1: `0.9620`
- `RF` F1: `0.9327`
- `DT-CTS` F1: `0.9249`
- `DT-CTS` thresholds: `14`
- threshold reduction vs `DT`: `61.11%`

From the latest hierarchical mitigation run:

- attack-byte reduction vs `no_pushback`: `99.92%`
- false block events: `0`
- local rate-limit events: `23`
- upstream pushback events: `10`
- hard block events: `8`

## Dataset Notes

- The active reproduction pipeline uses `reproduction/datasets/combine.csv`.
- `build_dataset()` extracts the paper-compatible `BENIGN vs Wednesday DoS` subset.
- If local data is unavailable, the helper code can still fall back to synthetic flows.

## Docker

```bash
cd /home/team/NT140.Q21.ANTN/Final
docker build -f reproduction/Dockerfile -t nt140-sistar-repro .
docker run --rm -v "$PWD/reproduction/output:/app/reproduction/output" nt140-sistar-repro
```

The container path is still useful for the core Python reproduction, but the main workflow is easiest to run directly on the shared workspace.
