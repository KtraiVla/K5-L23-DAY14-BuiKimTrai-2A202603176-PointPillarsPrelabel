import argparse
import csv
import hashlib
import itertools
import json
import math
import sys
import time
from dataclasses import replace
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo))
from scripts import vf_d14
import vf_pp.core as core
from vf_pp.core import Config, Detector, correction_cost, postprocess

run = repo / 'd14_2A202603176'
out = run / 'improvement_A_only'
out.mkdir(exist_ok=True)
parser = argparse.ArgumentParser(description='Reproduce the exploratory A-only search; writes derived experiment files.')
parser.add_argument('--data', type=Path, required=True, help='Path to the local Data-VF dataset')
args = parser.parse_args()
data = args.data
# The exploratory search started from the first tied sweep winner, min_points=0.
base = replace(Config.from_dict(json.loads((run / 'best_config.json').read_text(encoding='utf-8-sig'))), min_points=0)
names = vf_d14.read_frame_list(str(run / 'frames_A.txt'))
gt = vf_d14.load_reference(str(run / 'ref_A.json'), data, names, require_all=True)
points = {row['name']: vf_d14.load_points(row) for row in vf_d14.frame_rows(data, names)}
source_hash = hashlib.sha256((repo / 'vf_pp/core.py').read_bytes()).hexdigest()
run_cfg = replace(base, score_thr=0.05, thr_car=None, thr_cyc=None, thr_ped=None)
cache = Path(__file__).parent / 'raw_A_optimization.json'
cache_key = {'config': run_cfg.to_dict(), 'frames': names, 'core_sha256': source_hash,
             'reference_sha256': hashlib.sha256((run / 'ref_A.json').read_bytes()).hexdigest()}
cached = json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else None
if cached and cached['key'] == cache_key:
    raw = cached['raw']
    print('Reusing exact raw model outputs for A.', flush=True)
else:
    detector = Detector(run_cfg)
    raw = {}
    for name in names:
        start = time.time()
        raw[name] = detector.raw_detect(points[name])
        print(f'{name}: {len(raw[name])} raw boxes, {time.time() - start:.1f}s', flush=True)
    cache.write_text(json.dumps({'key': cache_key, 'raw': raw}), encoding='utf-8')

# Memoize a pure geometry operation within this process only. Source files and
# post-processing/matching rules remain unchanged.
original_point_count = core.points_in_box
point_cache = {}
geometry = ('x','y','z','length','width','height','yaw')
def counted(raw_points, box):
    key = (id(raw_points), tuple(box[k] for k in geometry))
    if key not in point_cache:
        point_cache[key] = original_point_count(raw_points, box)
    return point_cache[key]
core.points_in_box = counted
metric_cache = {name: {} for name in names}
def score(name, predictions):
    key = tuple(sorted(tuple(round(float(box[k]), 6) for k in geometry) + (int(box['label']),) for box in predictions))
    if key not in metric_cache[name]:
        metric_cache[name][key] = correction_cost(gt[name], predictions)
    return metric_cache[name][key]

def config_distance(cfg):
    bd, cd = base.to_dict(), cfg.to_dict()
    changed = [k for k in bd if k != 'extra' and bd[k] != cd[k]]
    distance = 0.0
    for key in changed:
        before, after = bd[key], cd[key]
        if key in ('thr_car','thr_cyc','thr_ped'):
            distance += abs((after if after is not None else cfg.score_thr) - (before if before is not None else base.score_thr)) / 0.1
        elif key == 'min_points':
            distance += abs(after - before) / 10
        else:
            distance += abs(after - before) / 0.1
    return len(changed), round(distance, 6)

configs = [base]
for threshold, minimum in itertools.product((0.35,0.375,0.4,0.425,0.45,0.475,0.5), (0,5,10,15)):
    configs.append(replace(base, score_thr=threshold, min_points=minimum))
