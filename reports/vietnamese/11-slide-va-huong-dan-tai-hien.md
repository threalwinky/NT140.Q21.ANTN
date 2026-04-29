# Slide va huong dan tai hien SISTAR

File nay gom 2 muc tieu trong cung mot noi:

1. Cho ban mot kich ban slide PowerPoint co the dung ngay khi thuyet trinh.
2. Cho ban mot lo trinh step-by-step de tai hien mot phan y tuong paper, so sanh voi baseline, va de xuat mot cai tien nho.

Paper goc:

- `SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes`
- `ACM CCS 2025`

Repo nay da co mot reproduction rut gon, va minh da chay lai de xac nhan output hien tai:

- `DT` F1: `0.9912`
- `RF` F1: `0.9912`
- `DT-CTS` F1: `0.9646`
- `DT-CTS` giam threshold tu `22` xuong `15` so voi `DT`
- `gated_pushback` giam `97.04%` attack bytes toi victim so voi `no_pushback`

## 1. Hieu dung paper de len slide

### 1.1. Bai toan la gi?

Paper giai bai toan:

- phat hien DDoS du nhanh de phan ung theo thoi gian thuc,
- nhung van phai du nhe de chay duoc tren programmable switch,
- va khong chi detect, ma con phai giam thieu attack traffic som hon trong mang.

Mau thuan trung tam cua paper:

- mo hinh manh hon thi thuong dung nhieu feature, nhieu threshold, nhieu table entry,
- trong khi switch lai bi gioi han bo nho, stage, va match-action resource.

### 1.2. Threat model la gi?

Paper khong co mot section rieng ten `Threat Model`, vi vay phan nay nen trinh bay duoi dang:

> Tu system overview, pushback design, va evaluation, nhom rut ra threat model ngam dinh cua paper.

Threat model hop ly de noi:

- ke tan cong gui luong lon DDoS tu phia ngoai vao mang, co the la flood protocol-level hoac application-layer;
- traffic tan cong di qua nhieu switch truoc khi toi victim;
- muc tieu cua attacker la lam can kiet bang thong, tai nguyen mang, hoac tai nguyen server;
- he thong phong thu duoc trien khai trong `single administrative domain`, vi du data center hoac enterprise network;
- cac programmable switch trong cung he thong co the hop tac voi nhau bang `alert packet` va `pushback`.

### 1.3. Gia dinh cua paper la gi?

Gia dinh ky thuat:

- mang co programmable switch va co the lap trinh bang P4 hoac tuong duong;
- switch co the trich xuat mot tap packet-level va flow-level feature da chon;
- model duoc train offline, sau do encode va nap vao switch;
- switch co du register, table va stage de chay mot model da duoc rut gon;
- cac switch tin cay nhau trong mien quan tri va hieu duoc custom alert header;
- pushback chi day nguoc len `upstream switch`, khong phai mot co che global tren toan Internet.

Gia dinh danh gia:

- dataset dai dien cho hanh vi DoS/DDoS;
- threshold count duoc dung nhu mot proxy cho kha nang deploy;
- attack du manh de tao ra khac biet ro rang tren feature va luong traffic.

### 1.4. Phuong phap cua paper la gi?

Paper co 4 manh ghep chinh:

1. `Feature engineering`
   - chon mot tap feature packet-level va flow-level co ich cho DDoS, nhung van phai hop voi gioi han data plane.
2. `DT-CTS`
   - trong qua trinh xay decision tree, gioi han so threshold moi feature duoc phep dung.
   - muc tieu la giam so nut quyet dinh va giam do phuc tap khi encode len switch.
3. `Feature encoding`
   - bien cac khoang gia tri cua feature thanh ma nhi phan ngan gon de ternary-match trong switch.
4. `Distributed pushback`
   - switch phat hien tan cong gui alert packet len upstream switch de block som hon, gan nguon hon.

### 1.5. Ket qua cua paper can nho

Ket qua paper nen dua vao slide:

