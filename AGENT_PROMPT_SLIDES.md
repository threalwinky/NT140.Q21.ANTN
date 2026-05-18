# Master Prompt - Tạo Slide Trình Bày SISTAR Reproduction

## Role & Mục Tiêu
Bạn là một chuyên gia tạo slide trình bày kỹ thuật. Bạn cần tạo một bộ slide trình bày chi tiết về dự án SISTAR Reproduction, **dành cho người chưa bao giờ nghe qua dự án này**. Slide phải có mạch kể chuyện giống hệt file `presentation.md` đã cung cấp, từ mở đầu đến kết luận.

## Output Format
Xuất slide ở định dạng **Markdown**. Mỗi slide cách nhau bằng dòng `---`. Cấu trúc mỗi slide:
ss
```
---
Title: Tiêu đề slide
Content:
- Bullet 1 (≤ 12 từ)
- Bullet 2
- Bullet 3
SpeakerNotes: "Kịch bản nói 2-3 câu ngắn gọn, tự nhiên"
Assets: [file_ảnh_nếu_có.png] hoặc []
Icon: 🚀 (emoji icon)
Design: "Brief visual recommendation"
---
```

## Design & Visual Guidelines

### Color Scheme (Network-Inspired)
- **Primary**: Deep Blue (#1E3A5F) - Network nodes, headers, main elements
- **Secondary**: Cyan/Turquoise (#00BCD4) - Data flow, connections, active links
- **Accent**: Coral Orange (#FF6B6B) - Attack/warning signals, high-priority alerts
- **Success**: Soft Green (#4CAF50) - Mitigation success, positive outcomes
- **Background**: Light Gradient (#F5F7FA to #E8EFF5) - Subtle network pattern or grid
- **Text**: Dark Gray (#2C3E50) - Body text, high contrast
- **Text Light**: Gray (#666666) - Secondary text, speaker notes

### Typography (Vietnamese-Friendly)
**Font Family Recommendation:**
- **Tiêu đề**: **Segoe UI** (bold, 28-32px) hoặc **Roboto** (sans-serif, tốt cho Việt)
- **Bullets**: **Arial Unicode MS** hoặc **Segoe UI** (regular, 16-18px) - hỗ trợ dấu Việt tốt
- **Speaker notes**: *Tahoma* hoặc *Segoe UI* (italic, 14px)
- **Code/Technical**: `Consolas` hoặc `Monaco` (monospace, 12-14px)
- **Backup**: Nếu các font trên không có, dùng **Calibri** (tương thích tốt, có dấu)

**Font Sizing:**
- H1 (Slide Title): 32px bold, Primary Blue
- H2 (Section): 24px bold, Primary Blue
- Bullets: 16px regular, Dark Gray (max 7 bullets per slide)
- Caption: 12px light, Gray
- Speaker Notes: 14px italic, Gray

### Visual Elements & Icons (Network-Themed)
**Slide Icons (mỗi slide có icon riêng ở góc phải 20-24px):**
- Slide 1: 🚀 | Slide 2: 🛡️ | Slide 3: ⚠️ | Slide 4: ⚙️ | Slide 5: 💡
- Slide 6: ⚡ | Slide 7: 🌳 | Slide 8: 🔬 | Slide 9: 📊 | Slide 10: 🤖
- Slide 11: 📈 | Slide 11.5: 🌍 | Slide 12: 📉 | Slide 13: 🔄 | Slide 14: ✅
- Slide 15: ⭐ | Slide 16: 📋 | Slide 17: 🎯 | Slide 18: ❓ | Slide 19: 📚

### Decorative & Layout Elements
**Background Patterns:**
- Network pattern: Subtle lines/nodes in background (opacity 5-10%)
- Gradient: Top-to-bottom fade from light cyan to white
- Divider: `═══════════════════` (cyan/primary blue, thin opacity)
- Side accent: Vertical colored bar on left edge (2-3px, primary blue)

**Emphasis & Highlight:**
- **Key terms**: Bold in Primary Blue #1E3A5F
- *Important point*: Italics in Coral Orange #FF6B6B
- `Technical terms`: Monospace with light background #F0F4F8
- Highlight box: Border Cyan with light fill, rounded corners (8px)
- Number badge: Circle with number (20x20px) in corner, opacity 60%, Primary Blue

**Icons & Decorations:**
- **Bullet points**: Custom network node icon (instead of •)
- **Arrows**: `→` (right flow), `←` (left flow), `↑` (data up), `↓` (mitigation)
- **Emphasis**: ★ before important bullet
- **Connection lines**: Visual flow between concepts using `──` or `│`
- **Data packets**: Small circle icons 🔹 representing network packets

### Diagram & Visual Recommendations (Network Architecture Theme)

**Slide-by-Slide Visuals:**
- **Slide 1**: Header with ACM CCS logo + network topology background (subtle grid)
- **Slide 2**: Flow diagram [🛡️ Attackers] ──→ [📊 Many Requests] ──→ [⚠️ Overloaded Server] (network-style boxes)
- **Slide 3**: 2-column comparison with divider line: Left (Red/❌ Old Way), Right (Green/✅ SISTAR Way)
- **Slide 4**: Vertical stack boxes: [Control Plane - top] separated by thick line from [Data Plane - bottom]
- **Slide 5**: 3 connected boxes with arrows: [🎯 Detection in Switch] ──→ [🤖 Lightweight ML] ──→ [🔄 Pushback Mechanism]
- **Slide 6**: Balance scale icon with weights on each side (Accuracy ⚖️ Deployability)
- **Slide 7**: Simple binary tree diagram with colored branches (Blue → Cyan → Green leaves)
- **Slide 8**: Process flow 3 boxes left-to-right: [#1 ML] ──→ [#2 Compare] ──→ [#3 Simulate] with numbered badges
- **Slide 9**: Table with 5 feature rows, each with small icon and description
- **Slide 10**: 3 model comparison boxes with star complexity ratings (⭐ to ⭐⭐⭐)
- **Slide 11**: Bar chart comparing F1-scores, Primary Blue bars with trend arrow
- **Slide 11.5**: NEW - Table with 4 datasets and comparison metrics, with "✓ GOOD GENERALIZATION" badge
- **Slide 12**: Side-by-side comparison: DT (30 thresholds) vs DT-CTS (13 thresholds) with 57% reduction arrow
- **Slide 13**: Network topology: [🚨 Attacker] ──→ [S1] ──→ [S2] ──→ [👤 Victim], with pushback arrows going back
- **Slide 14**: Before/After chart showing attack bytes reduction (from tall bar to short bar) with ✅ checkmark
- **Slide 15**: Sequence timeline: Detection#1 (yellow) ──→ Detection#2 (orange) ──→ Pushback (green)
- **Slide 16**: Numbered list (①, ②, ③) of limitations with ⚠️ icons on left
- **Slide 17**: Summary: 3-4 colored boxes with main takeaways and star icons
- **Slide 18**: Large "Thank You" text centered, with contact info below
- **Slide 19**: NEW - References section formatted as clean list with links highlighted in cyan

### Layout Best Practices (Vietnamese-Optimized)
- **Title alignment**: Centered for emphasis, left-aligned for body slides
- **Whitespace**: Generous margins (40-50px sides, 30px top/bottom)
- **Line height**: 1.6-1.8 for Vietnamese text (better readability with diacritics)
- **Bullet indentation**: 24px from left edge, sub-bullets +12px further
- **Network elements**: Visual connectors between related concepts (thin cyan lines)
- **Color usage**: 60% background, 30% primary color, 10% accent/warning colors

### Animation Suggestions (for PowerPoint/Google Slides)
- **Fade-in**: Bullets appear one-by-one (0.4s delay between)
- **Entrance**: Icons slide in from right (0.3s)
- **Flow arrows**: Animate to show left-to-right data flow (0.5s)
- **Chart bars**: Grow from bottom-up (0.6s)
- **Transitions**: Fade between slides (0.5s), no distracting sounds
- **Emphasis**: Highlight key metrics with glow effect on click

### Vietnamese Text Guidelines
- ✅ Use proper diacritical marks (à, á, ả, ã, ạ, etc.)
- ✅ Keep sentences short for better readability (max 15 words per bullet)
- ✅ Use common terms, avoid overly technical jargon
- ✅ Numbers: use "2.500" (dot as thousand separator) or "2500"
- ✅ Percentages: "57%" hoặc "57 phần trăm"
- ✅ Currencies/metrics: "ms" (milliseconds), "%" (percent), "bytes"

---

## Nội Dung Bắt Buộc - 19 Slide Theo Thứ Tự Kịch Bản

### **Slide 1: Mở Đầu**
- Tiêu đề slide
- Greeting & giới thiệu đề tài
- Tên paper: SISTAR
- Câu hỏi trung tâm: "Làm sao phát hiện và giảm thiểu DDoS nhanh hơn, ngay trong mạng?"
- Speaker notes: "Chào thầy/cô và các bạn. Hôm nay em trình bày project tái hiện rút gọn paper SISTAR. Dự án này nghiên cứu câu hỏi: làm sao phát hiện tấn công DDoS nhanh hơn, ngay trong mạng, thay vì đợi traffic đi tới server rồi mới xử lý?"
- **Icon**: 🚀
- **Visual**: Header design với Primary Blue background, logo SISTAR hoặc ACM CCS 2025
- **Design**: "Opening slide - title prominent, gradient background"

### **Slide 2: DDoS Là Gì?**
- Giải thích DDoS = Distributed Denial of Service
- Attacker dùng nhiều nguồn gửi traffic tới cùng một hệ thống
- Mục tiêu: làm dịch vụ chậm, quá tải, hoặc sập
- Ví dụ: server xử lý X request/giây, nhưng attacker gửi hàng triệu request/giây
- Hệ thống chống DDoS cần: phát hiện + chặn
- Speaker notes: "DDoS viết tắt Distributed Denial of Service. Attacker dùng rất nhiều nguồn gửi traffic tới cùng một hệ thống. Mục tiêu không phải đánh cắp dữ liệu, mà là làm cho dịch vụ bị chậm hoặc sập. Vì vậy, hệ thống chống DDoS cần hai việc: phát hiện traffic nào là tấn công, và chặn hoặc giảm thiểu traffic đó."
- **Icon**: 🛡️
- **Visual**: Diagram [Multiple Attackers] → [Many Requests] → [Server Overload]
- **Design**: "Flow arrows left-to-right, attacker sources top-left with red highlight"

### **Slide 3: Vấn Đề của Cách Xử Lý Truyền Thống**
- Cách cũ: gửi traffic lên server/controller trung tâm để phân tích
- Vấn đề: phát hiện quá muộn, traffic xấu đã đi qua gần hết mạng
- Hậu quả: tốn băng thông, gây tải cho switch/router, vẫn áp lực lên server nạn nhân
- Giải pháp: đưa phát hiện DDoS xuống data plane
- Speaker notes: "Cách xử lý phổ biến hiện nay là đẩy traffic lên server hoặc controller trung tâm rồi mới phân tích. Nhưng có một vấn đề lớn: khi hệ thống phát hiện ra tấn công, traffic xấu đã đi qua gần hết mạng rồi. Điều đó tốn băng thông và gây tải lên các switch ở giữa. SISTAR giải quyết điều này bằng cách đưa phát hiện DDoS xuống data plane, ngay trong switch."
- **Icon**: ⚠️
- **Visual**: Two-column comparison: "Traditional (slow)" vs "SISTAR (fast)"
- **Design**: "Left side in red/coral for old approach, right side in cyan for new solution"

### **Slide 4: Data Plane và Programmable Switch Là Gì?**
- Switch: thiết bị chuyển tiếp packet trong mạng
- Control plane: cấu hình luật, chậm nhưng linh hoạt
- Data plane: xử lý packet theo luật đã cài sẵn, rất nhanh
- Programmable data plane: có thể lập trình để thêm logic tùy chỉnh
- Ví dụ: switch tự đọc thông tin packet, tính đặc trưng, so sánh với luật, quyết định
- Speaker notes: "Switch là thiết bị chuyển tiếp packet. Nó có hai phần: control plane điều khiển và cấu hình luật; data plane xử lý packet theo luật đã cài sẵn. Bình thường data plane chỉ làm những việc cơ bản. Nhưng với programmable data plane, ta có thể lập trình switch để tự phân tích traffic. Đây là điểm quan trọng của SISTAR."
- **Icon**: ⚙️
- **Visual**: Architecture box diagram with two sections: Control Plane (top) vs Data Plane (bottom)
- **Design**: "Stack boxes vertically, use darker blue for control, lighter cyan for data plane"

### **Slide 5: Ý Tưởng Chính của SISTAR**
- Ý 1: Phát hiện ngay trong switch, không gửi lên server → phản ứng nhanh
- Ý 2: Dùng mô hình ML nhẹ (Decision Tree, Random Forest, DT-CTS) → giống luật if-else
- Ý 3: Pushback - gửi cảnh báo cho switch upstream → chặn gần nguồn hơn
- Speaker notes: "SISTAR có ba ý chính. Thứ nhất, phát hiện DDoS ngay trong switch, không phải gửi lên server. Thứ hai, dùng mô hình ML nhẹ như Decision Tree, vì nó giống logic if-else và phù hợp với switch. Thứ ba, nếu phát hiện attack thì gửi cảnh báo cho switch ở phía trước để chặn traffic gần nguồn hơn. Đó gọi là pushback."
- **Icon**: 💡
- **Visual**: 3 boxes side-by-side with icons and labels
- **Design**: "Each box has different color: cyan, orange, turquoise; numbered 1, 2, 3"

### **Slide 6: Vấn Đề Kỹ Thuật - Mô Hình Phải Đủ Nhẹ**
- Switch có tài nguyên rất hạn chế so với server
- Không thể chạy deep learning lớn hoặc xử lý phức tạp
- Bài toán không chỉ là: mô hình có chính xác không?
- Mà còn là: mô hình có đủ nhẹ để triển khai trên switch không?
- Giải pháp: DT-CTS
- Speaker notes: "Vấn đề khó của bài toán là switch có tài nguyên rất hạn chế. Nó không giống server có CPU mạnh. Vì vậy, bài toán không chỉ là tìm mô hình chính xác, mà còn phải tìm mô hình đủ nhẹ để triển khai lên switch. Đây là lý do paper đưa ra DT-CTS."
- **Icon**: ⚡
- **Visual**: Balance scale diagram with Accuracy on left, Deployability on right
- **Design**: "Scale tilted showing trade-off, use contrasting colors for each side"

### **Slide 7: DT-CTS Là Gì?**
- DT-CTS = Decision Tree - Constrained Threshold Segmentation
- Threshold: ngưỡng so sánh (ví dụ: nếu flow_packets_persecond > 500)
- Cây thường: nhiều threshold → chính xác nhưng nặng
- DT-CTS: giảm số threshold → gọn hơn, dễ triển khai
- Trade-off: độ chính xác giảm nhẹ, nhưng mô hình phù hợp với switch
- Speaker notes: "DT-CTS viết tắt Decision Tree - Constrained Threshold Segmentation. Threshold là các ngưỡng so sánh, ví dụ nếu packets/giây > 500 thì nghi ngờ attack. Cây bình thường thích dùng nhiều threshold để tăng accuracy, nhưng DT-CTS ép mô hình giảm số threshold để gọn hơn. Đổi lại, accuracy có giảm nhẹ, nhưng mô hình phù hợp hơn với switch."
- **Icon**: 🌳
- **Visual**: Simple binary tree diagram with if-then-else branches, highlight reduced thresholds
- **Design**: "Tree nodes in blue, branches in cyan, leaf nodes in green/orange"

### **Slide 8: Project Của Em Làm Gì?**
- Không tái hiện trên phần cứng thật (Tofino, BMv2)
- Reproduction rút gọn tập trung 3 phần chính:
  1. Phát hiện DDoS bằng mô hình ML
  2. So sánh số threshold để đánh giá deployability
  3. Mô phỏng pushback để xem giảm attack bytes tới victim bao nhiêu
- Speaker notes: "Project này không tái hiện toàn bộ hệ thống trên phần cứng thật. Thay vào đó, project làm một bản reproduction rút gọn, tập trung vào 3 phần: phát hiện DDoS bằng mô hình, so sánh số threshold, và mô phỏng pushback."
- **Icon**: 🔬
- **Visual**: 3 boxes in sequence with arrows: [ML Training] → [Comparison] → [Simulation]
- **Design**: "Numbered badges 1, 2, 3 on top of boxes, arrows show flow left-to-right"

### **Slide 9: Dataset Dùng Trong Project**
- Dataset: CICIDS2017, cụ thể là tập DoS-Wednesday
- Dataset phổ biến để nghiên cứu DDoS detection
- Feature được trích xuất:
  - protocol
  - init_win_bytes_forward
  - fwd_header_length
  - packet_length_mean
  - flow_packets_persecond
- Ý nghĩa: các đặc trưng này đại diện hành vi traffic
- Speaker notes: "Project dùng dataset CICIDS2017, cụ thể là tập DoS-Wednesday. Đây là dataset phổ biến để nghiên cứu DDoS. Từ dataset, project lấy 5 feature: protocol, init window bytes, header length, packet length mean, flow packets per second. Các feature này giúp mô hình phân biệt traffic bình thường và attack."
- **Icon**: 📊
- **Visual**: Table showing 5 features with brief descriptions or icons
- **Design**: "Table with alternating row colors (white/light gray), feature names in bold"

### **Slide 10: Các Mô Hình Được So Sánh**
- Decision Tree (DT): baseline đơn giản, dễ hiểu, dễ triển khai
- Random Forest (RF): chính xác hơn DT, nhưng nặng hơn, khó triển khai
- DT-CTS: ít threshold hơn DT, cân bằng accuracy và deployability
- Speaker notes: "Project huấn luyện và so sánh 3 mô hình. Decision Tree là baseline đơn giản. Random Forest thường chính xác hơn nhưng nặng hơn. DT-CTS là mô hình quan trọng nhất, cố giảm threshold để dễ triển khai lên switch."
- **Icon**: 🤖
- **Visual**: 3 model boxes with complexity indicators (⭐ to ⭐⭐⭐)
- **Design**: "Boxes arranged horizontally, each with different accent color and complexity badges"

### **Slide 11: Kết Quả Phân Loại**
- F1-score của mỗi mô hình:
  - Decision Tree: ~0.9864
  - Random Forest: ~0.9712
  - DT-CTS: ~0.9574
- F1 là chỉ số cân bằng precision và recall
- DT-CTS F1 thấp hơn một chút, nhưng được thiết kế để giảm chi phí triển khai
- Speaker notes: "Kết quả F1-score là: Decision Tree 0.9864, Random Forest 0.9712, DT-CTS 0.9574. F1 là chỉ số cân bằng giữa chính xác và đủ bao. Thấy DT-CTS F1 thấp hơn Decision Tree, nhưng đó là do DT-CTS được thiết kế không chỉ tối đa accuracy, mà còn để giảm chi phí triển khai."
- **Icon**: 📈
- **Visual**: Bar chart comparing F1-scores across 3 models with trend line
- **Design**: "Bars in cyan/primary blue, highlight DT-CTS with accent color"

### **Slide 11.5: Tính Tổng Quát Hóa - Multi-Dataset Validation (NEW)**
- Câu hỏi: DT-CTS có hoạt động trên các loại tấn công khác không?
- Project test trên 4 datasets khác nhau:
  - CICIDS2017: DoS (Hulk, Slowloris) - tấn công truyền thống
  - CICIDS2018: DDoS (HTTP Flood, LOIC) - tấn công đa giao thức
  - CIC-DDoS2019: SYN/UDP/ICMP Flood - tấn công cường độ rất cao
  - CICIoT2023: Mirai IoT Botnet - tấn công phân tán từ IoT
- Kết quả: **Accuracy trung bình 0.9888** - tổng quát hóa tốt!
- Latency ổn định (~0.001ms) trên tất cả dataset
- **Icon**: 🌍
- **Visual**: Table with 4 datasets comparing Accuracy, F1-Score, FPR, FNR, Latency with check marks
- **Design**: "Table with green checkmarks for good results, highlight GOOD GENERALIZATION badge"
- Speaker notes: "Một câu hỏi quan trọng là: mô hình DT-CTS có hoạt động tốt trên các loại tấn công khác không? Để kiểm chứng điều này, chúng em test DT-CTS trên 4 datasets khác nhau, bao gồm DoS truyền thống, DDoS HTTP, tấn công cường độ cao, và tấn công IoT botnet. Kết quả cho thấy accuracy trung bình 0.9888, rất ổn định. Latency cũng luôn dưới 0.001ms. Điều này chứng minh DT-CTS tổng quát hóa tốt trên nhiều loại attack khác nhau, không bị overfitting trên CICIDS2017."

### **Slide 13: Kết Quả Threshold**
- Số threshold dùng:
  - Decision Tree: 30 threshold
  - DT-CTS: 13 threshold (CIC-DDoS2019) → 14 threshold (CICIDS2017)
- DT-CTS giảm khoảng 55-57% số threshold so với Decision Tree
- Ý nghĩa: ít rule → ít tài nguyên bảng match → dễ triển khai trên switch
- Nhận xét: Số threshold giảm trên các datasets khác nhau, chứng tỏ DT-CTS linh hoạt
- Speaker notes: "Về số threshold: Decision Tree dùng 30 threshold, nhưng DT-CTS giảm xuống 13-14 tuỳ dataset. Trung bình DT-CTS giảm khoảng 55-57% số threshold. Đây rất quan trọng vì ít threshold hơn nghĩa là ít rule, ít bảng match, dễ triển khai lên switch."
- **Icon**: 📉
- **Visual**: Comparison chart: bars for each dataset showing DT vs DT-CTS threshold count, with reduction percentage
- **Design**: "Grouped bars in cyan and orange, reduction % highlighted with green arrow"

### **Slide 14: Pushback Simulation Là Gì?**
- Mô phỏng mạng đơn giản gồm nhiều hop (3 switches)
- So sánh 3 chính sách xử lý attack:
  1. no_pushback: không chặn sớm, attack vẫn tới victim
  2. immediate_pushback: phát hiện là chặn ngay upstream
  3. gated_pushback: phải phát hiện 2 lần liên tiếp rồi mới pushback (cân bằng hơn)
- Mục tiêu: kiểm chứng hiệu quả pushback trong giảm attack traffic
- Speaker notes: "Phần pushback simulation mô phỏng một mạng đơn giản với 3 switches. Ý tưởng là so sánh các chính sách: không pushback, immediate pushback, và gated pushback. Gated pushback yêu cầu phát hiện 2 lần attack liên tiếp rồi mới pushback, để tránh block nhầm traffic hợp lệ."
- **Icon**: 🔄
- **Visual**: Network diagram 3-hop: [🚨 Attacker] ──→ [S1] ──→ [S2] ──→ [👤 Victim] with pushback arrows going back
- **Design**: "Network nodes as circles/boxes, attack flow red, pushback flow green, topology diagram style"

### **Slide 15: Kết Quả Pushback**
- Attack bytes tới victim:
  - Không pushback: **2.9M bytes** ❌
  - Gated pushback: **65K bytes** ✅
- **Giảm 97.80% attack traffic!**
- Benign traffic được giữ: ~305M bytes, chỉ 2 false block events
- Kết luận: Gated pushback cực hiệu quả, an toàn
- Speaker notes: "Kết quả cho thấy: không pushback thì attack bytes tới victim là 2.9 triệu. Gated pushback giảm xuống 65 nghìn bytes. Tức là giảm 98% attack traffic. Ngoài ra, hệ thống vẫn giữ được 305 triệu bytes benign traffic và chỉ có 2 lần chặn nhầm. Điều này rất tuyệt vời."
- **Icon**: ✅
- **Visual**: Before/After comparison: tall bar (2.9M) → short bar (65K) with 97.8% reduction arrow, benign traffic preserved
- **Design**: "Before column red/orange, after column green/cyan, reduction % highlighted with star icon"

### **Slide 16: Cải Tiến Nhỏ của Project**
- Cải tiến: **gated_pushback** thay vì cứ phát hiện là chặn ngay
- Lý do: nếu mô hình phát hiện sai (false positive), có thể chặn nhầm
- Gated_pushback: yêu cầu **2 lần phát hiện** malicious liên tiếp → an toàn hơn
- Kết quả: Giảm false blocks từ 145 xuống 2 ✅
- Speaker notes: "Ngoài việc tái hiện paper, project có một cải tiến nhỏ là gated_pushback. Thay vì cứ phát hiện attack là chặn ngay, hệ thống yêu cầu phải phát hiện 2 lần malicious liên tiếp rồi mới pushback. Immediate pushback có 145 false block events, nhưng gated pushback chỉ có 2. Điều này giúp an toàn hơn, tránh chặn nhầm traffic hợp lệ."
- **Icon**: ⭐
- **Visual**: Sequence timeline: Detection#1 (yellow ⚠️) ──→ Confirm State ──→ Detection#2 (orange 🔔) ──→ Pushback (green ✅)
- **Design**: "Horizontal timeline with state boxes, false blocks comparison chart below (145 → 2)"

### **Slide 17: Giới Hạn của Project**
- ① Reproduction rút gọn, không triển khai trên phần cứng thật (Tofino/BMv2)
- ② Số threshold chỉ là proxy, chưa phải resource thật (TCAM, SRAM)
- ③ Pushback là mô phỏng đơn giản, không phải mạng thực tế
- Dù có giới hạn, project vẫn tái hiện được các **ý chính của paper**
- Speaker notes: "Project có một số giới hạn. Thứ nhất, đây là reproduction rút gọn, không triển khai trên phần cứng thật. Thứ hai, số threshold chỉ là proxy, chưa phải số đo resource thật. Thứ ba, pushback là mô phỏng đơn giản, không phải mạng thực tế. Tuy nhiên, project vẫn tái hiện được các ý chính của paper."
- **Icon**: 📋
- **Visual**: Numbered list (①②③) with ⚠️ icons on left, subtle background boxes
- **Design**: "Left-aligned list with orange warning icons, limitation items in light red boxes"

### **Slide 18: Kết Luận**
- ★ SISTAR là cách tiếp cận **hiệu quả** cho DDoS
- ★ Phát hiện trong switch → phản ứng **nhanh** (< 0.001ms)
- ★ DT-CTS → mô hình **nhẹ nhưng chính xác** (95.68% accuracy)
- ★ Gated Pushback → giảm **97.8% attack traffic**
- ★ Trade-off: Accuracy ↔ Deployability → **Cân bằng tốt**
- Speaker notes: "Kết luận: SISTAR là cách tiếp cận hiệu quả. Thay vì phát hiện ở server, SISTAR phát hiện ngay trong switch để phản ứng nhanh dưới 0.001ms. DT-CTS giúp mô hình đủ nhẹ với 95.68% accuracy. Pushback giúp chặn attack sâu vào mạng. Kết quả project cho thấy DT-CTS giảm 55-57% threshold, gated pushback giảm 97.8% attack bytes. Multi-dataset validation chứng minh DT-CTS tổng quát hóa tốt. Điểm quan trọng nhất là sự cân bằng giữa phát hiện tốt, triển khai nhẹ, và hiệu quả mitigation."
- **Icon**: 🎯
- **Visual**: 5 highlight boxes with star icons, each with key metric and emoji
- **Design**: "Boxes with primary blue header and cyan border, star ★ icons, metric values highlighted"

### **Slide 19: References & Related Work (NEW)**
- Bài toán DDoS:
  - Paxson et al. (2011) - ACM SIGCOMM
  - Mirkovic & Reiher (2004) - DDoS Taxonomy
- Mô hình ML:
  - Breiman (2001) - Random Forests
  - Buczak & Guven (2016) - ML for Intrusion Detection
- Programmable Networks:
  - Bosshart et al. (2014) - **P4 Language**
  - Intel **Tofino** Switch
- Datasets:
  - Sharafaldin et al. (2018) - **CICIDS2017**
  - CIC-DDoS2019, CICIoT2023
- Mitigation:
  - Ioannidis & Bellovin (2002) - **Pushback Mechanism**
- Speaker notes: "Slide này liệt kê các paper và tài nguyên tham khảo mà chúng em dùng trong project. Bao gồm công trình về DDoS, ML, programmable networks, datasets, và cơ chế mitigation. Các paper này rất quan trọng cho việc viết report cuối kì. Thầy có thể tham khảo thêm từ các công trình này."
- **Icon**: 📚
- **Visual**: Clean list format with paper titles and authors in cyan color, links highlighted
- **Design**: "List format with paper icons 📄, organized by category, bullet points with proper indentation"

### **Slide 20: Câu Kết / Q&A**
- **Nếu chỉ nhớ một câu:**
  "SISTAR tái hiện ý tưởng dùng mô hình cây quyết định **nhẹ** để phát hiện DDoS **ngay trong switch**, rồi dùng **pushback** để chặn attack **gần nguồn**, giảm tải cho mạng."
- Cảm ơn các bạn đã lắng nghe
- **Sẵn sàng trả lời câu hỏi** ❓
- Speaker notes: "Nếu chỉ nhớ một câu về project này: SISTAR tái hiện ý tưởng dùng mô hình cây quyết định nhẹ để phát hiện DDoS ngay trong switch, rồi dùng pushback để chặn traffic từ sớm. Kết quả project cho thấy hiệu quả cực tốt: latency < 0.001ms, giảm 98% attack traffic, tổng quát hóa tốt trên 4 attack types khác nhau. Cảm ơn các bạn đã lắng nghe. Em sẵn sàng trả lời các câu hỏi."
- **Icon**: ❓
- **Visual**: "Thank You" in large bold text (Primary Blue), with network background pattern, contact placeholder
- **Design**: "Minimalist centered design, primary blue background gradient, white text, network topology pattern overlay (opacity 5%)"

---

## Quy Tắc Chất Lượng Bắt Buộc

1. **Mỗi slide ≤ 7 bullets, mỗi bullet ≤ 12 từ** (Vietnamese-optimized)
2. **Speaker notes phải giống kịch bản nói tự nhiên**, không chỉ là bullet nhắc ý (tự nhiên, dễ nghe)
3. **Không được đảo thứ tự slide** - phải tuân theo kịch bản 20 bước trên
4. **Mỗi slide phải có heading rõ ràng**, icon, visual recommendation, design notes
5. **Nội dung phải dễ hiểu cho người chưa biết** - tránh thuật ngữ quá chuyên sâu
6. **Assets**: nếu có ảnh/figure từ `reproduction/output/`, hãy reference tên file
7. **Typography**: Dùng font hỗ trợ Việt (Segoe UI, Arial Unicode MS, Roboto)
8. **Colors**: Tuân theo color scheme (Primary Blue #1E3A5F, Cyan #00BCD4, Coral #FF6B6B)
9. **Design**: Thêm network-themed background patterns, decorative elements (═, ──, ★, etc.)
10. **Emphasis**: Dùng **bold** cho key metrics, *italic* cho emphasis, `monospace` cho technical

## Output Expected
File Markdown có **20 slide** (19 content + 1 thank you), mỗi slide tuân theo format trên, với:
- Speaker notes là kịch bản nói hoàn chỉnh (tự nhiên, 2-3 câu)
- Visual recommendations cho từng slide
- Design guidelines rõ ràng
- Icon và decorative elements suggestions
- Network topology & architecture diagrams
- Data visualizations (charts, tables, flows)

## Cách Gọi Prompt Này
"Dùng master prompt dưới đây để tạo slide PowerPoint/Keynote Markdown gồm 20 slide theo đúng kịch bản trình bày. Output phải là file Markdown có:
- Mạch kích bản giống `presentation.md` mở rộng
- Vietnamese text properly formatted với dấu chính tả
- Design guidelines chi tiết cho PowerPoint creators
- Network-themed visual recommendations
- Metrics & data points từ multi-dataset validation
- Dễ hiểu cho người chưa biết gì về project
Slide phải SINH ĐỘNG, CÓ HỌA TIẾT, CÓ BACKGROUND ĐẸP, FONT HỢP TIẾNG VIỆT."
