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

- đọc dataset `CICIDS2017 Wednesday` nếu file đã có
- nếu không có thì fallback sang synthetic dataset
- train 3 mô hình:
  - `DT`
  - `RF`
  - `DT-CTS`
- chạy mô phỏng `pushback`
- xuất bảng kết quả, hình, và file tóm tắt

Trên máy hiện tại, đường dẫn dataset thật đang là:

```bash
/home/team/NT140.Q21.ANTN/Final/datasets/cicids2017/Wednesday-workingHours.pcap_ISCX.csv
```

Tuy nhiên trên máy hiện tại file này đang là `Git LFS pointer`, chưa phải CSV đầy đủ. `reproduction/src/data_pipeline.py` hiện đã được sửa để:

- dùng dataset thật nếu đọc được đúng format
- tự động fallback sang synthetic dataset nếu file chỉ là placeholder hoặc không đúng cột

Điều đó có nghĩa là lần chạy local mặc định trên máy này hiện đang dùng synthetic dataset, trừ khi bạn tải nội dung CSV thật về đầy đủ.

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
- `datasets/cicids2017/Wednesday-workingHours.pcap_ISCX.csv`

## 6. Dataset đang dùng

Script sẽ ưu tiên file này:

```bash
/home/team/NT140.Q21.ANTN/Final/datasets/cicids2017/Wednesday-workingHours.pcap_ISCX.csv
```

Bạn có thể kiểm tra nguồn dataset bằng:

```bash
cat output/dataset_source.txt
```
