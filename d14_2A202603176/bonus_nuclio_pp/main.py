"""Nuclio serverless handler running vf_pp PointPillars inside CVAT 3D."""
from __future__ import annotations

import base64
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

# Support both staged Nuclio layout (vf_pp alongside main.py) and local repo layout
_HERE = Path(__file__).resolve().parent
for _cand in (_HERE, _HERE.parent.parent):
    if (_cand / "vf_pp").is_dir() and str(_cand) not in sys.path:
        sys.path.insert(0, str(_cand))

from vf_pp.core import Config, Detector, VF_NAMES  # noqa: E402


def parse_pcd(pcd_bytes: bytes) -> np.ndarray:
    """Parse binary/ascii VF .pcd (x y z rgb) into (N, 4) float32 VF LiDAR points.

    Inverts ``scripts.vf_common.intensity_gray`` so intensity recovery matches raw VF
    log scaling as closely as the 8-bit quantized grayscale channel permits.
    """
    nl_pos = 0
    header_lines: list[str] = []
    data_mode = "binary"
    while True:
        next_nl = pcd_bytes.find(b"\n", nl_pos)
        if next_nl == -1:
            raise ValueError("Malformed PCD header: DATA section not found")
        line = pcd_bytes[nl_pos:next_nl].decode("ascii", errors="replace").strip()
        nl_pos = next_nl + 1
        header_lines.append(line)
        if line.upper().startswith("DATA "):
            data_mode = line.split(None, 1)[1].strip().lower()
            break

    meta: dict[str, list[str]] = {}
    for ln in header_lines:
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split()
        meta[parts[0].upper()] = parts[1:]

    fields = [f.lower() for f in meta.get("FIELDS", ["x", "y", "z", "rgb"])]
    sizes = [int(s) for s in meta.get("SIZE", ["4"] * len(fields))]
    types = [t.upper() for t in meta.get("TYPE", ["F"] * len(fields))]
    counts = [int(c) for c in meta.get("COUNT", ["1"] * len(fields))]
    n_points = int(meta.get("POINTS", ["0"])[0])
    if n_points == 0:
        return np.zeros((0, 4), dtype=np.float32)

    if data_mode == "ascii":
        rows = []
        for raw_row in pcd_bytes[nl_pos:].decode("ascii", errors="ignore").splitlines():
            cols = raw_row.split()
            if len(cols) >= 4:
                rows.append([float(cols[0]), float(cols[1]), float(cols[2]), float(cols[3])])
        arr = np.asarray(rows, dtype=np.float32)
        return arr if len(arr) else np.zeros((0, 4), dtype=np.float32)

    if data_mode != "binary":
        raise ValueError(f"Unsupported PCD DATA mode: {data_mode!r}")

    fmt_map = {("F", 4): "f", ("F", 8): "d", ("U", 4): "I", ("U", 2): "H", ("U", 1): "B", ("I", 4): "i"}
    stride = sum(s * c for s, c in zip(sizes, counts))
    payload = pcd_bytes[nl_pos:]
    if len(payload) < n_points * stride:
        n_points = len(payload) // stride
    if n_points == 0:
        return np.zeros((0, 4), dtype=np.float32)

    dtype_fields = []
    for fname, sz, tp, cnt in zip(fields, sizes, types, counts):
        np_code = fmt_map.get((tp, sz))
        if np_code is None:
            raise ValueError(f"Unsupported PCD field type/size: {fname} {tp}{sz}")
        dt = f"<{np_code}"
        dtype_fields.append((fname, dt if cnt == 1 else (dt, (cnt,))))

    rec = np.frombuffer(payload[: n_points * stride], dtype=np.dtype(dtype_fields))
    out = np.zeros((n_points, 4), dtype=np.float32)
    out[:, 0] = rec["x"].astype(np.float32)
    out[:, 1] = rec["y"].astype(np.float32)
    out[:, 2] = rec["z"].astype(np.float32)

    if "intensity" in fields:
        out[:, 3] = rec["intensity"].astype(np.float32)
    elif "rgb" in fields:
        # Handle float-packed RGB or uint32 packed (g<<16 | g<<8 | g)
        if rec["rgb"].dtype == np.float32:
            rgb_u32 = rec["rgb"].view(np.uint32)
        else:
            rgb_u32 = rec["rgb"].astype(np.uint32)
        gray = ((rgb_u32 >> 16) & 0xFF).astype(np.float32)
        t = np.clip((gray - 40.0) / 215.0, 0.0, 1.0)
        # Clamp strictly matching inverse of int(40 + 215 * min(1, log1p(v)/log1p(50)))
        out[:, 3] = np.where(gray <= 40.0, 0.0, np.expm1(t * math.log1p(50.0))).astype(np.float32)

    return out


class _SimpleResponse:
    """Fallback response wrapper for offline unit testing without nuclio-sdk."""

    def __init__(self, body, content_type="application/json", status_code=200):
        self.body = body
        self.content_type = content_type
        self.status_code = status_code


def init_context(context) -> None:
    context.user_data.detector = Detector(Config(score_thr=0.1, min_points=0))


def handler(context, event):
    body = event.body if isinstance(event.body, dict) else json.loads(event.body)
    threshold = float(body.get("threshold", 0.3))
    pcd_raw = base64.b64decode(body["image"])
    points = parse_pcd(pcd_raw)
    boxes = context.user_data.detector.detect(points)

    results = []
    for box in boxes:
        score = float(box.get("score", 0.0))
        if score < threshold:
            continue
        label_name = VF_NAMES.get(box["label"], str(box["label"]))
        results.append({
            "type": "cuboid",
            "label": label_name,
            "confidence": f"{score:.4f}",
            "points": [
                round(float(box["x"]), 4),
                round(float(box["y"]), 4),
                round(float(box["z"]), 4),
                0.0,
                0.0,
                round(float(box["yaw"]), 4),
                round(float(box["length"]), 4),
                round(float(box["width"]), 4),
                round(float(box["height"]), 4),
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            ],
        })

    resp_cls = getattr(context, "Response", _SimpleResponse)
    return resp_cls(
        body=json.dumps(results),
        content_type="application/json",
        status_code=200,
    )
