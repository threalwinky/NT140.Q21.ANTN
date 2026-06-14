# Note: Các Khái Niệm Chính Trong Paper/Reproduction

## 1. Mục Tiêu Benchmark

Benchmark dùng để trả lời 2 câu hỏi:

- Model phân loại DDoS có chính xác không?
- Model có đủ nhẹ để triển khai trên switch/data plane không?

Trong project này, ta không chỉ nhìn accuracy, mà còn nhìn:

- F1, precision, recall để đo khả năng phân loại.
- Threshold count để đo độ gọn của model.
- Pushback metrics để đo hiệu quả giảm thiểu attack.

## 2. Confusion Matrix

Với bài toán binary classification:

- `0`: benign traffic
- `1`: attack traffic

Các giá trị cơ bản:

- `TP`: attack được dự đoán đúng là attack.
- `TN`: benign được dự đoán đúng là benign.
- `FP`: benign bị dự đoán nhầm là attack.
- `FN`: attack bị dự đoán nhầm là benign.

Ý nghĩa ngắn gọn:

- `FP` cao: chặn nhầm traffic bình thường.
- `FN` cao: bỏ sót attack.

## 3. Accuracy

Accuracy đo tỷ lệ dự đoán đúng trên tất cả mẫu.

```text
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

Nhận xét:

- Dễ hiểu nhưng có thể gây hiểu nhầm nếu dataset lệch lớp.
- Ví dụ benign quá nhiều thì model đoán benign nhiều vẫn có accuracy cao.

## 4. Precision

Precision trả lời câu hỏi:

> Trong các flow bị model dự đoán là attack, bao nhiêu flow thật sự là attack?

```text
Precision = TP / (TP + FP)
```

Ý nghĩa:

- Precision cao: ít chặn nhầm benign traffic.
- Quan trọng khi hệ thống có cơ chế block/pushback.

## 5. Recall

Recall trả lời câu hỏi:

> Trong tất cả attack thật, model phát hiện được bao nhiêu?

```text
Recall = TP / (TP + FN)
```

Ý nghĩa:

- Recall cao: ít bỏ sót attack.
- Trong DDoS detection, recall attack rất quan trọng vì attack bị bỏ sót vẫn có thể đi tới victim.

## 6. F1 Score

F1 là trung bình hài hòa giữa precision và recall.

```text
F1 = 2 * Precision * Recall / (Precision + Recall)
```

Ý nghĩa:

- F1 cao: model cân bằng tốt giữa bắt attack và tránh chặn nhầm.
- Phù hợp hơn accuracy khi dataset lệch lớp.

## 7. Balanced Accuracy

Balanced accuracy tính trung bình khả năng nhận đúng từng lớp.

```text
Balanced Accuracy = (Recall_benign + Recall_attack) / 2
```

Ý nghĩa:

- Tốt hơn accuracy khi số lượng benign và attack không cân bằng.
- Nếu model chỉ giỏi một lớp và tệ ở lớp còn lại, balanced accuracy sẽ phản ánh rõ hơn.

## 8. Threshold Count

Threshold là ngưỡng so sánh trong cây quyết định.

Ví dụ:

```text
flow_packets_persecond <= 500
packet_length_mean <= 120
```

Trong data plane, mỗi threshold có thể cần chuyển thành rule/register/condition.

Ý nghĩa:

- Threshold count càng thấp thì model càng nhẹ.
- Model nhẹ hơn sẽ dễ đưa vào switch/P4/data plane hơn.

Trong reproduction hiện tại:

```text
DT     = 34 thresholds
RF     = 254 thresholds
DT-CTS = 14 thresholds
```

Kết luận:

```text
DT-CTS giảm 58.82% threshold so với DT ở cấu hình 7 features.
```

## 9. F1 Per Threshold

Chỉ số này đo hiệu quả trên mỗi threshold.

```text
F1 per threshold = F1 / Threshold Count
```

Ý nghĩa:

- Cao hơn nghĩa là model đạt F1 tốt với ít threshold hơn.
- Phù hợp để chứng minh DT-CTS có trade-off tốt giữa accuracy và footprint.

## 10. Latency

Latency là thời gian model cần để dự đoán một flow.

Ý nghĩa:

- Latency thấp: phản ứng nhanh hơn.
- Quan trọng với DDoS vì traffic attack đến rất nhanh.

## 11. Pushback Metrics

Pushback là cơ chế chặn traffic ở upstream, gần nguồn tấn công hơn.

Các metric chính:

- `attack_bytes_reaching_victim`: attack bytes vẫn đến được victim, càng thấp càng tốt.
- `benign_bytes_reaching_victim`: benign bytes vẫn được giữ lại, càng cao càng tốt.
- `false_block_events`: số lần chặn nhầm benign source, càng thấp càng tốt.
- `attack reduction`: phần trăm attack giảm so với không pushback.
- `benign preserved`: phần trăm benign còn giữ lại so với không pushback.

Kết quả improvement hiện tại:

```text
Immediate pushback:
- attack bytes tới victim: 0
- false block events: 11

