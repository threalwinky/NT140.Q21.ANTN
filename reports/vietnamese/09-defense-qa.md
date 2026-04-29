# Câu hỏi và trả lời khi bảo vệ

## Câu 1. Vì sao nhóm chọn paper này?

Gợi ý trả lời:

> Nhóm chọn paper này vì paper mới, thuộc ACM CCS 2025, đúng phạm vi network security, và có cả đóng góp về thuật toán lẫn hệ thống. Ngoài ra, ý tưởng cốt lõi của paper có thể tái hiện một phần bằng software mà không cần đầy đủ phần cứng gốc.

## Câu 2. Đóng góp chính của paper là gì?

Gợi ý trả lời:

> Đóng góp chính là kết hợp phát hiện DDoS bằng cây quyết định có ràng buộc threshold với cơ chế pushback phân tán trong programmable data plane.

## Câu 3. Nhóm đã tái hiện chính xác phần nào?

Gợi ý trả lời:

> Nhóm tái hiện các ý tưởng cốt lõi của paper trong môi trường phần mềm rút gọn: `DT-CTS` để giảm độ phức tạp mô hình, so sánh threshold với baseline, và cơ chế pushback để giảm attack traffic ở upstream.

## Câu 4. Vì sao không tái hiện phần Tofino?

Gợi ý trả lời:

> Nhóm không có quyền truy cập programmable switch thật, và môi trường local cũng không có đầy đủ P4/BMv2 stack để tái hiện phần cứng đúng như paper. Vì vậy nhóm tập trung vào reproduction rút gọn nhưng vẫn có đánh giá định lượng rõ ràng.

## Câu 5. Vì sao dùng CICIDS2017 Wednesday?

Gợi ý trả lời:

> Vì paper nhắc tới CICIDS2017 trong phần đánh giá, và Wednesday là ngày chứa nhiều hành vi DoS/DDoS như Hulk, GoldenEye, slowloris và Slowhttptest, nên rất phù hợp với bài toán của nhóm.

## Câu 6. Vì sao DT-CTS thú vị nếu F1 thấp hơn DT?

Gợi ý trả lời:

> Vì mục tiêu của paper không chỉ là tối đa hóa F1, mà là đạt trade-off hợp lý giữa hiệu năng và khả năng triển khai. Trong reproduction của nhóm, `DT-CTS` giảm threshold `31.82%`, và đó chính là phần bám sát ý tưởng paper nhất.

## Câu 7. Vì sao không chọn RF làm mô hình cuối nếu RF cũng mạnh?

Gợi ý trả lời:

> RF mạnh về phân loại, nhưng dùng rất nhiều threshold hơn. Trong kết quả của nhóm, RF dùng `115` threshold trong khi DT-CTS chỉ dùng `15`, nên RF kém hấp dẫn hơn nếu nhìn từ góc độ triển khai.

## Câu 8. Đóng góp riêng của nhóm ngoài paper là gì?

Gợi ý trả lời:

> Nhóm đề xuất `gated_pushback`, tức là chỉ block upstream sau hai lần phát hiện liên tiếp. Cải tiến này giảm false block từ `20` xuống `3` trong khi vẫn giảm mạnh attack traffic.

## Câu 9. Kết quả quan trọng nhất của nhóm là gì?

Gợi ý trả lời:

> Kết quả quan trọng nhất là bản reproduction rút gọn vẫn chứng minh được hai ý tưởng chính của SISTAR: mô hình có thể gọn hơn mà vẫn đủ hiệu quả, và pushback giúp giảm mạnh attack traffic trước khi tới victim.

## Câu 10. Nếu có thêm thời gian thì nhóm sẽ làm gì?

Gợi ý trả lời:

> Nhóm sẽ triển khai đầy đủ hơn trên BMv2/P4, mở rộng topology, và so sánh thêm các chiến lược phân bổ threshold hoặc nhiều chính sách pushback khác.
