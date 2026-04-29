# Dàn ý thuyết trình

Đây là một dàn ý ngắn gọn, phù hợp với kiểu thuyết trình môn học.

## Slide 1. Tiêu đề

- tên paper
- thành viên nhóm
- câu claim ngắn gọn của đồ án

## Slide 2. Bài toán

- DDoS khó phát hiện nhanh
- phát hiện tập trung làm tăng độ trễ
- switch có giới hạn tài nguyên

## Slide 3. Ý tưởng paper

- in-switch detection
- `DT-CTS`
- feature encoding
- distributed pushback

## Slide 4. Vì sao paper này đáng làm

- mới và venue mạnh
- không chỉ lý thuyết
- kết hợp cả detection và mitigation

## Slide 5. Nhóm tái hiện gì

- reproduction phần mềm rút gọn
- `DT`, `RF`, `DT-CTS`
- mô phỏng pushback
- một cải tiến nhỏ: `gated_pushback`

## Slide 6. Dataset và feature

- Kaggle CICIDS2017 Wednesday
- bài toán benign vs attack
- 5 feature được chọn

## Slide 7. Kết quả classification

- chiếu `classification_f1.png`
- giải thích `DT`, `RF`, `DT-CTS`

## Slide 8. Kết quả threshold

- chiếu `threshold_usage.png`
- giải thích vì sao ít threshold quan trọng cho deployability

## Slide 9. Kết quả pushback

- chiếu `pushback_attack_bytes.png`
- so sánh `no_pushback`, `immediate_pushback`, `gated_pushback`

## Slide 10. Cải tiến của nhóm

- định nghĩa `gated_pushback`
- giải thích vì sao nó giảm false blocking

## Slide 11. Giới hạn

- không có Tofino thật
- không tái hiện đúng tài nguyên phần cứng
- topology đơn giản hơn paper

## Slide 12. Kết luận

- nhóm đã tái hiện được ý tưởng chính của SISTAR ở dạng rút gọn
- cho thấy rõ trade-off giữa hiệu năng và deployability
- cho thấy pushback upstream giúp giảm attack traffic hiệu quả
