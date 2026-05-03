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

## Output

The script writes results to:

- `output/classification_metrics.csv`
- `output/threshold_metrics.csv`
- `output/pushback_metrics.csv`
- `output/summary.md`
- `output/*.png`

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
