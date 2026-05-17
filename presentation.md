---
1. Mở đầu

Chào thầy/cô và các bạn.

Hôm nay em trình bày project tái hiện rút gọn paper SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes.

Nói ngắn gọn, project này nghiên cứu một câu hỏi:

▎ Làm sao phát hiện và giảm thiểu tấn công DDoS nhanh hơn, ngay trong mạng, thay vì đợi traffic đi tới server rồi mới xử lý?

---
2. DDoS là gì?

Trước hết, DDoS là viết tắt của Distributed Denial of Service.

Hiểu đơn giản, attacker dùng rất nhiều nguồn gửi traffic tới cùng một hệ thống. Mục tiêu không nhất thiết là đánh cắp dữ liệu, mà là làm cho dịch vụ bị chậm, quá tải hoặc sập.

Ví dụ: nếu một server bình thường xgiây, nhưng attacker gửi vào hàngtriệu request mỗi giây, thì người dùng thật có thể không truy cập được dịch vụ nữa.

Vì vậy, hệ thống chống DDoS cần làm hai việc:

- phát hiện traffic nào là tấn công,
- và chặn hoặc giảm thiểu traffic đ

---
3. Vấn đề của cách xử lý truyền thống

Một cách xử lý phổ biến là để traffic đi tới server hoặc controller trung tâm rồi mới phân tích.

Cách này có một vấn đề lớn:

▎ Khi hệ thống phát hiện ra tấn công thì traffic xấu đã đi qua gần hết mạng rồi.

Điều đó làm tốn băng thông, gây tải cho các switch/router ở giữa, và cuối cùng vẫn gây áp lực lên
server nạn nhân.

Do đó, paper SISTAR đề xuất một hướ

▎ Đưa việc phát hiện DDoS xuống ngarong data plane.

---
4. Data plane và programmable switch là gì?

Switch có thể hiểu là thiết bị chuyển tiếp packet trong mạng.

Nó có hai phần chính:

- control plane: phần điều khiển, cấu hình luật, thường linh hoạt nhưng chậm hơn;
- data plane: phần xử lý packet trựcác luật đã được cài sẵn.

Bình thường data plane chỉ làm nhữnpacket. Nhưng với programmable dataplane, ta có thể lập trình switch để làm thêm một số logic tùy chỉnh.

Ví dụ:

- đọc thông tin packet,
- tính một số đặc trưng đơn giản,
- so sánh với luật,
- quyết định traffic có đáng nghi h

Đây là điểm quan trọng của SISTAR: để phát hiện tấn công nhanh hơn.

---
5. Ý tưởng chính của SISTAR

SISTAR có thể tóm tắt bằng 3 ý chính.

Ý thứ nhất: phát hiện ngay trong switch

Thay vì gửi toàn bộ traffic lên server để phân tích, switch sẽ tự quan sát traffic và đưa ra quyết
định sơ bộ.

Điều này giúp phản ứng nhanh hơn vàtâm.

Ý thứ hai: dùng mô hình ML nhẹ

Paper dùng các mô hình dạng cây quy

- Decision Tree,
- Random Forest,
- và đặc biệt là DT-CTS.

Decision Tree phù hợp vì nó giống cn thành luật cho switch.

Ví dụ:

Nếu số packet/giây quá cao → nghi n
Nếu kích thước packet bất thường → càng nghi ngờ attack

Ý thứ ba: pushback

Nếu một switch phát hiện traffic tấn công, nó không chỉ chặn tại chỗ. Nó còn gửi cảnh báo cho switch
 ở phía trước, gần nguồn tấn công h

Cơ chế này gọi là pushback.

Mục tiêu là chặn traffic xấu càng ssâu vào mạng.

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

▎ Decision Tree - Constrained Thres

Hiểu đơn giản, đây là một cây quyếtít threshold hơn.

Threshold là các ngưỡng so sánh.

Ví dụ:

Nếu flow_packets_persecond > 500 th

Số 500 chính là một threshold.

Một cây quyết định bình thường có tĐiều đó giúp mô hình chính xác hơn,nhưng lại khiến việc triển khai lên switch nặng hơn.

DT-CTS cố gắng giảm số threshold này.

Đổi lại, độ chính xác có thể giảm nhẹ, nhưng mô hình sẽ gọn hơn và phù hợp hơn với programmable
switch.

---
8. Project của em làm gì?

Project này không tái hiện toàn bộ hệ thống SISTAR trên phần cứng thật như Tofino hay BMv2.

Thay vào đó, project làm một bản reproduction rút gọn, tập trung vào 3 phần cốt lõi:

1. phát hiện DDoS bằng mô hình ML,
2. so sánh số threshold để đánh giá
3. mô phỏng pushback để xem có giảm traffic tấn công tới victim không.

---
9. Dataset dùng trong project

Project dùng dataset CICIDS2017, cụesday.

Đây là dataset phổ biến trong nghiêDDoS detection.

Từ dataset, project lấy một số feat

- protocol,
- init window bytes forward,
- forward header length,
- packet length mean,
- flow packets per second.

Các feature này đại diện cho hành v

Ví dụ:

- traffic tấn công có thể có số pac
- kích thước packet hoặc header có thể khác traffic bình thường.

---
10. Các mô hình được so sánh

Project huấn luyện và so sánh 3 mô

1. Decision Tree

Đây là baseline đơn giản, dễ hiểu,

2. Random Forest

Random Forest thường chính xác hơn  định.

Nhưng điểm yếu là nặng hơn, khó tri

3. DT-CTS

Đây là mô hình quan trọng nhất tron

DT-CTS cố giảm số threshold để mô hdata plane.

---
11. Kết quả phân loại

