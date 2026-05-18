# Working log: SISTAR BMv2/Mininet DDoS lab

Ngày ghi chú: 2026-05-18

File này ghi lại những gì đã làm được trong session hiện tại để tiếp tục mô phỏng SISTAR bằng Mininet + BMv2 + P4.

## 1. Mục tiêu của session

Mục tiêu chính là mở rộng project từ phần reproduction Python sang mô phỏng gần với paper hơn:

- Chạy logic phát hiện DDoS trực tiếp trên programmable switch bằng P4/BMv2.
- Dùng Mininet để mô phỏng topology nhiều switch.
- Sinh traffic benign và attack-like trong môi trường lab local.
- Dùng DT-CTS để export rule sang bảng ternary trong P4.
- Mô phỏng mitigation/pushback bằng cách cài rule chặn source IP ở upstream switch.

## 2. Những phần code đã được thêm/cập nhật trong project

### 2.1. Cập nhật P4 pipeline

File chính:

```text
SISTAR/BMv2/DT.p4
```

Các thay đổi chính:

- Căn chỉnh feature layout với reproduction Python:
  1. `protocol`
  2. `init_win_bytes_forward`
  3. `fwd_header_length`
  4. `packet_length_mean`
  5. `flow_packets_persecond`
- Thêm UDP parsing.
- Thêm metadata `drop_flag` để packet đã bị drop không bị `ipv4_lpm` forward lại.
- Thêm bảng `source_block` để mô phỏng pushback mitigation theo source IP.
- Đổi thứ tự xử lý trong ingress pipeline:

```text
source_block -> feature classification -> DDoS_ternary -> ipv4_lpm nếu chưa drop
```

### 2.2. Thêm tool export DT-CTS rule sang BMv2 CLI

Các file mới:

```text
SISTAR/BMv2/tools/tree_to_ternary.py
SISTAR/BMv2/tools/cli_templates.py
SISTAR/BMv2/tools/export_dtcts_rules.py
```

Chức năng:

- Train DT-CTS bằng dataset synthetic hoặc Kaggle nếu có.
- Chuyển cây DT-CTS thành tập các giá trị feature-bin 10-bit.
- Sinh command cho `simple_switch_CLI`:
  - ghi threshold register
  - thêm rule `DDoS_ternary`
  - thêm rule IPv4 forwarding
  - hỗ trợ rule `source_block`

Đã chạy thành công:

```bash
python3 SISTAR/BMv2/tools/export_dtcts_rules.py \
  --dataset synthetic \
  --output-dir SISTAR/BMv2/generated \
  --topology lab3
```

Kết quả đã sinh:

```text
SISTAR/BMv2/generated/dtcts_rules.json
SISTAR/BMv2/generated/s1_commands.cli
SISTAR/BMv2/generated/s2_commands.cli
SISTAR/BMv2/generated/s3_commands.cli
```

Kết quả mẫu khi export:

```text
Dataset: Synthetic DDoS-like flow dataset
Rows: 4800
DT-CTS accuracy: 0.9992
DT-CTS F1: 0.9992
DDoS ternary entries: 640
Wrote rules to: SISTAR/BMv2/generated
```

### 2.3. Thêm Mininet/BMv2 lab scripts

Các file mới:

```text
SISTAR/BMv2/lab/mininet_sistar.py
SISTAR/BMv2/lab/traffic_generator.py
SISTAR/BMv2/lab/receiver.py
SISTAR/BMv2/lab/pushback_controller.py
SISTAR/BMv2/lab/pcap_replay.py
```

Chức năng từng file:

- `mininet_sistar.py`: start topology Mininet gồm `h1`, `h2`, `h3`, `s1`, `s2`, `s3`; compile P4; start BMv2; load CLI rules.
- `traffic_generator.py`: sinh traffic benign hoặc attack-like bằng Scapy, giới hạn trong lab.
- `receiver.py`: đếm packet tới victim host `h3` theo source IP và protocol.
- `pushback_controller.py`: cài rule `source_block` vào upstream switch, mặc định dùng `s2` cho source `h2`.
- `pcap_replay.py`: replay PCAP người dùng cung cấp vào lab với giới hạn số packet/tốc độ.

