# Tự rà soát Lab14 — 2A202603176

**Bộ file kỹ thuật đã được chuẩn bị; chưa đủ căn cứ xác nhận toàn bộ bài đạt yêu cầu.** Hai phần chính còn thiếu là dự đoán 5b có nội dung trước sweep và vòng kiểm nhãn của người học sau các phát hiện QA. Người học đã cung cấp nhận xét về xe bus bị sót; nhận xét đã được đưa vào mục 3 báo cáo với đúng thời điểm sau thực nghiệm. Chưa nộp LMS.

## Đối chiếu yêu cầu

| Yêu cầu | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| Môi trường PointPillars chạy được | ĐẠT | Selftest CPU đã chạy; dự đoán, sweep và compare đã sinh được. |
| Data-VF đầy đủ | ĐẠT cục bộ | 300 LiDAR, 2100 ảnh, 5 calibration; 2405 file khớp CRC archive. Không commit dữ liệu. |
| MSSV và SEED đúng | ĐẠT kiểm tra nội bộ | `2A202603176`, seed_tag `393590736f`; tái sinh bằng hàm chọn frame của đề và so sánh nguyên danh sách. Không sửa tay frame. Đây không phải kết quả từ `check_student.py` của coach. |
| Tập A 3 frame, B 12 frame | ĐẠT | Hai tập không trùng nhau; mọi dự đoán/tham chiếu có đúng tập frame. |
| Giữ pre-label gốc A | ĐẠT | `pred_A.json`: 82 hộp, cấu hình mặc định; bản lọc riêng 49 hộp. |
| Nhãn tham chiếu A | ĐẠT cấu trúc, CHỜ chất lượng | 41 hộp, 3 Bus bổ sung; không phải chỉ xóa hộp. Nguồn task #32 đã lưu, không có Track. Cần kiểm lại các vị trí trong `VISUAL_REVIEW.md`. |
| Dự đoán trước sweep 5b | CHƯA ĐẠT | Commit `053e29949860394539643056ae41a1ad0f36d7a0` chỉ có template; thiếu nội dung dự đoán thật. Không tạo lại hoặc backdate. |
| Sweep và lựa chọn cấu hình | ĐẠT dữ liệu kỹ thuật | Đủ 15 tổ hợp; `.4/5` đồng hạng tốt nhất trên A. Có giải thích tie và leave-one-out tái dựng từ CSV. |
| Compare và số đo A | ĐẠT | Đủ 3 JPG mở được; chi phí 16.2 → 6.3, giảm 61.11%; ảnh được liên kết trong báo cáo. |
| Nhận xét cá nhân / đối chiếu với 5b | ĐÃ CÓ nhận xét; 5b CÒN THIẾU | Người học nhận thấy tập A bỏ sót một vài vật thể như xe bus; AI chỉ sửa câu chữ. Thiếu dự đoán gốc nên không thể kết luận dự đoán 5b đúng/sai. Có bản nháp giải thích gửi coach, chưa gửi. |
| Pre-label B theo cấu hình cuối | ĐẠT file; có lệch trình tự | 243 hộp, metadata khớp cấu hình cuối. Task #33 dùng preset này trước khi hoàn tất sweep; đã công bố rõ trong báo cáo. |
| `ref_B.json` đủ 12 frame | ĐẠT cấu trúc | 242 hộp; có thay đổi thực so với model, không trùng toàn bộ. Nguồn backup task #33 đã lưu, không có Track. |
| Mọi nhãn B đã đúng | CHƯA XÁC NHẬN | 10/12 frame không đổi hình học/lớp so với preview. Xem đủ 15 ảnh tổng hợp đã phát hiện các vị trí cần kiểm người; chi phí thấp không xác nhận nhãn đúng. |
| Đo công sửa B | ĐẠT với bản nhãn hiện tại | Xóa 3, thêm 2, sửa 0; chi phí 2.9. Nếu nhãn đổi, phải đo lại. |
| Báo cáo đúng template | CÓ 5 MỤC; 5b CÒN THIẾU | Đủ số đo, ảnh, LOO, giới hạn, nhận xét do người học cung cấp và khai báo hỗ trợ AI. Mục 1/3 ghi rõ thiếu bằng chứng 5b thay vì giả nội dung. |
| Repo đúng tên và coach mở được | ĐẠT | Repo public `K5-L23-DAY14-BuiKimTrai-2A202603176-PointPillarsPrelabel`; giữ nguyên lịch sử Git. |
| Dữ liệu và bí mật không đi vào bài nộp | ĐẠT kiểm tra stage | `staged_file_audit.json`: không có Data-VF, third_party, venv, ZIP, .env, ảnh camera/QA, SEED nguyên văn hoặc token theo mẫu đã kiểm. Đây là kiểm tra các thay đổi đang nộp, không phải kiểm toán toàn bộ lịch sử. |
| Link commit có SHA đã nộp LMS | CHƯA NỘP | Người học dùng đúng SHA đã push; repo có file không đồng nghĩa đã nộp LMS. |
| Điểm cộng | KHÔNG THỰC HIỆN | Tùy chọn; không bịa log đo thao tác hay tích hợp CVAT. |

