# Cách chạy reproduction

## 1. Chạy toàn bộ thí nghiệm

Di chuyển vào thư mục:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
```

Chạy:

```bash
python3 src/run_reproduction.py
```

Lệnh này sẽ tự:

- tải hoặc dùng lại cache của dataset Kaggle `dhoogla/cicids2017`
- đọc trực tiếp file raw parquet `DoS-Wednesday-no-metadata.parquet`
- nếu không tải/đọc được thì fallback sang synthetic dataset
- train 3 mô hình:
  - `DT`
  - `RF`
  - `DT-CTS`
- chạy mô phỏng `pushback`
- xuất bảng kết quả, hình, và file tóm tắt

Nguồn dataset thật ưu tiên hiện tại là:

```bash
dhoogla/cicids2017 / DoS-Wednesday-no-metadata.parquet
```

`reproduction/src/data_pipeline.py` hiện đã được sửa để:

- dùng raw parquet từ Kaggle thông qua `kagglehub`
- tự động fallback sang synthetic dataset nếu Kaggle không truy cập được hoặc file không đúng format

Lưu ý: bản parquet raw này không có cột `Destination Port`, nên reproduction dùng `Protocol` thay cho feature đó.

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

Di chuyển về root của repo:

```bash
cd /home/team/NT140.Q21.ANTN/Final
docker build -f reproduction/Dockerfile -t nt140-sistar-repro .
docker run --rm -v "$PWD/reproduction/output:/app/reproduction/output" nt140-sistar-repro
```

Cách build này cần thiết vì code trong `src/config.py` còn đọc thêm:

- `SISTAR/model/DT-CTS.py`
- dataset Kaggle `dhoogla/cicids2017` qua `kagglehub`

## 6. Dataset đang dùng

Script sẽ ưu tiên nguồn này:

```bash
dhoogla/cicids2017 / DoS-Wednesday-no-metadata.parquet
```

Bạn có thể kiểm tra nguồn dataset bằng:

```bash
cat output/dataset_source.txt
```
