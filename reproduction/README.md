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
- `src/multi_dataset_validation.py`
  - Compatibility helper that validates DT-CTS on the generated benchmark CSV.
- `src/paper_benchmark_3models.py`
  - Single-file benchmark with `DT`, `RF`, `DT-CTS` for feature sets 3/5/7 and bar-chart output.

## What should I run?

If you want the full demo in one command, run this file:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_full_demo.py
```

That single command will:

- run the core reproduction pipeline
  - split `combine.csv` into 75% train and 25% benchmark
  - train `DT`, `RF`, and `DT-CTS` on the 75% split
  - benchmark on the 20% hold-out split
- write all csv/png/md outputs to `output/`
- generate report-ready comparison figures automatically

If you only want the core reproduction pipeline, run:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_reproduction.py
```

## Run locally

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_full_demo.py
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

## Benchmark Validation

The repository keeps `src/multi_dataset_validation.py` only as a compatibility helper. The active benchmark flow now uses a 75/25 stratified split of `combine.csv` and evaluates `DT`, `RF`, and `DT-CTS` on the 25% hold-out set.

If you want to rerun the benchmark validation directly, use:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/multi_dataset_validation.py
```

## Data Benchmark 3-Model Benchmark

Run:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/paper_benchmark_3models.py
```

This single script benchmarks the 20% hold-out split of `combine.csv` using three model families:

- `DT`
- `RF`
- `DT-CTS`

For each model, it evaluates feature-set sizes `3`, `5`, and `7`, then exports both CSV results and bar charts.

Outputs:

```text
output/benchmark_combine_75_25_dt_rf_dtcts.csv
output/benchmark_combine_75_25_dt_rf_dtcts.png
```

## Output

The script writes results to:

- `output/classification_metrics.csv`
- `output/threshold_metrics.csv`
- `output/pushback_metrics.csv`
- `output/benchmark_metrics.csv`
 - `output/benchmark_combine_75_25_dt_rf_dtcts.csv` **(NEW)**
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
