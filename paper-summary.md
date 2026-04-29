# Tóm tắt dễ hiểu paper SISTAR

## 1. Thông tin nhanh

- **Tên paper**: `SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes`
- **Hội nghị**: `ACM CCS 2025`
- **Chủ đề**: phát hiện và giảm thiểu DDoS bằng **programmable data plane**

## 2. Paper này nói về cái gì?

Paper đề xuất một hệ thống tên là **SISTAR** để:

- phát hiện tấn công DDoS nhanh ngay trong mạng,
- giảm tải cho máy chủ nạn nhân,
- và chặn traffic tấn công sớm hơn bằng cơ chế **pushback**.

Ý tưởng chính là:

- thay vì đợi traffic đi tới server rồi mới xử lý,
- switch trong mạng sẽ tự phát hiện dấu hiệu DDoS,
- sau đó báo cho các switch khác để chặn traffic từ sớm.

## 3. Vì sao bài toán này khó?

DDoS khó xử lý vì:

- lưu lượng rất lớn,
- kiểu tấn công ngày càng đa dạng,
- nếu phân tích bằng server/CPU tập trung thì dễ bị chậm,
- nếu dùng mô hình ML quá lớn thì switch không đủ tài nguyên để chạy.

Nói ngắn gọn:

- **muốn chính xác** thì mô hình thường phức tạp,
- **muốn chạy trên switch** thì mô hình phải nhẹ.

Paper này cố giải quyết đúng mâu thuẫn đó.

## 4. Giải thích các khái niệm nền tảng trước khi đọc paper

Nếu bạn chưa quen các khái niệm mạng và ML, hãy hiểu các ý sau trước. Đây là phần quan trọng nhất để đọc paper mà không bị “ngợp”.

### 4.1. DDoS là gì?

`DDoS` = `Distributed Denial of Service`.

Hiểu rất đơn giản:

- attacker dùng rất nhiều máy hoặc nguồn traffic cùng lúc,
- gửi một lượng lớn request/packet tới cùng một mục tiêu,
- làm đường truyền, CPU, bộ nhớ, hoặc bảng kết nối của nạn nhân bị quá tải.

Mục tiêu của DDoS không nhất thiết là “xâm nhập”.
Mục tiêu thường là:

- làm dịch vụ chậm,
- làm dịch vụ sập,
- hoặc làm người dùng hợp lệ không truy cập được.

Vì vậy, một hệ thống chống DDoS cần làm 2 việc:

- **phát hiện** traffic nào là tấn công,
- **giảm thiểu** traffic đó trước khi nó gây nghẽn.

### 4.2. Switch là gì? Data plane và control plane là gì?

`Switch` là thiết bị chuyển tiếp packet trong mạng.

Ta có thể hiểu switch có hai “phần việc”:

- **data plane**: phần xử lý packet rất nhanh, theo từng packet, ví dụ forward, drop, sửa header
- **control plane**: phần cấu hình luật, bảng định tuyến, chính sách, thường chậm hơn nhưng linh hoạt hơn

Một cách hình dung:

- `data plane` giống như quầy soát vé xử lý khách rất nhanh theo luật đã có sẵn
- `control plane` giống như người quản lý cập nhật luật cho quầy soát vé

Paper này quan trọng ở chỗ:

- thay vì gửi traffic lên server để phân tích rồi mới ra lệnh,
- nó cố đưa một phần việc phát hiện xuống **data plane** để phản ứng nhanh hơn.

### 4.3. Programmable data plane là gì?

`Programmable data plane` là data plane có thể lập trình được, thay vì chỉ làm vài chức năng cố định.

Điều đó cho phép switch:

- parse nhiều loại header,
- giữ một ít state,
- tính toán một số thống kê đơn giản,
- match packet vào các luật phức tạp hơn,
- và quyết định forward/drop theo logic tự thiết kế.

Đây là lý do paper dùng P4 và programmable switch.

Nhưng cái giá phải trả là:

- tài nguyên phần cứng ít,
- số stage xử lý bị giới hạn,
- bộ nhớ bảng match bị giới hạn,
- không thể nhét một mô hình ML quá nặng vào switch.

