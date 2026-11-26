"""Read-only local technical audit. This is not the coach's check_student.py.

Run from any directory with the lab venv Python:
python d14_2A202603176/verify_submission.py --data PATH_TO_DATA_VF
Supply the official SEED via D14_SEED or --seed; it is never written to disk.
Quality of annotations and historical/personal 5b content require human review.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import vf_common as vf, vf_d14
from vf_pp.core import Config, correction_cost


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def metrics(reference, predictions):
    rows = {name: correction_cost(boxes, predictions[name])
            for name, boxes in reference.items()}
    total = {key: sum(row[key] for row in rows.values())
             for key in ('gt', 'pred', 'match', 'delete', 'add', 'edit')}
    total['cost'] = round(.3 * total['delete'] + total['add'] + .5 * total['edit'], 2)
    return {'total': total, 'per_frame': rows}


def geometry(boxes):
    keys = ('x', 'y', 'z', 'length', 'width', 'height', 'yaw')
    return collections.Counter(tuple(round(float(box[key]), 4) for key in keys)
                               + (box['label'],) for box in boxes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--seed', default=os.environ.get('D14_SEED', ''))
    args = parser.parse_args()
    require(bool(args.seed.strip()), 'Supply the official SEED via D14_SEED or --seed.')
    run = Path(__file__).resolve().parent
    student = '2A202603176'
    counts = {seq: len(stamps) for seq, stamps in vf.list_sequences(args.data).items()}
    require(counts == {seq: 60 for seq in range(1, 6)}, 'Data-VF must contain all five sequences of 60 frames.')
    frames = {part: vf_d14.read_frame_list(str(run / f'frames_{part}.txt')) for part in ('A', 'B')}
    require(frames == vf_d14.select_d14(student, args.seed.strip(), counts), 'Frame assignment differs from official selector.')
    require(len(frames['A']) == 3 and len(frames['B']) == 12, 'Wrong frame counts.')
    require(set(frames['A']).isdisjoint(frames['B']), 'A and B overlap.')
    tag = vf_d14.seed_tag(args.seed.strip())
    for part in frames:
        require(f'seed_tag={tag}' in (run / f'frames_{part}.txt').read_text(encoding='utf-8-sig'), 'Wrong seed_tag.')
        for row in vf_d14.frame_rows(args.data, frames[part]):
            require(row['lidar'].is_file() and len(row['cameras']) == 7, f"Missing data: {row['name']}")

    docs = {name: load(run / f'{name}.json')
            for name in ('pred_A', 'pred_A_filtered', 'ref_A', 'pred_B', 'ref_B')}
    for name, doc in docs.items():
        part = name.split('_')[1]
        require(set(doc['frames']) == set(frames[part]), f'{name}: missing or extra frame.')
        for boxes in doc['frames'].values():
            for box in boxes:
                require(box['label'] in vf.CLASS_IDS, f'{name}: unknown class.')
                keys = ('x', 'y', 'z', 'length', 'width', 'height', 'yaw')
                require(all(math.isfinite(float(box[key])) for key in keys), f'{name}: non-finite box.')
                require(min(float(box[key]) for key in ('length', 'width', 'height')) > 0, f'{name}: invalid size.')

    cfg = Config.from_dict(load(run / 'best_config.json')).to_dict()
    require(docs['pred_A']['meta']['config'] == Config().to_dict(), 'pred_A is not the original default configuration.')
    require(docs['pred_B']['meta']['config'] == cfg, 'pred_B configuration differs from best_config.')
    require(docs['pred_A_filtered']['meta']['config'] == cfg, 'Filtered A configuration differs from best_config.')
    changes = {key for key in cfg if cfg[key] != Config().to_dict()[key]}
    require(changes <= {'score_thr', 'min_points'}, 'This offline A check supports only threshold/min-points changes.')
    filtered = {name: [box for box in boxes if box['score'] >= cfg['score_thr'] and box['npts'] >= cfg['min_points']]
                for name, boxes in docs['pred_A']['frames'].items()}
    require(all(geometry(filtered[name]) == geometry(docs['pred_A_filtered']['frames'][name])
                for name in frames['A']), 'Filtered A boxes differ from threshold/min-points filtering.')
    results = {
        'A_default': metrics(docs['ref_A']['frames'], docs['pred_A']['frames']),
        'A_tuned': metrics(docs['ref_A']['frames'], docs['pred_A_filtered']['frames']),
        'B_tuned': metrics(docs['ref_B']['frames'], docs['pred_B']['frames']),
    }
    with (run / 'sweep.csv').open(encoding='utf-8-sig', newline='') as handle:
        sweep = list(csv.DictReader(handle))
    require({(float(row['score_thr']), int(row['min_points'])) for row in sweep}
            == {(score, points) for score in (.1, .2, .3, .4, .5) for points in (0, 5, 10)}, 'Incomplete mandatory sweep.')
    chosen = next(row for row in sweep if float(row['score_thr']) == cfg['score_thr'] and int(row['min_points']) == cfg['min_points'])
    for key in ('delete', 'add', 'edit', 'cost'):
        require(abs(float(chosen[key]) - results['A_tuned']['total'][key]) < 1e-8, f'Sweep mismatch: {key}')
    require(any(geometry(docs['ref_B']['frames'][name]) != geometry(docs['pred_B']['frames'][name])
                for name in frames['B']), 'Every B reference box equals model output.')
    saved = load(run / 'validation_summary.json')
    for name, result in results.items():
        require(saved[name] == result, f'Stale validation_summary: {name}')
    qa = load(run / 'pointcloud_qa_summary.json')
    with (run / 'pointcloud_qa.csv').open(encoding='utf-8-sig', newline='') as handle:
        qa_rows = list(csv.DictReader(handle))
    refs = sum(len(boxes) for name in ('ref_A', 'ref_B') for boxes in docs[name]['frames'].values())
    require(len(qa_rows) == qa['total_boxes'] == refs, 'QA reference counts differ.')
    require(sum(bool(row['flags']) for row in qa_rows) == qa['boxes_with_warnings'], 'QA warning count differs.')
    snapshot_path = run / 'live_cvat_review_snapshot.json'
    if snapshot_path.exists():
        snapshot = load(snapshot_path)
        for part in frames:
            current_hash = hashlib.sha256((run / f'ref_{part}.json').read_bytes()).hexdigest()
            require(snapshot['references_sha256'][part] == current_hash, 'Live-review snapshot is stale; rebuild before using its object IDs.')
        with (run / 'review_checklist.csv').open(encoding='utf-8-sig', newline='') as handle:
            checklist = list(csv.DictReader(handle))
        require(len(checklist) == refs, 'Review checklist count differs.')
        for row in checklist:
            box = docs[f"ref_{row['part']}"]['frames'][row['frame']][int(row['reference_idx']) - 1]
            require(row['label'] == box['label'] and all(abs(float(row[key]) - box[key]) < 1e-8
                    for key in ('x', 'y', 'z', 'length', 'width', 'height', 'yaw')), 'Review checklist differs from reference.')
    for name in frames['A']:
        with Image.open(run / 'compare' / f'{name}.jpg') as picture:
            picture.verify()
    report = ROOT / 'report/individual/2A202603176_BuiKimTrai.md'
    content = report.read_text(encoding='utf-8-sig')
    require(all(f'## {number}.' in content for number in range(1, 6)), 'Missing report section.')
    require(not any(token in content for token in ('<ID>', '<MSSV>', '<Họ và tên>', 'd14_<')), 'Unfilled report template.')
    for target in re.findall(r'\]\(([^)]+)\)', content):
        if not target.startswith(('http:', 'https:')):
            require((report.parent / target).resolve().exists(), f'Broken report link: {target}')
    require(bool(re.search(r'!\[[^\]]*\]\([^)]*compare/[^)]*\.jpg\)', content)), 'No comparison image in report.')
    proposal_path = run / 'qa_proposed/B_proposal.json'
    if proposal_path.exists():
        proposal = load(proposal_path)
        observed = load(run / 'qa_proposed/cvat_validation.json')
        journal = load(run / 'qa_proposed/B_changes.json')
        require(proposal['meta']['source_reference_sha256'] == hashlib.sha256((run / 'ref_B.json').read_bytes()).hexdigest(), 'QA proposal source is stale.')
        require(proposal['meta']['not_for_submission_as_reference'] is True and observed['human_validated'] is False, 'QA proposal status is inconsistent.')
        require(set(proposal['frames']) == set(frames['B']), 'QA proposal frame set differs.')
        for name, boxes in proposal['frames'].items():
            require(len(boxes) == observed['frame_counts_observed_in_UI'][name], 'QA proposal/UI box counts differ.')
            require(dict(collections.Counter(box['label'] for box in boxes)) == observed['class_counts_observed_in_UI'][name], 'QA proposal/UI classes differ.')
            for box in boxes:
                require(box['label'] in vf.CLASS_IDS and all(math.isfinite(float(box[key])) for key in ('x', 'y', 'z', 'length', 'width', 'height', 'yaw'))
                        and min(box[key] for key in ('length', 'width', 'height')) > 0, 'Invalid QA proposal box.')
        require(sum(map(len, proposal['frames'].values())) == journal['proposed_boxes'] == observed['total_boxes'], 'QA proposal totals differ.')
        require(journal['original_boxes'] - journal['proposed_boxes'] == sum(action['action'] == 'propose_delete' for action in journal['actions']), 'QA proposal deletion journal differs.')
    print(json.dumps({'technical_checks': 'PASS', 'student': student, 'seed_tag': tag,
                      'metrics': {name: value['total'] for name, value in results.items()},
                      'frame_list_sha256': {part: hashlib.sha256((run / f'frames_{part}.txt').read_bytes()).hexdigest() for part in frames},
                      'not_validated': ['historical 5b prediction', 'human quality of every annotation', 'LMS submission'],
                      'quality_review': f"PENDING: {qa['boxes_with_warnings']}/{qa['total_boxes']} boxes have heuristic warnings; see VISUAL_REVIEW.md."},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, StopIteration) as error:
        print(f'TECHNICAL CHECK FAILED: {error}', file=sys.stderr)
        sys.exit(1)
