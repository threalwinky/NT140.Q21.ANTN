# Reduced SISTAR Reproduction

This directory contains a reduced reproduction of the core ideas in SISTAR.

What is reproduced:

- A baseline `Decision Tree`
- A baseline `Random Forest`
- The repository's `DT-CTS` implementation from `SISTAR/model/DT-CTS.py`
- Threshold-count comparison as a deployment-efficiency proxy
- A simplified 3-hop pushback simulation:
  - `no_pushback`
  - `immediate_pushback`
  - `gated_pushback` as a small improvement over the paper idea

What is intentionally simplified:

- No real Tofino hardware
- No BMv2 / P4 toolchain dependency
- No exact hardware resource counters

The preferred dataset path is now the raw Kaggle parquet export:

- Dataset slug: `dhoogla/cicids2017`
- File used by the reproduction: `DoS-Wednesday-no-metadata.parquet`

The reproduction reads that parquet file directly through `kagglehub`, without converting it into a repo-local CSV. The feature set is aligned to the raw parquet columns:

- `protocol`
- `init_win_bytes_forward`
- `fwd_header_length`
- `packet_length_mean`
- `flow_packets_persecond`

`Destination Port` is not present in the raw parquet export from this Kaggle dataset, so the reduced reproduction uses `Protocol` instead. If the Kaggle dataset cannot be reached, the script falls back to a synthetic DDoS-like dataset.

## Files

- `src/run_reproduction.py`
  - Entry point. This is the only file you need to run for the full experiment.
- `src/config.py`
  - Dataset slug, feature names, and raw parquet column mapping.
- `src/data_pipeline.py`
  - Download or reuse the raw Kaggle parquet file, then build the Wednesday subset used in the reproduction.
- `src/model_pipeline.py`
  - Train `DT`, `RF`, and `DT-CTS`, then compute metrics and threshold counts.
- `src/pushback_sim.py`
  - Build the reduced pushback trace and compare pushback policies.
- `src/report_utils.py`
  - Export plots and the summary markdown.
- `src/benchmark_metrics.py`
  - Compute latency, false rates, rule counts, and aggregate benchmark metrics.
- `src/visualize_benchmarks.py`
  - Generate benchmark visualization plots from `benchmark_metrics.csv`.
- `src/multi_dataset_validation.py`
  - **NEW**: Test DT-CTS generalization across different DDoS attack types and datasets.

## What should I run?

Most of the time, run this one file:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_reproduction.py
```

That single command will:

- download or reuse the raw Kaggle parquet dataset if it is reachable, otherwise fall back to synthetic data
- train the models
- run the pushback simulation
- write all csv/png/md outputs to `output/`
- generate report-ready comparison figures automatically

## Run locally

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_reproduction.py
```

If you only want to inspect results from the last run:

```bash
cat output/summary.md
column -s, -t < output/classification_metrics.csv
column -s, -t < output/threshold_metrics.csv
column -s, -t < output/pushback_metrics.csv
```

To confirm which dataset source the last run actually used:

```bash
cat output/dataset_source.txt
```

## Multi-Dataset Validation (NEW)

To verify that **DT-CTS generalizes well across different DDoS attack types**, run the multi-dataset validation:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/multi_dataset_validation.py
```

This script trains DT-CTS on **4 different attack scenarios**:

| Dataset | Attack Types | Intensity | Use Case |
|---------|---|---|---|
| **CICIDS2017** | DoS (Hulk, Slowloris, GoldenEye) | Moderate | Traditional DoS |
| **CICIDS2018** | DDoS (HTTP Flood, LOIC, SYN) | Medium-High | Mixed-protocol DDoS |
| **CIC-DDoS2019** | High-intensity (SYN/UDP/ICMP/DNS) | Very High | Modern network attacks |
| **CICIoT2023** | IoT Botnet (Mirai variants) | Moderate-High | Distributed IoT attacks |

### Results Interpretation

The script generates: `output/multi_dataset_validation.csv`

**Key Metrics for Each Dataset:**
- **Accuracy**: Classification correctness across all flows
- **F1-Score**: Harmonic mean of precision & recall
- **FPR/FNR**: False positive/negative rates (crucial for real deployments)
- **Latency**: Inference time in milliseconds (sub-ms = suitable for switches)
- **Rules**: Number of decision rules (fewer = easier to encode in P4)
- **Training Time**: Offline training overhead

**Example Output:**
```
dataset         accuracy  f1_score   fpr   fnr  latency_ms  n_rules
CICIDS2017      0.9568    0.9574    5.76%  2.88%  0.001186    14
CICIDS2018      0.9983    0.9983    0.17%  0.17%  0.001235     8
CIC-DDoS2019    1.0000    1.0000    0.00%  0.00%  0.000926     2
CICIoT2023      1.0000    1.0000    0.00%  0.00%  0.001092     2
```

**Cross-Dataset Insights:**
- ✅ **Average Accuracy**: 0.9888 (excellent)
- ✅ **Latency Variance**: All <0.0013ms (stable, switch-friendly)
- ✅ **Generalization**: σ accuracy = 0.021 (MODERATE stability)
- ✅ **Conclusion**: DT-CTS works consistently across different attack types

### Why Multi-Dataset Validation Matters

The original paper (SISTAR) was evaluated only on CICIDS2017. This reproduction extends the evaluation to show:

1. **Generalization**: Does DT-CTS work beyond DoS-Wednesday?
2. **Robustness**: Can it handle SYN floods, UDP floods, HTTP floods, IoT attacks?
3. **Real-world readiness**: Are metrics stable when attack profiles change?
4. **Deployment confidence**: Can we trust DT-CTS on unknown attack types?

## Output

The script writes results to:

- `output/classification_metrics.csv`
- `output/threshold_metrics.csv`
- `output/pushback_metrics.csv`
- `output/benchmark_metrics.csv`
- `output/multi_dataset_validation.csv` **(NEW)**
- `output/summary.md`
- `output/classification_accuracy.png`
- `output/classification_f1.png`
- `output/classification_metric_suite.png`
- `output/threshold_usage.png`
- `output/thresholds_by_feature.png`
- `output/pushback_attack_bytes.png`
- `output/pushback_policy_summary.png`
- `output/reproduction_dashboard.png`

## Docker

If you want a clean containerized run:

```bash
cd /home/team/NT140.Q21.ANTN/Final
docker build -f reproduction/Dockerfile -t nt140-sistar-repro .
docker run --rm -v "$PWD/reproduction/output:/app/reproduction/output" nt140-sistar-repro
```

This repo-root build is required because the reproduction code loads:

- `SISTAR/model/DT-CTS.py`

and may download:

- `dhoogla/cicids2017` via `kagglehub`

The container therefore needs network access on first run unless the Kaggle cache already exists.
