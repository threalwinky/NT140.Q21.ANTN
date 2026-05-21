# Master Prompt - Tạo Slide PPTX Báo Cáo SISTAR Reproduction

## Vai trò của agent

Bạn là một chuyên gia thiết kế PowerPoint, giảng viên an toàn mạng và người kể chuyện kỹ thuật. Hãy tạo một file `.pptx` báo cáo đồ án bằng tiếng Việt cho project reproduction paper:

**SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes**

Slide dùng để báo cáo với thầy/cô trong đồ án môn học. Người nghe có thể chưa biết nhiều về mạng máy tính, DDoS, programmable switch hoặc machine learning, nên nội dung phải dễ hiểu, trực quan và có mạch kể chuyện rõ ràng.

## Mục tiêu chính

Tạo bộ slide giúp người nghe hiểu được:

1. DDoS là gì và vì sao khó chống.
2. Paper SISTAR giải quyết vấn đề bằng cách đưa phát hiện DDoS vào programmable data plane.
3. DT, RF, DT-CTS là gì và vì sao DT-CTS phù hợp hơn với switch.
4. Project này tái hiện rút gọn các ý tưởng chính của SISTAR.
5. Kết quả reproduction: phân loại, độ phức tạp model, latency, pushback.
6. Phần cải tiến của project: **gated pushback** giúp giảm false block so với immediate pushback.
7. Phạm vi và giới hạn: đây là reduced reproduction + improvement, không phải triển khai đầy đủ 100% như paper trên production network.

## Yêu cầu output

Tạo file PowerPoint `.pptx` hoàn chỉnh, gồm khoảng **22-24 slide**.

Mỗi slide phải có:

- Tiêu đề rõ ràng.
- Nội dung ngắn gọn, không quá nhiều chữ.
- Visual chính: diagram, chart, timeline, icon hoặc hình minh họa.
- Speaker notes 3-5 câu để người trình bày biết cần nói gì.
- Layout đẹp, thống nhất, dễ nhìn.

Nếu công cụ không thể xuất trực tiếp `.pptx`, hãy tạo nội dung theo format dễ chuyển sang PowerPoint, nhưng vẫn phải mô tả đầy đủ layout, visual, speaker notes và asset cần dùng.

## Nguyên tắc quan trọng về nội dung

Không được nói quá phạm vi project.

Dùng cách diễn đạt đúng:

> Project tái hiện các ý tưởng chính của SISTAR ở mức reduced reproduction, gồm ML evaluation, pushback simulation, BMv2/P4 lab và phần cải tiến gated pushback.

Không được viết:

> Project đã implement hoàn toàn SISTAR giống paper trên hệ thống production.

Phải phân biệt rõ:

- **Paper gốc**: SISTAR dùng programmable data plane để phát hiện và giảm thiểu DDoS bằng lightweight ML và pushback.
- **Project reproduction**: train/evaluate DT, RF, DT-CTS; đo metric; mô phỏng pushback; có BMv2/P4 lab.
- **Phần cải tiến**: `gated_pushback` chỉ block sau 2 lần malicious liên tiếp để giảm chặn nhầm benign traffic.

## Nguồn nội dung cần đọc trong project

Trước khi tạo slide, hãy đọc các file sau nếu có quyền truy cập:

- `README.md`
- `paper-summary.md`
- `presentation.md`
- `working.md`
- `reproduction/src/`
- `reproduction/output/classification_metrics.csv`
- `reproduction/output/threshold_metrics.csv`
- `reproduction/output/benchmark_metrics.csv`
- `reproduction/output/pushback_metrics.csv`
- `reproduction/output/multi_dataset_validation.csv`
- `reproduction/output/summary.md`
- `reproduction/improvement/README.md`
- `reproduction/improvement/run_gated_improvement.py`
- `reproduction/improvement/report_utils_improvement.py`

Có thể dùng hình/charts có sẵn nếu tồn tại:

