# Báo cáo Day 14 — Bui Kim Trai — 2A202603176

- Mã học viên dùng với `--student`: `2A202603176`.
- `seed_tag`: `393590736f`; SEED không được lưu trong bài nộp.
- Tập A: `s01f18`, `s03f31`, `s04f28`.
- Tập B: `s01f02`, `s01f27`, `s01f48`, `s02f11`, `s02f29`, `s02f54`, `s03f08`, `s03f24`, `s03f57`, `s05f01`, `s05f24`, `s05f45`.
- Các số đo dưới đây dùng nhãn đã lưu trên CVAT cá nhân. Báo cáo ghi nhận kết quả kỹ thuật và những yêu cầu còn thiếu, chưa xác nhận chất lượng nhãn đạt toàn bộ rubric.

## 1. Dự đoán trước sweep (bước 5b)

**Thiếu bằng chứng dự đoán trước sweep.** Commit `053e29949860394539643056ae41a1ad0f36d7a0` có tiêu đề `5b: du doan truoc sweep`, nhưng nội dung báo cáo tại commit này chỉ là template: hai dòng dự đoán vẫn là dấu ba chấm. Tiêu đề commit không chứng minh đã viết dự đoán.

Không bổ sung một dự đoán rồi trình bày như đã viết trước sweep, không đổi thời gian và không viết lại lịch sử Git. Tiêu chí 5b chưa hoàn thành; việc chấp nhận thiếu sót này thuộc quyết định của coach.

Đã chuẩn bị [bản nháp giải thích gửi coach](../../d14_2A202603176/COACH_NOTE_DRAFT.md), nhưng chưa gửi và chưa có quyết định của coach.

## 2. Tập A: sửa tay và tune

`pred_A.json` giữ nguyên dự đoán gốc: 82 hộp. `ref_A.json` có 41 hộp trên đủ 3 frame: 29 Car, 2 Pedestrian, 7 Cyclist và 3 Bus. Nguồn nhãn là task CVAT #32, `D14-2A202603176-A`, sau khi người học lưu sửa nhãn. Task này được tạo từ bản đã lọc `score_thr=0.4`, `min_points=5` gồm 49 hộp; bản đó được giữ riêng trong `pred_A_filtered.json`. Bảng dưới là phép đo lại so với tham chiếu, không phải nhật ký từng thao tác trên CVAT.

Chi phí theo đề: `0.3 × xóa + 1.0 × thêm + 0.5 × sửa`, chỉ tính hộp trong phạm vi 50 m; ghép bằng BEV IoU tối thiểu 0.3.

| Cấu hình | Số hộp dự đoán | Xóa | Thêm | Sửa | Chi phí |
|---|---:|---:|---:|---:|---:|
| Gốc: `score_thr=0.1`, `min_points=0` | 82 | 44 | 3 | 0 | 16.2 |
| `best_config.json`: `score_thr=0.4`, `min_points=5` | 49 | 11 | 3 | 0 | 6.3 |

Chỉ hai tham số trên thay đổi so với cấu hình gốc. Các tham số về voxel, phép xoay, NMS, range và kích thước giữ giá trị mặc định.

Sweep bắt buộc gồm 15 cấu hình: `score_thr=0.1,0.2,0.3,0.4,0.5` kết hợp `min_points=0,5,10`, lưu ở [sweep.csv](../../d14_2A202603176/sweep.csv). Tại `score_thr=0.4`, cả ba giá trị `min_points` đồng hạng chi phí 6.3 trên A. Script chọn hàng đầu là `min_points=0`. Cấu hình cuối dùng `min_points=5`, một phương án đồng hạng đã được sử dụng khi tạo task CVAT trước đó; dữ liệu A không chứng minh giá trị 5 tốt hơn 0 hoặc 10.

Leave-one-out dưới đây được tái dựng từ các cột chi phí từng frame trong `sweep.csv`, dùng quy tắc chọn hàng đầu khi bằng điểm. Đây không phải bản chép lại đầu ra terminal nguyên gốc:

```text
s01f18: selected {'score_thr': 0.4, 'min_points': 0} -> 2.5 (best possible 2.5)
s03f31: selected {'score_thr': 0.4, 'min_points': 0} -> 2.2 (best possible 2.2)
s04f28: selected {'score_thr': 0.4, 'min_points': 0} -> 1.6 (best possible 1.6)
```

| Frame A | Chi phí gốc | Chi phí cấu hình cuối |
|---|---:|---:|
| `s01f18` | 6.7 | 2.5 |
| `s03f31` | 7.0 | 2.2 |
| `s04f28` | 2.5 | 1.6 |

