# Môi trường và cách chạy

Đường dẫn chính:

- mã nguồn reproduction: `../reproduction/src/`
- output: `../reproduction/output/`
- file dataset local:
  - `../datasets/cicids2017/Wednesday-workingHours.pcap_ISCX.csv`

Entry point:

- `../reproduction/src/run_reproduction.py`

Lệnh chạy:

```bash
cd /home/winky/workspace/learning/doan/nt140/reproduction
python3 src/run_reproduction.py
```

Script sẽ tự động:

1. đọc `CICIDS2017 Wednesday` từ Kaggle
2. làm sạch các giá trị lỗi như `inf` và các giá trị âm bất thường
3. lấy mẫu cân bằng giữa benign và attack
4. train `DT`, `RF`, `DT-CTS`
5. tính metric phân loại
6. tính metric về threshold
7. sinh trace mô phỏng pushback
8. so sánh `no_pushback`, `immediate_pushback`, `gated_pushback`
9. ghi output vào `../reproduction/output/`

Lệnh hữu ích sau khi chạy:

```bash
cat ../reproduction/output/summary.md
column -s, -t < ../reproduction/output/classification_metrics.csv
column -s, -t < ../reproduction/output/threshold_metrics.csv
column -s, -t < ../reproduction/output/pushback_metrics.csv
```

Các file output quan trọng:

- `../reproduction/output/summary.md`
- `../reproduction/output/classification_metrics.csv`
- `../reproduction/output/threshold_metrics.csv`
- `../reproduction/output/pushback_metrics.csv`
- `../reproduction/output/classification_accuracy.png`
- `../reproduction/output/classification_f1.png`
- `../reproduction/output/threshold_usage.png`
- `../reproduction/output/pushback_attack_bytes.png`

Nếu muốn chạy bằng Docker:

```bash
cd /home/winky/workspace/learning/doan/nt140/reproduction
docker build -t nt140-sistar-repro .
docker run --rm -v "$PWD/output:/app/output" nt140-sistar-repro
```