### 2.4. Thêm tài liệu và dependency lab

Các file mới/cập nhật:

```text
SISTAR/BMv2/HOW_TO_RUN_MININET_VI.md
SISTAR/BMv2/requirements-lab.txt
SISTAR/BMv2/README.md
```

Trong đó:

- `HOW_TO_RUN_MININET_VI.md`: hướng dẫn tiếng Việt cách cài tool, sinh rule, chạy Mininet, gửi traffic, apply pushback.
- `requirements-lab.txt`: thêm dependency Python cho lab, hiện có `scapy`.
- `README.md`: cập nhật workflow BMv2 mới và đánh dấu các script `entry*.sh` cũ là legacy/manual examples.

## 3. Toolchain đã cài thành công trên máy

Ban đầu máy chưa có các lệnh:

```bash
which p4c-bm2-ss
which simple_switch
which simple_switch_CLI
which mn
```

Sau đó đã cài/build các thành phần cần thiết.

### 3.1. BMv2 đã cài xong

Đã build và install BMv2. Kiểm tra thành công:

```bash
which simple_switch
which simple_switch_CLI
```

Output:

```text
/usr/local/bin/simple_switch
/usr/local/bin/simple_switch_CLI
```

Đã test `simple_switch_CLI --help` thành công, hiển thị usage của BM runtime CLI.

### 3.2. P4 compiler đã cài xong

Đã build/install `p4c`. Kiểm tra thành công:

```bash
which p4c-bm2-ss
```

Output:

```text
/usr/local/bin/p4c-bm2-ss
```

### 3.3. Mininet đã cài xong

Kiểm tra thành công:

```bash
which mn
```

Output:

```text
/usr/bin/mn
```

### 3.4. Toolchain đầy đủ hiện tại

Đã xác nhận đủ 4 tool chính:

```text
/usr/local/bin/p4c-bm2-ss
/usr/local/bin/simple_switch
/usr/local/bin/simple_switch_CLI
/usr/bin/mn
```

## 4. Các lỗi đã gặp và đã xử lý

### 4.1. Lỗi Python PEP 668 khi cài BMv2 dependency

Lỗi gặp phải:

```text
error: externally-managed-environment
```

Nguyên nhân: Python hệ thống trên Ubuntu mới không cho `pip install` trực tiếp vào system environment.

Cách xử lý đã dùng:

```bash
PIP_BREAK_SYSTEM_PACKAGES=1 ./install_deps.sh
```

hoặc khi cần quyền root:

```bash
sudo env PIP_BREAK_SYSTEM_PACKAGES=1 ./install_deps.sh
```

Sau đó tiếp tục build/install BMv2 bằng:

```bash
./autogen.sh
./configure
make -j$(nproc)
sudo make install
sudo ldconfig
```

### 4.2. Thiếu Scapy khi chạy traffic generator

Lỗi gặp phải trong Mininet:

```text
ModuleNotFoundError: No module named 'scapy'
```

Cách xử lý:

- Cài `python3-scapy` bằng apt hoặc cài bằng pip với `--break-system-packages`.
- Sau khi cài, `traffic_generator.py` chạy được.

### 4.3. Receiver ban đầu không hiện log ngay

Nguyên nhân: output của Python bị buffer khi redirect vào file.

Cách xử lý: chạy receiver bằng `python3 -u` để unbuffered output:

```bash
h3 sh -c "python3 -u SISTAR/BMv2/lab/receiver.py --iface h3-eth0 --duration 120 --interval 5 > /tmp/h3_receiver.log 2>&1 &"
```

### 4.4. Receiver cần chỉ định interface rõ ràng

Receiver hoạt động tốt hơn khi chỉ rõ interface `h3-eth0`:

```bash
--iface h3-eth0
```

### 4.5. Copy command nhiều dòng trong Mininet dễ bị lỗi

Đã gặp lỗi command bị dính dòng cũ, ví dụ:

```text
bash: --pps: command not found
```

