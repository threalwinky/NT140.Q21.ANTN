# Hướng dẫn chạy mô phỏng SISTAR bằng Mininet + BMv2

Tài liệu này hướng dẫn chạy mô phỏng local-only: traffic đi qua các switch BMv2 chạy P4, switch phân loại DDoS bằng rule DT-CTS, và controller có thể cài rule pushback để chặn nguồn tấn công ở upstream switch.

## 1. Cảnh báo an toàn

- Chỉ chạy các script traffic trong Mininet hoặc mạng lab riêng.
- Không dùng `attack-lab` hoặc replay PCAP tới IP thật trên Internet/LAN thật.
- Script đã giới hạn đích trong các subnet lab `10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24` và giới hạn tốc độ/gói.
- `attack-lab` và PCAP replay yêu cầu flag xác nhận `--i-understand-this-is-mininet-only`.

## 2. Mô hình topology

Topology demo gồm 3 host và 3 switch:

```text
h1 benign client  ─ s1 ┐
                       ├─ s3 ─ h3 victim
h2 attack-lab     ─ s2 ┘
```

IP/MAC mặc định:

| Node | IP | MAC |
|---|---|---|
| h1 | `10.0.1.1` | `08:00:00:00:01:11` |
| h2 | `10.0.2.2` | `08:00:00:00:02:22` |
| h3 | `10.0.3.3` | `08:00:00:00:03:33` |

Thrift ports:

| Switch | Thrift port |
|---|---:|
| s1 | `9090` |
| s2 | `9091` |
| s3 | `9092` |

## 3. Cài phần mềm cần thiết

Cài Python dependency của lab:

```bash
cd /home/team/NT140.Q21.ANTN/Final
python3 -m pip install -r reproduction/requirements.txt
python3 -m pip install -r SISTAR/BMv2/requirements-lab.txt
```

Cài Mininet nếu máy chưa có:

```bash
sudo apt update
sudo apt install -y mininet
```

Cần có thêm các lệnh của P4/BMv2:

```bash
which p4c-bm2-ss
which simple_switch
which simple_switch_CLI
which mn
```

Nếu một trong các lệnh trên chưa tồn tại, hãy cài môi trường P4/BMv2 theo gói hoặc VM chính thức mà lớp/máy lab của bạn hỗ trợ. Sau khi cài xong, chạy lại các lệnh `which` để xác nhận.

## 4. Sinh rule DT-CTS cho BMv2

Mặc định dùng synthetic dataset nhỏ, ổn định và chạy offline:

```bash
cd /home/team/NT140.Q21.ANTN/Final
python3 SISTAR/BMv2/tools/export_dtcts_rules.py \
  --dataset synthetic \
  --output-dir SISTAR/BMv2/generated \
  --topology lab3
```

Kết quả mong đợi:

```text
SISTAR/BMv2/generated/dtcts_rules.json
SISTAR/BMv2/generated/s1_commands.cli
SISTAR/BMv2/generated/s2_commands.cli
SISTAR/BMv2/generated/s3_commands.cli
```

Nếu đã cấu hình Kaggle dataset trong phần reproduction, có thể đổi sang:

```bash
python3 SISTAR/BMv2/tools/export_dtcts_rules.py \
  --dataset kaggle \
  --output-dir SISTAR/BMv2/generated \
  --topology lab3
```

## 5. Chạy Mininet/BMv2 lab

Từ thư mục project:

```bash
cd /home/team/NT140.Q21.ANTN/Final
sudo python3 SISTAR/BMv2/lab/mininet_sistar.py \
  --p4 SISTAR/BMv2/DT.p4 \
  --commands-dir SISTAR/BMv2/generated
```

Script sẽ:

1. Compile `DT.p4` thành `SISTAR/BMv2/generated/DT.json`.
2. Start `s1`, `s2`, `s3` bằng `simple_switch`.
3. Load threshold registers, DDoS ternary rules và IPv4 forwarding rules bằng `simple_switch_CLI`.
4. Mở Mininet CLI.

Nếu đã compile sẵn và chỉ muốn chạy lại lab:

```bash
sudo python3 SISTAR/BMv2/lab/mininet_sistar.py \
  --no-compile \
  --commands-dir SISTAR/BMv2/generated
```

