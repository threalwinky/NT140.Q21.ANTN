# Cách chạy reproduction

## 1. Chạy toàn bộ workflow

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_full_demo.py
```

Lệnh này sẽ:

- chạy reproduction chính với `DT`, `RF`, `DT-CTS`
- mô phỏng `Hierarchical Confidence-Aware Pushback`
- chạy benchmark paper-style `DT / RF / DT-CTS` với `3 / 5 / 7` feature
- chạy riêng phần improvement và ghi output vào `reproduction/improvement/output`

## 2. Chỉ chạy reproduction chính

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_reproduction.py
```

Script này sẽ:

- đọc dataset từ `combine.csv`
- train `DT`, `RF`, `DT-CTS`
- tính classification metrics, threshold metrics, latency/FPR/FNR
- chạy ba policy:
  - `no_pushback`
  - `immediate_pushback`
  - `hierarchical_confidence_pushback`
- xuất CSV, PNG và `summary.md`

## 3. Chỉ chạy benchmark paper-style

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/paper_benchmark_3models.py
```

Script này tạo:

- `output/benchmark_cicids2017_dt_rf_dtcts.csv`
- các plot `benchmark_*.png`
- confusion matrices cho từng model / số feature

## 4. Chỉ chạy improvement riêng

```bash
cd /home/team/NT140.Q21.ANTN/Final
python3 reproduction/improvement/run_hierarchical_improvement.py
```

## 5. Xem nhanh kết quả

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
cat output/summary.md
column -s, -t < output/classification_metrics.csv
column -s, -t < output/threshold_metrics.csv
column -s, -t < output/pushback_metrics.csv
```

## 6. Các file quan trọng sau khi chạy

Trong `reproduction/output/`:

- `classification_metrics.csv`
- `threshold_metrics.csv`
- `benchmark_metrics.csv`
- `pushback_metrics.csv`
- `pushback_detail.csv`
- `summary.md`
- `pushback_attack_bytes.png`
- `pushback_policy_summary.png`

Trong `reproduction/improvement/output/`:

- `TEACHER_SUMMARY.md`
- `teacher_comparison_table.csv`
- `teacher_policy_comparison.png`
- `teacher_attack_timeline.png`
- `hierarchical_improvement_dashboard.png`

## 7. Dataset đang dùng

Workflow hiện tại ưu tiên:

```text
reproduction/datasets/combine.csv
```

Bạn có thể kiểm tra nguồn dataset của lần chạy gần nhất bằng:

```bash
cat output/dataset_source.txt
```