Kinh nghiệm: trong Mininet CLI nên chạy command dài trên một dòng, tránh copy command có dấu `\` nhiều dòng.

## 5. Lab Mininet/BMv2 đã chạy được

Đã chạy lab bằng script:

```bash
sudo python3 SISTAR/BMv2/lab/mininet_sistar.py \
  --p4 SISTAR/BMv2/DT.p4 \
  --commands-dir SISTAR/BMv2/generated
```

Script đã vào Mininet CLI thành công.

Trong Mininet, đã chạy:

```bash
pingall
```

Kết quả:

```text
*** Results: 0% dropped (6/6 received)
```

Điều này xác nhận:

- Topology Mininet chạy được.
- BMv2 switch chạy được.
- IPv4 forwarding giữa `h1`, `h2`, `h3` hoạt động.

## 6. Receiver ở h3 đã bắt packet thành công

Đã chạy receiver:

```bash
h3 sh -c "python3 -u SISTAR/BMv2/lab/receiver.py --iface h3-eth0 --duration 120 --interval 5 > /tmp/h3_receiver.log 2>&1 &"
```

Đã test bằng ping:

```bash
h1 ping -c 3 10.0.3.3
```

Ping thành công:

```text
3 packets transmitted, 3 received, 0% packet loss
```

Receiver log đã bắt được ICMP:

```text
[interval] total packets: 6
  10.0.1.1/ICMP: 3
  10.0.3.3/ICMP: 3