- `DT-CTS` giam threshold khoang `70%` ma van giu do chinh xac cao;
- paper claim chi can `3 feature` da dat khoang `98% F1`;
- tren `6 dataset`, phan lon dat `95%+ accuracy`, ngoai le `IoT23`;
- tren hardware switch, paper bao cao resource rat thap:
  - memory usage duoi `3%`,
  - `tMATCH xBar` khoang `1.8%`,
  - `6 stages`, `7 tables`,
  - flow-table entries muc thap;
- pushback giam `ATBU` them `9%` den `41%` tuy vi tri deploy;
- response time paper bao cao nho hon `1 giay`.

### 1.6. Ket qua reproduction trong repo nay

Day la phan ban nen noi ro la `reproduction rut gon`, khong phai lap lai toan bo Tofino/BMv2 cua tac gia.

| Muc | Ket qua |
| --- | --- |
| Dataset | `CICIDS2017 Wednesday subset from Kaggle` |
| Bai toan | `BENIGN` vs `attack` |
| Feature | `5 feature` |
| Baseline | `DT`, `RF` |
| Mo hinh paper | `DT-CTS` |
| Mitigation policy | `no_pushback`, `immediate_pushback`, `gated_pushback` |

Bang classification:

| Mo hinh | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| DT | 0.9912 | 0.9873 | 0.9952 | 0.9912 |
| RF | 0.9912 | 0.9936 | 0.9888 | 0.9912 |
| DT-CTS | 0.9640 | 0.9489 | 0.9808 | 0.9646 |

Bang threshold:

| Mo hinh | Tong threshold | Max threshold tren 1 feature |
| --- | ---: | ---: |
| DT | 22 | 7 |
| RF | 115 | 34 |
| DT-CTS | 15 | 3 |

Bang pushback:

| Policy | Attack bytes toi victim | Benign bytes toi victim | False block |
| --- | ---: | ---: | ---: |
| no_pushback | 1,731,491 | 3,509,171,465 | 0 |
| immediate_pushback | 362 | 693,712,885 | 20 |
| gated_pushback | 51,302 | 2,020,443,640 | 3 |

Thong diep chinh:

- `DT-CTS` hy sinh mot it F1 de doi lay model gon hon;
- `gated_pushback` can bang hon `immediate_pushback`;
- reproduction van the hien dung trade-off cot loi cua paper.

## 2. Kich ban slide PowerPoint

Ban co the dung `12 slide`. Moi slide duoi day gom:

- `Noi dung tren slide`: nhung gi nen dat len man hinh
- `Loi noi`: script ngan de thuyet trinh
- `Hinh`: hinh nen chen neu co

### Slide 1. Tieu de va claim

Noi dung tren slide:

- `SISTAR: DDoS detection and mitigation on programmable data planes`
- `Reproduction rut gon tren CICIDS2017 Wednesday`
- claim: `giu duoc y tuong cot loi cua paper: model gon hon + pushback upstream`

Loi noi:

> Nhóm em chọn paper SISTAR của ACM CCS 2025. Điểm hay của paper là không chỉ phát hiện DDoS bằng machine learning trong switch, mà còn kết hợp cơ chế pushback để giảm traffic tấn công sớm hơn trong mạng. Phần đồ án của nhóm tái hiện các ý tưởng cốt lõi đó trong một prototype phần mềm rút gọn.

Hinh:

- neu can, chen ten paper va so do pipeline don gian tu ban ve.

### Slide 2. Bai toan va dong luc

Noi dung tren slide:

- DDoS can detect nhanh va dung
- switch lai rat han che tai nguyen
- detect trung tam hoac model qua nang se cham va kho deploy

Loi noi:

> Bài toán khó ở đây là nếu muốn phát hiện chính xác thì ta thường cần nhiều feature và mô hình phức tạp. Nhưng nếu muốn đưa logic đó xuống switch để phản ứng theo thời gian thực thì tài nguyên phần cứng lại rất hạn chế. Paper này giải quyết đúng mâu thuẫn đó.

### Slide 3. Threat model va gia dinh

Noi dung tren slide:

- attacker gui DDoS traffic qua nhieu switch toi victim
- mien trien khai: `single administrative domain`
- cac switch hop tac bang `alert packet` va `pushback`
- model train offline, deploy online

