# Báo cáo Day 14 — Bui Kim Trai — 2A202603176

- Mã học viên dùng với `--student`: `2A202603176`; bộ frame được sinh bằng đúng mã này tại [frames_A.txt](../../d14_2A202603176/frames_A.txt) và [frames_B.txt](../../d14_2A202603176/frames_B.txt).
- `seed_tag`: `393590736f`; SEED không được lưu trong bài nộp.
- Tập A (3 frame): `s01f18`, `s03f31`, `s04f28`.
- Tập B (12 frame): `s01f02`, `s01f27`, `s01f48`, `s02f11`, `s02f29`, `s02f54`, `s03f08`, `s03f24`, `s03f57`, `s05f01`, `s05f24`, `s05f45`.
- Nguồn nhãn: xuất trực tiếp từ CVAT cá nhân (task `#32` `D14-2A202603176-A` và task `#33` `D14-2A202603176-B`) bằng `scripts/vf_cvat.py reference`.

## 1. Dự đoán trước sweep (bước 5b)

**Thiếu bằng chứng dự đoán trước sweep.** Commit `053e29949860394539643056ae41a1ad0f36d7a0` có tiêu đề `5b: du doan truoc sweep`, nhưng nội dung báo cáo tại commit này chỉ là template (hai dòng dự đoán vẫn là dấu ba chấm). Tiêu đề commit không chứng minh đã viết nội dung dự đoán.

Không bổ sung dự đoán rồi trình bày như đã viết trước sweep, không đổi thời gian và không viết lại lịch sử Git. Tiêu chí 5b chưa hoàn thành; việc xem xét thiếu sót này thuộc quyết định của coach. Đã chuẩn bị [bản nháp giải thích gửi coach](../../d14_2A202603176/COACH_NOTE_DRAFT.md).

## 2. Tập A: sửa tay và tune

[pred_A.json](../../d14_2A202603176/pred_A.json) giữ nguyên dự đoán gốc cấu hình mặc định (`score_thr=0.1`, `min_points=0`): `82` hộp (`59 Car`, `4 Pedestrian`, `19 Cyclist`).

[ref_A.json](../../d14_2A202603176/ref_A.json) sau rà soát 7 camera và LiDAR gồm **31 hộp** trên 3 frame (`s01f18`: 10, `s03f31`: 5, `s04f28`: 16), gồm `25 Car`, `3 Bus`, `2 Cyclist`, `1 Pedestrian` (toàn bộ dạng `Shape`, `0` Track; trong đó đã bật `occluded=true` cho `12/31` vật bị che một phần gồm `s01f18 #2, #9` và `s04f28 #19, #25, #28`).

Công thức chi phí sửa của lab: `0.3 × xóa + 1.0 × thêm + 0.5 × sửa` (chỉ tính hộp trong 50 m; ghép bằng BEV IoU tối thiểu `0.3`, lệch kích thước/tâm vượt ngưỡng tính `1` sửa).

| Cấu hình | Số hộp dự đoán | Khớp | Xóa | Thêm | Sửa | Chi phí |
|---|---:|---:|---:|---:|---:|---:|
| Mặc định: `score_thr=0.1`, `min_points=0` | 82 | 28 | 54 | 3 | 3 | 20.7 |
| Đã chọn ([best_config.json](../../d14_2A202603176/best_config.json)): `score_thr=0.5`, `min_points=0` | 36 | 26 | 10 | 5 | 1 | 8.5 |

Chỉ **một** tham số thay đổi so với cấu hình mặc định: `score_thr: 0.1 -> 0.5`; tham số `min_points` giữ nguyên giá trị mặc định `0` (cả `0`, `5`, `10` cho cùng chi phí `8.5` trên Tập A). Các tham số voxel (`0.16`), intensity (`clip`), `ground_mode=fixed`, `passes=4`, `nms_thr=0.01`, `range_m=50.0` và quy tắc suy lớp lớn giữ nguyên mặc định.

Sweep bắt buộc 15 tổ hợp (`score_thr` ∈ `{0.1, 0.2, 0.3, 0.4, 0.5}` × `min_points` ∈ `{0, 5, 10}`) lưu tại [sweep.csv](../../d14_2A202603176/sweep.csv):

