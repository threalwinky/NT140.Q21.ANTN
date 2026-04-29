# Cách chạy reproduction

## 1. Chạy toàn bộ thí nghiệm

Di chuyển vào thư mục:

```bash
cd /home/winky/workspace/learning/doan/nt140/reproduction
```

Chạy:

```bash
python3 src/run_reproduction.py
```

Lệnh này sẽ tự:

- đọc dataset `CICIDS2017 Wednesday` nếu file đã có
- nếu không có thì fallback sang synthetic dataset
- train 3 mô hình:
  - `DT`
  - `RF`
  - `DT-CTS`
- chạy mô phỏng `pushback`
- xuất bảng kết quả, hình, và file tóm tắt

## 2. Xem kết quả nhanh

Xem bản tóm tắt:

```bash
cat output/summary.md
```

Xem bảng metric classification:

```bash
column -s, -t < output/classification_metrics.csv
```

Xem bảng threshold:

```bash
column -s, -t < output/threshold_metrics.csv
```

Xem bảng pushback:

```bash
column -s, -t < output/pushback_metrics.csv
```

## 3. Các hình output

Sau khi chạy xong, các hình nằm ở:

- `output/classification_accuracy.png`
- `output/classification_f1.png`
- `output/threshold_usage.png`
- `output/pushback_attack_bytes.png`

## 4. File nào cần chạy?

Chỉ cần chạy đúng **1 file**:

- `src/run_reproduction.py`

Các file còn lại chỉ là module phụ:

- `src/config.py`
- `src/data_pipeline.py`
- `src/model_pipeline.py`
- `src/pushback_sim.py`
- `src/report_utils.py`

## 5. Nếu muốn chạy bằng Docker

Trong thư mục `reproduction`:

```bash
docker build -t nt140-sistar-repro .
docker run --rm -v "$PWD/output:/app/output" nt140-sistar-repro
```

## 6. Dataset đang dùng

Script sẽ ưu tiên file này:

```bash
/home/winky/workspace/learning/doan/nt140/datasets/cicids2017/Wednesday-workingHours.pcap_ISCX.csv
```

Bạn có thể kiểm tra nguồn dataset bằng:

```bash
cat output/dataset_source.txt
```
