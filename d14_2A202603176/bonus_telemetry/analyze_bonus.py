"""Helper for Bonus Direction 1: evaluate telemetry logs per-frame & compare vs correction cost."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bonus.telemetry_metrics import session_metrics  # noqa: E402
from scripts import vf_common as vf, vf_d14  # noqa: E402
from vf_pp.core import correction_cost  # noqa: E402


def main() -> int:
    vf.configure_utf8_stdio()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("logs", nargs="+", type=Path, help="d14-telemetry-*.json logs from browser")
    ap.add_argument("--gt", type=Path, default=ROOT / "d14_2A202603176" / "ref_B.json")
    ap.add_argument("--pred", type=Path, default=ROOT / "d14_2A202603176" / "pred_B.json")
    ap.add_argument("--frames", type=Path, default=ROOT / "d14_2A202603176" / "frames_B.txt")
    ap.add_argument("--split-dir", type=Path, default=ROOT / "out" / "telemetry_per_frame")
    ap.add_argument("--csv", type=Path, default=ROOT / "d14_2A202603176" / "telemetry.csv")
    args = ap.parse_args()

    frame_names = vf_d14.read_frame_list(str(args.frames))
    per_frame_events: dict[str, list[dict]] = defaultdict(list)

    for p in args.logs:
        evs = json.loads(p.read_text(encoding="utf-8-sig"))
        if not isinstance(evs, list):
            continue
        for ev in evs:
            fidx = ev.get("frame")
            if isinstance(fidx, int) and 0 <= fidx < len(frame_names):
                per_frame_events[frame_names[fidx]].append(ev)

    rows = []
    if len(args.logs) == 1 and per_frame_events:
        args.split_dir.mkdir(parents=True, exist_ok=True)
        for fn in frame_names:
            fevs = per_frame_events.get(fn, [])
            if not fevs:
                continue
            out_p = args.split_dir / f"d14-telemetry-{fn}.json"
            clean_evs = [{k: v for k, v in e.items() if k != "frame"} for e in fevs]
            out_p.write_text(json.dumps(clean_evs, indent=1), encoding="utf-8")
            rows.append({"file": fn, **session_metrics(clean_evs)})
    else:
        for p in sorted(args.logs):
            evs = json.loads(p.read_text(encoding="utf-8-sig"))
            if evs:
                rows.append({"file": p.stem, **session_metrics(evs)})

    if not rows:
        print("No telemetry events found in logs.", file=sys.stderr)
        return 1

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {args.csv} ({len(rows)} session rows).")

    gt = json.loads(args.gt.read_text(encoding="utf-8-sig"))["frames"]
    pr = json.loads(args.pred.read_text(encoding="utf-8-sig"))["frames"]
    tot_clicks = sum(r["canvas_clicks"] for r in rows)
    tot_keys = sum(r["shortcut_keys"] for r in rows)
    tot_sec = sum(r["active_span_s"] for r in rows)
    c_tot = {"delete": 0, "add": 0, "edit": 0, "cost": 0.0}
    for fn in frame_names:
        if fn in gt and fn in pr:
            c = correction_cost(gt[fn], pr[fn])
            for k in c_tot:
                c_tot[k] += c[k]
    ops = max(c_tot["delete"] + c_tot["add"] + c_tot["edit"], 1)
    print(f"Total actions recorded: clicks={tot_clicks}, shortcuts={tot_keys}, active_span_s={tot_sec}")
    print(f"Ground-truth correction ops (B): delete={c_tot['delete']}, add={c_tot['add']}, edit={c_tot['edit']}, cost={c_tot['cost']:.1f}")
    print(f"Avg clicks/op={tot_clicks/ops:.2f}, avg sec/op={tot_sec/ops:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