for car, cyc, ped, minimum, merge in itertools.product((0.4,0.425,0.44,0.45,0.475), (0.35,0.4,0.425), (0.35,0.4,0.45), (0,5,10,15), (0.05,0.1,0.15)):
    configs.append(replace(base, thr_car=car, thr_cyc=cyc, thr_ped=ped, min_points=minimum, merge_nms_thr=merge))
unique = {}
for cfg in configs:
    cfg = replace(cfg, **{key: None for key in ('thr_car','thr_cyc','thr_ped') if getattr(cfg, key) == cfg.score_thr})
    unique[json.dumps(cfg.to_dict(), sort_keys=True)] = cfg
configs = list(unique.values())
results = []
for index, cfg in enumerate(configs, 1):
    per_frame = {name: score(name, postprocess(raw[name], points[name], cfg)) for name in names}
    total = {key: sum(row[key] for row in per_frame.values()) for key in ('delete','add','edit')}
    total['cost'] = round(0.3 * total['delete'] + total['add'] + 0.5 * total['edit'], 2)
    results.append({'cfg': cfg, 'per_frame': per_frame, **total, 'complexity': config_distance(cfg)})
    if index % 100 == 0 or index == len(configs):
        print(f'Evaluated {index}/{len(configs)} A-only candidates', flush=True)

baseline = next(row for row in results if row['cfg'].to_dict() == base.to_dict())
eligible = [row for row in results if all(row['per_frame'][name]['cost'] <= baseline['per_frame'][name]['cost'] for name in names)]
selected = min(eligible, key=lambda row: (row['cost'], row['complexity'], json.dumps(row['cfg'].to_dict(), sort_keys=True)))
loo = []
for held in names:
    pick = min(results, key=lambda row: (round(sum(row['per_frame'][name]['cost'] for name in names if name != held), 6), row['complexity'], json.dumps(row['cfg'].to_dict(), sort_keys=True)))
    loo.append({'held_out': held, 'selected_config': pick['cfg'].to_dict(), 'held_out_cost': pick['per_frame'][held]['cost'],
                'best_possible_cost': min(row['per_frame'][held]['cost'] for row in results), 'baseline_cost': baseline['per_frame'][held]['cost']})

results.sort(key=lambda row: (row['cost'], row['complexity']))
with (out / 'sweep_extended_A.csv').open('w', encoding='utf-8', newline='') as handle:
    fields = ['score_thr','thr_car','thr_cyc','thr_ped','min_points','merge_nms_thr','cost','delete','add','edit'] + names
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for row in results:
        values = row['cfg'].to_dict()
        writer.writerow({**{key: values[key] for key in fields[:6]}, **{key: row[key] for key in ('cost','delete','add','edit')}, **{name: row['per_frame'][name]['cost'] for name in names}})

frozen = selected['cfg'].to_dict()
(out / 'candidate_config.json').write_text(json.dumps(frozen, indent=1), encoding='utf-8')
selected_predictions = {name: postprocess(raw[name], points[name], selected['cfg']) for name in names}
vf_d14.save_boxes(out / 'pred_A_candidate.json', selected_predictions, {'config': frozen, 'frames': names, 'selection': 'A only, frozen before B evaluation'})
summary = {'selection_policy': 'A only; no frame worse than baseline; minimize total A cost, then changed-knob count and distance. B not read during selection.',
           'candidate_count': len(results), 'baseline': {key: baseline[key] for key in ('cost','delete','add','edit')},
           'candidate': {key: selected[key] for key in ('cost','delete','add','edit')},
           'candidate_config': frozen, 'candidate_config_sha256': hashlib.sha256((out / 'candidate_config.json').read_bytes()).hexdigest(),
           'A_per_frame': selected['per_frame'], 'leave_one_out': loo,
           'reference_sha256': cache_key['reference_sha256'], 'B_evaluated': False}
(out / 'selection_A.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
assert hashlib.sha256((repo / 'vf_pp/core.py').read_bytes()).hexdigest() == source_hash
print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