Trong grid bắt buộc, các lần bỏ một frame đều chọn cùng ngưỡng score; cấu hình cuối đồng hạng và cho cùng kết quả A. Đây là bằng chứng ổn định trong grid nhỏ này, chưa đủ để kết luận tổng quát hóa tốt.

Sau đó có thử nghiệm mở rộng 564 cấu hình trên A, gồm ngưỡng theo lớp, số điểm tối thiểu và merge NMS. Ứng viên `thr_car=0.44`, `score_thr=0.4`, `min_points=0` giảm chi phí A xuống 5.7, nhưng leave-one-out mở rộng không ổn định: khi bỏ `s04f28`, cấu hình được chọn từ hai frame còn lại có chi phí 2.6 trên frame giữ lại, so với 1.6 của cấu hình cuối. Khi đo ứng viên trên B, chi phí là 19.9 với 19 hộp cần thêm. Ứng viên này không được dùng cho bài nộp. Chi tiết lưu trong [improvement_A_only](../../d14_2A202603176/improvement_A_only/).

Việc so sánh lại ứng viên và cấu hình cũ đã diễn ra khi có nhãn B. Phần thử nghiệm mở rộng là phân tích thăm dò; B không còn là một lần kiểm thử độc lập chưa từng được xem. Không sửa nhãn tham chiếu hoặc công thức chấm để giảm chi phí.

## 3. Trước/sau (bước 8)

![So sánh cấu hình gốc và cấu hình cuối trên s01f18](../../d14_2A202603176/compare/s01f18.jpg)

Có đủ ảnh so sánh của cả ba frame trong [compare](../../d14_2A202603176/compare/). Tổng chi phí A giảm từ 16.2 xuống 6.3, tức `(16.2 - 6.3) / 16.2 × 100 = 61.11%`.

Số hộp phải xóa giảm 44 xuống 11; số hộp phải thêm vẫn là 3 và số hộp sửa theo ngưỡng của script là 0. Mức giảm 9.9 điểm bằng `33 × 0.3`, đến từ giảm hộp thừa. Đây là giảm chi phí theo công thức, chưa phải mức tiết kiệm thời gian thực tế.

**Nhận xét cá nhân do người học cung cấp sau khi xem tập A** (AI chỉ sửa câu chữ):

> Ở tập A, tôi thấy mô hình bỏ sót một vài vật thể, chẳng hạn như xe bus.

Nhận xét này phù hợp với số đo hiện tại: cả cấu hình gốc và cấu hình cuối còn 3 hộp cần thêm trên A; ba hộp bổ sung trong tham chiếu là Bus. Việc tăng threshold đã giảm hộp thừa theo bảng số đo, nhưng không bổ sung được ba vật thể này. Phần giải thích số liệu ở đây do công cụ tổng hợp; không trình bày như nhận xét về threshold do người học đã tự cung cấp.

**Đối chiếu dự đoán 5b:** không có nội dung dự đoán trước sweep để kết luận đúng hay sai. Nhận xét trên được cung cấp sau khi đã có kết quả, không phải bằng chứng 5b và không được ghi lùi thời điểm.

## 4. Tập B

`pred_B.json` có 243 hộp, metadata cấu hình khớp `best_config.json`. `ref_B.json` có 242 hộp trên đủ 12 frame: 190 Car, 3 Pedestrian, 47 Cyclist và 2 Truck. Nguồn là task CVAT #33, `D14-2A202603176-B-preview`, sau khi lưu nhãn. File được lấy từ bản sao lưu task rồi chuyển cuboid bằng hàm `scripts.vf_common.cuboid_from_cvat` của lab; không lấy nhãn Labels-VF của coach.

Trong vòng rà soát tiếp theo, task #33 đã được đổi tên thành `D14-2A202603176-B` để khớp lệnh xuất của lab. Việc đổi tên không sửa hình học/lớp của nhãn. Tên `B-preview` ở metadata file tham chiếu ghi nhận đúng tên task tại lần xuất cũ.

Lưu ý trình tự: task B-preview đã được tạo trước khi hoàn tất sweep, dùng preset `score_thr=0.4`, `min_points=5`. Cấu hình cuối trùng preset này. Không trình bày đây là quy trình giữ kín B hoàn toàn đến sau khi chọn cấu hình.

Số đo bằng lệnh trong đề, với cấu hình cuối và `ref_B.json`:

| Xóa | Thêm | Sửa | Chi phí |
|---:|---:|---:|---:|
| 3 | 2 | 0 | 2.9 |

