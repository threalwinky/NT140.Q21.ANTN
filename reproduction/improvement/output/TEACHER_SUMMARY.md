# Gated Pushback Improvement

## Mục tiêu

Thư mục này tách riêng phần cải tiến `gated_pushback` để so sánh rõ với cơ chế pushback gốc/paper-like trong reproduction.
Tất cả kết quả ở đây được ghi riêng trong `reproduction/improvement/output`, không ghi đè kết quả gốc ở `reproduction/output`.

## Dataset và model

- Dataset source: `Loaded CICIDS2017 combine.csv (paper-compatible BENIGN vs Wednesday DoS subset)`
- Model dùng cho mitigation: `DT-CTS` đã train từ pipeline reproduction hiện có.
- Trace pushback là mô phỏng flow-level gồm nhiều source theo time window, không phải đo trực tiếp từ mạng thật.

## Ý nghĩa các policy

| Policy | Ý nghĩa |
|---|---|
| `no_pushback` | Baseline: không chặn upstream. |
| `immediate_pushback` | Pushback gốc/paper-like: phát hiện malicious một lần là block source. |
| `gated_pushback` | Cải tiến: chỉ block source sau 2 lần malicious liên tiếp. |

## Kết quả chính

| Metric | No pushback | Immediate/original | Gated improvement |
|---|---:|---:|---:|
| Attack bytes tới victim | 1,086,319 | 166,883 | 167,316 |
| Benign bytes giữ lại | 4,733,448,168 | 4,596,858,402 | 4,644,432,863 |
| False block events | 0 | 3 | 0 |
| Attack reduction vs no pushback | 0.00% | 84.64% | 84.60% |
| Benign preserved vs no pushback | 100.00% | 97.11% | 98.12% |

## Nhận xét để báo cáo

- `immediate_pushback` giảm attack mạnh nhất nhưng false block cao: `3` lần chặn nhầm.
- `gated_pushback` vẫn giảm `84.60%` attack bytes so với không pushback.
- So với immediate, gated giảm false block từ `3` xuống `0`.
- Gated giữ lại `98.12%` benign bytes so với baseline, trong khi immediate chỉ giữ `97.11%`.

## File nên mở khi show cho thầy

1. `gated_improvement_dashboard.png`
2. `teacher_policy_comparison.png`
3. `teacher_attack_timeline.png`
4. `teacher_comparison_table.csv`