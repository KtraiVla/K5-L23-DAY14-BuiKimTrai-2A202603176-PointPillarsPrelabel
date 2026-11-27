# Tự rà soát Lab14 — 2A202603176

**Cập nhật cuối (27/11/2026):** Toàn bộ pipeline bắt buộc trên tập nhãn đã làm sạch (**31 hộp Tập A**, **161 hộp Tập B**, tổng **192 hộp** từ CVAT `#32/#33`) và **Bonus Hướng 2** (Nuclio `pp-2a202603176` chạy live trong CVAT) đã hoàn tất và qua kiểm tra nhất quán kỹ thuật. Thiếu sót lịch sử duy nhất là nội dung bước 5b tại commit `053e299` (giữ nguyên lịch sử Git, có `COACH_NOTE_DRAFT.md`). Việc nộp link commit SHA lên LMS thuộc thao tác của người học trên trình duyệt.

## Đối chiếu yêu cầu

| Yêu cầu | Trạng thái | Bằng chứng / chi tiết |
|---|---|---|
| Môi trường PointPillars chạy được | ĐẠT | `.venv` chạy đủ inference, sweep, compare, QA và Nuclio bundle cục bộ. |
| Data-VF đầy đủ | ĐẠT cục bộ | 300 LiDAR, 2100 ảnh, 5 calib; không commit lên repo. |
| MSSV và SEED đúng | ĐẠT | `2A202603176`, `seed_tag=393590736f`; `frames_A.txt` (3), `frames_B.txt` (12) không sửa tay. |
| Giữ pre-label gốc A | ĐẠT | `pred_A.json`: 82 hộp (`0.1 / 0`), `pred_A_filtered.json`: 36 hộp (`0.5 / 0`). |
| Nhãn tham chiếu A (`ref_A.json`) | ĐẠT | **31 hộp** (`25 Car`, `3 Bus`, `2 Cyclist`, `1 Pedestrian`), xuất từ CVAT `#32` (`0` Track). |
| Dự đoán trước sweep 5b | THIẾU LỊCH SỬ | Commit `053e29949860394539643056ae41a1ad0f36d7a0` chỉ có template. Không backdate; có `COACH_NOTE_DRAFT.md`. |
| Sweep A & chọn cấu hình | ĐẠT | `sweep.csv` đủ 15 tổ hợp `{0.1..0.5}×{0,5,10}`; `best_config.json` chọn `score_thr=0.5, min_points=0` (`cost=8.5`, LOO 3/3 fold chọn `0.5/0`). |
| Compare & số đo A | ĐẠT | Đủ 3 JPG ở `compare/`; chi phí giảm **`20.7 -> 8.5` (`-58.94%`, làm tròn `59%`)**. |
| Nhận xét cá nhân / đối chiếu 5b | ĐẠT phần nhận xét | Có nhận xét thật về sót `Bus` sau thực nghiệm; khai báo trung thực không phải bằng chứng 5b. |
| Pre-label B (`pred_B.json`) | ĐẠT | **175 hộp** dùng `best_config.json` (`0.5 / 0`). |
| Nhãn tham chiếu B (`ref_B.json`) | ĐẠT | **161 hộp** (`126 Car`, `19 Cyclist`, `9 Truck`, `4 Pedestrian`, `3 Bus`), xuất từ CVAT `#33` (`0` Track). |
| Đo công sửa B | ĐẠT | Cấu hình chọn `0.5/0`: `delete=53, add=39, edit=12 -> cost=60.9` (giảm `35.07%` so với mặc định `0.1/0`: `93.8`). |
| Point-cloud QA (15 frame / 192 hộp) | ĐẠT | `13/15` frame **0 cảnh báo**; chỉ `2/192` cờ `possible_tight_box` hợp lệ do vật thể/tường lân cận (`s03f31` & `s01f02` Bus). |
| Báo cáo đúng template | ĐẠT | [2A202603176_BuiKimTrai.md](../report/individual/2A202603176_BuiKimTrai.md) đủ 5 mục chuẩn, zero placeholder, link hợp lệ, khai báo AI minh bạch. |
| Bảo mật & Git sạch | ĐẠT | Không commit `Data-VF`, `third_party/`, `.venv`, `.env`, `.pth`, `png_*`, SEED gốc hay mật khẩu. |
| **Bonus Hướng 2 (CVAT Serverless)** | **ĐẠT LIVE** | Nuclio `pp-2a202603176` trạng thái `ready (1/1)`, thử nghiệm API trên task `#35` khớp **63/63 (`100%`)** `<= 0.5 m` với `pred_A` (`threshold=0.3`). |
| Bonus Hướng 1 (Telemetry Helper) | TOOLING SẴN SÀNG | `bonus_telemetry/analyze_bonus.py` sẵn sàng; không tạo log bấm chuột giả. |
| Nộp link commit SHA trên LMS | CHỜ NGƯỜI HỌC | Thực hiện sau khi nhận commit SHA cuối cùng của lần push này. |

## Kiểm chứng kỹ thuật sau chỉnh sửa cuối

Xem chi tiết kết quả chạy sau chỉnh sửa cuối trong [validation_summary.json](validation_summary.json), [technical_check_results.json](technical_check_results.json), [test_check_results.json](test_check_results.json), [staged_file_audit.json](staged_file_audit.json) và [full_review_20261127.json](full_review_20261127.json).
