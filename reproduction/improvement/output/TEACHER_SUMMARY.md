# Hierarchical Confidence-Aware Pushback

## Mục tiêu

Thư mục này tách riêng phần cải tiến `Hierarchical Confidence-Aware Pushback` để so sánh với cơ chế pushback gốc/paper-like trong reproduction.
Tất cả kết quả ở đây được ghi riêng trong `reproduction/improvement/output`, không ghi đè kết quả gốc ở `reproduction/output`.

## Dataset và model

- Dataset source: `Loaded CICIDS2017 combine.csv from combine.csv (paper-compatible BENIGN vs Wednesday DoS subset)`
- Model mitigation dùng hai tầng DT-CTS: edge detector 3 feature và core detector đầy đủ để xác nhận.
- Trace pushback là mô phỏng flow-level gồm nhiều source theo time window, không phải đo trực tiếp từ mạng thật.

## Ý nghĩa các policy

| Policy | Ý nghĩa |
|---|---|
| `no_pushback` | Baseline: không chặn upstream. |
| `immediate_pushback` | Pushback gốc/paper-like: phát hiện malicious một lần là block source. |
| `hierarchical_confidence_pushback` | Cải tiến: edge và core cùng tích lũy suspicion score trước khi leo thang mitigation. |

## Kết quả chính

| Metric | No pushback | Immediate/original | Hierarchical improvement |
|---|---:|---:|---:|
| Attack bytes tới victim | 5,876,251 | 0 | 4,591 |
| Benign bytes giữ lại | 2,196,901,718 | 1,760,928,313 | 2,052,047,683 |
| False block events | 0 | 11 | 0 |
| Attack reduction vs no pushback | 0.00% | 100.00% | 99.92% |
| Benign preserved vs no pushback | 100.00% | 80.16% | 93.41% |

## Nhận xét để báo cáo

- `immediate_pushback` giảm attack mạnh nhất về tốc độ phản ứng nhưng false block cao: `11` lần chặn nhầm.
- `hierarchical_confidence_pushback` vẫn giảm `99.92%` attack bytes so với không pushback.
- So với immediate, hierarchical giảm false block từ `11` xuống `0`.
- Hierarchical giữ lại `93.41%` benign bytes so với baseline, trong khi immediate chỉ giữ `80.16%`.
- Số lần phản ứng theo mức của hierarchical: local rate-limit = `23`, upstream pushback = `10`, hard block = `8`.

## File nên mở khi show cho thầy

1. `hierarchical_improvement_dashboard.png`
2. `teacher_policy_comparison.png`
3. `teacher_attack_timeline.png`
4. `teacher_comparison_table.csv`