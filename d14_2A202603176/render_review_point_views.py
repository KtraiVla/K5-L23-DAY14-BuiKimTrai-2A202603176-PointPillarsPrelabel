"""Generate scientific orthographic LiDAR checks; never changes reference labels."""
import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

repo=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(repo))
from scripts import vf_d14
run=repo/'d14_2A202603176'
parser=argparse.ArgumentParser(description='Render orthographic LiDAR checks from the current review checklist; does not edit labels.')
parser.add_argument('--data',type=Path,required=True)
parser.add_argument('--out',type=Path,default=run/'png_review_live_ids')
args=parser.parse_args()
out=args.out
out.mkdir(exist_ok=True)
data=args.data
with (run/'review_checklist.csv').open(encoding='utf-8-sig',newline='') as handle:
    rows=list(csv.DictReader(handle))
extra={('s02f54',n) for n in (106,113,114,115,117,120,122,126)}|{('s05f01',197)}
cache={}
try:
    font=ImageFont.truetype('arial.ttf',15)
    small=ImageFont.truetype('arial.ttf',13)
except OSError:
    font=ImageFont.load_default(size=15)
    small=ImageFont.load_default(size=13)
count=0
for row in rows:
    ident=(row['frame'],int(row['cvat_object_id']))
    if not row['flags'] and ident not in extra:
        continue
    if row['frame'] not in cache:
        frame=vf_d14.frame_rows(data,[row['frame']])[0]
        cache[row['frame']]=vf_d14.load_points(frame)[:,:3]
    points=cache[row['frame']]
    x,y,z,length,width,height,yaw=(float(row[k]) for k in ('x','y','z','length','width','height','yaw'))
    c,s=math.cos(yaw),math.sin(yaw)
    diff=points-np.array([x,y,z])
    local=np.column_stack((c*diff[:,0]+s*diff[:,1],-s*diff[:,0]+c*diff[:,1],diff[:,2]))
    halves=np.array([length,width,height])/2
    margin=np.array([2.0,2.0,2.0])
    local=local[np.all(np.abs(local)<=halves+margin,axis=1)]
    inside=np.all(np.abs(local)<=halves,axis=1)
    sheet=Image.new('RGB',(1500,500),'#111722')
    draw=ImageDraw.Draw(sheet)
    title=f"{row['part']} {row['frame']} | CVAT #{row['cvat_object_id']} {row['label']} | center=({x:.2f},{y:.2f},{z:.2f}) m | L/W/H={length:.2f}/{width:.2f}/{height:.2f} m"
    draw.text((15,10),title,fill='#ffffff',font=font)
    for panel,(a,b,name) in enumerate(((0,1,'TOP: local X/Y'),(0,2,'SIDE: local X/Z'),(1,2,'FRONT: local Y/Z'))):
        left=panel*500+50;top=70;right=panel*500+480;bottom=410
        ranges=[halves[a]+margin[a],halves[b]+margin[b]]
        scale=min((right-left)/(ranges[0]*2),(bottom-top)/(ranges[1]*2))
        cx=(left+right)/2;cy=(top+bottom)/2
        def transform(u,v):return cx+float(u)*scale,cy-float(v)*scale
        draw.text((left,45),name,fill='#ffffff',font=font)
        for value in range(-int(ranges[0]),int(ranges[0])+1):
            u,_=transform(value,0)
            draw.line((u,top,u,bottom),fill='#242c38')
            draw.text((u-8,bottom+4),str(value),fill='#b9c3d2',font=small)
        for value in range(-int(ranges[1]),int(ranges[1])+1):
            _,v=transform(0,value)
            draw.line((left,v,right,v),fill='#242c38')
            draw.text((left-30,v-7),str(value),fill='#b9c3d2',font=small)
        for point,is_inside in zip(local,inside):
            u,v=transform(point[a],point[b])
            if left<=u<=right and top<=v<=bottom:
                draw.ellipse((u-1,v-1,u+1,v+1),fill='#58b8ff' if is_inside else '#8f99a7')
        x0,y0=transform(-halves[a],halves[b]);x1,y1=transform(halves[a],-halves[b])
        draw.rectangle((x0,y0,x1,y1),outline='#ff7070',width=2)
        if b==2 and row['ground_gap_m']:
            ground=-height/2-float(row['ground_gap_m'])
            _,gy=transform(0,ground)
            if top<=gy<=bottom:
                draw.line((left,gy,right,gy),fill='#f2b255',width=2)
                draw.text((left+4,gy-18),'heuristic ground',fill='#f2b255',font=small)
    draw.text((15,445),'Blue: points inside current box | Gray: nearby points | Red: current box | Values: metres in the box-local axes',fill='#d5dce7',font=small)
    draw.text((15,472),'Review aid only. Ground is a heuristic; surrounding points may belong to another object. No labels were edited.',fill='#d5dce7',font=small)
    sheet.save(out/f"{row['part']}_{row['frame']}_object_{row['cvat_object_id']}_points.png")
    count+=1
print('Orthographic QA sheets generated:',count)
