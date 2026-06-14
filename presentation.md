---
1. Mở đầu

Chào thầy/cô và các bạn.

Hôm nay em trình bày project tái hiện rút gọn paper SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes.

Nói ngắn gọn, project này nghiên cứu một câu hỏi:

▎ Làm sao phát hiện và giảm thiểu tấn công DDoS nhanh hơn, ngay trong mạng, thay vì đợi traffic đi tới server rồi mới xử lý?

---
2. DDoS là gì?

Trước hết, DDoS là viết tắt của Distributed Denial of Service.

Hiểu đơn giản, attacker dùng rất nhiều nguồn cùng gửi traffic tới một hệ thống. Mục tiêu không nhất thiết là đánh cắp dữ liệu, mà là làm dịch vụ bị chậm, quá tải hoặc ngừng hoạt động.

Vì vậy, hệ thống chống DDoS cần làm hai việc:

- phát hiện traffic nào là tấn công,
- và chặn hoặc giảm thiểu traffic đó càng sớm càng tốt.

---
3. Vấn đề của cách xử lý truyền thống

Một cách xử lý phổ biến là để traffic đi tới server hoặc controller trung tâm rồi mới phân tích.

Cách này có một vấn đề lớn:

▎ Khi hệ thống phát hiện ra tấn công thì traffic xấu đã đi qua gần hết mạng rồi.

Điều đó làm tốn băng thông, gây tải cho các switch/router ở giữa, và cuối cùng vẫn gây áp lực lên
server nạn nhân.

Do đó, paper SISTAR đề xuất một hướng tiếp cận khác:

▎ Đưa việc phát hiện DDoS xuống gần data plane hơn.

---
4. Data plane và programmable switch là gì?

Switch có thể hiểu là thiết bị chuyển tiếp packet trong mạng.

Nó có hai phần chính:

- control plane: phần điều khiển, cấu hình luật, thường linh hoạt nhưng chậm hơn;
- data plane: phần xử lý packet trực tiếp theo các luật đã được cài sẵn.

Bình thường data plane chỉ làm các thao tác forward packet. Nhưng với programmable data plane, ta có thể lập trình switch để làm thêm một số logic tùy chỉnh.

Ví dụ:

- đọc thông tin packet,
- tính một số đặc trưng đơn giản,
- so sánh với luật,
- quyết định traffic có đáng nghi hay không.

Đây là điểm quan trọng của SISTAR: để phát hiện tấn công nhanh hơn.

---
5. Ý tưởng chính của SISTAR

SISTAR có thể tóm tắt bằng 3 ý chính.

Ý thứ nhất: phát hiện ngay trong switch.

Thay vì gửi toàn bộ traffic lên server để phân tích, switch sẽ tự quan sát traffic và đưa ra quyết
định sơ bộ.

Điều này giúp phản ứng nhanh hơn và giảm phụ thuộc vào điểm phân tích tập trung.

Ý thứ hai: dùng mô hình ML nhẹ.

Paper dùng các mô hình dạng cây quyết định:

- Decision Tree,
- Random Forest,
- và đặc biệt là DT-CTS.

Decision Tree phù hợp vì nó khá dễ chuyển thành luật so sánh trên switch.

Ví dụ:

- nếu số packet/giây quá cao thì đáng nghi,
- nếu kích thước packet bất thường thì mức nghi ngờ tăng thêm.

Ý thứ ba: pushback.

Nếu một switch phát hiện traffic tấn công, nó không chỉ chặn tại chỗ. Nó còn gửi cảnh báo cho switch
ở phía trước, gần nguồn tấn công hơn.

Cơ chế này gọi là pushback.

Mục tiêu là chặn traffic xấu càng sớm càng tốt, trước khi nó đi sâu vào mạng.

---
6. Vấn đề kỹ thuật: mô hình phải đủ nhẹ

Một điểm khó của bài toán là switch có tài nguyên rất hạn chế.

Switch không giống server. Nó không thể chạy mô hình deep learning lớn hoặc xử lý phức tạp.

Vì vậy, bài toán không chỉ là:

▎ Mô hình có chính xác không?

Mà còn là:

▎ Mô hình có đủ nhẹ để triển khai trên switch không?

Đây là lý do paper đưa ra DT-CTS.

---
7. DT-CTS là gì?

DT-CTS là viết tắt của:

▎ Decision Tree - Constrained Threshold Sets