- `reproduction/output/classification_f1.png`
- `reproduction/output/classification_accuracy.png`
- `reproduction/output/classification_metric_suite.png`
- `reproduction/output/threshold_usage.png`
- `reproduction/output/thresholds_by_feature.png`
- `reproduction/output/benchmark_latency.png`
- `reproduction/output/benchmark_false_rates.png`
- `reproduction/output/benchmark_rules.png`
- `reproduction/output/pushback_policy_summary.png`
- `reproduction/output/pushback_attack_bytes.png`
- `reproduction/output/reproduction_dashboard.png`
- `reproduction/improvement/output/gated_improvement_dashboard.png`
- `reproduction/improvement/output/teacher_policy_comparison.png`
- `reproduction/improvement/output/teacher_attack_timeline.png`

Nếu ảnh không tồn tại, hãy tự dựng chart từ số liệu được cung cấp bên dưới.

## Số liệu chính cần đưa vào slide

### Classification metrics

| Model | Accuracy | F1 |
|---|---:|---:|
| DT | 0.9864 | 0.9864 |
| RF | 0.9712 | 0.9712 |
| DT-CTS | 0.9568 | 0.9574 |

Thông điệp:

- DT có F1 cao nhất trong reproduction.
- DT-CTS thấp hơn một chút nhưng nhẹ hơn đáng kể.
- Với programmable switch, độ gọn của model rất quan trọng.

### Threshold/rule complexity

| Model | Rules | Thresholds |
|---|---:|---:|
| DT | 31 | 30 |
| RF | - | 166 |
| DT-CTS | 14 | 13 |

Thông điệp:

- DT-CTS giảm mạnh số threshold so với DT/RF.
- Ít threshold/rule hơn nghĩa là dễ map sang match-action table hơn.
- Đây là lý do DT-CTS phù hợp hơn cho data plane.

### Latency

- DT mean latency khoảng `0.029 ms`.
- RF mean latency khoảng `0.246 ms`.
- DT-CTS mean latency khoảng `0.0012 ms`.

Thông điệp:

- DT-CTS có inference latency rất thấp trong reproduction.
- Model nhỏ/gọn phù hợp với tư duy xử lý nhanh trong switch.

### Pushback simulation

| Policy | Attack bytes tới victim | Benign bytes giữ lại | False block |
|---|---:|---:|---:|
| no_pushback | 2,938,459 | 392,296,909 | 0 |
| immediate_pushback | 351 | 102,678,554 | 21 |
| gated_pushback | 64,791 | 305,761,878 | 2 |

Thông điệp:

- `no_pushback`: attack tới victim nhiều nhất.
- `immediate_pushback`: giảm attack mạnh nhất nhưng false block cao.
- `gated_pushback`: vẫn giảm attack rất mạnh, nhưng giữ benign traffic tốt hơn và chỉ có 2 false block.

### Gated pushback improvement

Cơ chế:

```text
Lần 1 bị nghi ngờ malicious  -> ghi nhận, chưa block
Lần 2 liên tiếp vẫn malicious -> mới block source upstream
```

Thông điệp trình bày:

> Immediate pushback giống như thấy nghi ngờ là khóa ngay. Gated pushback giống như cần xác nhận thêm một lần để tránh khóa nhầm người dùng bình thường.

## Phong cách thiết kế tổng thể

### Tư duy thiết kế

Ưu tiên **visual-first**:

- 60-70% diện tích slide nên dành cho hình ảnh, diagram, chart hoặc khoảng trắng.
- 30-40% diện tích còn lại dành cho text ngắn.
- Không biến slide thành tài liệu đọc.
- Slide chỉ nên là “gợi ý thị giác”; phần giải thích nằm trong speaker notes.

Mỗi slide nên trả lời một câu hỏi duy nhất, ví dụ:

- DDoS là gì?
- Vì sao xử lý ở server là muộn?
- SISTAR đưa detection vào switch như thế nào?
- DT-CTS giảm độ phức tạp ra sao?
- Gated pushback cải tiến điểm gì?