Hierarchical Confidence-Aware Pushback:
- attack bytes tới victim: 4,591
- false block events: 0
- local rate-limit events: 23
- upstream pushback events: 10
- hard block events: 8
```

Kết luận:

```text
Hierarchical Confidence-Aware Pushback vẫn giảm attack rất mạnh,
nhưng không block vội như immediate pushback.
```

## 11.1. Cơ Chế Pushback: Switch Làm Gì?

Ý tưởng của pushback:

```text
Không chỉ chặn attack ở gần victim,
mà đẩy hành động chặn ngược về switch gần nguồn tấn công hơn.
```

Luồng xử lý đơn giản:

```text
1. Switch quan sát traffic/flow đi qua.
2. Switch hoặc controller trích xuất feature của flow.
3. Model phân loại flow là benign hoặc attack.
4. Nếu flow bị xem là attack, switch/controller xác định source đáng nghi.
5. Hệ thống cài rule để drop/block traffic từ source đó.
6. Rule có thể được cài ở switch upstream, tức là switch gần nguồn hơn.
```

Switch sẽ làm gì cụ thể?

- Nhận packet/flow đi qua.
- So sánh feature với các threshold/rule đã được cài.
- Nếu flow match rule attack thì đánh dấu là malicious.
- Drop packet hoặc không forward packet đó.
- Có thể thông báo controller để cài rule chặn source ở switch phía trước.

Với `immediate_pushback`:

```text
Chỉ cần source bị dự đoán attack 1 lần
=> block source ngay.
```

Ưu điểm:

- Chặn attack rất nhanh.

Nhược điểm:

- Dễ chặn nhầm benign nếu model false positive.

Với `hierarchical_confidence_pushback`:

```text
Source không bị block ngay.
Hệ thống cộng suspicion score theo bằng chứng từ edge switch,
core switch và traffic spike.
```

Khi score tăng dần, phản ứng leo thang theo mức:

```text
monitor
-> local rate-limit
-> upstream pushback
-> hard block
```

Ưu điểm:

- Giảm chặn nhầm benign.
- Vẫn phản ứng sớm với attack thật.
- Hợp với ý tưởng nhiều switch phối hợp của SISTAR hơn.

Kết quả mô phỏng hiện tại:

```text
Immediate pushback:
- attack bytes tới victim: 0
- false block events: 11

Hierarchical Confidence-Aware Pushback:
- attack bytes tới victim: 4,591
- false block events: 0
```

Kết luận ngắn:

```text
Pushback giúp chặn attack sớm hơn trong mạng.
Hierarchical Confidence-Aware Pushback làm việc này theo nhiều mức,
nên giảm block nhầm mà vẫn giữ hiệu quả giảm attack rất cao.
```

## 12. Gini Impurity

Gini impurity đo độ "lẫn tạp" của một node trong Decision Tree.

Công thức tổng quát:

```text
Gini(S) = 1 - sum(p_i^2)
```

Trong đó:

- `S`: tập mẫu tại node.
- `p_i`: tỷ lệ mẫu thuộc lớp i trong node.

Với bài toán binary benign/attack:

```text
Gini(S) = 1 - p_benign^2 - p_attack^2
```

Nếu node rất sạch:

```text
100% benign hoặc 100% attack
=> Gini = 0
```

Nếu node bị trộn đều:

```text
50% benign, 50% attack
=> Gini = 1 - 0.5^2 - 0.5^2 = 0.5
```

## 13. Gini Gain

Khi Decision Tree thử một threshold, nó chia node thành 2 node con:

- left: feature <= threshold
- right: feature > threshold

Gini sau khi split:

```text
Gini_split =
    (n_left / n) * Gini(left)
  + (n_right / n) * Gini(right)
