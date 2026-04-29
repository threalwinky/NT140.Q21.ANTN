# Cải tiến nhỏ ngoài paper

Đồ án thêm một cải tiến nhỏ lên ý tưởng pushback ban đầu:

- `gated_pushback`

Định nghĩa:

- Thay vì pushback ngay sau một lần phát hiện độc hại,
- hệ thống chỉ kích hoạt block upstream khi cùng một nguồn bị phát hiện độc hại trong `2` cửa sổ liên tiếp.

Vì sao cải tiến này hợp lý:

- detector trong thực tế có thể có false positive
- block ngay lập tức thường quá nhạy và dễ chặn nhầm
- một lớp xác nhận nhỏ giúp giữ traffic hợp lệ tốt hơn

Mục tiêu:

- giảm false positive trong mitigation
- giảm mất mát benign traffic
- vẫn giữ attack traffic ở mức thấp

So sánh:

## Immediate pushback

- triệt tiêu attack rất mạnh
- gây collateral damage lớn
- false block events: `20`

## Gated pushback

- yếu hơn một chút so với immediate pushback về mức độ chặn tuyệt đối
- nhưng giảm mạnh collateral damage
- false block events: `3`
- benign bytes preserved: `2,020,443,640`

Kết luận:

> `gated_pushback` là một tinh chỉnh kỹ thuật nhỏ nhưng thực dụng lên logic pushback của SISTAR. Nó hy sinh một phần rất nhỏ tính quyết liệt để đổi lấy khả năng giữ benign traffic tốt hơn rõ rệt.

Câu nên dùng trong báo cáo:

> Ngoài việc tái hiện ý tưởng phát hiện bằng `DT-CTS` và cơ chế pushback, nhóm đề xuất một cải tiến nhỏ là `gated_pushback`, trong đó việc chặn upstream chỉ được kích hoạt khi cùng một nguồn bị phát hiện độc hại trong hai cửa sổ liên tiếp. Cải tiến này giúp giảm chặn nhầm đáng kể trong khi vẫn giữ được phần lớn hiệu quả giảm thiểu tấn công.