## Đối chiếu rubric

- Mục 1 (20 điểm): có tham chiếu A và thao tác bổ sung Bus; chất lượng vẫn cần người học rà theo guideline.
- Mục 2 (20 điểm): có sweep, cấu hình, lý do đồng hạng và kết quả LOO; nêu rõ thử nghiệm mở rộng đã xem B.
- Mục 3 (20 điểm): thiếu dự đoán 5b thực trước sweep; không có cơ sở xác nhận đạt tiêu chí này.
- Mục 4 (30 điểm): có đủ 12 frame B và nhãn có thay đổi; chất lượng hộp thừa/sót/sai lớp còn rủi ro, nhất là các vị trí ưu tiên trong `VISUAL_REVIEW.md`.
- Mục 5 (10 điểm): báo cáo công bố số đo, nguồn nhãn, giới hạn, hỗ trợ AI và phần còn thiếu; không quy chi phí thành giờ công.

Không tự cho điểm thay coach và không khẳng định đạt 100/100.

## Kiểm chứng đã chạy

- Kiểm tra nội bộ `verify_submission.py`: PASS cho bộ file hiện tại; đúng MSSV/SEED, frame, cấu hình, số đo và liên kết.
- Unit test có sẵn `test_cvat_cuboid.py`: 12/12 PASS, kiểm phép chuyển cuboid CVAT.
- Unit test có sẵn `test_scoring_range.py`: 10/10 PASS, kiểm phạm vi và cách tính công sửa.
- Unit test có sẵn `test_json_bom.py`: 1/1 PASS, kiểm đọc JSON BOM.
- Tổng 23 test trên đều PASS. Không dùng kết quả này để suy ra 283 hộp tham chiếu đều đúng.
- Giữ nguyên byte của hai file frame do script sinh trên Windows bằng `.gitattributes`; không để Git tự chuyển CRLF thành LF trong bài nộp. Nội dung frame không sửa tay.
- Kiểm tra tiếp theo: checklist 283 hộp khớp từng lớp, XYZ, kích thước và yaw với tham chiếu; SHA256 tham chiếu khớp snapshot đọc sidebar CVAT. Bảng 62 cảnh báo vẫn để `PENDING_HUMAN_REVIEW`.

## Chạy lại kiểm tra kỹ thuật

Tại gốc repo, dùng Python trong `.venv`. Đặt SEED do coach cung cấp vào biến môi trường trong phiên hiện tại; không lưu SEED vào file bài nộp:

```powershell
$DataVF = 'D:\VinUni-AI in Action\Lab14\Data-VF'
# Đặt $env:D14_SEED bằng SEED chính thức ở terminal của bạn trước khi chạy.
& '.\.venv\Scripts\python.exe' -B 'd14_2A202603176/verify_submission.py' --data "$DataVF"
& '.\.venv\Scripts\python.exe' -B 'd14_2A202603176/reproduce_reference_qa.py' --data "$DataVF"
```

Lệnh thứ nhất chỉ đọc file, trả `technical_checks: PASS` khi cấu trúc, tập frame, cấu hình, chi phí, sweep, ảnh và liên kết báo cáo khớp nhau. Nó không chấm chất lượng nhãn hoặc thay checker coach. Lệnh thứ hai tạo lại CSV cảnh báo và ảnh QA cục bộ; không sửa nhãn.

## Việc còn lại do người học thực hiện

Vòng hỗ trợ tiếp theo đã chuẩn bị `REVIEW_ACTIONS.md`, checklist đủ 283 hộp, bảng riêng 62 cảnh báo và ảnh camera/BEV/ba mặt cắt cục bộ theo object ID. Đây là hỗ trợ kiểm, chưa phải xác nhận người học đã kiểm nhãn.

Sau khi người học yêu cầu AI kiểm tiếp, đã tạo task đề xuất riêng #34: bỏ 6 hộp tại cây/bồn hoa và chỉnh một Truck, đủ 236 hộp/12 frame; đã mở từng frame xác nhận số lượng/lớp và Details của Truck. Chiều dài xe tải còn là ước lượng do bị che. Tham chiếu A/B gốc giữ nguyên; không đánh dấu bản đề xuất là nhãn đã được người kiểm. Xem `qa_proposed/README.md`.

1. Mở task A #32 và B #33, rà các vị trí ưu tiên trong `VISUAL_REVIEW.md` và các hộp có cảnh báo trong `pointcloud_qa.csv`. Sửa đúng điểm, lớp, kích thước và mặt đất, rồi Save.
2. Xuất nhãn mới, tính lại toàn bộ số đo liên quan và cập nhật báo cáo/commit sau khi nhãn thay đổi. Không ghi đè nhãn đã sửa bằng pre-label.
3. Kiểm tra nhận xét cá nhân đã được sửa câu chữ đúng ý mình. Dùng `COACH_NOTE_DRAFT.md` để trình bày trung thực việc thiếu 5b với coach; không thể khắc phục thời điểm dự đoán chỉ bằng thêm câu sau sweep.
4. Khi đã kiểm xong, nộp link **commit có SHA** trên LMS bằng tài khoản của mình; kiểm deadline theo ngày lab thực tế.