```

Gini gain:

```text
Gini Gain = Gini(parent) - Gini_split
```

Ý nghĩa:

- Gain càng cao thì split càng tốt.
- Decision Tree chọn feature và threshold có Gini Gain cao nhất.

## 14. Feature Encoding

Feature encoding là bước biến traffic raw thành vector số để model có thể học.

Trong project:

```text
Raw traffic/flow
-> extract feature
-> clean numeric value
-> encode label
-> train model
```

Ví dụ feature:

- `destination_port`
- `flow_packets_persecond`
- `packet_length_mean`
- `bwd_packet_length_mean`
- `flow_iat_std`
- `fwd_iat_std`
- `bwd_packet_length_std`

Label encoding:

```text
BENIGN -> 0
DoS/DDoS attack -> 1
```

Xử lý numeric:

- Chuyển feature về dạng số.
- Thay `inf`, `-inf`, `NaN` bằng giá trị hợp lệ.
- Clip giá trị quá lớn để tránh outlier làm lệch model.

## 15. Feature Encoding Trong Data Plane

Trong switch/P4, không thể xử lý ML nặng như server.

Vì vậy các feature được dùng theo kiểu đơn giản:

```text
feature value <= threshold ?
```

Mỗi threshold tạo ra một vùng giá trị.

Ví dụ có 2 threshold:

```text
t1 = 100
t2 = 500
```

Thì feature có thể được chia thành 3 vùng:

```text
value <= 100
100 < value <= 500
value > 500
```

Ý nghĩa:

- DT thường có nhiều threshold riêng lẻ.
- DT-CTS giới hạn số threshold mỗi feature.
- Nhiều node có thể tái sử dụng cùng một tập threshold.
- Do đó DT-CTS nhẹ hơn và phù hợp hơn với data plane.

## 16. Vì Sao DT-CTS Phù Hợp SISTAR

Decision Tree:

- Dễ hiểu.
- Dễ chuyển thành rule.
- Nhưng có thể tạo nhiều threshold.

Random Forest:

- Accuracy/F1 tốt.
- Nhưng nhiều cây nên threshold/rule rất lớn.
- Khó triển khai trực tiếp trên switch.

DT-CTS:

- Giữ cấu trúc cây quyết định.
- Giới hạn threshold mỗi feature.
- Giảm footprint.
- Vẫn giữ F1 gần Decision Tree.

Kết quả 7 features hiện tại:

```text
DT:
- F1 = 0.9665
- threshold = 34

