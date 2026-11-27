"""Call CVAT /api/lambda/requests for deployed Nuclio PointPillars and match vs offline preds."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from base64 import b64encode
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts import vf_common as vf, vf_d14  # noqa: E402
from d14_2A202603176.bonus_nuclio_pp.stage_and_eval import match_within_radius  # noqa: E402


def _req(url: str, auth_header: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": auth_header}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def main() -> int:
    vf.configure_utf8_stdio()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default="http://localhost:8080")
    ap.add_argument("--user", required=True)
    ap.add_argument("--task", type=int, required=True, help="CVAT task id to run lambda on (use a test/copy task)")
    ap.add_argument("--function", default="pp-2a202603176")
    ap.add_argument("--threshold", type=float, default=0.3)
    ap.add_argument("--offline", type=Path, required=True, help="pred_A.json or pred_B.json for comparison")
    ap.add_argument("--out", type=Path, default=ROOT / "d14_2A202603176" / "bonus_nuclio_pp" / "lambda_match_report.json")
    ap.add_argument("--skip-invoke", action="store_true", help="Only fetch existing annotations and match")
    args = ap.parse_args()

    pw = os.environ.get("CVAT_PASSWORD")
    if not pw:
        raise SystemExit("Set CVAT_PASSWORD environment variable first.")
    auth = "Basic " + b64encode(f"{args.user}:{pw}".encode("utf-8")).decode("ascii")
    host = args.host.rstrip("/")

    if not args.skip_invoke:
        res = _req(
            f"{host}/api/lambda/requests",
            auth,
            method="POST",
            payload={"function": args.function, "task": args.task, "threshold": args.threshold, "cleanup": True},
        )
        req_id = res["id"]
        print(f"Started lambda request {req_id} on task {args.task}...")
        while True:
            st = _req(f"{host}/api/lambda/requests/{req_id}", auth)
            status = st.get("status")
            prog = st.get("progress", 0)
            print(f"  status={status}, progress={prog}")
            if status in ("finished", "failed", "unknown"):
                if status != "finished":
                    raise SystemExit(f"Lambda failed: {st}")
                break
            time.sleep(2.0)

    # Fetch meta frames & job annotations via API (avoids cvat#9144 export bug)
    task_info = _req(f"{host}/api/tasks/{args.task}", auth)
    jobs = _req(f"{host}/api/jobs?task_id={args.task}", auth).get("results", [])
    meta = _req(f"{host}/api/tasks/{args.task}/data/meta", auth)
    frames = [vf.frame_name(*vf.parse_frame_name(f["name"])) for f in meta["frames"]]

    cvat_by_frame = {fn: [] for fn in frames}
    for job in jobs:
        ann = _req(f"{host}/api/jobs/{job['id']}/annotations", auth)
        labels = {lab["id"]: lab["name"] for lab in _req(f"{host}/api/labels?task_id={args.task}", auth).get("results", [])}
        for s in ann.get("shapes", []):
            if s.get("type") != "cuboid":
                continue
            fn = frames[s["frame"]]
            cvat_by_frame[fn].append(vf.cuboid_from_cvat(s["points"], labels.get(s["label_id"], "?"), "lwh", bool(s.get("occluded"))))

    offline_doc = json.loads(args.offline.read_text(encoding="utf-8-sig"))["frames"]
    report_rows = []
    for fn in frames:
        off_boxes = [b for b in offline_doc.get(fn, []) if float(b.get("score", 1.0)) >= args.threshold]
        c_boxes = cvat_by_frame[fn]
        matched = match_within_radius(c_boxes, off_boxes, 0.5)
        report_rows.append({"frame": fn, "cvat_boxes": len(c_boxes), "offline_boxes": len(off_boxes), "matched_le_0_5m": matched})
        print(f"  {fn}: CVAT={len(c_boxes)}, offline={len(off_boxes)}, matched<=0.5m={matched}")

    payload = {
        "task_id": args.task,
        "task_name": task_info.get("name"),
        "function": args.function,
        "threshold": args.threshold,
        "rows": report_rows,
        "totals": {
            "cvat_boxes": sum(r["cvat_boxes"] for r in report_rows),
            "offline_boxes": sum(r["offline_boxes"] for r in report_rows),
            "matched_le_0_5m": sum(r["matched_le_0_5m"] for r in report_rows),
        },
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved match report -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
