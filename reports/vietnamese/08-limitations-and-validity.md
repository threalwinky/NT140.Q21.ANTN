# Giới hạn và độ giá trị của kết quả

Đây là một reproduction rút gọn, không phải reproduction phần cứng đầy đủ.

## Các giới hạn chính

1. Không có programmable switch thật
   - nhóm không tuyên bố đã tái hiện chính xác ở mức Tofino

2. Không có đo đạc đúng tài nguyên P4/BMv2 trong thí nghiệm cuối
   - vì vậy các claim về SRAM/TCAM của paper không được kiểm chứng trực tiếp

3. Bài toán được đơn giản hóa thành phân loại nhị phân
   - benign vs attack
   - đơn giản hơn bài toán nhiều lớp chi tiết

4. Bộ feature được rút gọn
   - chỉ dùng 5 feature để bám paper và giữ thí nghiệm dễ hiểu

5. Topology pushback được đơn giản hóa
   - thí nghiệm mitigation dùng topology logic nhỏ, không phải mạng programmable hoàn chỉnh

## Vì sao kết quả vẫn có ý nghĩa

- thí nghiệm classification vẫn đo được trade-off giữa chất lượng và độ gọn của mô hình
- thí nghiệm threshold phản ánh trực tiếp ý tưởng chính của paper
- thí nghiệm pushback vẫn thể hiện trực giác hệ thống: chặn upstream giúp giảm attack traffic trước khi tới victim

## Threats to validity

- kết quả có thể thay đổi nếu lấy mẫu khác trên Wednesday
- hiệu năng mô hình có thể thay đổi nếu chọn feature khác
- mô phỏng pushback đơn giản hơn nhiều so với triển khai P4/BMv2 thực

Câu nên dùng trong báo cáo:

> Mục tiêu của đồ án không phải tái hiện chính xác toàn bộ claim phần cứng của SISTAR, mà là tái hiện các nguyên lý thiết kế cốt lõi của paper trong một môi trường phần mềm có thể chạy được và đánh giá được.
