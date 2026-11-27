# Bài làm Lab14 — Bui Kim Trai — 2A202603176

**Trạng thái: đã hoàn tất toàn bộ pipeline kỹ thuật (Tập A, Sweep, Compare, Tập B, Point-Cloud QA) và Bonus Hướng 2 live Nuclio trong CVAT; còn các bước xác nhận của người học/LMS trước giờ nộp.** Kết quả kiểm tra tự động xác nhận tính nhất quán toàn bộ file nộp và khớp live CVAT `#32`/`#33`; việc thiếu nội dung bước 5b ở commit lịch sử `053e299` được khai báo minh bạch với coach.

## File dùng để chấm (Mandatory + Bonus)

| Yêu cầu | File | Kết quả cuối cùng |
|---|---|---|
| Frame theo MSSV/SEED | [A](d14_2A202603176/frames_A.txt), [B](d14_2A202603176/frames_B.txt) | 3 A, 12 B; `seed_tag=393590736f`; không sửa tay frame. |
| Pre-label gốc A | [pred_A.json](d14_2A202603176/pred_A.json) | 82 hộp (`59 Car`, `4 Pedestrian`, `19 Cyclist`), cấu hình mặc định `0.1 / 0`. |
| Tham chiếu A | [ref_A.json](d14_2A202603176/ref_A.json) | **31 hộp** (`25 Car`, `3 Bus`, `2 Cyclist`, `1 Pedestrian`), xuất từ CVAT `#32` (`0` Track). |
| Sweep A | [sweep.csv](d14_2A202603176/sweep.csv) | Đủ 15 tổ hợp `{0.1..0.5} × {0,5,10}` kèm [leave_one_out.txt](d14_2A202603176/leave_one_out.txt) (3/3 fold chọn `0.5/0`). |
| Cấu hình thắng cuộc | [best_config.json](d14_2A202603176/best_config.json) | `score_thr=0.5`, `min_points=0` (đồng hạng `8.5` với `min_points=5, 10`). |
| Pre-label B | [pred_B.json](d14_2A202603176/pred_B.json) | **175 hộp** (`146 Car`, `26 Cyclist`, `3 Pedestrian`), dùng `best_config.json`. |
| Ảnh trước/sau A | [compare](d14_2A202603176/compare/) | Đủ 3 JPG (`s01f18`, `s03f31`, `s04f28`), khớp [metrics_A_compare.log](d14_2A202603176/metrics_A_compare.log). |
| Nhãn tham chiếu B | [ref_B.json](d14_2A202603176/ref_B.json) | **161 hộp** (`126 Car`, `19 Cyclist`, `9 Truck`, `4 Pedestrian`, `3 Bus`), xuất từ CVAT `#33` (`0` Track). |
| Báo cáo cá nhân | [2A202603176_BuiKimTrai.md](report/individual/2A202603176_BuiKimTrai.md) | Đủ 5 mục chuẩn, LOO, compare, bảng 12 frame B, giới hạn, Bonus Hướng 2 và khai báo AI. |
| Bonus Hướng 2 (Nuclio) | [bonus_nuclio_pp](d14_2A202603176/bonus_nuclio_pp/README.md) | Live model `pp-2a202603176` trong CVAT (`#35`); [lambda_match_report.json](d14_2A202603176/bonus_nuclio_pp/lambda_match_report.json): **63/63 (`100%`)** khớp `<= 0.5 m`; còn thiếu video ngắn. |
| Bonus Hướng 1 (Helper) | [bonus_telemetry](d14_2A202603176/bonus_telemetry/README.md) | Helper sẵn sàng cho phiên bấm chuột trình duyệt; không tạo log telemetry giả. |

## Kết quả định lượng cuối

| Tập / cấu hình | Dự đoán | Khớp | Xóa | Thêm | Sửa | Chi phí |
|---|---:|---:|---:|---:|---:|---:|
| A mặc định (`0.1 / 0`) | 82 | 28 | 54 | 3 | 3 | 20.7 |
| A đã chọn (`0.5 / 0`) | 36 | 26 | 10 | 5 | 1 | **8.5** (`-58.94%`) |
| B mặc định (`0.1 / 0`, đối chứng) | 371 | 145 | 226 | 16 | 20 | 93.8 |
| B đã chọn (`0.5 / 0`) | 175 | 122 | 53 | 39 | 12 | **60.9** (`-35.07%` so với mặc định) |

- **Point-cloud QA (15 frame / 192 hộp):** `13/15` frame có **0** cảnh báo `vf_qa.py`; chỉ còn **2/192** cảnh báo `possible_tight_box` do xe `Bus` đỗ sát công trình/xe lân cận (`A/s03f31` và `B/s01f02`, chiều rộng `2.65 m` hợp lệ).

## Việc còn lại thuộc phía người học

1. **5b lịch sử (`053e299`):** gửi giải thích trung thực cho coach dựa trên [COACH_NOTE_DRAFT.md](d14_2A202603176/COACH_NOTE_DRAFT.md).
2. **Xác nhận cuối của người học trên CVAT & video Bonus:** mở rà nhanh task `#32`, `#33` (trong đó đã bật `occluded=true` cho `12/31` hộp A và `46/161` hộp B bị che khuất) và quay video ngắn tab **Models** / task `#35` của `pp-2a202603176` nếu muốn đủ điều kiện `+3` điểm Bonus Hướng 2.
3. **Nộp LMS:** lấy **URL commit có mã SHA đầy đủ** mới nhất sau khi push lên GitHub và nộp lên LMS trước **12:00 trưa**.

## Bằng chứng kiểm tra và tái lập

- [FINAL_REVIEW.md](d14_2A202603176/FINAL_REVIEW.md), [VISUAL_REVIEW.md](d14_2A202603176/VISUAL_REVIEW.md), [REVIEW_ACTIONS.md](d14_2A202603176/REVIEW_ACTIONS.md).
- [validation_summary.json](d14_2A202603176/validation_summary.json), [live_cvat_review_snapshot.json](d14_2A202603176/live_cvat_review_snapshot.json), [full_review_20261127.json](d14_2A202603176/full_review_20261127.json).
- [checklist 192 hộp](d14_2A202603176/review_checklist.csv), [2 cảnh báo proximity](d14_2A202603176/review_warnings_62.csv), [pointcloud_qa.csv](d14_2A202603176/pointcloud_qa.csv).
- SEED gốc, mật khẩu, `Data-VF`, `third_party/`, weights `.pth` và ảnh QA cục bộ (`png_*`) đều nằm ngoài Git/bài nộp.