## 6. Quan sát packet tới victim

Trong Mininet CLI, chạy receiver ở `h3`:

```bash
h3 python3 SISTAR/BMv2/lab/receiver.py --duration 60 --interval 5
```

Receiver sẽ in tổng số packet nhận được theo source IP và protocol.

## 7. Gửi traffic benign

Trong Mininet CLI:

```bash
h1 python3 SISTAR/BMv2/lab/traffic_generator.py \
  --mode benign \
  --dst 10.0.3.3 \
  --count 20 \
  --pps 2
```

Kỳ vọng: `h3` vẫn thấy packet từ `10.0.1.1`.

## 8. Gửi traffic attack-like trong lab

Trong Mininet CLI:

```bash
h2 python3 SISTAR/BMv2/lab/traffic_generator.py \
  --mode attack-lab \
  --dst 10.0.3.3 \
  --count 200 \
  --pps 20 \
  --i-understand-this-is-mininet-only
```

Kỳ vọng: các packet attack-like từ `10.0.2.2` bị giảm hoặc drop theo rule DT-CTS đã export vào bảng `MyIngress.DDoS_ternary`.

## 9. Áp dụng pushback mitigation

Mở terminal khác trong cùng thư mục project, cài rule chặn source `10.0.2.2` ở upstream switch `s2`:

```bash
cd /home/team/NT140.Q21.ANTN/Final
python3 SISTAR/BMv2/lab/pushback_controller.py \
  --source-ip 10.0.2.2 \
  --upstream-switch s2 \
  --apply
```

Sau đó gửi lại traffic attack-like từ `h2`. Kỳ vọng: packet từ `10.0.2.2` bị chặn ngay tại `s2`, trước khi về `s3/h3`.

Có thể xem trước command mà chưa cài rule bằng cách bỏ `--apply`:

```bash
python3 SISTAR/BMv2/lab/pushback_controller.py \
  --source-ip 10.0.2.2 \
  --upstream-switch s2
```

## 10. Replay PCAP tùy chọn

Chỉ dùng PCAP tự cung cấp và vẫn replay vào IP lab:

```bash
h2 python3 SISTAR/BMv2/lab/pcap_replay.py \
  --pcap /path/to/sample.pcap \
  --dst 10.0.3.3 \
  --count 200 \
  --pps 20 \
  --i-understand-this-is-mininet-only
```

Script sẽ rewrite destination IP về `10.0.3.3`, giới hạn số packet và tốc độ gửi.

## 11. Kiểm tra lỗi thường gặp

### `Required command not found: p4c-bm2-ss`

P4 compiler chưa có trong PATH. Cài P4 compiler/BMv2 rồi kiểm tra lại bằng `which p4c-bm2-ss`.

### `Required command not found: simple_switch`

BMv2 chưa có trong PATH. Cài BMv2 rồi kiểm tra lại bằng `which simple_switch`.

### Receiver không thấy packet benign

Kiểm tra lab đang chạy, rule forwarding đã load, và bạn chạy generator trong Mininet CLI bằng prefix `h1` hoặc `h2`.

### Attack-like traffic vẫn tới h3 sau pushback

Kiểm tra đúng thrift port/switch upstream. Với topology mặc định, chặn `h2` tại `s2` dùng thrift port `9091`.

## 12. File chính trong lab

| File | Vai trò |
|---|---|
| `DT.p4` | P4 pipeline: feature extraction, DT-CTS ternary table, source-block pushback, IPv4 forwarding |
| `tools/export_dtcts_rules.py` | Train DT-CTS và export rule BMv2 |
| `tools/tree_to_ternary.py` | Chuyển attack leaves của tree thành 10-bit feature-bin values |
| `tools/cli_templates.py` | Sinh command cho `simple_switch_CLI` |
| `lab/mininet_sistar.py` | Start topology Mininet + BMv2 |
| `lab/traffic_generator.py` | Sinh traffic benign/attack-like an toàn trong lab |
| `lab/receiver.py` | Đếm packet tới victim |
| `lab/pushback_controller.py` | Cài rule pushback `source_block` |
| `lab/pcap_replay.py` | Replay PCAP tùy chọn, có giới hạn tốc độ |
