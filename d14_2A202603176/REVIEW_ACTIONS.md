# Vòng kiểm nhãn tiếp theo — có object ID cụ thể

Trạng thái: **Đề xuất kiểm tra, chưa áp dụng thay đổi nhãn**. Đã đọc trực tiếp sidebar của cả 15 frame trên CVAT: đủ 41 hộp A và 242 hộp B; số lượng và thứ tự lớp khớp file tham chiếu. Việc đọc sidebar không xác nhận hộp đã đúng hình học hoặc đúng vật thể.

Task #33 hiện tên `D14-2A202603176-B`. Việc đổi tên đã lưu; hình học và lớp của nhãn vẫn giữ nguyên. Task A #32 không đổi.

## Những hộp ưu tiên đã có ảnh riêng

| Task / frame CVAT | Tên frame | Object ID đang thấy trên CVAT | Phát hiện khi xem ảnh | Cách xử lý sau khi người học kiểm |
|---|---|---|---|---|
| B #33 / 5 | `s02f54` | 113, 114, 117, 120 | Các hộp Cyclist chiếu lên cây/bồn hoa; chưa thấy người điều khiển xe tương ứng. Đặc biệt #113 có đáy cao hơn mặt đường heuristic 1.14 m. | Đối chiếu các camera và LiDAR. Nếu đúng là cây/bồn hoa hoặc xe hai bánh không có người lái thì xóa hộp, không chỉnh xuống đất để giữ lại một vật thể không thuộc lớp. |
| B #33 / 5 | `s02f54` | 122, 126 | Hai hộp Car chiếu lên vùng bồn hoa trong camera 07/08. | Kiểm LiDAR và camera; xóa nếu không có xe thật. Không xóa chỉ dựa trên việc hộp có ít điểm. |
| B #33 / 5 | `s02f54` | 106, 115 | Hộp nhỏ tại hàng rào/cây bên trái; ảnh có thể bị che. | Kiểm tra riêng, không gộp vào quyết định xóa tự động. Với Cyclist phải thấy/có cơ sở nhận ra người đang lái hoặc ngồi trên xe. |
| B #33 / 9 | `s05f01` | 197 | Camera 09 cho thấy xe tải lớn màu xanh, nhưng hộp hiện tại là Car: tâm khoảng `(-0.59, 10.00, -0.77)` m, L/W/H khoảng `4.17/1.78/1.70` m. Side/Front cho thấy nhiều điểm phía trên và ngoài hộp. | Kiểm nhận diện Truck rồi vẽ/chỉnh lại hộp bao toàn xe, đáy sát đường, đúng đầu xe. Không chỉ đổi lớp mà giữ kích thước Car. Phần sau xe bị che nên chưa đưa ra kích thước chính xác thay người gán nhãn. |

Các ID là **client object ID trong phiên được quan sát**. Sau import hoặc thay đổi nhãn, ID có thể đổi; kiểm thêm lớp, tâm XYZ và hình học để tránh sửa nhầm hộp.

## Kiểm đủ 283 hộp và 62 cảnh báo

- [review_checklist.csv](review_checklist.csv): đủ 283 hộp, có task, frame CVAT, object ID, reference idx, XYZ, kích thước, yaw, số điểm, khoảng hở mặt đất, cảnh báo và ô ghi quyết định. Mọi dòng bắt đầu ở `PENDING_HUMAN_REVIEW`; chưa đánh dấu kiểm xong thay người học.
- [review_warnings_62.csv](review_warnings_62.csv): 62 hộp có ít nhất một cảnh báo heuristic, được tách riêng để kiểm trước.
- [live_cvat_review_snapshot.json](live_cvat_review_snapshot.json): bản đối chiếu số lượng/lớp với sidebar đang chạy và SHA256 của các file tham chiếu tại lúc chuẩn bị.
- Ảnh camera/BEV theo object ID của hai frame ưu tiên và 66 hình Top/Side/Front đã được tạo **cục bộ**. Những hình này không được đưa lên GitHub vì có dữ liệu cảnh và không phải file bắt buộc của bài nộp. Chúng được cung cấp trong thư mục outputs của phiên hỗ trợ.

Ở các hình Top/Side/Front: xanh là điểm trong hộp hiện tại, xám là điểm lân cận, đỏ là biên hộp, cam là mặt đất ước lượng. Các trục đã được xoay về hệ cục bộ của hộp. Đường mặt đất vẫn là heuristic; điểm ngoài hộp có thể thuộc vật bên cạnh. Không dùng ảnh này để tự động nới toàn bộ hộp cho hết cảnh báo.

## Cách hoàn tất vòng kiểm

1. Người học xác nhận từng vật thể và ghi quyết định thực tế: giữ, xóa, thêm, đổi lớp hoặc chỉnh hình học. Với trường hợp chưa chắc, ghi `UNCERTAIN_CLASS`, `UNCERTAIN_SCOPE` hoặc `LOW_VISIBILITY` theo guideline.
2. Áp dụng trên CVAT, kiểm Top/Side/Front và camera, rồi **Save**. Không dùng `prelabel --replace`.
3. Xuất tham chiếu mới sau Save. Nếu sửa A thì chạy lại sweep A và compare; nếu cấu hình thay đổi thì tạo lại dự đoán B để đo. Không chọn nhãn để làm chi phí thấp đi.
4. Chạy lại QA và kiểm tra cấu trúc. Cập nhật số liệu báo cáo và push commit mới. Chỉ đánh dấu chất lượng đã kiểm sau khi người học thật sự xem và xác nhận.

## Các phần khác đã chuẩn bị

- Nhận xét người học cung cấp về xe bus bị sót đã được sửa câu chữ và đưa vào mục 3 báo cáo, ghi đúng là nhận xét **sau** thực nghiệm.
- [COACH_NOTE_DRAFT.md](COACH_NOTE_DRAFT.md) đã có lời giải thích thiếu 5b; chưa gửi và chưa có phản hồi coach.
- Repo GitHub đã có bộ file kỹ thuật. Chưa xác nhận đã nộp LMS; đường link repo GitHub không phải đường dẫn trang bài nộp LMS.