Hiểu đơn giản, đây là một cây quyết định được ràng buộc để dùng ít threshold hơn.

Threshold là các ngưỡng so sánh.

Ví dụ:

Nếu `flow_packets_persecond > 500`

Số 500 chính là một threshold.

Một cây quyết định bình thường có thể dùng rất nhiều threshold khác nhau. Điều đó có thể giúp mô hình chính xác hơn, nhưng cũng làm việc triển khai lên switch nặng hơn.

DT-CTS cố gắng giảm số threshold này.

Đổi lại, độ chính xác có thể giảm nhẹ, nhưng mô hình sẽ gọn hơn và phù hợp hơn với programmable switch.

---
8. Project của em làm gì?

Project này không tái hiện toàn bộ hệ thống SISTAR trên phần cứng thật như Tofino hay BMv2.

Thay vào đó, project làm một bản reproduction rút gọn, tập trung vào 3 phần cốt lõi:

1. phát hiện DDoS bằng mô hình ML,
2. so sánh số threshold để đánh giá khả năng triển khai,
3. mô phỏng pushback để xem có giảm traffic tấn công tới victim không.

---
9. Dataset dùng trong project

Trong luồng benchmark chính hiện tại, project dùng dataset rút gọn được build từ `reproduction/datasets/combine.csv`, dựa trên CICIDS2017.

Đây là dataset rất phổ biến trong nghiên cứu DDoS detection.

Trong reproduction chính, mô hình dùng 5 feature:

- protocol,
- init window bytes forward,
- forward header length,
- packet length mean,
- flow packets per second.

Các feature này đại diện cho hành vi lưu lượng ở mức flow.

Ví dụ:

- traffic tấn công có thể có số packet/giây cao bất thường,
- kích thước packet hoặc header có thể khác traffic bình thường.

---
10. Các mô hình được so sánh

Project huấn luyện và so sánh 3 mô hình:

1. Decision Tree.

Đây là baseline đơn giản, dễ hiểu, và dễ triển khai.

2. Random Forest.

Random Forest thường chính xác hơn Decision Tree đơn lẻ.

Nhưng điểm yếu là nặng hơn, khó triển khai hơn trong data plane.

3. DT-CTS.

Đây là mô hình quan trọng nhất trong project.

DT-CTS cố giảm số threshold để mô hình gọn hơn khi đưa xuống data plane.

---
11. Kết quả phân loại

Trong lần chạy reproduction mới nhất, kết quả là:

- Decision Tree: Accuracy `0.9901`, F1 `0.9620`
- Random Forest: Accuracy `0.9821`, F1 `0.9327`
- DT-CTS: Accuracy `0.9800`, F1 `0.9249`

F1 là chỉ số cân bằng giữa precision và recall.

Ta thấy DT-CTS có F1 thấp hơn Decision Tree một chút.

Nhưng điều quan trọng là DT-CTS được thiết kế không chỉ để tối đa độ chính xác, mà còn để giảm chi
phí triển khai.

---
12. Benchmark paper-style bổ sung

Ngoài reproduction chính, project còn chạy thêm benchmark paper-style cho `DT / RF / DT-CTS` với `3 / 5 / 7` feature để kiểm tra tính ổn định của kết quả.

Kết quả tốt nhất của `DT-CTS` trong benchmark này là:

- dùng `7 feature`,
- F1 đạt `0.9614`,
- dùng `14 threshold`,
- giảm `58.82%` số threshold so với `DT` cùng cấu hình.

Điểm cần nhấn mạnh là dù không phải mô hình chính xác nhất tuyệt đối, `DT-CTS` vẫn giữ chất lượng đủ tốt trong khi chi phí triển khai thấp hơn đáng kể.

---
13. Kết quả threshold

Về số threshold:

- Trong reproduction chính: `DT` dùng `36 threshold`
- `DT-CTS` dùng `14 threshold`

Tức là `DT-CTS` giảm khoảng `61.11%` số threshold so với `DT`.

Đây là kết quả rất quan trọng.

Nó cho thấy DT-CTS chấp nhận giảm nhẹ chất lượng để đổi lấy mô hình nhẹ hơn đáng kể.

Với programmable switch, ít threshold hơn nghĩa là:

- ít rule hơn,
- ít tài nguyên bảng match hơn,
- dễ triển khai hơn trong data plane.

---
14. Pushback simulation là gì?

Sau phần phát hiện, project mô phỏng một mạng đơn giản gồm nhiều hop.

