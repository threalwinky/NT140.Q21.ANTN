# Kết quả thực nghiệm

Nguồn dataset:

- `CICIDS2017 Wednesday subset from Kaggle`

Các label chính trong Wednesday:

- `BENIGN`
- `DoS Hulk`
- `DoS GoldenEye`
- `DoS slowloris`
- `DoS Slowhttptest`
- `Heartbleed`

Bài toán trong reproduction được chuyển thành nhị phân:

- `BENIGN` -> benign
- tất cả label còn lại -> attack

## Kết quả phân loại

Lấy từ `../reproduction/output/classification_metrics.csv`:

| Mô hình | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| DT | 0.9912 | 0.9873 | 0.9952 | 0.9912 |
| RF | 0.9912 | 0.9936 | 0.9888 | 0.9912 |
| DT-CTS | 0.9640 | 0.9489 | 0.9808 | 0.9646 |

Diễn giải:

- `DT` và `RF` là hai baseline mạnh nhất nếu chỉ nhìn chất lượng phân loại.
- `DT-CTS` thấp hơn về F1, nhưng vẫn đủ mạnh để sử dụng.
- Kết quả này phù hợp với trade-off chính của paper:
  - chấp nhận mất một phần hiệu năng để đổi lấy khả năng triển khai tốt hơn.

## Kết quả về hiệu quả threshold

Lấy từ `../reproduction/output/threshold_metrics.csv`:

| Mô hình | Tổng threshold | Số feature dùng | Threshold tối đa trên một feature |
| --- | ---: | ---: | ---: |
| DT | 22 | 5 | 7 |
| RF | 115 | 5 | 34 |
| DT-CTS | 15 | 5 | 3 |

Diễn giải:

- `DT-CTS` giảm tổng threshold từ `22` xuống `15` so với `DT`.
- Tương ứng mức giảm là `31.82%`.
- Cột cuối phản ánh rõ nhất ý tưởng triển khai của paper:
  - `DT-CTS` khống chế mỗi feature tối đa `3` threshold,
  - trong khi `DT` và đặc biệt là `RF` dùng nhiều hơn đáng kể.

Đây là phần tái hiện gần nhất với đóng góp chính của paper.

## Kết quả pushback

Lấy từ `../reproduction/output/pushback_metrics.csv`:

| Policy | Attack bytes tới victim | Benign bytes tới victim | Attack flows tới victim | Benign flows tới victim | False block events |
| --- | ---: | ---: | ---: | ---: | ---: |
| no_pushback | 1,731,491 | 3,509,171,465 | 240 | 1200 | 0 |
| immediate_pushback | 362 | 693,712,885 | 3 | 347 | 20 |
| gated_pushback | 51,302 | 2,020,443,640 | 16 | 1007 | 3 |

Diễn giải:

- `immediate_pushback` là policy mạnh tay nhất.
- Nó gần như triệt tiêu attack traffic, nhưng chặn nhầm benign rất nhiều và tạo ra nhiều false block.
- `gated_pushback` cân bằng hơn:
  - vẫn giảm attack bytes `97.04%` so với `no_pushback`,
  - giữ lại benign traffic tốt hơn nhiều so với `immediate_pushback`,
  - và giảm false block từ `20` xuống `3`.

Kết luận chính:

> Bản reproduction thu gọn này ủng hộ hướng thiết kế của SISTAR: mô hình gọn hơn và cơ chế pushback upstream có thể giảm attack traffic hiệu quả, đồng thời policy pushback thận trọng hơn sẽ giữ benign traffic tốt hơn.
