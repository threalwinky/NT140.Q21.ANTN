# Tổng quan paper

Paper:

- Tên: `SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes`
- Venue: `ACM CCS 2025`

Vấn đề paper giải quyết:

- Phát hiện DDoS cần đủ chính xác để nhận ra các kiểu tấn công phức tạp.
- Nhưng programmable switch có giới hạn tài nguyên phần cứng rất chặt.
- Nhiều hướng trước đây thường rơi vào một trong các vấn đề:
  - dùng quá nhiều feature,
  - dùng quá nhiều threshold và table entry,
  - không quan tâm đủ tới hành vi ở mức flow,
  - hoặc không có cơ chế phối hợp giữa nhiều switch.

Các ý chính của paper:

1. `Phát hiện trong switch`
   - phát hiện ngay trong data plane thay vì gửi hết traffic tới server hay controller trung tâm

2. `DT-CTS`
   - ràng buộc số threshold được dùng bởi mỗi feature trong quá trình xây decision tree
   - mục tiêu là làm mô hình gọn hơn và dễ triển khai hơn

3. `Feature encoding`
   - biến quyết định của mô hình thành giá trị mã hóa nhỏ gọn để switch match hiệu quả

4. `Distributed pushback`
   - nếu một switch phát hiện tấn công, nó gửi cảnh báo cho switch upstream
   - nhờ đó switch upstream có thể chặn sớm hơn

Vì sao paper phù hợp với môn học:

- đúng phạm vi network security
- mới và thuộc top venue
- có cả đóng góp về thuật toán lẫn hệ thống
- có thể tái hiện một phần mà không cần đúng phần cứng gốc

Điểm mạnh của paper:

- xử lý cả phát hiện lẫn giảm thiểu
- quan tâm tới khả năng triển khai thực tế, không chỉ điểm số ML
- có đóng góp kỹ thuật rõ ràng là `DT-CTS`
- đánh giá cả chất lượng mô hình lẫn góc nhìn resource/deployment

Giới hạn của paper:

- rất khó tái hiện đầy đủ nếu không có P4/BMv2 hoặc Tofino
- các kết quả về tài nguyên phần cứng khó kiểm chứng chính xác nếu thiếu môi trường gốc
- giả định triển khai thực tế mạnh hơn mức mà sinh viên thường có

Để đọc bản giải thích dễ hiểu hơn, xem:

- `../paper-summary.md`
