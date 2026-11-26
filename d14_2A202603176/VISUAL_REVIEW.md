# Rà soát nhãn A/B — còn cần người học kiểm tra

Trạng thái: **CHƯA XÁC NHẬN CHẤT LƯỢNG NHÃN ĐẠT**. Đây là ghi chú AI sau khi xem 15 ảnh tổng hợp gồm 7 camera và BEV, kết hợp heuristic `scripts/vf_qa.py`. Không phải nhãn chuẩn và không thay thế người gán nhãn. Không tự động xóa, thêm, đổi lớp hay dời hộp trong `ref_A.json`/`ref_B.json`.

Vòng tiếp theo đã có [object ID, tọa độ và đề xuất xử lý cụ thể](REVIEW_ACTIONS.md), [checklist 283 hộp](review_checklist.csv) và [62 hộp có cảnh báo](review_warnings_62.csv). Task #33 đã đổi tên thành `D14-2A202603176-B`.

## Các vị trí ưu tiên

Các frame CVAT dưới đây đếm từ **0**, theo thứ tự frame trong task lúc xuất backup. Mở đúng frame theo tên trước khi sửa. Dùng camera để nhận diện vật thể; dùng LiDAR và ba mặt cắt để xác định tâm, kích thước, đáy và khoảng cách 50 m. Phép chiếu một hộp rất gần cảm biến có thể trải rộng trên ảnh; không xóa chỉ vì hình chiếu lớn.

| Ưu tiên | Task / frame CVAT | Tên frame | Vị trí cần kiểm tra |
|---|---|---|---|
| Cao | B #33 / 5 | `s02f54` | Camera 07/08: nhiều hộp Car đỏ và Cyclist xanh nằm trên vùng bồn hoa/cây. Đối chiếu LiDAR để phân biệt vật thể thật với hộp thừa. |
| Cao | B #33 / 9 | `s05f01` | Camera 09: xe tải lớn màu xanh phía sau đang được phủ bởi hộp Car nhỏ ở phần đầu xe. Kiểm tra toàn xe, lớp Truck và kích thước; camera 05/06/07 cũng có hộp tại bụi cây. |
| Cao | B #33 / 3 | `s02f11` | Camera 05/09: có xe buýt trắng phía trước/ngã tư chưa thấy hộp Bus tương ứng. Kiểm tra xe có trong phạm vi 50 m và đủ điểm LiDAR để bổ sung theo guideline hay không. |
| Cao | B #33 / 8 | `s03f57` | Camera 05/09: kiểm tra xe lớn phía sau; camera 07/08 có hộp xanh/đỏ ở cây và biển chỉ đường. |
| Vừa | B #33 / 2 | `s01f48` | Kiểm tra hộp Car/Cyclist gần cây và các hộp lớn gần cảm biến; 8 hộp có cảnh báo heuristic. |
| Vừa | B #33 / 6 | `s03f08` | Kiểm tra các hộp chiếu lên tường/cây; xác nhận vật thể bằng nhiều camera và điểm LiDAR. |
| Vừa | B #33 / 7 | `s03f24` | Camera 05/06/09: kiểm tra Car ở dải cây giữa đường; không suy lỗi chỉ từ hộp chiếu lớn gần cảm biến. |
| Vừa | B #33 / 10 | `s05f24` | Camera 08: kiểm tra lớp/hộp tại dãy xe đạp, xe máy và vật thể sát vỉa hè; xác nhận các Car xa ở giao lộ. |
| Vừa | B #33 / 11 | `s05f45` | Camera 06/08/09: xe lớn màu xanh bên kia giao lộ cần kiểm tra lớp/kích thước và phạm vi; rà các Car ở vỉa hè. |
| Vừa | B #33 / 4 | `s02f29` | Kiểm tra các hộp rất gần xe gắn cảm biến và các Cyclist sát cây; hình chiếu rộng chưa đủ kết luận là hộp thừa. |
| Vừa | B #33 / 0, 1 | `s01f02`, `s01f27` | Hai Truck đã bổ sung có đối tượng tương ứng trên camera. Tiếp tục kiểm đáy, tâm, hướng đầu xe và toàn bộ kích thước theo điểm LiDAR. |
| Vừa | A #32 / 0, 1 | `s01f18`, `s03f31` | Rà các Car/Cyclist ở vùng cây/tường và hộp có cảnh báo; lần lượt có 2 và 6 cảnh báo heuristic. |
| Thấp hơn | A #32 / 2 | `s04f28` | Không có cảnh báo heuristic, nhưng vẫn phải xem đủ mọi vật thể và kiểm hộp Bus; không có cảnh báo không có nghĩa nhãn hoàn toàn đúng. |

## Danh sách theo từng hộp

[pointcloud_qa.csv](pointcloud_qa.csv) có 283 hàng, gồm part, frame, `idx`, lớp, khoảng cách, số điểm trong hộp, khoảng hở mặt đất và cảnh báo. `idx` là thứ tự hộp bắt đầu từ 1 trong file tham chiếu đã xuất, **không phải CVAT object ID**. Dùng thêm lớp/vị trí để tìm đúng hộp.

Có 62 hộp mang ít nhất một cảnh báo: 30 có thể quá chật, 15 có thể chìm, 26 có thể lơ lửng; tổng theo loại lớn hơn 62 do một hộp có thể có nhiều cảnh báo. Chưa có lỗi rỗng hoặc quá ít điểm theo heuristic này. Heuristic không phát hiện chắc chắn hộp cây bị gán thành xe và không tìm hết vật thể bị sót.

Ảnh tổng hợp được giữ **cục bộ**, không commit ảnh camera Data-VF. Có thể tạo lại bằng script `reproduce_reference_qa.py`; output ở `png_reference_A/` và `png_reference_B/` đã được gitignore.

## Sau khi sửa trên CVAT

1. Mở task [A #32](http://localhost:8080/tasks/32) và [B #33](http://localhost:8080/tasks/33), sửa theo `docs/GUIDELINE.md`, dùng **Shape**, rồi bấm **Save**.
2. Xuất lại đúng task A/B. Task #33 đã được đổi tên từ `D14-2A202603176-B-preview` thành `D14-2A202603176-B` để dùng lệnh `vf_cvat.py reference --task B`. Metadata trong file tham chiếu cũ giữ tên nguồn lúc xuất. Có thể tiếp tục dùng phương án backup và chuyển đổi như lần xuất trước. Không dùng `prelabel --replace`: thao tác đó xóa nhãn đã sửa.
3. Nếu A thay đổi, chạy lại sweep A, chọn cấu hình và tạo lại dự đoán B. Giữ bản tham chiếu cũ để đối chiếu; không ghi đè nhãn đã sửa trên CVAT bằng pre-label.
4. Tính lại compare A, chi phí B, QA và cập nhật bảng báo cáo. Chi phí 6.3/2.9 hiện tại chỉ đúng với các file đang được lưu.
5. Chạy `verify_submission.py` với Data-VF và SEED chính thức, commit/push bản cập nhật, sau đó dùng SHA mới khi nộp LMS. Ghi chú vòng kiểm nhãn chỉ được đánh dấu hoàn tất sau khi người học thực sự đã kiểm.