### 4.4. Flow là gì?

`Flow` có thể hiểu là một nhóm packet thuộc cùng một “cuộc hội thoại” mạng.

Thường flow được xác định bởi:

- source IP
- destination IP
- source port
- destination port
- protocol

Người ta hay gọi đó là `5-tuple`.

Vì sao flow quan trọng?

- một packet riêng lẻ có thể trông bình thường,
- nhưng nếu nhìn cả luồng trong một khoảng thời gian, bạn sẽ thấy bất thường như số packet/giây tăng đột biến.

Nói ngắn gọn:

- `packet-level` cho biết “gói này trông như thế nào”
- `flow-level` cho biết “hành vi của cả luồng này ra sao”

### 4.5. Feature là gì?

`Feature` là các đặc trưng số mà mô hình dùng để phân biệt benign và attack.

Ví dụ:

- `destination port`
- `fwd header length`
- `packet length mean`
- `flow packets per second`

Bạn có thể nghĩ feature là các “dấu hiệu” mà hệ thống quan sát được.

Giống như bác sĩ không nhìn bệnh nhân theo cảm giác mơ hồ, mà nhìn vào:

- nhiệt độ,
- nhịp tim,
- huyết áp,
- xét nghiệm máu.

ML model cũng vậy: nó không “đoán mò”, nó nhìn vào feature.

### 4.6. Decision Tree (DT) là gì?

`Decision Tree` là mô hình phân loại hoạt động như một cây các câu hỏi `if-else`.

Ví dụ rất đơn giản:

- nếu `flow_packets_persecond` quá cao -> nghi ngờ attack
- nếu thêm `packet_length_mean` rất nhỏ -> càng giống SYN flood
- cuối cùng đi tới lá của cây và ra quyết định `benign` hay `attack`

Ưu điểm của `DT`:

- dễ hiểu
- dễ giải thích
- logic giống luật `if-then`
- phù hợp với switch hơn so với deep learning

Điểm yếu:

- cây thường có thể dùng rất nhiều ngưỡng chia (`threshold`)
- càng nhiều ngưỡng thì càng khó encode lên switch

### 4.7. Random Forest (RF) là gì?

`Random Forest` là tập hợp nhiều cây quyết định.

Mỗi cây bỏ phiếu, rồi hệ thống lấy kết quả đa số.

Ưu điểm:

- thường chính xác hơn một cây đơn lẻ
- ổn định hơn

Nhược điểm trong paper này:

- nhiều cây hơn nghĩa là logic phức tạp hơn
- tổng số threshold và rule thường lớn hơn nhiều
- vì vậy khó triển khai trên switch hơn

Cho nên:

- `RF` mạnh về độ chính xác
- nhưng `DT` hoặc `DT-CTS` hợp với mục tiêu triển khai trên data plane hơn

### 4.8. Threshold là gì?

`Threshold` là một ngưỡng số dùng để chia dữ liệu.

Ví dụ:

- nếu `flow_packets_persecond <= 500` thì đi nhánh trái
- nếu `> 500` thì đi nhánh phải

Số `500` ở đây chính là một threshold.

Nếu một feature dùng quá nhiều threshold, ví dụ:

- `<= 50`
- `<= 100`
- `<= 300`
- `<= 700`
- `<= 1500`

thì hệ thống phải nhớ nhiều mốc hơn, tạo nhiều lớp hơn, và việc ánh xạ sang bảng match trên switch sẽ nặng hơn.

### 4.9. DT-CTS là gì?

`DT-CTS` = `Decision Tree - Constrained Threshold Segmentation`.

Đây là ý tưởng cốt lõi nhất của paper.

Hiểu rất đơn giản:

- cây quyết định bình thường thích đặt nhiều threshold nếu điều đó giúp tăng accuracy
- nhưng switch không thích quá nhiều threshold vì tốn tài nguyên
- `DT-CTS` ép mô hình phải “tiết kiệm threshold”

Lợi ích:

- cây gọn hơn
- ít ngưỡng hơn
- dễ encode hơn
- ít rule/bảng match hơn

Chi phí:

- accuracy hoặc F1 có thể giảm nhẹ

Nói theo ngôn ngữ hệ thống:

- `DT` tối ưu cho chất lượng phân loại
- `DT-CTS` tối ưu cho khả năng triển khai

### 4.10. Encode feature và ternary matching là gì?

Đây là chỗ nhiều người mới đọc paper thường bị mơ hồ.

Ý tưởng là:

- thay vì đem nguyên cả cây quyết định phức tạp lên switch,
- paper biến mỗi feature thành một **class** nhỏ, ví dụ 0, 1, 2, 3
- sau đó ghép các class đó lại thành một mã ngắn
- rồi dùng bảng match của switch để quyết định benign hay attack

Ví dụ:

- `destination_port` thuộc lớp 1
- `packet_length_mean` thuộc lớp 3
- `flow_packets_persecond` thuộc lớp 2

ghép lại thành một mã đặc trưng tổng hợp.

`Ternary matching` là kiểu match cho phép:

- bit 0
- bit 1
- hoặc `*` nghĩa là “không quan tâm”

Kiểu match này hợp với switch vì switch rất giỏi tra bảng match-action.

### 4.11. Pushback, upstream và alert là gì?

`Pushback` là cơ chế chặn traffic tấn công từ sớm hơn trên đường đi.

`Upstream` nghĩa là phía gần nguồn traffic hơn.

Ví dụ đường đi:

- attacker -> gateway switch -> core switch -> victim

Nếu chỉ chặn ở sát victim thì:

- traffic xấu vẫn đi qua gần hết mạng rồi mới bị chặn

Nếu switch gần victim phát hiện tấn công và gửi `alert` cho switch upstream, thì switch upstream có thể chặn sớm hơn.

Lợi ích:

- giảm băng thông bị lãng phí
- giảm tải cho các switch phía sau
- giảm tải cho victim

Rủi ro:

- nếu phát hiện sai mà chặn ngay thì có thể chặn nhầm traffic hợp lệ

Đó là lý do phần mitigation luôn phải cân bằng giữa:

- chặn mạnh tay
- và tránh false positive

## 5. Ý tưởng cốt lõi của SISTAR

SISTAR có 4 ý chính:

### 5.1. Phát hiện ngay trong data plane

Hệ thống không đẩy hết traffic lên controller hay server để phân tích.
Thay vào đó, switch sẽ tự:

- lấy feature từ packet/flow,
- chạy mô hình phân loại,
- quyết định traffic có đáng ngờ hay không.

Điểm mạnh:

- phản ứng nhanh,
- giảm độ trễ,
- giảm tải cho hệ thống trung tâm.

### 5.2. Dùng Decision Tree nhưng tối ưu cho switch

Paper không chọn deep learning nặng, mà dùng **Decision Tree** và **Random Forest** vì:

- dễ ánh xạ sang pipeline match-action của switch,
- logic quyết định rõ ràng,
- phù hợp với tài nguyên phần cứng hạn chế.

Nhưng Decision Tree bình thường vẫn có thể có quá nhiều ngưỡng so sánh.

### 5.3. DT-CTS: giảm số ngưỡng so sánh

Đây là đóng góp kỹ thuật quan trọng nhất.

`DT-CTS` = `Decision Tree - Constrained Threshold Segmentation`

Ý tưởng dễ hiểu:

- khi huấn luyện cây quyết định, paper **giới hạn số threshold** được dùng cho mỗi feature,
- nhờ đó mô hình gọn hơn,
- dễ encode lên switch hơn,
- tốn ít bảng match hơn,
- nhưng vẫn giữ accuracy/F1 khá cao.

Nói đơn giản:

- cây thường: chọn nhiều ngưỡng, chính xác nhưng nặng
- cây DT-CTS: ép dùng ít ngưỡng hơn, nhẹ hơn để chạy trong switch

### 5.4. Pushback: chặn traffic sớm hơn

Nếu một switch phát hiện tấn công, nó không chỉ tự xử lý cục bộ.
Nó còn gửi **alert** cho switch upstream để:

- cài rule chặn sớm hơn,
- đẩy việc lọc traffic ra gần nguồn tấn công hơn,
- giảm lượng traffic độc hại đi sâu vào mạng.

Đây là phần “mitigation”, không chỉ là “detection”.

## 6. Hệ thống hoạt động như thế nào?

Paper chia hệ thống thành 3 giai đoạn chính:

### 6.1. Training

- lấy dữ liệu traffic,
- trích xuất feature,
- huấn luyện DT / RF,
- tối ưu bằng DT-CTS / RF-CTS,
- encode mô hình để triển khai lên switch.

### 6.2. Deployment

- các switch khác nhau có thể cài mô hình khác nhau,
- switch ở gateway dùng mô hình nhẹ để phát hiện nhanh,
- switch ở phía core/spine có thể dùng mô hình mạnh hơn để phân tích kỹ hơn.

### 6.3. Detection + Mitigation

- packet đi vào switch,
- switch trích xuất feature,
- mô hình quyết định benign hay attack,
- nếu thấy tấn công thì tạo alert,
- alert kích hoạt pushback để switch upstream chặn sớm.

## 7. Vai trò của từng bộ phận trong toàn hệ thống

Nếu ghép tất cả các khái niệm lại, SISTAR có thể được hiểu như một dây chuyền gồm các khối sau:

### 7.1. Bộ trích xuất feature

Nhiệm vụ:

- lấy traffic thô
- biến nó thành các con số mà mô hình hiểu được

Nếu không có khối này, mô hình sẽ không có đầu vào để ra quyết định.

### 7.2. Bộ phân loại `DT` / `RF` / `DT-CTS`

Nhiệm vụ:

- nhìn vào feature
- quyết định luồng traffic là `benign` hay `attack`

Vai trò khác nhau:

- `DT`: baseline dễ hiểu, dễ triển khai
- `RF`: baseline mạnh về accuracy nhưng nặng
- `DT-CTS`: phương án paper ưu tiên vì cân bằng giữa accuracy và deployability

### 7.3. Bộ nén threshold và mã hoá quyết định

Nhiệm vụ:

- giảm số ngưỡng cần dùng
- biến feature liên tục thành các lớp rời rạc
- ghép các lớp đó thành dạng switch có thể match nhanh

Đây là cầu nối giữa:

- thế giới ML
- và thế giới bảng match-action của switch

### 7.4. Programmable switch pipeline

Nhiệm vụ:

- đọc packet khi nó đi qua switch
- cập nhật một số thống kê flow
- áp dụng logic phân loại
- quyết định forward hay drop

Đây là nơi SISTAR tạo ra lợi thế về tốc độ phản ứng.

### 7.5. Bộ alert và pushback

Nhiệm vụ:

- khi phát hiện tấn công, gửi cảnh báo cho switch khác
- cài rule chặn từ upstream

Đây là bộ phận giúp SISTAR không chỉ “nhìn thấy tấn công”, mà còn “hành động để giảm thiểu”.

### 7.6. Toàn hệ thống đang tối ưu điều gì?

Nếu tóm gọn thành 1 câu:

> SISTAR cố tối ưu một bài toán hai mục tiêu: phát hiện đủ tốt, nhưng vẫn đủ nhẹ để nhét vào switch và phản ứng đủ sớm để chặn traffic trước khi nó tới nạn nhân.

## 8. Paper dùng loại feature nào?

Paper dùng cả:

- **packet-level features**: lấy từ packet đơn lẻ
- **flow-level features**: thống kê trên một luồng

Ví dụ ý tưởng feature:

- destination port
- header length
- packet length mean
- flow packets per second
- các thống kê thời gian và kích thước flow

Thông điệp ở đây là:

- chỉ nhìn từng packet thì chưa đủ,
- nhưng nếu lấy quá nhiều flow feature thì switch sẽ tốn tài nguyên,
- nên paper cố chọn **ít feature nhưng hiệu quả**.

## 9. Vì sao paper dùng programmable data plane?