| Frame B | Hộp tham chiếu | Xóa | Thêm | Sửa | Chi phí |
|---|---:|---:|---:|---:|---:|
| `s01f02` | 23 | 2 | 1 | 0 | 1.6 |
| `s01f27` | 20 | 1 | 1 | 0 | 1.3 |
| `s01f48` | 27 | 0 | 0 | 0 | 0.0 |
| `s02f11` | 20 | 0 | 0 | 0 | 0.0 |
| `s02f29` | 15 | 0 | 0 | 0 | 0.0 |
| `s02f54` | 21 | 0 | 0 | 0 | 0.0 |
| `s03f08` | 20 | 0 | 0 | 0 | 0.0 |
| `s03f24` | 12 | 0 | 0 | 0 | 0.0 |
| `s03f57` | 19 | 0 | 0 | 0 | 0.0 |
| `s05f01` | 28 | 0 | 0 | 0 | 0.0 |
| `s05f24` | 23 | 0 | 0 | 0 | 0.0 |
| `s05f45` | 14 | 0 | 0 | 0 | 0.0 |

Hai hộp tham chiếu Truck ở `s01f02` và `s01f27` không được ghép với dự đoán theo điều kiện của script, đóng góp 2.0 điểm thêm hộp; ba hộp cần xóa đóng góp 0.9 điểm. Trong phép đo hiện tại, phần thêm hộp tốn chi phí nhiều nhất. Không có nhật ký bấm chuột để suy ra thao tác thực tế nào tốn nhiều thời gian nhất.

10/12 frame B giữ nguyên hình học và lớp so với preview ban đầu. Việc này không tự chứng minh chưa được xem, nhưng chi phí gần 0 cũng không chứng minh nhãn đúng. Kiểm tra lại bằng LiDAR và ảnh camera đã phát hiện các vị trí cần người học rà soát, đặc biệt các hộp tại cây/bồn hoa và xe lớn. Danh sách nằm trong [VISUAL_REVIEW.md](../../d14_2A202603176/VISUAL_REVIEW.md). Chất lượng nhãn B còn chờ xác nhận sau vòng sửa này.

## 5. Giới hạn

1. Tập A chỉ có 3 frame. Đồng hạng trên A và leave-one-out trong một grid nhỏ không bảo đảm cấu hình tốt trên cảnh khác; thử nghiệm mở rộng đã cho thấy rủi ro này.
2. PointPillars học KITTI với ba lớp Car/Pedestrian/Cyclist, không học trực tiếp Truck/Bus. Việc suy lớp xe lớn bằng kích thước có thể sai hoặc bỏ sót. Có 3 Bus được bổ sung trong tham chiếu A; mô hình vẫn cần người kiểm.
3. Chi phí sửa là chỉ số dựa trên ghép hộp và ngưỡng sai lệch. `edit=0` không có nghĩa mọi hộp đã sát điểm, sát mặt đường và đúng hướng đầu xe. Chỉ số không phải thời gian lao động và không kiểm tra mọi vật thể bị bỏ sót trong tham chiếu.
4. Nhãn tham chiếu do người học sửa từ pre-label; có nguy cơ giữ lại lỗi của mô hình. B đã được xem trước khi chốt toàn bộ phân tích, nên kết quả B hiện tại không phải đánh giá độc lập.
5. Heuristic của `scripts/vf_qa.py` gắn cảnh báo cho 62/283 hộp tham chiếu: 30 cảnh báo có thể quá chật, 15 có thể chìm và 26 có thể lơ lửng; một hộp có thể mang nhiều cảnh báo. Đây là gợi ý kiểm tra, không phải 62 lỗi đã được xác nhận. Những vị trí này cần người học mở CVAT kiểm lại.
6. Thiếu dự đoán 5b có nội dung trước sweep nên chưa thể đối chiếu dự đoán đúng/sai. Đã có nhận xét cá nhân sau thực nghiệm, nhưng nhận xét đó không thay thế yêu cầu về thời điểm 5b. Không khẳng định bài đã đạt đủ mọi yêu cầu hoặc đủ điểm rubric.

### Nguồn và hỗ trợ công cụ

AI hỗ trợ chuẩn bị môi trường, chạy lệnh, xuất/đổi định dạng sao lưu CVAT, thử cấu hình, tổng hợp số đo, rà soát file và diễn đạt phần kết quả kỹ thuật. AI dùng thêm heuristic QA sẵn có của lab và xem ảnh chiếu nhãn để lập danh sách cần kiểm tra; không sửa nhãn tham chiếu bằng công cụ tự động, không tạo dự đoán 5b hoặc kết luận cá nhân thay người học. Không sửa code mô hình, ngưỡng chấm hoặc dùng nhãn của người khác.

Kết quả tự kiểm được lưu tại [FINAL_REVIEW.md](../../d14_2A202603176/FINAL_REVIEW.md) và [validation_summary.json](../../d14_2A202603176/validation_summary.json). Kiểm tra cấu trúc đạt không thay thế việc coach chấm chất lượng nhãn và lịch sử 5b.