Loi noi:

> Paper không tách riêng thành một section threat model, nên nhóm em trình bày threat model rút ra từ kiến trúc hệ thống. Ta giả định đây là mạng do một tổ chức kiểm soát, ví dụ data center hoặc enterprise network, nơi nhiều programmable switch có thể tin cậy nhau và gửi alert packet cho nhau để chặn traffic ở upstream.

### Slide 4. Kien truc tong quat cua SISTAR

Noi dung tren slide:

- Training phase
- Deployment phase
- Detection + alert + pushback phase

Loi noi:

> SISTAR hoạt động theo ba pha. Đầu tiên là train model với feature đã chọn. Sau đó model được encode và triển khai phân tán trên nhiều switch. Khi chạy thật, switch tự extract feature, classify traffic, tạo alert packet, rồi kích hoạt pushback để đẩy việc chặn lên gần nguồn hơn.

Hinh:

- ve lai Figure 2 theo ban don gian hoa, hoac tu ve:
  `traffic -> feature extraction -> DT-CTS encode/match -> alert -> upstream pushback`

### Slide 5. Dong gop ky thuat chinh

Noi dung tren slide:

- `DT-CTS`
- `feature encoding`
- `distributed pushback`

Loi noi:

> Đóng góp kỹ thuật trọng tâm là DT-CTS. Thay vì để decision tree tự do sinh ra quá nhiều threshold, paper giới hạn số threshold cho từng feature ngay từ lúc xây cây. Sau đó các khoảng giá trị được encode thành bit để ternary-match trên switch. Cuối cùng là cơ chế pushback phân tán giữa nhiều switch.

### Slide 6. Nhom tai hien phan nao?

Noi dung tren slide:

- tai hien rut gon tren software
- `DT`, `RF`, `DT-CTS`
- dem threshold nhu proxy cho deployability
- mo phong pushback 3-hop
- them `gated_pushback`

Loi noi:

> Vì nhóm không có Tofino thật, tụi em chủ động chọn reproduction rút gọn. Phần giữ trung thực là trade-off giữa chất lượng phân loại và độ gọn của mô hình, cùng với ý tưởng pushback. Phần cải tiến nhỏ của nhóm là gated pushback để giảm chặn nhầm.

### Slide 7. Dataset, feature, baseline

Noi dung tren slide:

- dataset: `CICIDS2017 Wednesday`
- bai toan nhị phân: benign vs attack
- 5 feature:
  - `destination_port`
  - `init_win_bytes_forward`
  - `fwd_header_length`
  - `packet_length_mean`
  - `flow_packets_persecond`

Loi noi:

> Bản reproduction dùng Wednesday subset của CICIDS2017 vì đây là phần dữ liệu có nhiều hành vi DoS và cũng gần với phần đánh giá của paper. Nhóm rút bài toán về benign và attack để giữ thí nghiệm gọn, sau đó so sánh ba mô hình DT, RF và DT-CTS trên cùng tập feature.

### Slide 8. Ket qua classification

Noi dung tren slide:

- `DT` va `RF` co F1 cao nhat: `0.9912`
- `DT-CTS` F1: `0.9646`
- trade-off: giam nhe accuracy de doi lay deployability

Loi noi:

> Nếu chỉ xét chất lượng phân loại thì DT và RF đang tốt nhất trong reproduction này. Tuy nhiên DT-CTS vẫn giữ F1 khá cao, khoảng 0.9646. Điểm quan trọng là paper không tối ưu thuần accuracy, mà tối ưu accuracy dưới ràng buộc phần cứng.

Hinh:

- `../../reproduction/output/classification_f1.png`

### Slide 9. Ket qua threshold va kha nang deploy

Noi dung tren slide:

- `DT`: `22` threshold
- `RF`: `115` threshold
- `DT-CTS`: `15` threshold
- giam `31.82%` so voi `DT`

Loi noi:

> Đây là slide quan trọng nhất nếu muốn chứng minh nhóm hiểu đóng góp của paper. RF mạnh nhưng cực kỳ nặng nếu nhìn vào threshold. DT-CTS giảm số threshold rõ rệt, và mỗi feature chỉ dùng tối đa 3 threshold trong reproduction này. Điều đó làm mô hình dễ encode và dễ đưa xuống switch hơn.

Hinh:

- `../../reproduction/output/threshold_usage.png`

### Slide 10. Ket qua pushback va cai tien nho

Noi dung tren slide:

- `immediate_pushback`: chan rat manh nhung chan nham nhieu
- `gated_pushback`: giam attack bytes `97.04%`
- false block giam tu `20` xuong `3`

Loi noi:

> Nếu block ngay khi vừa detect một lần, hệ thống gần như triệt tiêu attack traffic nhưng collateral damage lớn. Nhóm thêm một cải tiến nhỏ là gated pushback: chỉ block upstream nếu cùng source bị phát hiện độc hại trong hai cửa sổ liên tiếp. Kết quả là vẫn giảm attack bytes rất mạnh, nhưng false block giảm đáng kể.

Hinh:

- `../../reproduction/output/pushback_attack_bytes.png`

### Slide 11. Uu diem, han che, tinh thuc te

Noi dung tren slide:

- uu diem: nhanh, gon, co tu duy deploy
- han che: phu thuoc feature va mien quan tri
- tinh thuc te: hop voi enterprise/DC co programmable switch

Loi noi:

> Ưu điểm lớn nhất của SISTAR là nó nghĩ như một hệ thống thật: phải detect được, phải gọn, và phải có mitigation. Hạn chế là nó giả định khá mạnh về hạ tầng programmable switch và sự tin cậy giữa các switch. Trong thực tế, ý tưởng này hợp với enterprise network hoặc data center hơn là Internet mở.

### Slide 12. Ket luan va demo plan

Noi dung tren slide:

- da tai hien duoc y tuong cot loi
- da co baseline, metric, va cai tien nho
- demo: chay `run_reproduction.py` va mo `output/`

Loi noi:

> Tóm lại, nhóm không claim tái hiện đầy đủ toàn bộ môi trường phần cứng của paper, nhưng đã tái hiện được các nguyên lý cốt lõi: DT-CTS cho trade-off accuracy và deployability, cùng với pushback để giảm attack traffic sớm hơn. Phần demo sẽ chạy script reproduction và mở trực tiếp các bảng kết quả cùng các hình output.

## 3. Cach noi cho dung khi bao ve

Nen noi:

- `Nhóm tái hiện các ý tưởng cốt lõi của paper trong một prototype phần mềm rút gọn.`
- `Threshold count được dùng như một proxy cho khả năng triển khai trên programmable switch.`
- `Nhóm không claim đã lặp lại đầy đủ kết quả tài nguyên phần cứng của Tofino.`

Khong nen noi:

- `Nhóm reproduce y chang paper.`
- `Kết quả threshold trong repo này tương đương trực tiếp với SRAM/TCAM thật.`
- `Gated pushback là cải tiến của paper gốc.`

Nen noi dung hon:

- `Gated pushback là cải tiến nhỏ do nhóm đề xuất dựa trên trực giác của paper.`

## 4. Huong dan tai hien mot phan y tuong paper step-by-step

### 4.1. Muc tieu tai hien

Ta khong tai hien toan bo Tofino/BMv2 stack. Ta chi tai hien phan:

1. train va so sanh `DT`, `RF`, `DT-CTS`;
2. do so threshold nhu mot proxy cho deployability;
3. mo phong `pushback`;
4. thu mot cai tien nho cho mitigation.

### 4.2. Kien truc he thong don gian hoa

```text
Dataset -> Preprocess -> Train {DT, RF, DT-CTS}
        -> Evaluate {accuracy, precision, recall, F1}
        -> Count thresholds
        -> Build pushback trace
        -> Simulate {no_pushback, immediate_pushback, gated_pushback}
        -> Compare attack bytes, benign bytes, false blocks
```

### 4.3. File nao can doc va chay

Code quan trong:

- `reproduction/src/run_reproduction.py`
- `reproduction/src/data_pipeline.py`
- `reproduction/src/model_pipeline.py`
- `reproduction/src/pushback_sim.py`
- `SISTAR/model/DT-CTS.py`

Output quan trong:

- `reproduction/output/classification_metrics.csv`
- `reproduction/output/threshold_metrics.csv`
- `reproduction/output/pushback_metrics.csv`
- `reproduction/output/classification_f1.png`
- `reproduction/output/threshold_usage.png`
- `reproduction/output/pushback_attack_bytes.png`

### 4.4. Buoc 1: Chay lai reproduction

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_reproduction.py
```

Script se tu:

- nap `CICIDS2017 Wednesday` neu file ton tai;
- neu khong co, fallback sang synthetic dataset;
- train `DT`, `RF`, `DT-CTS`;
- sinh trace pushback;
- xuat CSV, PNG va file tong ket.

### 4.5. Buoc 2: Xac nhan du lieu va feature

Kiem tra file:

- `reproduction/output/dataset_source.txt`
- `reproduction/src/config.py`

Tai repo nay, feature dang dung la:

- `destination_port`
- `init_win_bytes_forward`
- `fwd_header_length`
- `packet_length_mean`
- `flow_packets_persecond`

Y nghia:

- 2 feature dau nghieng ve packet/header behavior;
- `flow_packets_persecond` giup bat burst traffic;
- bo feature nay du nho de de giai thich va de gan voi paper.

### 4.6. Buoc 3: So sanh baseline voi y tuong paper

Baseline:

- `DT`: de thay moc accuracy voi mot cay quyet dinh thuong;
- `RF`: de thay neu uu tien quality classification thi threshold no se phinh ra nhanh the nao.

Mo hinh paper:

- `DT-CTS`: dung implementation trong `SISTAR/model/DT-CTS.py`.

Dieu can nhin:

- `DT` va `RF` cho ta tran muc classification tot;
- `DT-CTS` cho ta bai hoc kien truc: hy sinh mot phan nho quality de model gon hon.

### 4.7. Buoc 4: Danh gia deployability bang threshold count

Trong reproduction nay, nhom dung:

- `total_thresholds`
- `max_thresholds_on_single_feature`

lam proxy cho kha nang encode len switch.

Ly do:

- nhieu threshold hon nghia la nhieu khoang gia tri hon;
- nhieu khoang gia tri hon nghia la can nhieu bit encode, nhieu match entry, nhieu logic so sanh hon.

Day la phan gan nhat voi dong gop ky thuat cua paper.

### 4.8. Buoc 5: Xay he thong pushback don gian hoa

File can xem:

- `reproduction/src/pushback_sim.py`

He thong mo phong:

- `24` source logic;
- `8` source dau la attack source trong mot khoang thoi gian;
- `60` cua so thoi gian;
- traffic attack co burst manh hon o mot doan ngan;
- model `DT-CTS` duoc dung lam detector cho pushback.

Ba policy:

- `no_pushback`
- `immediate_pushback`
- `gated_pushback`

### 4.9. Buoc 6: So sanh baseline mitigation

Baseline mitigation:

- `no_pushback`: de biet neu khong chan som thi bao nhieu attack traffic van toi victim.
- `immediate_pushback`: version manh tay, de thay muc tran attack va chi phi collateral damage.

Cai tien nho:

- `gated_pushback`: chi block neu mot source bi predict malicious trong `2` cua so lien tiep.

Ly do chon baseline nay:

- de minh co mot muc so sanh rat ro giua `khong chan`, `chan ngay`, va `chan co xac nhan`.

### 4.10. Buoc 7: Doc ket qua cho dung

Neu ban thay:

- `DT-CTS` thap hon `DT/RF` ve F1

thi khong nen ket luan la paper that bai.

Phai ket luan dung:

- `DT-CTS` giam quality mot it, nhung doi lai giam do phuc tap;
- trong paper, do phuc tap moi la rang buoc that su quan trong vi muc tieu la deploy tren switch.

Neu ban thay:

- `immediate_pushback` chan attack rat tot nhung mat benign nhieu

thi thong diep dung la:

- mitigation manh tay co gia cua no;
- can mot co che xac nhan nho de giam collateral damage.

### 4.11. Buoc 8: De xuat cai tien nho tu paper

Cai tien hien tai trong repo:

- `gated_pushback`

Mo ta ngan:

- thay vi block ngay sau 1 lan detect, yeu cau `2` cua so lien tiep moi block.

Vi sao hop ly:

- model detect co false positive;
- pushback la hanh dong mitigation, sai o day dat gia hon sai trong classification;
- them 1 lop xac nhan nho thuong la trade-off thuc dung.

Neu muon mo rong them sau nay, ban co the thu:

1. `k-of-n gating`
   - vi du `2/3` cua so thay vi `2 lien tiep`.
2. `alert cooldown`
   - sau khi block thi doi them vai cua so moi cho alert moi.
3. `confidence-aware pushback`
   - block chi khi flow roi vao la co xac suat attack cao, neu ban nang cap model.

## 5. Danh gia ket qua

### 5.1. Uu diem

- Paper co tu duy he thong, khong chi chay dua accuracy.
- `DT-CTS` la dong gop ro rang, de giai thich va hop logic voi switch.
- Pushback giup day mitigation len gan nguon, co y nghia thuc te hon viec chi bao dong.
- Reproduction trong repo nay co baseline, metric, va output ro rang, de demo.

### 5.2. Han che

- Khong co programmable switch that nen khong xac minh truc tiep duoc claim `SRAM/TCAM/stage`.
- Bai toan da rut gon thanh `benign vs attack`, chua giu duoc full multi-class richness.
- Threshold count chi la `proxy`, chua phai chi so phan cung that.
- Pushback simulation la topology logic nho, chua co traffic replay va control plane that.
- `DT-CTS.py` trong repo la ban giao duc, khong chac trung hoan toan voi code dung cho paper.

### 5.3. Muc do phu hop voi thuc te

Rat phu hop neu boi canh la:

- enterprise network;
- data center;
- mot mien quan tri dong, co programmable switch;
- can detect nhanh o edge va co co che phoi hop giua nhieu switch.

It phu hop hon neu:

- mang mo, khong kiem soat duoc upstream;
- ha tang khong co programmable data plane;
- can giai quyet adversary rat manh, co kha nang khai thac alert channel.

Ket luan thuc te nen noi:

> Y tuong cua SISTAR thuc te trong boi canh mang noi bo co the lap trinh va co quy trinh van hanh tap trung. No it phu hop hon cho Internet rong mo, nhung rat dang gia o goc nhin data center va enterprise defense.

## 6. Ban demo nhanh

Neu giang vien hoi demo gi, ban lam rat gon:

1. Chay:

```bash
cd /home/team/NT140.Q21.ANTN/Final/reproduction
python3 src/run_reproduction.py
```

2. Mo 3 bang:

```bash
column -s, -t < output/classification_metrics.csv
column -s, -t < output/threshold_metrics.csv
column -s, -t < output/pushback_metrics.csv
```

3. Mo 3 hinh:

- `output/classification_f1.png`
- `output/threshold_usage.png`
- `output/pushback_attack_bytes.png`

4. Noi 3 cau chot:

- `DT-CTS` hy sinh mot it F1 de doi lay model gon hon.
- Threshold giam nghia la de deploy len switch hon.
- `gated_pushback` giu benign traffic tot hon `immediate_pushback`.

## 7. Cau ket luan co the doc nguyen van

> Nhóm em không tái hiện toàn bộ hạ tầng phần cứng của SISTAR, nhưng đã tái hiện được đúng phần ý tưởng quan trọng nhất của paper: một mô hình phát hiện DDoS được ràng buộc để phù hợp hơn với programmable switch, và một cơ chế pushback giúp giảm traffic tấn công từ sớm trong mạng. Kết quả reproduction cho thấy trade-off giữa chất lượng phân loại và khả năng triển khai là có thật, đồng thời một cải tiến nhỏ như gated pushback có thể giảm chặn nhầm đáng kể mà vẫn giữ hiệu quả mitigation rất cao.
