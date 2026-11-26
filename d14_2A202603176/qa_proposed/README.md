# Bản AI hỗ trợ kiểm nhãn — chưa phải tham chiếu để nộp

Đã tạo và kiểm trực tiếp trên [CVAT task #34](http://localhost:8080/tasks/34), job [#34](http://localhost:8080/tasks/34/jobs/34), tên `D14-2A202603176-B-AI-QA-review`.

Task này tách riêng khỏi A #32 và B #33. `ref_A.json`/`ref_B.json` vẫn giữ nhãn người học đã lưu trước đó. Không dùng `B_proposal.json` làm nhãn đã được người kiểm, không đo lại rồi thay bảng số liệu bắt buộc bằng một tham chiếu AI chưa xác nhận.

## Các thay đổi đã thực hiện trong bản đề xuất

1. Frame CVAT 5, `s02f54`: bỏ 6 hộp có source object ID `113, 114, 117, 120, 122, 126` của task #33. Ảnh camera chiếu các hộp này lên cây/bồn hoa; các mặt cắt LiDAR cho thấy cấu trúc cảnh lân cận. Đây là nhận định của AI, chưa có xác nhận người học.
2. Frame CVAT 9, `s05f01`: source object #197 của task #33 được đề xuất thành **Truck**, object **#191 trong task mới #34**. Hộp cũ Car chỉ phủ một phần đầu xe; hộp đề xuất rộng/cao hơn và đổi hướng đầu xe về phía cảm biến.
3. Chiều dài Truck **6.8 m là ước lượng**, do không thấy rõ phần đuôi. Kích thước đề xuất L/W/H là `6.8/2.55/3.15` m; đây không phải phép đo chuẩn cho toàn bộ xe. Trường `note` trên CVAT ghi rõ `AI_QA_PROPOSAL`, chiều dài tạm thời và `NOT HUMAN VALIDATED`. Source của hộp đã chỉnh được đặt `auto`.

Không có quy tắc tự động “xóa mọi hộp có cảnh báo” hay “nới mọi hộp cho hết cảnh báo”. Hai source object #106/#115 ở hàng rào vẫn giữ để kiểm riêng. Các cảnh báo khác vẫn cần đối chiếu vật thể, không tự coi là lỗi thật.

## Kiểm chứng đã thực hiện

- Đủ 12 frame B; tổng 236 hộp trong bản đề xuất, so với 242 hộp tham chiếu cũ.
- Mở từng frame trên CVAT #34; số hộp và số lớp khớp `B_proposal.json`.
- Mở Details của Truck #191 trên CVAT: đúng L/W/H `6.8/2.55/3.15`, đúng lớp Truck và đúng ghi chú bất định.
- Archive được kiểm CRC; dữ liệu point cloud và camera giữ nguyên byte so với backup nguồn.
- Tâm/kích thước/yaw đều hữu hạn, kích thước dương; không có Track.
- Hai file tham chiếu gốc giữ nguyên SHA256. Không thay lịch sử 5b hoặc chạy lại sweep theo nhãn đề xuất.

Các kiểm tra trên xác nhận bản đề xuất đã nhập đúng dữ liệu được chuẩn bị, **không xác nhận mọi nhãn đã đúng**. Có thể còn hộp thừa/sót ở các frame khác. Phần chiều dài xe tải đặc biệt cần người học/coach xác nhận bằng các view có đủ bằng chứng.

## File trong thư mục

- `B_proposal.json`: 12 frame với nhãn đề xuất, metadata đánh dấu chưa có người kiểm.
- `B_changes.json`: nhật ký 6 hộp bỏ và một hộp Truck chỉnh, lưu hình học trước/sau và source ID.
- `cvat_validation.json`: bằng chứng kiểm số lượng/lớp qua UI và ghi chú bất định.

Ảnh camera/BEV và các mặt cắt được giữ cục bộ ở outputs của phiên hỗ trợ và các thư mục `png_*` đã gitignore, không đưa Data-VF lên GitHub.