```

Ý nghĩa:

- `10.0.1.1/ICMP`: packet từ h1 tới h3.
- `10.0.3.3/ICMP`: ICMP reply từ h3.

## 7. Benign traffic generator đã chạy được

Đã chạy benign traffic từ `h1`:

```bash
h1 python3 SISTAR/BMv2/lab/traffic_generator.py --iface h1-eth0 --mode benign --dst 10.0.3.3 --count 20 --pps 2
```

Receiver log đã bắt được traffic TCP/UDP từ `10.0.1.1`:

```text
10.0.1.1/UDP: 1
10.0.1.1/TCP: 2
```

Có thêm một số packet từ `10.0.3.3/TCP`, có thể là reply/RST do TCP packet tạo ra. Đây không phải lỗi nghiêm trọng.

## 8. Trạng thái hiện tại

Đã hoàn thành:

- Code BMv2/P4 lab đã được thêm vào project.
- Rule exporter DT-CTS đã chạy được.
- Toolchain gồm BMv2, P4 compiler, Mininet đã cài xong.
- Mininet/BMv2 topology chạy được.
- `pingall` thành công với `0% dropped`.
- Receiver ở `h3` đã bắt được ICMP.
- Benign traffic từ `h1` đã đi qua switch và tới `h3`.

Chưa hoàn thành trong phần test thực nghiệm:

- Chưa chạy xong test attack-like từ `h2`.
- Chưa apply pushback rule vào `s2`.
- Chưa so sánh log trước và sau pushback.

## 9. Bước tiếp theo cần làm

### 9.1. Gửi attack-like traffic từ h2

Trong Mininet CLI:

```bash
h2 python3 SISTAR/BMv2/lab/traffic_generator.py --iface h2-eth0 --mode attack-lab --dst 10.0.3.3 --count 200 --pps 20 --i-understand-this-is-mininet-only
```

Sau đó xem log:

```bash
h3 tail -n 80 /tmp/h3_receiver.log
```

Cần quan sát số packet từ:

```text
10.0.2.2/TCP
10.0.2.2/UDP
```

### 9.2. Apply pushback từ terminal thứ hai

Mở terminal mới, không phải trong Mininet CLI:

```bash
cd /home/dangminhtu/Workspace/Final
python3 SISTAR/BMv2/lab/pushback_controller.py --source-ip 10.0.2.2 --upstream-switch s2 --apply
```

Kỳ vọng output:

```text
Switch: s2
Thrift port: 9091
table_add MyIngress.source_block MyIngress.drop 10.0.2.2 =>
Pushback source-block rule installed
```

### 9.3. Gửi lại attack-like traffic sau pushback

Quay lại Mininet CLI:

```bash
h2 python3 SISTAR/BMv2/lab/traffic_generator.py --iface h2-eth0 --mode attack-lab --dst 10.0.3.3 --count 200 --pps 20 --i-understand-this-is-mininet-only
```

Xem log:

```bash
h3 tail -n 100 /tmp/h3_receiver.log
```

Kỳ vọng: sau khi pushback, số packet từ `10.0.2.2` không tăng nữa hoặc tăng rất ít, vì source đã bị chặn ở upstream switch `s2`.

## 10. Lệnh hữu ích để tiếp tục từ trạng thái sạch

Nếu cần chạy lại từ đầu:

```bash
cd /home/dangminhtu/Workspace/Final
sudo mn -c
python3 SISTAR/BMv2/tools/export_dtcts_rules.py --dataset synthetic --output-dir SISTAR/BMv2/generated --topology lab3
sudo python3 SISTAR/BMv2/lab/mininet_sistar.py --p4 SISTAR/BMv2/DT.p4 --commands-dir SISTAR/BMv2/generated
```

Trong Mininet:

```bash
pingall
h3 sh -c "python3 -u SISTAR/BMv2/lab/receiver.py --iface h3-eth0 --duration 120 --interval 5 > /tmp/h3_receiver.log 2>&1 &"
h1 ping -c 3 10.0.3.3
h3 tail -n 40 /tmp/h3_receiver.log
h1 python3 SISTAR/BMv2/lab/traffic_generator.py --iface h1-eth0 --mode benign --dst 10.0.3.3 --count 20 --pps 2
h2 python3 SISTAR/BMv2/lab/traffic_generator.py --iface h2-eth0 --mode attack-lab --dst 10.0.3.3 --count 200 --pps 20 --i-understand-this-is-mininet-only
h3 tail -n 100 /tmp/h3_receiver.log
```

## 11. Handoff cho agent mới

Phần này dùng để agent khác chỉ cần đọc `working.md` là có thể hướng dẫn tiếp mà không cần toàn bộ transcript.

### 11.1. Project path quan trọng

Trong môi trường assistant ban đầu, project nằm ở:

```text
/home/team/NT140.Q21.ANTN/Final
```

Nhưng trên terminal của người dùng khi cài tool và chạy Mininet, project thực tế nằm ở:

```text
/home/dangminhtu/Workspace/Final
```

Khi hướng dẫn người dùng chạy lệnh, ưu tiên dùng path người dùng đang dùng:

```bash
cd /home/dangminhtu/Workspace/Final
```

Nếu không chắc path, yêu cầu người dùng chạy:

```bash
pwd
ls
```

Thư mục đúng phải có:

```text
README.md
SISTAR
reproduction
working.md
```

### 11.2. Toolchain đã được xác nhận hoạt động

Người dùng đã build/cài xong BMv2, P4 compiler và Mininet. Output đã xác nhận:

```text
/usr/local/bin/p4c-bm2-ss
/usr/local/bin/simple_switch
/usr/local/bin/simple_switch_CLI
/usr/bin/mn
```

Không cần hướng dẫn cài lại từ đầu trừ khi người dùng mở máy/môi trường khác.

### 11.3. Trạng thái Mininet gần nhất trước khi ghi chú

Người dùng đã vào được Mininet CLI bằng script:

```bash
sudo python3 SISTAR/BMv2/lab/mininet_sistar.py --p4 SISTAR/BMv2/DT.p4 --commands-dir SISTAR/BMv2/generated
```

Trong `mininet>`, đã chạy:

```bash
pingall
```

Kết quả:

```text
*** Results: 0% dropped (6/6 received)
```

Đã chạy receiver ở `h3` với interface rõ ràng:

```bash
h3 sh -c "python3 -u SISTAR/BMv2/lab/receiver.py --iface h3-eth0 --duration 120 --interval 5 > /tmp/h3_receiver.log 2>&1 &"
```

Đã test ping từ `h1` sang `h3`:

```bash
h1 ping -c 3 10.0.3.3
```

Ping thành công và receiver bắt được:

```text
10.0.1.1/ICMP: 3
10.0.3.3/ICMP: 3
```

Đã chạy benign traffic từ `h1`:

```bash
h1 python3 SISTAR/BMv2/lab/traffic_generator.py --iface h1-eth0 --mode benign --dst 10.0.3.3 --count 20 --pps 2
```

Receiver đã thấy một số TCP/UDP từ `10.0.1.1`, ví dụ:

```text
10.0.1.1/UDP: 1
10.0.1.1/TCP: 2
```

Do đó phần forwarding + receiver + Scapy generator đã hoạt động.

### 11.4. Việc cần hướng dẫn tiếp ngay

Việc tiếp theo là hoàn thành demo attack-like và pushback.

#### A. Nếu người dùng vẫn đang ở `mininet>` và receiver còn chạy

Chạy attack-like traffic từ `h2`:

```bash
h2 python3 SISTAR/BMv2/lab/traffic_generator.py --iface h2-eth0 --mode attack-lab --dst 10.0.3.3 --count 200 --pps 20 --i-understand-this-is-mininet-only
```

Sau đó xem log:

```bash
h3 tail -n 100 /tmp/h3_receiver.log
```

Cần quan sát các dòng từ source `10.0.2.2`:

```text
10.0.2.2/TCP: ...
10.0.2.2/UDP: ...
```

#### B. Apply pushback từ terminal thứ hai

Trong terminal khác, không phải Mininet CLI:

```bash
cd /home/dangminhtu/Workspace/Final
python3 SISTAR/BMv2/lab/pushback_controller.py --source-ip 10.0.2.2 --upstream-switch s2 --apply
```

Kỳ vọng output:

```text
Switch: s2
Thrift port: 9091
table_add MyIngress.source_block MyIngress.drop 10.0.2.2 =>
Pushback source-block rule installed
```

#### C. Gửi lại attack-like sau pushback

Quay lại `mininet>`:

```bash
h2 python3 SISTAR/BMv2/lab/traffic_generator.py --iface h2-eth0 --mode attack-lab --dst 10.0.3.3 --count 200 --pps 20 --i-understand-this-is-mininet-only
```

Xem log:

```bash
h3 tail -n 120 /tmp/h3_receiver.log
```

Kỳ vọng: sau pushback, count từ `10.0.2.2/TCP` hoặc `10.0.2.2/UDP` không tăng nữa hoặc tăng rất ít.

### 11.5. Nếu cần reset lab từ đầu

Trong terminal bình thường:

```bash
cd /home/dangminhtu/Workspace/Final
sudo mn -c
python3 SISTAR/BMv2/tools/export_dtcts_rules.py --dataset synthetic --output-dir SISTAR/BMv2/generated --topology lab3
sudo python3 SISTAR/BMv2/lab/mininet_sistar.py --p4 SISTAR/BMv2/DT.p4 --commands-dir SISTAR/BMv2/generated
```

Trong `mininet>`:

```bash
pingall
h3 sh -c "python3 -u SISTAR/BMv2/lab/receiver.py --iface h3-eth0 --duration 180 --interval 5 > /tmp/h3_receiver.log 2>&1 &"
h1 ping -c 3 10.0.3.3
h3 tail -n 40 /tmp/h3_receiver.log
```

Nếu ping và log ICMP OK thì tiếp tục benign/attack/pushback.

### 11.6. Cách chạy command trong Mininet

Khi hướng dẫn người dùng trong Mininet CLI, dùng command một dòng. Không dùng dấu `\` để xuống dòng vì người dùng đã gặp lỗi command bị dính dòng, ví dụ:

```text
bash: --pps: command not found
```

Ví dụ đúng:

```bash
h1 python3 SISTAR/BMv2/lab/traffic_generator.py --iface h1-eth0 --mode benign --dst 10.0.3.3 --count 20 --pps 2
```

Ví dụ nên tránh trong Mininet:

```bash
h1 python3 SISTAR/BMv2/lab/traffic_generator.py \
  --mode benign \
  --dst 10.0.3.3
