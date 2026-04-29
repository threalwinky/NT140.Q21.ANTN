# Environment And Run

Project paths:

- reproduction code: `../reproduction/src/`
- reproduction outputs: `../reproduction/output/`
- local dataset file:
  - `../datasets/cicids2017/Wednesday-workingHours.pcap_ISCX.csv`

Python entry point:

- `../reproduction/src/run_reproduction.py`

Run command:

```bash
cd /home/winky/workspace/learning/doan/nt140/reproduction
python3 src/run_reproduction.py
```

What the script does:

1. load the Kaggle `CICIDS2017 Wednesday` subset
2. clean invalid values such as `inf` and negative numeric artifacts
3. sample a balanced subset of benign and attack flows
4. train `DT`, `RF`, and `DT-CTS`
5. compute classification metrics
6. compute threshold-usage metrics
7. generate a pushback trace
8. compare `no_pushback`, `immediate_pushback`, and `gated_pushback`
9. write outputs to `../reproduction/output/`

Useful commands after running:

```bash
cat ../reproduction/output/summary.md
column -s, -t < ../reproduction/output/classification_metrics.csv
column -s, -t < ../reproduction/output/threshold_metrics.csv
column -s, -t < ../reproduction/output/pushback_metrics.csv
```

Key output files:

- `../reproduction/output/summary.md`
- `../reproduction/output/classification_metrics.csv`
- `../reproduction/output/threshold_metrics.csv`
- `../reproduction/output/pushback_metrics.csv`
- `../reproduction/output/classification_accuracy.png`
- `../reproduction/output/classification_f1.png`
- `../reproduction/output/threshold_usage.png`
- `../reproduction/output/pushback_attack_bytes.png`

Docker option:

```bash
cd /home/winky/workspace/learning/doan/nt140/reproduction
docker build -t nt140-sistar-repro .
docker run --rm -v "$PWD/output:/app/output" nt140-sistar-repro
```