- Tại `score_thr=0.5`, cả ba giá trị `min_points` ∈ `{0, 5, 10}` đồng hạng chi phí **8.5** (`xóa=10, thêm=5, sửa=1`). Điều này xảy ra vì các hộp có `score >= 0.5` đều thuộc vật thể đủ gần/nhiều điểm, không có hộp nào dưới 10 điểm bị loại thêm bởi `min_points`. `scripts/pp_sweep.py` chọn cấu hình đầu bảng là `score_thr=0.5, min_points=0`.
- Ngưỡng tiếp theo `score_thr=0.4` cho chi phí **11.6** (`xóa=22, thêm=4, sửa=2`).

Kết quả **Leave-one-out** ([leave_one_out.txt](../../d14_2A202603176/leave_one_out.txt)): khi giữ từng frame A ra ngoài và chọn cấu hình tốt nhất trên 2 frame còn lại, cả 3 fold đều chọn cùng cấu hình `{'score_thr': '0.5', 'min_points': '0'}` và đạt đúng chi phí tối ưu của grid trên frame giữ lại:

```text
s01f18: cấu hình chọn {'score_thr': '0.5', 'min_points': '0'} -> 3.3 (tốt nhất có thể 3.3)
s03f31: cấu hình chọn {'score_thr': '0.5', 'min_points': '0'} -> 3.2 (tốt nhất có thể 3.2)
s04f28: cấu hình chọn {'score_thr': '0.5', 'min_points': '0'} -> 2.0 (tốt nhất có thể 2.0)
```

| Frame A | Hộp tham chiếu | Chi phí mặc định (`0.1 / 0`) | Chi phí đã chọn (`0.5 / 0`) |
|---|---:|---:|---:|
| `s01f18` | 10 | 8.1 | 3.3 |
| `s03f31` | 5 | 9.6 | 3.2 |
| `s04f28` | 16 | 3.0 | 2.0 |
| **Tổng** | **31** | **20.7** | **8.5** |

Sự đồng thuận 3/3 fold cho thấy `score_thr=0.5` ổn định trong grid 15 cấu hình của Tập A; tuy nhiên do Tập A chỉ có 3 frame, không tự suy ra `0.5` chắc chắn là tối ưu toàn cục trên mọi cảnh khác.

## 3. Trước/sau (bước 8)

![So sánh cấu hình gốc và cấu hình cuối trên s01f18](../../d14_2A202603176/compare/s01f18.jpg)

Ảnh so sánh của cả 3 frame A lưu trong [compare](../../d14_2A202603176/compare/) ([s01f18.jpg](../../d14_2A202603176/compare/s01f18.jpg), [s04f28.jpg](../../d14_2A202603176/compare/s04f28.jpg), [s03f31.jpg](../../d14_2A202603176/compare/s03f31.jpg)) cùng log [metrics_A_compare.log](../../d14_2A202603176/metrics_A_compare.log).

- Tổng chi phí A giảm từ **20.7** xuống **8.5**, tức giảm **`(20.7 - 8.5) / 20.7 × 100 = 58.94%`** (`pp_compare.py` làm tròn **59%**).
- Phân rã:
  - **Xóa** giảm từ `54` xuống `10` (cắt 44 hộp giả ở cây, hàng rào, xe hai bánh trống -> tiết kiệm `44 × 0.3 = 13.2` điểm).
  - **Thêm** tăng nhẹ từ `3` lên `5` (`+2.0` điểm) vì nâng ngưỡng lên `0.5` làm rơi một số xe xa/thưa điểm ngoài 3 xe `Bus`.
  - **Sửa** giảm từ `3` xuống `1` (`-1.0` điểm).
  - Tổng hợp: `-13.2 + 2.0 - 1.0 = -12.2` (`20.7 -> 8.5`). Đây là mức giảm theo công thức chi phí quy ước, không quy trực tiếp thành phút thao tác.

**Nhận xét cá nhân do người học cung cấp sau khi xem tập A** (AI hỗ trợ sửa câu chữ):

