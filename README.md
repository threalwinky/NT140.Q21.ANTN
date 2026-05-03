# NT140.Q21.ANTN — SISTAR: DDoS Detection & Mitigation Using Programmable Data Planes

> *SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes* (ACM CCS 2025)

## What is SISTAR?

SISTAR deploys lightweight ML-based DDoS detection directly on **programmable switches** (data plane), avoiding the latency of centralized server-based analysis. Its key contributions:

- **DT-CTS (Decision Tree — Constrained Threshold Segmentation)**: limits the number of split thresholds per feature so the model fits within switch hardware constraints (TCAM stages).
- **Pushback mitigation**: when a switch detects an attack, it sends alerts to upstream switches so they can block malicious traffic closer to the source.

## Quick Start

### Requirements

- Python 3.11+
- Dependencies: `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `kagglehub`, `pyarrow`

### Install

```bash
pip install -r reproduction/requirements.txt
```

### Run

```bash
cd reproduction
python3 src/run_reproduction.py
```

This single command will:

1. Download the CIC-IDS2017 dataset from Kaggle (`dhoogla/cicids2017`), or fall back to synthetic data
2. Train 3 models: **DT**, **RF**, **DT-CTS**
3. Run the pushback simulation (no_pushback / immediate_pushback / gated_pushback)
4. Write all results to `reproduction/output/`

### View Results

```bash
cat reproduction/output/summary.md
column -s, -t < reproduction/output/classification_metrics.csv
column -s, -t < reproduction/output/threshold_metrics.csv
column -s, -t < reproduction/output/pushback_metrics.csv
```

### Docker

```bash
docker build -f reproduction/Dockerfile -t nt140-sistar-repro .
docker run --rm -v "$PWD/reproduction/output:/app/reproduction/output" nt140-sistar-repro
```

## Dataset

- **Primary**: [CIC-IDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) via Kaggle (`dhoogla/cicids2017`), using the Wednesday (DoS) parquet file
- **Fallback**: Synthetic DDoS-like flow dataset (auto-generated if Kaggle is unavailable)
- **Features used**: `Protocol`, `Init Win Bytes Forward`, `Fwd Header Length`, `Packet Length Mean`, `Flow Packets/s`