Trong lần chạy reproduction, kết quả F1 là:

- Decision Tree: khoảng 0.9864
- Random Forest: khoảng 0.9712
- DT-CTS: khoảng 0.9574

F1 là chỉ số cân bằng giữa precision và recall.

Ta thấy DT-CTS có F1 thấp hơn Decision Tree một chút.

Nhưng điều quan trọng là DT-CTS được thiết kế không chỉ để tối đa độ chính xác, mà còn để giảm chi
phí triển khai.

---
11.5. Tính tổng quát hóa: Multi-Dataset Validation (NEW)

Kết quả trên chỉ là trên CICIDS2017 DoS-Wednesday.

Câu hỏi đặt ra là: **Mô hình DT-CTS có hoạt động tốt trên các loại tấn công khác không?**

Để kiểm chứng điều này, em tài hiện một bước mới: **Multi-Dataset Validation**.

Mô hình được huấn luyện lại trên 4 dataset khác nhau, đại diện cho các loại DDoS attack khác nhau:

| Dataset | Loại Attack | Đặc điểm |
|---|---|---|
| **CICIDS2017** | DoS (Hulk, Slowloris) | Tấn công truyền thống, cường độ vừa |
| **CICIDS2018** | DDoS (HTTP Flood, LOIC) | Tấn công đa giao thức, cường độ cao |
| **CIC-DDoS2019** | SYN/UDP/ICMP Flood | Tấn công cường độ rất cao |
| **CICIoT2023** | Mirai IoT Botnet | Tấn công từ thiết bị IoT |

**Kết quả trên 4 dataset:**

- CICIDS2017: Accuracy 0.9568, F1 0.9574, FPR 5.76%, FNR 2.88%
- CICIDS2018: Accuracy 0.9983, F1 0.9983, FPR 0.17%, FNR 0.17%
- CIC-DDoS2019: Accuracy 1.0000, F1 1.0000, FPR 0.00%, FNR 0.00%
- CICIoT2023: Accuracy 1.0000, F1 1.0000, FPR 0.00%, FNR 0.00%

**Nhận xét:**

- Trung bình Accuracy: 0.9888 ✅
- Độ chênh lệch (σ): 0.0213 (ổn định)
- Latency: ~0.001ms trên tất cả dataset (nhất quán, phù hợp switch)
- Kết luận: **DT-CTS tổng quát hóa tốt** trên các loại tấn công khác nhau

---
13. Kết quả threshold

Về số threshold:

- Decision Tree dùng 30 threshold
- DT-CTS dùng 13 threshold

Tức là DT-CTS giảm khoảng 56.67% sốee.

Đây là kết quả rất quan trọng.

Nó cho thấy DT-CTS hy sinh một phầnmô hình nhẹ hơn đáng kể.

Với programmable switch, ít thresho

- ít rule hơn,
- ít tài nguyên bảng match hơn,
- dễ triển khai hơn trong data plan

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
  - giảm attack nhanh nhưng có nguy
3. gated_pushback
  - chỉ pushback sau khi phát hiện
  - thận trọng hơn để giảm false block.

---
15. Kết quả pushback

Kết quả cho thấy:

- Không pushback: attack bytes tới tes
- Gated pushback: attack bytes tới victim còn khoảng 64,791 bytes

Tức là giảm khoảng 97.80% attack traffic tới victim.

Ngoài ra, gated pushback vẫn giữ được khoảng 305,761,878 bytes benign traffic, và chỉ có 2 false
block events.

Điều này cho thấy pushback giúp giả sâu vào mạng.

---
16. Cải tiến nhỏ của project

Ngoài việc tái hiện ý tưởng paper, project có thêm một cải tiến nhỏ là gated_pushback.

Thay vì cứ phát hiện attack là chặn ngay, hệ thống yêu cầu phải có 2 lần phát hiện malicious liên
tiếp rồi mới pushback.

Lý do là nếu mô hình phát hiện sai ó thể chặn nhầm traffic hợp lệ.

Gated pushback giúp cân bằng hơn gi

- chặn attack,
- và tránh block nhầm benign traffic.

---
17. Giới hạn của project

Project này có một số giới hạn.

Thứ nhất, đây là reproduction rút gware thật.

Thứ hai, số threshold chỉ là proxy , chưa phải số đo resource thật nhưTCAM hoặc SRAM.

Thứ ba, phần pushback là mô phỏng đơn giản, chưa phải hệ thống mạng thực tế.

Tuy nhiên, project vẫn tái hiện được các ý chính của paper:

- mô hình ML có thể phát hiện DDoS,
- DT-CTS giúp giảm threshold,
- pushback giúp giảm traffic tấn công tới victim.

---
18. Kết luận

Tóm lại, project này cho thấy SISTAtế cho bài toán DDoS.

Thay vì chỉ phát hiện ở server, SISswitch để phản ứng nhanh hơn.

DT-CTS giúp mô hình đủ nhẹ để phù he.

Pushback giúp chặn traffic tấn công và mạng phía sau.

Kết quả reproduction cho thấy:

- DT-CTS giảm 56.67% threshold so v
- gated pushback giảm 97.80% attack bytes tới victim,
- và vẫn giữ được phần lớn benign t

Vì vậy, điểm quan trọng nhất của pracy, mà là sự cân bằng giữa:

▎ phát hiện tốt, triển khai nhẹ, và

---
19. Câu kết khi thuyết trình

Nếu chỉ nhớ một câu về project này, thì đó là:

▎ Project này tái hiện ý tưởng SISTAR: dùng mô hình cây quyết định nhẹ để phát hiện DDoS ngay trong switch, rồi dùng pushback để chặnng mạng.