> Ở tập A, tôi thấy mô hình bỏ sót một vài vật thể, chẳng hạn như xe bus.

Nhận xét này khớp với số đo thực tế trên `ref_A.json`: cả trước và sau tune mô hình vẫn bỏ sót cả 3 xe `Bus` trên Tập A do PointPillars KITTI chỉ huấn luyện trên 3 lớp `Car / Pedestrian / Cyclist`. Không dùng nhận xét sau thực nghiệm này để thay thế bằng chứng dự đoán bước 5b.

## 4. Tập B

Áp dụng `best_config.json` (`score_thr=0.5`, `min_points=0`) chạy pre-label 12 frame Tập B tạo [pred_B.json](../../d14_2A202603176/pred_B.json) gồm **175 hộp** (`146 Car`, `26 Cyclist`, `3 Pedestrian`).

[ref_B.json](../../d14_2A202603176/ref_B.json) được xuất trực tiếp từ CVAT task `#33` (`D14-2A202603176-B`) sau rà soát 12 frame bằng 7 camera + LiDAR, gồm **161 hộp** (`126 Car`, `19 Cyclist`, `9 Truck`, `4 Pedestrian`, `3 Bus`, `0` Track; trong đó đã bật `occluded=true` cho `46/161` xe bị che một phần).

So sánh chi phí sửa Tập B (chạy `scripts/pp_prelabel.py` ghi trong [metrics_B.log](../../d14_2A202603176/metrics_B.log), đối chiếu thêm với cấu hình mặc định `0.1 / 0`):

| Cấu hình trên Tập B | Dự đoán | Khớp | Xóa | Thêm | Sửa | Chi phí |
|---|---:|---:|---:|---:|---:|---:|
| Mặc định (`0.1 / 0`, đối chứng) | 371 | 145 | 226 | 16 | 20 | 93.8 |
| Đã chọn ([best_config.json](../../d14_2A202603176/best_config.json): `0.5 / 0`) | 175 | 122 | 53 | 39 | 12 | **60.9** |

Chi phí sửa từng frame Tập B dưới cấu hình cuối (`score_thr=0.5`, `min_points=0`):

| Frame B | Hộp tham chiếu | Hộp dự đoán | Khớp | Xóa | Thêm | Sửa | Chi phí |
|---|---:|---:|---:|---:|---:|---:|---:|
| `s01f02` | 21 | 19 | 17 | 2 | 4 | 2 | 5.6 |
| `s01f27` | 16 | 18 | 15 | 3 | 1 | 0 | 1.9 |
| `s01f48` | 17 | 16 | 13 | 3 | 4 | 0 | 4.9 |
| `s02f11` | 14 | 15 | 11 | 4 | 3 | 2 | 5.2 |
| `s02f29` | 9 | 13 | 9 | 4 | 0 | 0 | 1.2 |
| `s02f54` | 9 | 15 | 8 | 7 | 1 | 0 | 3.1 |
| `s03f08` | 16 | 18 | 12 | 6 | 4 | 2 | 6.8 |
| `s03f24` | 5 | 8 | 3 | 5 | 2 | 0 | 3.5 |
| `s03f57` | 11 | 10 | 6 | 4 | 5 | 0 | 6.2 |
| `s05f01` | 10 | 19 | 8 | 11 | 2 | 4 | 7.3 |
| `s05f24` | 19 | 14 | 11 | 3 | 8 | 1 | 9.4 |
| `s05f45` | 14 | 10 | 9 | 1 | 5 | 1 | 5.8 |
| **Tổng (12 frame)** | **161** | **175** | **122** | **53** | **39** | **12** | **60.9** |

Trong tổng chi phí `60.9`, phần **thêm hộp** chiếm tỷ trọng lớn nhất (`39 × 1.0 = 39.0` điểm), tiếp theo là **xóa hộp** (`53 × 0.3 = 15.9`) và **sửa kích thước** (`12 × 0.5 = 6.0`), phản ánh thực tế `score_thr=0.5` cắt tốt hộp giả (`xóa` giảm `226 -> 53`) nhưng bỏ sót một số xe tải/xe buýt/xe che khuất (`add=39`).

## 5. Giới hạn

