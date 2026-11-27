# Bonus Hướng 1 — Đo thao tác sửa nhãn (`cvat-telemetry-addon.user.js`)

## Cách ghi log hợp lệ trên CVAT Task B (`http://localhost:8080/tasks/33`)
1. Cài **Tampermonkey** (hoặc mở `F12` → tab **Console** dán toàn bộ nội dung script ghi nhận thao tác).
   - Script gốc của repo: [`bonus/cvat-telemetry-addon.user.js`](../../bonus/cvat-telemetry-addon.user.js)
   - Bản đồng hành tự gắn chỉ số frame đang mở để tách theo từng frame (mức Khá +5 / Wow +7): xem hướng dẫn trong cuộc trò chuyện.
2. Khi mở job `D14-2A202603176-B` (#33), đi lần lượt đủ 12 frame, rà / chỉnh hình hộp và bấm **Save** (`Ctrl+S`).
3. Trước khi đóng tab, mở `F12` → Console gõ `__d14Telemetry.download()` để lưu `d14-telemetry-job*.json`.

## Phân tích & đối chiếu công thức chi phí
```powershell
# Tách theo frame (nếu dùng bản gắn frame), xuất CSV chuẩn qua bonus/telemetry_metrics.py
.\.venv\Scripts\python.exe d14_2A202603176\bonus_telemetry\analyze_bonus.py <file_log>.json --csv d14_2A202603176\telemetry.csv
```
Ghi bảng phân tích và đối chiếu tỷ lệ click / thời gian giữa thao tác Thêm, Sửa, Xoá (so với trọng số `0.3 / 1.0 / 0.5`) vào mục Bonus trong báo cáo.
