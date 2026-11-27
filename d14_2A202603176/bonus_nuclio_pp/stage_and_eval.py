"""Stage clean Nuclio deploy bundle (without committing third_party/weights) and compare PCD vs offline boxes."""
from __future__ import annotations

import argparse
import base64
import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts import vf_common as vf, vf_d14  # noqa: E402
from d14_2A202603176.bonus_nuclio_pp import main as nuclio_main  # noqa: E402


def stage_bundle(out_dir: Path) -> Path:
    """Copy minimal Nuclio deploy artifacts into an untracked staging folder (`out/`)."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    shutil.copy2(here / "main.py", out_dir / "main.py")
    shutil.copy2(here / "function.yaml", out_dir / "function.yaml")
    shutil.copytree(ROOT / "vf_pp", out_dir / "vf_pp", ignore=shutil.ignore_patterns("__pycache__"))
    model_src = ROOT / "third_party" / "PointPillars" / "pointpillars" / "model"
    model_dst = out_dir / "third_party" / "PointPillars" / "pointpillars" / "model"
    shutil.copytree(model_src, model_dst, ignore=shutil.ignore_patterns("__pycache__"))
    weights_src = ROOT / "third_party" / "PointPillars" / "pretrained" / "epoch_160.pth"
    weights_dst = out_dir / "third_party" / "PointPillars" / "pretrained" / "epoch_160.pth"
    weights_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(weights_src, weights_dst)
    return out_dir


def match_within_radius(cvat_boxes: list[dict], offline_boxes: list[dict], radius_m: float = 0.5) -> int:
    """Count greedy 1-to-1 same-label center matches within radius_m."""
    used: set[int] = set()
    matches = 0
    for cb in cvat_boxes:
        best_j = None
        best_d = radius_m + 1e-9
        for j, ob in enumerate(offline_boxes):
            if j in used or cb["label"] != ob["label"]:
                continue
            d = math.hypot(cb["x"] - ob["x"], cb["y"] - ob["y"])
            d3 = math.sqrt((cb["x"] - ob["x"]) ** 2 + (cb["y"] - ob["y"]) ** 2 + (cb["z"] - ob["z"]) ** 2)
            if d3 <= radius_m and d3 < best_d:
                best_d = d3
                best_j = j
        if best_j is not None:
            used.add(best_j)
            matches += 1
    return matches


def main() -> int:
    vf.configure_utf8_stdio()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--frames", type=Path, default=ROOT / "d14_2A202603176" / "frames_A.txt")
    ap.add_argument("--offline", type=Path, default=ROOT / "d14_2A202603176" / "pred_A.json")
    ap.add_argument("--threshold", type=float, default=0.3)
    ap.add_argument("--stage-out", type=Path, default=ROOT / "out" / "nuclio_pp_2a202603176")
    ap.add_argument("--no-stage", action="store_true")
    args = ap.parse_args()

    if not args.no_stage:
        staged = stage_bundle(args.stage_out)
        print(f"Staged Nuclio bundle (gitignored): {staged}")

    names = vf_d14.read_frame_list(str(args.frames))
    rows = vf_d14.frame_rows(args.data, names)
    offline_doc = json.loads(args.offline.read_text(encoding="utf-8-sig"))["frames"]

    class _Ctx:
        class user_data:
            pass
        Response = nuclio_main._SimpleResponse

    class _Evt:
        def __init__(self, body):
            self.body = body

    ctx = _Ctx()
    nuclio_main.init_context(ctx)

    print(f"\nOffline PCD simulation (threshold={args.threshold:.2f}, radius<=0.5m):")
    tot_pcd, tot_off, tot_match = 0, 0, 0
    for row in rows:
        fn = row["name"]
        pcd_bytes = vf.bin_to_pcd(row["lidar"])
        resp = nuclio_main.handler(ctx, _Evt({"image": base64.b64encode(pcd_bytes).decode("ascii"), "threshold": args.threshold}))
        raw_preds = json.loads(resp.body)
        pcd_boxes = [vf.cuboid_from_cvat(p["points"], p["label"]) for p in raw_preds]
        off_boxes = [b for b in offline_doc[fn] if float(b.get("score", 1.0)) >= args.threshold]
        m = match_within_radius(pcd_boxes, off_boxes, 0.5)
        tot_pcd += len(pcd_boxes)
        tot_off += len(off_boxes)
        tot_match += m
        print(f"  {fn}: PCD={len(pcd_boxes):2d}, offline={len(off_boxes):2d}, matched_<=0.5m={m:2d}")
    print(f"Total: PCD={tot_pcd}, offline={tot_off}, matched_<=0.5m={tot_match}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
