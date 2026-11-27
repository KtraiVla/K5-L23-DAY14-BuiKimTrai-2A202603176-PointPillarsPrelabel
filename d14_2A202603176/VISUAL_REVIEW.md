# Kết quả rà soát trực quan 7 camera + LiDAR (15 frame / 192 hộp)

Trạng thái: **ĐÃ RÀ SOÁT & ĐỒNG BỘ LÊN CVAT `#32`/`#33`, CẦN NGƯỜI HỌC XEM XÁC NHẬN CUỐI TRƯỚC KHI KHÓA**. Các chỉnh sửa hình học, phân loại và dọn dương tính giả ở 15 frame đã được nạp lên CVAT (#32 Set A: 31 hộp; #33 Set B: 161 hộp; 100% Shape, 0 Track) và xuất lại qua `scripts/vf_cvat.py reference`.

## Tóm tắt trước và sau làm sạch

| Hạng mục | Nhãn thô ban đầu | Nhãn sau rà soát QA (`ref_A` + `ref_B`) | Ghi chú |
|---|---:|---:|---|
| Tổng hộp Set A (3 frame) | 41 | **31** | Bỏ hộp trên bụi cây/tường/xe hai bánh trống; chỉnh sát 3 `Bus` & xe đỗ. |
| Tổng hộp Set B (12 frame) | 242 | **161** | Bỏ ego-car ở 9 frame, bỏ hộp cây/tủ điện/rào; sửa/bổ sung `9 Truck` & `3 Bus`. |
| Cảnh báo `vf_qa.py` | 62 / 283 hộp | **2 / 192 hộp** | `13/15` frame đạt **0 cảnh báo**; 0 lỗi thiếu điểm, chìm hay lơ lửng. |

## Hai cảnh báo proximity còn lại (hợp lệ)

| Task / frame CVAT | Frame | CVAT ID | Ref idx | Lớp | Ghi chú kiểm tra | Quyết định |
|---|---|---:|---:|---|---|---|
| A `#32` / 1 | `s03f31` | 15 | 5 | `Bus` | `557` điểm trong hộp, đáy `+0.06 m`; 940 điểm thuộc tường nhà chờ BRT sát cạnh hộp rộng `2.65 m`. | `KEEP_VALID_PROXIMITY` |
| B `#33` / 0 | `s01f02` | 21 | 21 | `Bus` | `200` điểm trong hộp, đáy `+0.06 m`; 92 điểm thuộc lan can/xe kế cận sát mép ngoài `2.65 m`. | `KEEP_VALID_PROXIMITY` |

Xem danh sách đầy đủ toàn bộ 192 hộp ở [review_checklist.csv](review_checklist.csv) và chi tiết theo đối tượng ở [REVIEW_ACTIONS.md](REVIEW_ACTIONS.md).
