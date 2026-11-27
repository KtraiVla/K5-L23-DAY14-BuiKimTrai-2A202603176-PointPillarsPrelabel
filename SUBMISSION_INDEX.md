# Bài làm Lab14 — Bui Kim Trai — 2A202603176

**Trạng thái: đã có bộ file bắt buộc; chưa xác nhận đạt toàn bộ yêu cầu bài lab.** Rà soát ngày 27/11/2026 tái tạo được dự đoán, sweep và ảnh so sánh; các điểm còn thiếu nằm trong bảng dưới. Kết quả test không thay thế việc kiểm nhãn của người học hoặc quyết định của coach.

## File dùng để chấm

| Yêu cầu | File | Kết quả hiện tại |
|---|---|---|
| Frame theo mã học viên/SEED | [A](d14_2A202603176/frames_A.txt), [B](d14_2A202603176/frames_B.txt) | 3 A, 12 B; seed_tag `393590736f`; đã kiểm lại bằng selector của đề. |
| Pre-label gốc A | [pred_A.json](d14_2A202603176/pred_A.json) | 82 hộp, cấu hình mặc định; tái tạo khớp hoàn toàn. |
| Tham chiếu A | [ref_A.json](d14_2A202603176/ref_A.json) | 41 hộp, gồm 3 Bus; cấu trúc hợp lệ, còn vòng kiểm chất lượng. |
| Sweep A | [sweep.csv](d14_2A202603176/sweep.csv) | Đủ 15 cấu hình; tái tạo khớp mọi dòng. |
| Cấu hình đã chọn | [best_config.json](d14_2A202603176/best_config.json) | `score_thr=0.4`, `min_points=5`, đồng hạng tốt nhất trên A. |
| Pre-label B | [pred_B.json](d14_2A202603176/pred_B.json) | 243 hộp; cấu hình khớp và tái tạo khớp hoàn toàn. |
| Ảnh trước/sau A | [compare](d14_2A202603176/compare/) | Đủ 3 JPG, khớp từng byte với ảnh tái tạo. |
| Nhãn tham chiếu B | [ref_B.json](d14_2A202603176/ref_B.json) | 242 hộp/12 frame; đã có sửa so với model nhưng còn các phát hiện QA cần xử lý. |
| Báo cáo | [2A202603176_BuiKimTrai.md](report/individual/2A202603176_BuiKimTrai.md) | Đủ 5 mục, số đo, ảnh, LOO, giới hạn, nhận xét người học và khai báo hỗ trợ AI; thiếu nội dung 5b trước sweep. |

## Kết quả định lượng

| Tập / cấu hình | Xóa | Thêm | Sửa | Chi phí |
|---|---:|---:|---:|---:|
| A gốc | 44 | 3 | 0 | 16.2 |
| A đã chọn | 11 | 3 | 0 | 6.3 |
| B đã chọn, so với tham chiếu hiện tại | 3 | 2 | 0 | 2.9 |

Chi phí A giảm **61.11%** theo công thức của lab. Chỉ số này chưa phải thời gian tiết kiệm thực tế và không chứng minh tham chiếu đã đúng hết.

## Ba điểm chưa hoàn tất

1. **5b:** commit `053e299` chỉ có template trống. Không thể tạo lại bằng chứng dự đoán trước sweep bằng một câu viết sau khi đã có kết quả. Có [bản nháp giải thích cho coach](d14_2A202603176/COACH_NOTE_DRAFT.md); chưa được cung cấp xác nhận đã gửi hoặc phản hồi coach.
2. **Chất lượng nhãn:** 62/283 hộp có cảnh báo heuristic; đã có các phát hiện cụ thể ở cây/bồn hoa và xe tải. [Task AI đề xuất #34](http://localhost:8080/tasks/34/jobs/34) có 236 hộp, nhưng chưa được người học kiểm; chiều dài một Truck còn là ước lượng. Bản đề xuất chưa thay tham chiếu bắt buộc. Xem [danh sách hành động](d14_2A202603176/REVIEW_ACTIONS.md) và [ghi chú bản đề xuất](d14_2A202603176/qa_proposed/README.md).
3. **LMS:** chưa có bằng chứng đã nộp link commit có SHA. Push GitHub chưa phải hoàn tất nộp LMS. Khi cập nhật nhãn và số đo phải dùng SHA mới sau khi push.

## Bằng chứng rà soát và tái lập

- [Bản rà soát đầy đủ](d14_2A202603176/FINAL_REVIEW.md), [kết quả máy đọc](d14_2A202603176/full_review_20261127.json).
- [Số đo đã kiểm](d14_2A202603176/technical_check_results.json), [kết quả 55 kiểm tra](d14_2A202603176/test_check_results.json).
- [Log chạy lại và ảnh](d14_2A202603176/reproduction_20261127/README.md). Đây là bằng chứng tái lập ngày 27/11, không được dùng làm bằng chứng trước sweep.
- [Checklist từng hộp](d14_2A202603176/review_checklist.csv), [62 cảnh báo](d14_2A202603176/review_warnings_62.csv). Các dòng còn `PENDING_HUMAN_REVIEW`; không đánh dấu đã kiểm thay người học.

SEED nguyên văn, mật khẩu, Data-VF, weights và ảnh camera QA cục bộ không nằm trong bài nộp. Các file trong `qa_proposed/` và `improvement_A_only/` là bằng chứng hỗ trợ/thử nghiệm, tách khỏi các file bắt buộc ở bảng đầu.
