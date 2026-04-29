# Phạm vi tái hiện

Phạm vi tái hiện trong đồ án này là phạm vi rút gọn có chủ đích.

Những gì được tái hiện trung thực:

- ý tưởng so sánh `Decision Tree` thường với phiên bản bị ràng buộc threshold
- ý tưởng dùng số threshold như một đại diện cho khả năng triển khai
- ý tưởng `pushback` như một cơ chế giảm thiểu tấn công
- ý tưởng thêm một cải tiến nhỏ về mặt kỹ thuật vào logic mitigation

Những gì được đơn giản hóa:

- không có programmable switch thật
- không chạy đầy đủ toàn bộ P4 runtime stack trong thí nghiệm cuối
- không đo chính xác SRAM/TCAM như paper
- không tái hiện đúng môi trường Tofino hoặc BMv2 của tác giả trong phần đánh giá cuối

Vì sao phạm vi rút gọn này vẫn hợp lệ:

- yêu cầu môn học là `prototype / mô phỏng / reproduction thu gọn`, không bắt buộc đúng hạ tầng công nghiệp
- bản tái hiện vẫn kiểm tra được trade-off cốt lõi của paper:
  - mô hình gọn hơn so với chất lượng phân loại
- bản tái hiện vẫn kiểm tra được ý tưởng mitigation của paper:
  - pushback giúp giảm traffic tấn công sớm hơn trước khi tới victim

Phạm vi cuối cùng của đồ án:

1. Dataset
   - `CICIDS2017 Wednesday` từ Kaggle

2. Feature
   - `destination_port`
   - `init_win_bytes_forward`
   - `fwd_header_length`
   - `packet_length_mean`
   - `flow_packets_persecond`

3. Mô hình
   - `DT`
   - `RF`
   - `DT-CTS`

4. Chế độ mitigation
   - `no_pushback`
   - `immediate_pushback`
   - `gated_pushback`

Câu claim nên dùng trong báo cáo:

> Nhóm tái hiện các ý tưởng cốt lõi mang tính triển khai của SISTAR trong một môi trường phần mềm rút gọn, tập trung vào phát hiện bằng cây quyết định có ràng buộc threshold và giảm thiểu bằng cơ chế pushback.