Ý tưởng là so sánh các chính sách xử lý traffic tấn công.

Có 3 policy:

1. no_pushback
  - không chặn sớm,
  - traffic tấn công vẫn đi tới victim.
2. immediate_pushback
  - phát hiện attack là chặn ngay upstream,
  - giảm attack rất nhanh nhưng dễ chặn nhầm.
3. hierarchical_confidence_pushback
  - edge switch phát hiện sớm, core switch xác nhận sâu hơn,
  - phản ứng theo mức: monitor -> local rate-limit -> upstream pushback -> hard block.

---
15. Kết quả pushback

Kết quả cho thấy:

- `no_pushback`: attack bytes tới victim khoảng `5,876,251`
- `immediate_pushback`: attack bytes về `0` nhưng có `11 false block events`
- `Hierarchical Confidence-Aware Pushback`: attack bytes tới victim còn khoảng `4,591 bytes`

Tức là giảm khoảng 99.92% attack traffic tới victim.

Ngoài ra, hierarchical policy giữ được hơn 2.05 tỉ benign bytes và không có false block events.

Điều này cho thấy cơ chế pushback mới vừa giảm mạnh attack traffic, vừa tránh block vội benign source.

---
16. Cải tiến của project

Ngoài việc tái hiện ý tưởng paper, project có thêm một cải tiến mạnh hơn là
Hierarchical Confidence-Aware Pushback.

Thay vì block theo số lần phát hiện cố định, hệ thống cộng suspicion score từ nhiều nguồn bằng chứng:

- edge detector nghi ngờ sớm,
- core detector xác nhận mạnh hơn,
- traffic spike bất thường làm tăng mức độ tin cậy.

Khi score tăng dần, hệ thống sẽ đi qua các mức:

- monitor,
- local rate-limit,
- upstream pushback,
- hard block.

Điểm quan trọng là hệ thống không block ngay từ đầu.

- Nếu mới chỉ có nghi ngờ nhẹ ở edge, hệ thống chỉ monitor.
- Nếu nghi ngờ lặp lại, hệ thống rate-limit cục bộ để giảm tải trước.
- Nếu nhiều switch cùng xác nhận, hệ thống mới pushback upstream.
- Chỉ khi score vượt ngưỡng cao nhất và core detector vẫn kết luận malicious thì mới hard block.

---
17. Giới hạn của project

Project này có một số giới hạn.

Thứ nhất, đây là reproduction rút gọn, chưa phải triển khai trên phần cứng P4 thật.

Thứ hai, số threshold chỉ là proxy cho độ phức tạp triển khai, chưa phải số đo trực tiếp như TCAM hoặc SRAM.

Thứ ba, phần pushback là mô phỏng đơn giản, chưa phải hệ thống mạng thực tế.

Tuy nhiên, project vẫn tái hiện được các ý chính của paper:

- mô hình ML có thể phát hiện DDoS,
- DT-CTS giúp giảm threshold,
- pushback giúp giảm traffic tấn công tới victim.

---
18. Kết luận

Tóm lại, project này cho thấy SISTAR là một hướng tiếp cận thực tế cho bài toán DDoS.

Thay vì chỉ phát hiện ở server, SISTAR đưa việc phát hiện xuống gần switch để phản ứng nhanh hơn.

DT-CTS giúp mô hình đủ nhẹ để phù hợp với môi trường data plane.

Hierarchical Confidence-Aware Pushback giúp chặn traffic tấn công sớm hơn và bảo vệ mạng phía sau tốt hơn.

Kết quả reproduction cho thấy:

- DT-CTS giảm `61.11%` threshold so với `DT` trong reproduction chính,
- hierarchical confidence-aware pushback giảm 99.92% attack bytes tới victim,
- và vẫn giữ được benign traffic mà không tạo false block trong mô phỏng chính.

Vì vậy, điểm quan trọng nhất của project không chỉ là phát hiện được attack, mà là sự cân bằng giữa:

- phát hiện tốt,
- triển khai nhẹ,
- và phản ứng theo mức để giảm chặn nhầm.

---
19. Câu kết khi thuyết trình

Nếu chỉ nhớ một câu về project này, thì đó là:

▎ Project này tái hiện ý tưởng SISTAR: dùng mô hình cây quyết định nhẹ để phát hiện DDoS ngay trong switch, rồi dùng cơ chế pushback phân tầng để giảm tải và bảo vệ mạng tốt hơn.
