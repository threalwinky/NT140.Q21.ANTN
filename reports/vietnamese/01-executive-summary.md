# Tóm tắt điều hành

Đồ án này nghiên cứu paper `SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes` và tái hiện các ý tưởng cốt lõi của paper trong một môi trường phần mềm rút gọn.

Ý tưởng chính của paper là:

- phát hiện DDoS ngay trong programmable data plane,
- giảm độ phức tạp mô hình bằng `DT-CTS`,
- và giảm traffic tấn công từ sớm trong mạng bằng cơ chế `pushback`.

Do nhóm không có programmable switch thật, đồ án cố ý chọn một phạm vi tái hiện rút gọn nhưng vẫn có cơ sở kỹ thuật:

- baseline `Decision Tree`,
- baseline `Random Forest`,
- implementation `DT-CTS` lấy từ repo của SISTAR,
- so sánh số threshold như một proxy cho khả năng triển khai,
- và mô phỏng `pushback` trên topology logic 3-hop.

Phần tái hiện chạy trên `CICIDS2017 Wednesday` subset lấy từ Kaggle. Lựa chọn này phù hợp với paper vì Wednesday chứa nhiều hành vi DoS/DDoS và được paper nhắc tới trong phần đánh giá.

Kết quả chính:

- `DT` F1: `0.9912`
- `RF` F1: `0.9912`
- `DT-CTS` F1: `0.9646`
- `DT-CTS` giảm số threshold từ `22` xuống `15` so với `DT`
- mức giảm threshold so với `DT`: `31.82%`
- `gated_pushback` giảm `97.04%` attack bytes tới victim so với `no_pushback`

Phát biểu phạm vi đồ án:

> Đồ án tái hiện các ý tưởng cốt lõi của SISTAR trong một prototype phần mềm rút gọn: phát hiện DDoS bằng cây quyết định có ràng buộc threshold và giảm thiểu bằng cơ chế pushback, sau đó đánh giá định lượng trên tập CICIDS2017 Wednesday.