### Quy tắc ít chữ

- Mỗi slide tối đa 3-5 bullet.
- Mỗi bullet tối đa 8-12 từ.
- Tránh câu dài.
- Tránh đoạn văn trên slide.
- Ưu tiên keyword + số liệu + visual.
- Nếu cần giải thích dài, đưa vào speaker notes.

Ví dụ tốt:

```text
DT-CTS
- F1: 0.9574
- 14 rules
- 13 thresholds
- Latency: 0.0012 ms
```

Ví dụ không tốt:

```text
DT-CTS là một mô hình cây quyết định được giới hạn số lượng threshold trên từng feature để giảm độ phức tạp khi triển khai lên programmable switch trong data plane...
```

### Bố cục slide đề xuất

Dùng các layout sau luân phiên để tránh nhàm chán:

1. **Hero visual slide**
   - Một hình lớn ở giữa.
   - 1 câu headline ngắn.
   - Dùng cho mở đầu, DDoS, conclusion.

2. **Two-column comparison**
   - Trái: cách cũ / vấn đề.
   - Phải: SISTAR / giải pháp.
   - Dùng màu đỏ-cam cho vấn đề, xanh cho giải pháp.

3. **Pipeline diagram**
   - Các bước nối bằng mũi tên.
   - Dùng cho reproduction pipeline, packet processing, pushback.

4. **Metric card layout**
   - 3-4 thẻ số liệu lớn.
   - Mỗi thẻ gồm metric lớn + caption ngắn.
   - Dùng cho kết quả chính.

5. **Chart-focused slide**
   - Chart chiếm 70% slide.
   - Text chỉ là 2-3 insight bên cạnh.

6. **Timeline / state machine**
   - Dùng cho gated pushback.
   - Hiển thị suspicious lần 1, confirm lần 2, block.

7. **Architecture diagram**
   - Dùng cho data plane/control plane, programmable switch, BMv2 lab.

### Design system

Màu chính:

- Deep Navy `#1E3A5F`: title, header, network nodes.
- Cyan `#00BCD4`: data flow, arrows, highlight technical concept.
- Coral `#FF6B6B`: attack, warning, problem.
- Green `#4CAF50`: mitigation, benign traffic, improvement.
- Light Background `#F5F7FA`: nền sáng.
- Dark Text `#2C3E50`: text chính.
- Muted Gray `#6B7280`: caption, phụ chú.

Quy tắc dùng màu:

- Attack/DDoS: đỏ/cam.
- Benign traffic: xanh lá.
- SISTAR/data plane: xanh đậm/cyan.
- Baseline/no pushback: xám hoặc nâu nhạt.
- Không dùng quá 3 màu nổi trên cùng một slide.

Font:

- Title: Segoe UI Semibold, Arial, Calibri hoặc Roboto.
- Body: Segoe UI, Arial hoặc Calibri.
- Code/technical labels: Consolas hoặc monospace.
- Font size gợi ý:
  - Title: 32-40 pt.
  - Subtitle: 20-24 pt.
  - Bullet: 18-22 pt.
  - Caption: 11-13 pt.
  - Metric number: 36-56 pt.

Hiệu ứng thị giác:

- Nền sáng, có thể thêm pattern mạng rất nhẹ 3-5% opacity.
- Dùng rounded rectangle cho card.
- Dùng shadow nhẹ, không quá đậm.
- Dùng line icon đơn giản: server, switch, shield, tree, chart, warning, user.
- Không dùng quá nhiều emoji.
- Không dùng clipart rối.
- Không dùng ảnh nền làm giảm độ đọc.

### UI slide đẹp mắt

Mỗi slide nên có:

- Header nhỏ nhất quán: tên section hoặc số slide.
- Tiêu đề lớn, dễ đọc.
- Một visual chính rõ ràng.
- Khoảng trắng đủ rộng.
- Caption ngắn dưới chart/hình.
- Highlight số liệu quan trọng bằng metric card hoặc callout.

