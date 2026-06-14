# NT140.Q21.ANTN: SISTAR Reproduction with Hierarchical Confidence-Aware Pushback

**Project Title:** SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes

## Project Overview

This project reproduces the core ideas of the SISTAR paper in a software-only workflow and extends the mitigation logic with a stronger system-level improvement:

- in-network DDoS detection with lightweight tree-based models
- `DT-CTS` as the main deployable model
- a reduced pushback simulation
- a new `Hierarchical Confidence-Aware Pushback` policy

The new mitigation design uses a hierarchical confidence-aware policy. Instead of relying on a single fixed gate before blocking, the system now:

- uses an `edge DT-CTS` detector for early suspicion
- uses a `core DT-CTS` detector for stronger confirmation
- accumulates a `suspicion score` over time
- escalates mitigation through `monitor -> local rate-limit -> upstream pushback -> hard block`

That makes the improvement closer to the original SISTAR spirit of distributed, upstream-aware defense.

## Quick Start

Run the full refreshed workflow:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_full_demo.py
```

This now runs:

1. the reduced reproduction pipeline with hierarchical confidence-aware pushback
2. the paper-style `DT / RF / DT-CTS` benchmark for `3 / 5 / 7` features
3. the dedicated improvement comparison in `reproduction/improvement/output`

If you only want the reduced reproduction:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_reproduction.py
```

If you only want the improvement comparison:

```bash
cd /home/team/NT140.Q21.ANTN/Final
python3 reproduction/improvement/run_hierarchical_improvement.py
```

## Key Results

### Reduced Reproduction

From `reproduction/output/classification_metrics.csv`:

| Model | Accuracy | F1 |
|---|---:|---:|
| DT | 0.9901 | 0.9620 |
| RF | 0.9821 | 0.9327 |
| DT-CTS | 0.9800 | 0.9249 |

From `reproduction/output/threshold_metrics.csv`:

- `DT` total thresholds: `36`
- `DT-CTS` total thresholds: `14`
- threshold reduction vs `DT`: `61.11%`

### Paper-Style DT / RF / DT-CTS Benchmark

From `reproduction/output/benchmark_cicids2017_dt_rf_dtcts.csv`:

- best `DT-CTS` paper-style setting: `7 features`
- `DT-CTS` F1: `0.9614`
- `DT-CTS` threshold count: `14`
- threshold reduction vs `DT` at `7 features`: `58.82%`

This is the cleanest evidence in the repo that `DT-CTS` stays competitive while remaining much easier to deploy.

### Hierarchical Confidence-Aware Pushback

From `reproduction/output/pushback_metrics.csv`:

| Policy | Attack Bytes Reaching Victim | Benign Bytes Preserved | False Blocks |
|---|---:|---:|---:|
| no_pushback | 5,876,251 | 2,196,901,718 | 0 |
| immediate_pushback | 0 | 1,760,928,313 | 11 |
| hierarchical_confidence_pushback | 4,591 | 2,052,047,683 | 0 |

Key improvement metrics:

- attack-byte reduction vs `no_pushback`: `99.92%`
- `0` false block events
- `23` local rate-limit events
- `10` upstream pushback events
- `8` hard block events

This is the main improvement story of the project: the new policy still suppresses attack traffic very strongly, but it no longer jumps straight to hard blocking the way the immediate baseline does.

## Important Outputs

Main outputs:

- `reproduction/output/classification_metrics.csv`
- `reproduction/output/threshold_metrics.csv`
- `reproduction/output/benchmark_metrics.csv`
- `reproduction/output/pushback_metrics.csv`
- `reproduction/output/summary.md`
- `reproduction/output/benchmark_cicids2017_dt_rf_dtcts.csv`

Main plots:

- `reproduction/output/classification_accuracy.png`
- `reproduction/output/classification_f1.png`
- `reproduction/output/threshold_usage.png`
- `reproduction/output/pushback_attack_bytes.png`
- `reproduction/output/pushback_policy_summary.png`
- `reproduction/output/benchmark_accuracy.png`
- `reproduction/output/benchmark_f1_scores.png`

Improvement-only outputs:

- `reproduction/improvement/output/TEACHER_SUMMARY.md`
- `reproduction/improvement/output/teacher_comparison_table.csv`
- `reproduction/improvement/output/teacher_policy_comparison.png`
- `reproduction/improvement/output/teacher_attack_timeline.png`
- `reproduction/improvement/output/hierarchical_improvement_dashboard.png`

## Repository Layout

```text
NT140.Q21.ANTN/Final
├── README.md
├── paper.pdf
├── note.md
├── presentation.md
├── SISTAR/
│   ├── model/DT-CTS.py
│   ├── BMv2/
│   └── tofino/
└── reproduction/
    ├── src/
    │   ├── run_reproduction.py
    │   ├── run_full_demo.py
    │   ├── pushback_sim.py
    │   ├── model_pipeline.py
    │   └── paper_benchmark_3models.py
    ├── improvement/
    │   ├── run_hierarchical_improvement.py
    │   └── output/
    └── output/
```

## Notes

- The active dataset source in the current workflow is `reproduction/datasets/combine.csv`.
- `multi_dataset_validation.py` is kept mainly as a compatibility helper and is no longer the center of the current experiment flow.
- The BMv2 and Tofino folders remain useful as architectural references, but the main grading/demo path for this repo is the Python reproduction plus the hierarchical mitigation improvement.