```

### 11.7. Các cảnh báo/lỗi đã biết khi chạy tiếp

#### Scapy warning về MAC

Có thể thấy:

```text
WARNING: Mac address to reach destination not found. Using broadcast.
```

Cảnh báo này không nhất thiết làm fail demo, vì pingall và receiver đã chứng minh packet vẫn đi được. Khi chạy generator nên luôn thêm `--iface h1-eth0` hoặc `--iface h2-eth0`.

#### Receiver không in log ngay

Nếu `tail /tmp/h3_receiver.log` không thấy gì, nguyên nhân thường là buffering. Chạy receiver bằng `python3 -u`:

```bash
h3 sh -c "python3 -u SISTAR/BMv2/lab/receiver.py --iface h3-eth0 --duration 180 --interval 5 > /tmp/h3_receiver.log 2>&1 &"
```

#### Receiver hết thời gian

Receiver đang chạy với `--duration 120` hoặc `180`. Nếu log không tăng nữa, có thể receiver đã kết thúc. Chạy lại:

```bash
h3 pkill -f receiver.py
h3 sh -c "python3 -u SISTAR/BMv2/lab/receiver.py --iface h3-eth0 --duration 180 --interval 5 > /tmp/h3_receiver.log 2>&1 &"
```

#### `simple_switch_CLI` không connect khi apply pushback

Nếu pushback controller lỗi connect thrift, kiểm tra Mininet/BMv2 lab còn chạy không. Thrift port mapping mặc định:

```text
s1 -> 9090
s2 -> 9091
s3 -> 9092
```

Với source `h2 = 10.0.2.2`, upstream switch cần chặn là `s2`, thrift port `9091`.

### 11.8. Topology và địa chỉ cần nhớ

Topology:

```text
h1 benign client  -- s1 --\
                         s3 -- h3 victim