Ví dụ layout đẹp cho slide kết quả:

```text
+------------------------------------------------+
| Kết quả Pushback                               |
|                                                |
|  [Bar chart lớn: attack bytes by policy]       |
|                                                |
|  Insight cards:                                |
|  [97.8% giảm attack] [2 false blocks]          |
|                                                |
|  Caption: Gated cân bằng giữa giảm attack      |
|  và hạn chế chặn nhầm benign traffic.          |
+------------------------------------------------+
```

Ví dụ layout đẹp cho slide gated pushback:

```text
+------------------------------------------------+
| Cải tiến: Gated Pushback                       |
|                                                |
|  Suspicious lần 1  ->  Theo dõi tiếp           |
|       màu vàng             màu xám             |
|                                                |
|  Suspicious lần 2  ->  Block upstream          |
|       màu cam              màu xanh lá         |
|                                                |
|  Callout: giảm false block từ 21 xuống 2       |
+------------------------------------------------+
```

## Cấu trúc slide đề xuất

### Slide 1 - Title

Nội dung trên slide:

- SISTAR Reproduction & Gated Pushback Improvement
- Phát hiện và giảm thiểu DDoS bằng programmable data plane
- Tên sinh viên/nhóm/lớp

Visual:

- Network topology abstract: nhiều attacker đỏ, switch xanh, victim server.
- Nền xanh đậm hoặc gradient xanh nhẹ.

Speaker notes:

- Giới thiệu đề tài và paper SISTAR.
- Nói rõ đây là reproduction rút gọn kèm cải tiến gated pushback.
- Dẫn vào câu hỏi: làm sao phát hiện DDoS sớm hơn, ngay trong mạng?

### Slide 2 - DDoS là gì?

Nội dung:

- Nhiều nguồn gửi traffic cùng lúc.
- Server bị quá tải.
- Người dùng thật không truy cập được.

Visual:

- Diagram: nhiều attacker -> traffic đỏ -> server nghẽn.
- Có thể dùng ẩn dụ “kẹt xe trước cổng server”.

Speaker notes:

- Giải thích DDoS bằng ví dụ đời thường.
- Nhấn mạnh mục tiêu là làm dịch vụ không phục vụ được người dùng thật.

### Slide 3 - Vì sao chống DDoS khó?

Nội dung:

- Traffic đến rất nhanh.
- Phát hiện ở server là quá muộn.
- Mạng bị tốn băng thông.

Visual:

- Timeline: attacker -> network -> server -> detection muộn.
- Đánh dấu “too late” ở gần server.

Speaker notes:

- Giải thích nếu để traffic tới server rồi mới phân tích thì mạng đã chịu tải.
- Đây là động lực để paper xử lý sớm hơn trong switch.

### Slide 4 - Ý tưởng chính của SISTAR

Nội dung:

- Detect ngay trong switch.
- Dùng lightweight ML.
- Pushback để chặn gần nguồn.

Visual:

- 3 card lớn: In-switch detection, Lightweight ML, Pushback.
- Mũi tên nối 3 card.

Speaker notes:

- SISTAR đưa logic phát hiện xuống data plane.
- Model phải nhẹ vì switch có tài nguyên hạn chế.
- Pushback giúp chặn traffic ở upstream switch.

### Slide 5 - Data plane và control plane

Nội dung:

- Control plane: cấu hình, điều khiển.
- Data plane: xử lý packet cực nhanh.
- SISTAR xử lý ngay ở data plane.

Visual:

- Diagram 2 tầng: control plane phía trên, data plane phía dưới.
- Packet chạy qua data plane.

Speaker notes:

- Giải thích switch có phần điều khiển và phần xử lý gói tin.
- SISTAR tận dụng programmable data plane để xử lý attack sớm.

### Slide 6 - Programmable switch / P4