DT-CTS:
- F1 = 0.9614
- threshold = 14
```

Kết luận nên nói khi thuyết trình:

```text
DT-CTS hy sinh một phần rất nhỏ F1,
nhưng giảm hơn một nửa số threshold,
nên phù hợp hơn để đưa vào programmable data plane.
```

## 17. Các Feature Được Sử Dụng Trong Code

Trong benchmark hiện tại, code dùng 3 bộ feature: 3 features, 5 features và 7 features.

Bộ 3 features:

```text
destination_port
flow_packets_persecond
packet_length_mean
```

Bộ 5 features:

```text
destination_port
flow_packets_persecond
packet_length_mean
bwd_packet_length_mean
flow_iat_std
```

Bộ 7 features:

```text
destination_port
flow_packets_persecond
packet_length_mean
bwd_packet_length_mean
flow_iat_std
fwd_iat_std
bwd_packet_length_std
```

Ý nghĩa từng feature:

- `destination_port`: cổng đích của flow.
- `flow_packets_persecond`: số packet mỗi giây trong flow.
- `packet_length_mean`: độ dài packet trung bình.
- `bwd_packet_length_mean`: độ dài packet trung bình ở chiều backward.
- `flow_iat_std`: độ lệch chuẩn thời gian giữa các packet trong toàn flow.
- `fwd_iat_std`: độ lệch chuẩn thời gian giữa các packet ở chiều forward.
- `bwd_packet_length_std`: độ lệch chuẩn độ dài packet ở chiều backward.

Ý nghĩa chung:

- Các feature này mô tả hành vi lưu lượng mạng.
- DDoS thường làm thay đổi tốc độ packet, kích thước packet và mẫu thời gian giữa các packet.
- Vì vậy các feature này giúp model phân biệt benign traffic và attack traffic.

## 18. Giải Thích Sơ Đồ Overview of SISTAR

Sơ đồ overview của SISTAR mô tả cách hệ thống phát hiện và giảm thiểu DDoS ngay trong mạng.

Ý chính:

```text
Traffic đi vào mạng
-> switch quan sát và trích xuất feature
-> model phân loại benign/attack
-> nếu là attack thì chặn hoặc pushback
```

Các thành phần chính:

- `Programmable switch`: xử lý packet/flow ở data plane.
- `Feature extraction`: lấy các đặc trưng như packet rate, packet length, destination port.
- `ML model`: dùng DT/DT-CTS để phân loại traffic.
- `Controller`: điều phối, nhận cảnh báo và cài rule xuống switch.
- `Pushback`: đẩy rule chặn về switch upstream, gần nguồn tấn công hơn.

Luồng hoạt động ngắn gọn:

```text
1. Traffic từ nhiều source đi vào hệ thống.
2. Switch đọc thông tin packet/flow.
3. Switch hoặc controller tính feature.
4. Model dự đoán flow là benign hay attack.
5. Nếu benign: forward bình thường.
6. Nếu attack: drop/block traffic.
7. Controller có thể cài rule pushback ở switch gần source hơn.
```

Điểm quan trọng của SISTAR:

- Không chờ traffic đi tới victim rồi mới xử lý.
- Phát hiện sớm hơn ở trong mạng.
- Giảm tải cho victim và các link phía sau.
- Dùng model nhẹ để phù hợp với giới hạn tài nguyên của switch.

Câu nói ngắn khi thuyết trình:

```text
SISTAR đưa việc phát hiện DDoS xuống programmable data plane.
Switch không chỉ forward packet mà còn hỗ trợ phân loại traffic,
sau đó controller có thể cài rule để chặn hoặc pushback attack traffic.
```

## 19. Cải Tiến Hierarchical Confidence-Aware Pushback

Trong phần improvement, project dùng `hierarchical_confidence_pushback` làm cơ chế cải tiến chính.

Mục tiêu:

```text
Giảm chặn nhầm benign traffic,
nhưng vẫn giữ khả năng phát hiện sớm và giảm tải trên toàn tuyến mạng.
```

Có thể phân biệt 3 cơ chế như sau:

| Cơ chế | Ý tưởng | Ưu điểm | Nhược điểm |
|---|---|---|---|
| `no_pushback` | Không chặn upstream, chỉ để traffic đi qua | Không chặn nhầm benign | Attack vẫn tới victim nhiều |
| `immediate_pushback` | Phát hiện malicious 1 lần là block source ngay | Chặn attack nhanh | Dễ chặn nhầm nếu model false positive |
| `hierarchical_confidence_pushback` | Tích lũy suspicion score và leo thang theo mức | Giảm chặn nhầm benign, vẫn phản ứng sớm | Logic phức tạp hơn |

Trong paper/reproduction gốc, cơ chế pushback theo kiểu trực tiếp:

```text
Nếu source bị phát hiện attack
=> block/pushback ngay.
```

Cải tiến `hierarchical_confidence_pushback` thay đổi hoàn toàn cách mitigation:

```text
Edge switch phát hiện sớm -> cộng ít điểm nghi ngờ
Core switch xác nhận sâu hơn -> cộng nhiều điểm hơn
Traffic spike mạnh -> cộng thêm điểm
```

Khi score vượt các ngưỡng:

```text
Mức 1: monitor
Mức 2: local rate-limit
Mức 3: upstream pushback
Mức 4: hard block
```

Vì sao cần cơ chế này?

- Model ML có thể có false positive.
- Nếu block ngay sau 1 lần dự đoán attack, benign source có thể bị chặn nhầm.
- Nếu chỉ dùng một ngưỡng cứng kiểu fixed gate thì cải tiến vẫn còn khá nhỏ.
- Hierarchical Confidence-Aware Pushback biến mitigation thành một cơ chế phối hợp nhiều switch và nhiều mức phản ứng.

Kết quả mô phỏng hiện tại:

```text
No pushback:
- attack reduction: 0.00%
- false block events: 0

Immediate pushback:
- attack bytes tới victim: 0
- false block events: 11

Hierarchical Confidence-Aware Pushback:
- attack bytes tới victim: 4,591
- false block events: 0
- local rate-limit events: 23
- upstream pushback events: 10
- hard block events: 8
```

Nhận xét:

- `immediate_pushback` giảm attack mạnh nhất nhưng có 11 lần chặn nhầm.
- `hierarchical_confidence_pushback` vẫn giữ attack bytes tới victim ở mức rất thấp.
- Đồng thời nó giảm false block từ 11 xuống 0.
- Cơ chế mới còn cho thấy hệ thống đã thực sự đi qua các mức `rate-limit`, `pushback`, rồi mới `hard block`.

Câu nói ngắn khi thuyết trình:

```text
Hierarchical Confidence-Aware Pushback là cải tiến giúp hệ thống không block source quá vội.
Thay vì chặn ngay hoặc chỉ thêm một gate đơn giản,
nó tích lũy suspicion score từ nhiều switch rồi mới leo thang phản ứng.
Kết quả là attack vẫn bị giảm rất mạnh,
nhưng false block được loại bỏ trong mô phỏng của project.
```
