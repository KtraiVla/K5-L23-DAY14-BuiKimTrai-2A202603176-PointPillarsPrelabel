# Bonus Hướng 2 — PointPillars serverless trong CVAT (`pp-2a202603176`)

Thư mục này chứa mã nguồn nhẹ của Nuclio function theo [`bonus/huong-dan-model-3d.html`](../../bonus/huong-dan-model-3d.html) (không commit `third_party/` hay file trọng số `.pth`).

## 1. Kiến trúc `main.py` & `function.yaml`
- `parse_pcd(pcd_bytes)` đọc header + payload binary/ascii `.pcd` (`x y z rgb` do CVAT gửi qua `body["image"]` base64).
- Giải mã kênh xám `g = (rgb >> 16) & 0xFF` và đảo ngược hàm nén log trong `scripts/vf_common.py:intensity_gray`:
  `t = clip((g - 40) / 215, 0, 1)`, `intensity = expm1(t * log1p(50))` (bằng `0.0` nếu `g <= 40`).
- Nạp `vf_pp.core.Detector(Config(score_thr=0.1))` một lần trong `init_context`, lọc theo `body["threshold"]` (mặc định `0.3`), trả danh sách cuboid đúng 16 phần tử `[x, y, z, 0, 0, yaw, l, w, h, 0*7]`.

## 2. Đóng gói & chạy thử cục bộ (không cần sửa repo)
```powershell
.\.venv\Scripts\python.exe d14_2A202603176\bonus_nuclio_pp\stage_and_eval.py --data "<Data-VF>" --threshold 0.3
```
Lệnh trên đóng gói bundle Nuclio đầy đủ (gồm `vf_pp/` và trọng số cục bộ) vào `out/nuclio_pp_2a202603176/` (đã `.gitignore`) và chạy đối chiếu `.pcd` giả lập với `pred_A.json`.

## 3. Deploy lên CVAT Serverless (trong WSL Ubuntu `/home/kimtrai/cvat-day2`)
```bash
# 1) Bật Nuclio (tạo lại cvat_server/cvat_worker_annotation với CVAT_SERVERLESS=1, giữ nguyên DB/task cũ)
docker compose -f docker-compose.yml -f components/serverless/docker-compose.serverless.yml up -d

# 2) Deploy bằng nuctl đúng version dashboard (1.16.3-amd64)
nuctl create project cvat --platform local
nuctl deploy --project-name cvat --path /mnt/d/.../out/nuclio_pp_2a202603176 --file .../function.yaml --platform local
nuctl get functions --platform local

# 3) Gọi thử trên task thử nghiệm (không chạy đè lên D14-2A202603176-A/B đang nộp)
curl -u <user>:<pass> -H "Content-Type: application/json" -X POST http://localhost:8080/api/lambda/requests \
  -d '{"function": "pp-2a202603176", "task": 34, "threshold": 0.3, "cleanup": true}'
```
