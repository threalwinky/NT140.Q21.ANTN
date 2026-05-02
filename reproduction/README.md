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

Instead, the experiment uses a synthetic DDoS-like flow dataset with feature names aligned to the paper:

- `destination_port`
- `init_win_bytes_forward`
- `fwd_header_length`
- `packet_length_mean`
- `flow_packets_persecond`

If the file below exists, the script automatically switches to a real dataset run:

- `/home/team/NT140.Q21.ANTN/Final/datasets/cicids2017/Wednesday-workingHours.pcap_ISCX.csv`

This is the preferred mode because it matches the `Wednesday` subset used in the paper discussion for DoS/DDoS behavior.

On the current machine, that path exists but is currently only a `Git LFS` pointer, not the full CSV. The loader now detects incompatible / placeholder files and automatically falls back to the synthetic dataset, so the default local run on this machine uses synthetic data unless you fetch the real CSV contents.

## Files

- `src/run_reproduction.py`
  - Entry point. This is the only file you need to run for the full experiment.
- `src/config.py`
  - Paths, feature names, and dataset column mapping.
- `src/data_pipeline.py`
  - Load the Kaggle CICIDS2017 Wednesday subset or fall back to synthetic data.
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

- load the real dataset if it is usable, otherwise fall back to synthetic data
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
- `datasets/cicids2017/Wednesday-workingHours.pcap_ISCX.csv`

and both paths live outside `reproduction/`.
