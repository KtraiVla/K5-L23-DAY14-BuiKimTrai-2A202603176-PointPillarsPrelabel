import argparse
import collections
import csv
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(repo))
from scripts import vf_d14, vf_qa

run=repo/'d14_2A202603176'
parser=argparse.ArgumentParser(description='Regenerate local reference camera/BEV sheets and heuristic QA; does not edit labels.')
parser.add_argument('--data',type=Path,required=True)
data=parser.parse_args().data
all_rows=[]
summary={}
calibrations={}
for part in ('A','B'):
    reference=json.loads((run/f'ref_{part}.json').read_text(encoding='utf-8-sig'))['frames']
    images=run/f'png_reference_{part}'
    images.mkdir(exist_ok=True)
    for row in vf_d14.frame_rows(data,list(reference)):
        boxes=[dict(box,idx=index) for index,box in enumerate(reference[row['name']],1)]
        checks=vf_qa.check_frame(boxes,vf_qa.points_xyz(row['lidar']))
        all_rows.extend({'part':part,'frame':row['name'],**check} for check in checks)
        if row['seq'] not in calibrations:
            calibrations[row['seq']]=vf_qa.load_calib(data/f"sequence_{row['seq']:02d}")
        sheet,_=vf_qa.render_frame(row,boxes,calibrations[row['seq']])
        sheet.save(images/f"{row['name']}.jpg",quality=88)
        flagged=sum(bool(check['flags']) for check in checks)
        summary[row['name']]={'part':part,'boxes':len(boxes),'boxes_with_heuristic_warnings':flagged,
                              'preview':str((images/f"{row['name']}.jpg").relative_to(repo)).replace('\\','/')}
        print(f"{part}/{row['name']}: {len(boxes)} boxes, {flagged} warning(s)",flush=True)

fields=['part']+vf_qa.CHECK_FIELDS
with (run/'pointcloud_qa.csv').open('w',encoding='utf-8-sig',newline='') as handle:
    writer=csv.DictWriter(handle,fieldnames=fields)
    writer.writeheader()
    writer.writerows(all_rows)
categories=collections.Counter()
for check in all_rows:
    for flag in check['flags'].split('; '):
        if flag:
            if 'rỗng' in flag: categories['empty_box']+=1
            elif 'rất ít' in flag: categories['few_points']+=1
            elif 'chìm' in flag: categories['possible_sunk']+=1
            elif 'lơ lửng' in flag: categories['possible_floating']+=1
            elif 'chồng' in flag: categories['overlap']+=1
            elif 'chật' in flag: categories['possible_tight_box']+=1
            else: categories['size_or_orientation']+=1
document={'method':'Existing scripts/vf_qa.py heuristics; warnings are prompts for visual review, not confirmed labeling errors.',
          'total_boxes':len(all_rows),'boxes_with_warnings':sum(bool(row['flags']) for row in all_rows),
          'warning_categories':dict(categories),'frames':summary}
(run/'pointcloud_qa_summary.json').write_text(json.dumps(document,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({key:document[key] for key in ('total_boxes','boxes_with_warnings','warning_categories')},ensure_ascii=False,indent=2))
