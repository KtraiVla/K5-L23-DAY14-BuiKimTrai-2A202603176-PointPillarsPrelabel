# Tổng hợp thay đổi kiểm nhãn & xác minh CVAT `#32` / `#33`

Trạng thái: **Đã đồng bộ CVAT `#32` (`D14-2A202603176-A`, 31 hộp) và `#33` (`D14-2A202603176-B`, 161 hộp)** với toàn bộ góc chiếu 7 camera (`+X` xanh đầu xe) và mặt cắt LiDAR; `max_diff = 0.000000` qua vòng đẩy-xuất CVAT (`0` Track). Task AI nháp `#34` trước đó không còn dùng làm tham chiếu; task `#35` (`D14-2A202603176-BONUS-TEST`) chỉ phục vụ kiểm thử Bonus Hướng 2 Nuclio.

## Các nhóm xử lý chính đã áp dụng và xuất lại

1. **Loại dương tính giả (FP) từ pre-label trên 15 frame:**
   - Gỡ bỏ hoàn toàn các hộp phản xạ ảo trên xe gắn cảm biến (ego-car ở 9 frame Set B).
   - Gỡ bỏ các hộp `Car` / `Cyclist` đặt nhầm lên bồn hoa/bụi cây (đặc biệt `s02f54`, `s03f57`, `s05f01`), cột biển báo, tủ điện ven đường và xe hai bánh đỗ không có người điều khiển (`docs/GUIDELINE.md` yêu cầu `Cyclist` phải có người).
2. **Chuẩn hóa xe tải (`Truck`) và xe buýt (`Bus`) trên Set B & Set A:**
   - Phân loại đúng `3 Bus` trên Set A (`s01f18`, `s03f31`, `s04f28`), `3 Bus` và `9 Truck` trên Set B (kể cả xe tải lớn China Post `~6.5 m` tại `s05f01` chỉnh lại hướng yaw 180°, xe tải cẩu `~6.9 m` tại `s01f27`/`s05f45`, xe ben `~10.4 m`, xe tải `~8.6 m` tại `s01f02`).
   - Bổ sung các phương tiện thật bị model bỏ sót trong phạm vi `<= 50 m`.
3. **Tinh chỉnh đáy/chiều cao, thuộc tính `occluded` và rà QA `vf_qa.py`:**
   - Rà lại các hộp từng báo lơ lửng/chìm/quá chật cho khớp cụm điểm LiDAR thực và cao độ mặt đường (`pointcloud_qa.csv`: giảm từ `62/283` xuống còn **`2/192` cảnh báo** `possible_tight_box` đều là `Bus` cạnh tường/xe lân cận).
   - Bổ sung cờ `occluded=true` trên CVAT cho các xe bị che một phần sau dải phân cách/bụi cây/xe khác (`12/31` hộp Set A gồm `s01f18 #2, #9`, `s04f28 #19, #25, #28`, ... và `46/161` hộp Set B), giữ trạng thái `AI_QA_REFINED_CVAT_EXPORTED` để người học xác nhận cuối.

## Tài liệu đối chiếu

- [review_checklist.csv](review_checklist.csv): bảng đủ **192 hộp** kèm `task_id`, `cvat_frame`, `cvat_object_id`, `reference_idx`, tọa độ, số điểm LiDAR và trạng thái `AI_QA_REFINED_CVAT_EXPORTED`.
- [review_warnings_62.csv](review_warnings_62.csv): tách riêng **2 hộp** có cờ `possible_tight_box` hợp lệ (tên file CSV được giữ theo kiểm tra cấu trúc của `verify_submission.py`).
- [live_cvat_review_snapshot.json](live_cvat_review_snapshot.json): SHA256 và đối chiếu thứ tự lớp từng frame khớp CVAT `#32` & `#33`.
