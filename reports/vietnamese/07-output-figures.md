# Giải thích các hình output

File này giải thích các hình do reproduction sinh ra.

## 1. `classification_accuracy.png`

Ý nghĩa:

- so sánh `Accuracy` giữa `DT`, `RF`, và `DT-CTS`

Cách giải thích:

- `DT` và `RF` là hai baseline mạnh nhất nếu chỉ nhìn chất lượng phân loại
- `DT-CTS` thấp hơn một chút
- điều này là hợp lý vì `DT-CTS` cố tình ràng buộc threshold để dễ triển khai hơn

Thông điệp chính:

> `DT-CTS` không tối ưu chỉ cho accuracy, mà tối ưu cho trade-off giữa chất lượng và deployability.

## 2. `classification_f1.png`

Ý nghĩa:

- so sánh `F1-score` giữa `DT`, `RF`, và `DT-CTS`

Cách giải thích:

- F1 phù hợp hơn accuracy đơn thuần trong intrusion detection vì nó cân bằng precision và recall
- `DT` và `RF` đều quanh `0.991`
- `DT-CTS` vẫn giữ mức khá cao là `0.9646`

Thông điệp chính:

> Sau khi giảm độ phức tạp mô hình, `DT-CTS` vẫn đủ hiệu quả để dùng cho detection.

## 3. `threshold_usage.png`

Ý nghĩa:

- so sánh tổng số threshold của `DT`, `RF`, và `DT-CTS`

Cách giải thích:

- `RF` dùng rất nhiều threshold
- `DT` nhỏ hơn đáng kể
- `DT-CTS` là mô hình thân thiện triển khai nhất trong nhóm tree model

Các số chính:

- `DT`: `22`
- `DT-CTS`: `15`
- mức giảm: `31.82%`

Thông điệp chính:

> Đây là hình gần nhất với đóng góp hệ thống chính của paper.

## 4. `pushback_attack_bytes.png`

Ý nghĩa:

- thể hiện số attack bytes tới victim theo thời gian với 3 policy:
  - `no_pushback`
  - `immediate_pushback`
  - `gated_pushback`

Cách giải thích:

- `no_pushback` luôn cao vì không có chặn upstream
- `immediate_pushback` giảm nhanh nhất nhưng quá mạnh tay
- `gated_pushback` cũng giảm mạnh nhưng cân bằng hơn

Thông điệp chính:

> Pushback có tác dụng thật, và bản cải tiến `gated_pushback` thực dụng hơn vì vẫn giảm mạnh attack traffic mà giữ được nhiều benign traffic hơn.
