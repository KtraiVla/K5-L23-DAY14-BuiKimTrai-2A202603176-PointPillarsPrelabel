# Tái lập kỹ thuật ngày 27/11/2026

Các log trong thư mục này được tạo bằng script gốc của lab từ Data-VF cục bộ và nhãn tham chiếu hiện tại. Chúng ghi nhận lần tái lập sau thực nghiệm; không phải bằng chứng dự đoán 5b trước sweep. Không có SEED nguyên văn hoặc mật khẩu trong log.

- `pred_A.log`: inference cấu hình mặc định trên 3 frame A; JSON tái tạo khớp hoàn toàn `../pred_A.json`.
- `pred_B.log`: inference cấu hình cuối trên 12 frame B và đo với `../ref_B.json`; JSON tái tạo khớp hoàn toàn `../pred_B.json`.
- `sweep.log`: đủ 15 cấu hình A và đầu ra leave-one-out; mọi trường số của CSV tái tạo khớp file đã lưu. Script chọn min_points=0 trong các hàng đồng hạng; bài chọn min_points=5 có cùng chi phí A, đã giải thích trong báo cáo.
- `compare.log`: chạy lại cả hai cấu hình; ba ảnh tái tạo khớp từng byte với ảnh ở `../compare/`.

Các JSON/CSV/ảnh tái tạo trung gian được lưu cục bộ dưới `out/final_audit_20261127/`, không ghi đè file nộp. Bằng chứng SHA256, phiên bản môi trường và phạm vi kiểm tra ở `../full_review_20261127.json`.