Vì programmable switch có thể:

- xử lý packet ở tốc độ cao,
- tự giữ một phần state,
- chạy logic match-action tùy chỉnh,
- phù hợp với việc phát hiện bất thường ngay trong đường đi của traffic.

Nhưng nó cũng có hạn chế:

- số stage cố định,
- bộ nhớ TCAM/SRAM hạn chế,
- không hợp với mô hình ML quá phức tạp.

Vì vậy toàn bộ paper xoay quanh câu hỏi:

> Làm sao để có mô hình đủ tốt nhưng vẫn đủ nhẹ để chạy trên switch?

## 10. Kết quả chính của paper

Theo paper, SISTAR đạt các kết quả nổi bật sau:

- giữ được độ chính xác phát hiện cao,
- giảm số threshold đáng kể bằng DT-CTS,
- giảm tiêu thụ tài nguyên phần cứng,
- hoạt động tốt hơn một số phương pháp trước đó,
- cơ chế pushback giúp giảm lượng traffic tấn công đi qua mạng.

Một số ý đáng nhớ:

- paper nhấn mạnh có thể đạt F1 cao với số feature nhỏ,
- phần pushback giúp giảm băng thông bị chiếm bởi traffic tấn công,
- hệ thống được đánh giá cả ở góc nhìn ML lẫn góc nhìn tài nguyên switch.

## 11. Điểm mạnh của paper

- **Ý tưởng rõ ràng**: không chỉ phát hiện mà còn giảm thiểu tấn công
- **Thực tế hơn nhiều paper ML thuần**: quan tâm tới giới hạn phần cứng
- **Có đóng góp kỹ thuật cụ thể**: DT-CTS
- **Có góc nhìn hệ thống**: nhiều switch phối hợp với nhau
- **Đánh giá khá đầy đủ**: accuracy, F1, resource usage, pushback effect

## 12. Điểm yếu / giới hạn

Paper vẫn có một số giới hạn:

- phụ thuộc vào môi trường có programmable switches
- tái hiện đầy đủ ngoài lab/hardware thật không hề dễ
- một số kết quả tài nguyên phần cứng khó reproduce nếu không có Tofino/BMv2
- nếu attacker hiểu cơ chế alert/pushback, họ có thể tìm cách lạm dụng hoặc né tránh

Nói cách khác:

- ý tưởng mạnh,
- nhưng triển khai full như paper ngoài thực tế hoặc trong đồ án sinh viên là khá nặng.

## 13. Nếu đọc paper lần đầu, nên nhớ 3 câu này

### Câu 1

SISTAR là hệ thống **phát hiện DDoS ngay trong switch**, thay vì phụ thuộc hoàn toàn vào server hoặc controller.

### Câu 2

Đóng góp kỹ thuật quan trọng nhất là **DT-CTS**, tức là làm cây quyết định gọn hơn để phù hợp với phần cứng switch.

### Câu 3

SISTAR không chỉ **detect**, mà còn **pushback** để chặn traffic tấn công từ sớm ở upstream switch.

## 14. Một cách hiểu rất ngắn

Nếu phải tóm tắt paper này trong 1 đoạn:

> Paper đề xuất một framework tên SISTAR để phát hiện và giảm thiểu DDoS bằng programmable data plane. Ý tưởng chính là dùng một mô hình cây quyết định đã được tối ưu cho switch (`DT-CTS`) để giảm số ngưỡng so sánh, nhờ đó tiết kiệm tài nguyên nhưng vẫn giữ độ chính xác cao. Khi phát hiện tấn công, hệ thống tạo alert và dùng cơ chế pushback để các switch upstream chặn traffic sớm hơn, giảm tải cho nạn nhân và toàn mạng.

## 15. Phần nào quan trọng nhất nếu bạn làm đồ án?

Nếu dùng paper này làm đồ án, bạn nên tập trung vào 3 thứ:

1. **Hiểu đúng DT-CTS**
2. **Làm prototype phát hiện DDoS với ít feature**
3. **Mô phỏng pushback trên topology nhỏ**

Đó là phần “linh hồn” của paper.