h2 attack client  -- s2 --/
```

IP/MAC:

```text
h1: 10.0.1.1 / 08:00:00:00:01:11
h2: 10.0.2.2 / 08:00:00:00:02:22
h3: 10.0.3.3 / 08:00:00:00:03:33
```

Switch ports trong lab:

```text
s1 port 1 -> h1
s1 port 2 -> s3
s2 port 1 -> h2
s2 port 2 -> s3
s3 port 1 -> s1
s3 port 2 -> s2
s3 port 3 -> h3
```

### 11.9. Ý nghĩa kết quả demo

Nếu demo hoàn tất, có thể trình bày như sau:

1. `pingall 0% dropped`: network topology và forwarding chạy được.
2. Receiver bắt được `10.0.1.1/ICMP`: traffic benign đi qua switch tới victim.
3. Receiver bắt được TCP/UDP từ `10.0.1.1`: Scapy benign generator hoạt động.
4. Attack-like từ `10.0.2.2` được gửi qua `s2` và `s3` tới `h3`, hoặc bị giảm/drop bởi `DDoS_ternary` tùy rule DT-CTS.
5. Sau khi apply pushback, `source_block` ở `s2` chặn `10.0.2.2`, nên packet từ attacker không tăng thêm ở receiver log.

### 11.10. Nếu cần kiểm tra rule đã được load

Trong terminal bình thường có thể dùng `simple_switch_CLI` để kiểm tra table entries khi lab đang chạy:

```bash
simple_switch_CLI --thrift-port 9091
```

Trong CLI của BMv2 có thể dùng các lệnh như:

```text
show_tables
table_dump MyIngress.source_block
table_dump MyIngress.DDoS_ternary
```

Thoát CLI bằng:

```text
quit
```

### 11.11. Lưu ý về git/status

Trước đó có 2 thay đổi phụ ngoài trọng tâm:

```text
AGENT_PROMPT_SLIDES.md
reproduction/src/__pycache__/model_pipeline.cpython-312.pyc
```

`AGENT_PROMPT_SLIDES.md` có vẻ bị thêm nhầm chữ `ss`. File `__pycache__` chỉ là cache Python, không nên commit. Nếu agent mới chuẩn bị commit thì cần kiểm tra `git status` và loại các thay đổi không liên quan.
