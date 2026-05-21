# Gated Pushback Improvement

Thư mục này chứa riêng phần cải tiến `gated_pushback` để so sánh với cơ chế pushback gốc/paper-like trong reproduction.

Kết quả ở đây không ghi đè thư mục `../output` của reproduction gốc. Tất cả output được ghi vào:

```text
reproduction/improvemen/output
```

## Ý tưởng chính

Trong mô phỏng gốc, `immediate_pushback` sẽ block source ngay sau một lần flow bị dự đoán là malicious. Cách này giảm attack rất nhanh nhưng dễ chặn nhầm benign traffic nếu model false positive.

Cải tiến `gated_pushback` chỉ block source sau 2 lần malicious liên tiếp:

```text
Lần 1 bị nghi ngờ attack  -> ghi nhận, chưa block
Lần 2 liên tiếp vẫn attack -> mới block source upstream
```

Mục tiêu là giảm false block và giữ benign traffic tốt hơn, trong khi vẫn giảm mạnh attack traffic tới victim.

## Chạy thí nghiệm cải tiến

Từ project root:

```bash
python3 reproduction/improvemen/run_gated_improvement.py
```

Hoặc từ thư mục này:

```bash
cd reproduction/improvemen
python3 run_gated_improvement.py
```

## Output quan trọng

Sau khi chạy, mở các file sau trong `output/`:

- `TEACHER_SUMMARY.md`: tóm tắt tiếng Việt để báo cáo.
- `gated_improvement_dashboard.png`: dashboard chính nên show cho thầy.
- `teacher_policy_comparison.png`: biểu đồ so sánh no pushback, immediate, gated.
- `teacher_attack_timeline.png`: attack bytes tới victim theo thời gian.
- `teacher_comparison_table.csv`: bảng số liệu chi tiết.
- `improvement_pushback_metrics.csv`: metric pushback raw.
- `improvement_pushback_detail.csv`: log mô phỏng theo từng source/time window.

## Cách đọc kết quả

- `no_pushback`: baseline, không chặn upstream nên attack tới victim nhiều nhất.
- `immediate_pushback`: đại diện hành vi gốc/paper-like trong reproduction, block ngay sau 1 lần phát hiện malicious.
- `gated_pushback`: cải tiến, chỉ block sau 2 lần malicious liên tiếp.

Điểm cần nhấn mạnh khi báo cáo:

```text
Immediate pushback chặn attack mạnh nhất nhưng false block cao.
Gated pushback vẫn giảm attack rất mạnh, đồng thời giảm chặn nhầm và giữ benign traffic tốt hơn.
```