Nội dung:

- Switch có thể lập trình logic packet.
- Parser đọc header.
- Match-action table quyết định forward/drop.

Visual:

- Packet -> Parser -> Feature extraction -> Match-action table -> Forward/Drop.

Speaker notes:

- P4 cho phép mô tả switch xử lý packet như thế nào.
- Đây là nền tảng để biến model nhẹ thành rule trong switch.

### Slide 7 - Flow và feature

Nội dung:

- Flow = nhóm packet cùng hành vi.
- Feature mô tả traffic.
- Model dùng feature để phân loại.

Visual:

- Nhiều packet gom thành một flow card.
- Từ flow tách ra 5 feature.

Speaker notes:

- Giải thích flow đơn giản là một luồng traffic.
- Thay vì nhìn từng packet rời rạc, hệ thống nhìn đặc trưng hành vi của flow.

### Slide 8 - Feature trong reproduction

Nội dung:

- protocol
- init_win_bytes_forward
- fwd_header_length
- packet_length_mean
- flow_packets_persecond

Visual:

- Bảng 5 hàng, mỗi hàng có icon nhỏ và mô tả rất ngắn.
- Ví dụ: packet rate, kích thước packet, header length.

Speaker notes:

- Đây là 5 feature được dùng trong reproduction.
- Chúng thể hiện hành vi traffic, ví dụ tốc độ gói tin hoặc kích thước packet.

### Slide 9 - Machine Learning trong SISTAR

Nội dung:

- Input: flow features.
- Output: benign hoặc attack.
- Model cần nhỏ và nhanh.

Visual:

- Flow features -> ML model -> benign/attack.
- Benign màu xanh, attack màu đỏ.

Speaker notes:

- Mục tiêu của model là phân loại traffic.
- Tuy nhiên trong switch, model không được quá phức tạp.

### Slide 10 - Decision Tree dễ hiểu

Nội dung:

- Giống chuỗi câu hỏi Có/Không.
- Dễ chuyển thành luật if-else.
- Phù hợp hơn deep model lớn.

Visual:

- Cây quyết định nhỏ 3-5 node.
- Lá xanh là benign, lá đỏ là attack.

Speaker notes:

- Decision Tree dễ giải thích vì mỗi node là một điều kiện.
- Điều này phù hợp với match-action rule trong switch.

### Slide 11 - Vì sao cần DT-CTS?

Nội dung:

- Switch có tài nguyên giới hạn.
- Nhiều threshold gây tốn rule.
- DT-CTS giảm số threshold.

Visual:

- Cân bằng Accuracy vs Deployability.
- Một cây lớn được rút gọn thành cây nhỏ.

Speaker notes:

- Model chính xác nhưng quá lớn có thể không triển khai được.
- DT-CTS chấp nhận giảm nhẹ accuracy để đổi lấy model gọn hơn.

### Slide 12 - Reproduction pipeline

Nội dung:

- Load dataset.
- Train DT/RF/DT-CTS.
- Evaluate + simulate pushback.

Visual:

- Pipeline: Dataset -> Training -> Metrics -> Pushback simulation -> Report.

Speaker notes:

- Slide này mô tả project đã làm gì.
- Đây là reduced reproduction, tập trung vào ý tưởng chính và số liệu so sánh.

### Slide 13 - Dataset và phạm vi

Nội dung:

- CICIDS2017 DoS-Wednesday.
- Có synthetic fallback.
- Reduced reproduction, không phải production.

Visual:

- Dataset card + scope badge.
- Có nhãn “reduced reproduction”.

Speaker notes:

- Dataset chính là CICIDS2017 nếu có sẵn.
- Project cũng có fallback synthetic để chạy được trong môi trường thiếu dữ liệu.
- Cần nói rõ phạm vi để tránh hiểu nhầm là triển khai full như paper.

### Slide 14 - Kết quả phân loại

Nội dung:

- DT F1: 0.9864.
- RF F1: 0.9712.
- DT-CTS F1: 0.9574.

Visual:

- Bar chart F1 chiếm phần lớn slide.
- Callout: “DT-CTS thấp hơn nhẹ nhưng gọn hơn”.

Speaker notes:

- DT đạt F1 cao nhất.
- DT-CTS giảm nhẹ F1 nhưng mục tiêu của nó là deployability.

### Slide 15 - Độ phức tạp model

Nội dung:

- DT: 31 rules / 30 thresholds.
- RF: 166 thresholds.
- DT-CTS: 14 rules / 13 thresholds.

Visual:

- Bar chart threshold count.
- Mũi tên giảm từ DT sang DT-CTS.

Speaker notes:

- Đây là điểm quan trọng nhất của DT-CTS.
- Ít threshold hơn giúp dễ đưa logic vào switch hơn.

### Slide 16 - Latency

Nội dung:

- DT: khoảng 0.029 ms.
- RF: khoảng 0.246 ms.
- DT-CTS: khoảng 0.0012 ms.

Visual:

- Bar chart latency.
- DT-CTS được highlight màu xanh lá.

Speaker notes:

- DT-CTS có latency rất thấp trong reproduction.
- Điều này phù hợp với yêu cầu xử lý nhanh ở data plane.

### Slide 17 - Pushback trong paper

Nội dung:

- Không chỉ drop local.
- Báo upstream switch.
- Chặn gần nguồn attack hơn.

Visual:

- Attacker -> switch 1 -> switch 2 -> victim.
- Pushback arrow đi ngược về upstream.

Speaker notes:

- Pushback là cơ chế khi phát hiện attack thì báo switch phía trước.
- Mục tiêu là ngăn traffic càng gần nguồn càng tốt.

### Slide 18 - Ba policy pushback

Nội dung:

- no_pushback: không chặn sớm.
- immediate: phát hiện là chặn ngay.
- gated: cần xác nhận 2 lần.

Visual:

- 3 card policy đặt cạnh nhau.
- Mỗi card có icon trạng thái và màu riêng.

Speaker notes:

- Slide này chuẩn bị cho phần so sánh kết quả.
- Immediate mạnh nhưng có nguy cơ chặn nhầm.
- Gated thận trọng hơn.

### Slide 19 - Vấn đề của immediate pushback

Nội dung:

- Chặn rất nhanh.
- Nhưng false positive gây block nhầm.
- Benign traffic bị ảnh hưởng.

Visual:

- User bình thường bị chặn bởi barrier đỏ.
- Callout: “false block = chặn nhầm”.

Speaker notes:

- Nếu model dự đoán sai, immediate pushback có thể chặn nguồn hợp lệ.
- Đây là lý do project đề xuất gated pushback.

### Slide 20 - Cải tiến gated pushback

Nội dung:

- Lần 1: nghi ngờ, chưa block.
- Lần 2 liên tiếp: mới block.
- Mục tiêu: giảm false block.

Visual:

- Timeline/state machine lớn:
  - Normal -> Suspicious -> Confirmed malicious -> Block upstream.
- Dùng màu vàng, cam, xanh lá.

Speaker notes:

- Gated pushback cần thêm một lần xác nhận.
- Cách này giống như không khóa tài khoản ngay khi có một dấu hiệu nghi ngờ.
- Nó làm giảm rủi ro chặn nhầm benign traffic.

### Slide 21 - So sánh pushback

Nội dung:

- no_pushback: attack 2.94M bytes.
- immediate: false block 21.
- gated: false block 2, benign giữ tốt hơn.

Visual:

- 3 chart nhỏ hoặc 1 dashboard:
  - attack bytes tới victim.
  - benign bytes preserved.
  - false block events.
- Nếu có, dùng `pushback_policy_summary.png` hoặc `teacher_policy_comparison.png`.

Speaker notes:

- Immediate giảm attack mạnh nhất nhưng false block cao.
- Gated vẫn giảm attack rất mạnh và giảm false block từ 21 xuống 2.
- Gated giữ lại nhiều benign traffic hơn immediate.

### Slide 22 - BMv2/P4 lab

Nội dung:

- Có P4/BMv2 lab minh họa data plane.
- Topology Mininet 3 switches.
- Dùng để demo hướng triển khai.

Visual:

- Topology đơn giản: h1/h2 -> s1/s2 -> s3 -> h3.
- Gắn nhãn attacker, benign host, victim.

Speaker notes:

- Ngoài pipeline Python, project có phần lab BMv2/P4.
- Lab này giúp minh họa ý tưởng programmable data plane trong môi trường thử nghiệm.
- Đây vẫn là lab, không phải mạng production thật.

### Slide 23 - Giới hạn

Nội dung:

- Reduced reproduction.
- Pushback là mô phỏng flow-level.
- Lab BMv2/Mininet không phải production.
- Resource thật trên switch chưa đo đầy đủ.

Visual:

- 4 limitation cards, màu xám/cam nhẹ.

Speaker notes:

- Trình bày trung thực giới hạn của project.
- Tuy vậy project vẫn tái hiện được logic chính của paper và có cải tiến riêng.

### Slide 24 - Kết luận / Q&A

Nội dung:

- SISTAR: detect sớm trong switch.
- DT-CTS: model gọn, latency thấp.
- Gated pushback: giảm chặn nhầm.
- Cảm ơn thầy/cô.

Visual:

- 3 takeaway cards + Q&A.
- Nền sạch, ít chữ.

Speaker notes:

- Tóm tắt lại 3 ý chính.
- Nhấn mạnh project vừa reproduction vừa có improvement.
- Mời thầy/cô đặt câu hỏi.

## Speaker notes requirements

Speaker notes phải:

- Viết bằng tiếng Việt tự nhiên.
- Không đọc lại y nguyên bullet.
- Mỗi slide 3-5 câu.
- Giải thích thuật ngữ khó bằng ví dụ đơn giản.
- Nhấn mạnh “ý nghĩa” của chart, không chỉ đọc số.
- Với gated pushback, phải giải thích rõ trade-off giữa giảm attack và tránh chặn nhầm.

Ví dụ speaker note tốt:

```text
Ở đây, immediate pushback gần như chặn attack ngay lập tức, nên attack bytes tới victim rất thấp. Tuy nhiên, nhược điểm là nếu model dự đoán sai, nguồn benign cũng có thể bị block. Gated pushback chấp nhận để lọt thêm một ít attack ban đầu, nhưng đổi lại giảm false block rất nhiều và giữ benign traffic tốt hơn.
```

## Checklist chất lượng trước khi xuất file

Trước khi hoàn thành, tự kiểm tra:

- Slide có ít chữ không?
- Mỗi slide có visual chính chưa?
- Người không biết mạng có hiểu được không?
- Có phân biệt paper gốc, reproduction và improvement không?
- Có nói rõ project là reduced reproduction không?
- Có đưa đúng số liệu gated pushback không?
- Gated pushback có được giải thích bằng timeline dễ hiểu không?
- Chart có caption và insight không?
- Màu sắc có nhất quán không?
- Speaker notes có đủ để thuyết trình không?

## Tiêu chí đánh giá bộ slide

Bộ slide đạt yêu cầu nếu:

- Người nghe hiểu DDoS là gì trong 2 phút đầu.
- Người nghe hiểu vì sao phát hiện trong switch nhanh hơn.
- Người nghe hiểu DT-CTS giúp model nhỏ/gọn hơn.
- Người nghe hiểu pushback là chặn gần nguồn attack hơn.
- Người nghe hiểu gated pushback giảm false block so với immediate pushback.
- Slide nhìn chuyên nghiệp, hiện đại, ít chữ, nhiều hình.
- Có đủ số liệu để bảo vệ kết quả khi thầy/cô hỏi.