1. **Tập A chỉ có 3 frame:** `score_thr=0.5` đồng hạng ở `min_points` ∈ `{0, 5, 10}` và đồng thuận `3/3` LOO trên A, nhưng trên Tập B ngưỡng `0.5` làm tăng công thêm (`16 -> 39`) dù giảm chi phí tổng (`93.8 -> 60.9`). Trong thực tế có thể cân nhắc ngưỡng `0.3–0.4` khi công thêm lớn gấp `3.3×` công xóa.
2. **Hạn chế domain/lớp của checkpoint KITTI:** không được train lớp `Truck` và `Bus`, nên xe buýt (`3` ở A, `3` ở B) và xe tải (`9` ở B) thường bị gán nhầm thành `Car` nhỏ (`edit`) hoặc bỏ sót (`add`).
3. **Chỉ số `correction_cost` là ước lượng hình học:** không đo trực tiếp thời gian xoay chỉnh trên giao diện CVAT.
4. **Rà soát xác nhận cuối trên CVAT:** các đề xuất chỉnh sửa/loại hộp giả/`occluded` trên 15 frame (`#32`, `#33`) có AI hỗ trợ đối chiếu 7 camera và LiDAR; người học vẫn cần mở xem xác nhận cuối cùng trên CVAT trước khi khóa bài.
5. **Thiếu bằng chứng lịch sử 5b:** giải thích trung thực tại mục 1 và [COACH_NOTE_DRAFT.md](../../d14_2A202603176/COACH_NOTE_DRAFT.md).

---

### Điểm cộng (Bonus Hướng 2): PointPillars serverless trong CVAT (`pp-2a202603176`)

Đã hoàn chỉnh, build và triển khai thành công Nuclio function `pp-2a202603176` kết nối vào **CVAT Serverless (`Models`)** tại `http://localhost:8080` trên mạng `cvat_cvat` ([chi tiết kỹ thuật](../../d14_2A202603176/bonus_nuclio_pp/README.md), không chứa `third_party/` hay `.pth`).

- [main.py](../../d14_2A202603176/bonus_nuclio_pp/main.py) giải mã binary/ascii `.pcd` (`rgb`) và đảo ngược nén log `vf_common.intensity_gray`; [function.yaml](../../d14_2A202603176/bonus_nuclio_pp/function.yaml) cấu hình `spec.description` tương thích CVAT v2.74.1 và mạng `cvat_cvat`.
- Chạy qua API `/api/lambda/requests` (`threshold=0.3`) trên task thử nghiệm `#35` (`D14-2A202603176-BONUS-TEST`, không ghi đè `#32/#33`), kết quả tại [lambda_match_report.json](../../d14_2A202603176/bonus_nuclio_pp/lambda_match_report.json):

| Frame thử nghiệm | CVAT Lambda (`threshold=0.3`) | Offline `pred_A` (`score >= 0.3`) | Khớp tâm `<= 0.5 m` cùng lớp |
|---|---:|---:|---:|
| `s01f18` | 24 | 22 | 22 / 22 |
| `s03f31` | 25 | 23 | 23 / 23 |
| `s04f28` | 18 | 18 | 18 / 18 |
| **Tổng (3 frame)** | **67** | **63** | **63 / 63 (100%)** |

Độ lệch +4 hộp sát ngưỡng `0.3` đến từ lượng tử hóa `uint8` grayscale trong `.pcd`. *Ghi chú: đã xong code, deploy live và số đo `63/63`; chưa có video quay màn hình ngắn kèm link theo tiêu chí `+3` trong `bonus/README.md`.*

---

### Nguồn & khai báo hỗ trợ AI

AI hỗ trợ thiết lập môi trường CPU, đối chiếu 7 camera + mặt cắt LiDAR để đề xuất tinh chỉnh nhãn & cờ `occluded` trên CVAT `#32/#33`, viết module triển khai Bonus Nuclio `pp-2a202603176` và tổng hợp số đo báo cáo. Không sửa code core `vf_pp`/`scripts`, không dùng nhãn coach `Labels-VF`, không sửa lịch sử Git `053e299` và không tạo dữ liệu giả.
