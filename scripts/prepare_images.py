"""Prepare lossless screenshot fragments and an OCR PDF; never modifies sources."""
from pathlib import Path
import argparse, hashlib, json, re
import numpy as np
from PIL import Image,ImageDraw
from reportlab.pdfgen import canvas

def natural(path):
 return [int(x) if x.isdigit() else x.casefold() for x in re.split(r'(\d+)',path.name)]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--work',required=True)
 ap.add_argument('--nominal-height-ratio',type=float,default=1.18)
 ap.add_argument('--max-height-ratio',type=float,default=1.65);a=ap.parse_args()
 src=Path(a.input).resolve();work=Path(a.work).resolve()
 if not src.is_dir():raise SystemExit('Input directory does not exist')
 if src==work or src in work.parents:raise SystemExit('Keep work directory outside source image directory')
 if a.nominal_height_ratio<=0 or a.max_height_ratio<=a.nominal_height_ratio:raise SystemExit('Invalid height ratios')
 files=sorted([p for p in src.iterdir() if p.suffix.lower() in {'.png','.jpg','.jpeg','.tif','.tiff','.bmp','.webp'}],key=natural)
 if not files:raise SystemExit('No supported image files')
 if (work/'pages.json').exists():raise SystemExit('pages.json exists; use a new work directory for a new preparation')
 work.mkdir(parents=True,exist_ok=True);pieces=work/'pages';pieces.mkdir(exist_ok=True)
 preview=work/'preview';preview.mkdir(exist_ok=True);pages=[];sources=[]
 Image.MAX_IMAGE_PIXELS=None
 for file in files:
  with Image.open(file) as opened:im=opened.convert('RGB')
  w,h=im.size;gray=np.asarray(im.convert('L'))
  sources.append({'name':file.name,'path':str(file),'width':w,'height':h,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
  ys=np.flatnonzero(((gray>140)&(gray<240)).mean(axis=1)>.97);groups=[]
  for y in ys:
   if not groups or y-groups[-1][-1]>max(3,round(w*.005)):groups.append([int(y)])
   else:groups[-1].append(int(y))
  bounds=[0]
  for group in groups:
   y=int(np.median(group))+2
   if y-bounds[-1]>w*.36:bounds.append(y)
  if h-bounds[-1]>w*.06:bounds.append(h)
  else:bounds[-1]=h
  for lo,hi in zip(bounds,bounds[1:]):
   height=hi-lo;cuts=[lo];reasons=['image_start' if lo==0 else 'gray_separator']
   if height>w*a.max_height_ratio:
    ink=(gray[lo:hi,int(w*.08):int(w*.94)]<170).mean(axis=1)
    radius=max(3,round(w*.005));score=np.convolve(ink,np.ones(radius)/radius,mode='same')
    n=max(2,round(height/(w*a.nominal_height_ratio)))
    for k in range(1,n):
     target=round(height*k/n);window=round(w*.15)
     low=max(cuts[-1]-lo+round(w*.48),target-window);high=min(height-round(w*.36),target+window)
     if low>=high:continue
     candidates=np.arange(low,high)
     best=int(candidates[np.argmin(score[low:high]+abs(candidates-target)/max(1,window)*.012)])
     cuts.append(lo+best);reasons.append('low_ink_split_review_required')
   cuts.append(hi)
   for j,(start,end) in enumerate(zip(cuts,cuts[1:])):
    dest=pieces/f'page-{len(pages)+1:03d}.png';im.crop((0,start,w,end)).save(dest)
    pages.append({'page':len(pages)+1,'source':file.name,'source_path':str(file),'start':start,'end':end,
                  'path':str(dest),'width':w,'height':end-start,'cut_before':reasons[j]})
  print(f'prepared {file.name}: {w}x{h}',flush=True)
 c=canvas.Canvas(str(work/'source_pages.pdf'))
 for item in pages:
  w=595.276;h=w*item['height']/item['width'];c.setPageSize((w,h))
  c.drawImage(item['path'],0,0,width=w,height=h);c.showPage()
 c.save()
 for start in range(0,len(pages),6):
  sheet=Image.new('RGB',(1500,1450),'#d6d6d6');draw=ImageDraw.Draw(sheet)
  for k,p in enumerate(pages[start:start+6]):
   im=Image.open(p['path']);im.thumbnail((490,680));x=k%3*500;y=k//3*725
   sheet.paste(im,(x,y+30));draw.text((x+8,y+7),str(p['page']),fill='black')
  sheet.save(preview/f'contact-{start//6+1:02d}.jpg',quality=90)
 (work/'pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
 (work/'source_manifest.json').write_text(json.dumps({'sources':sources,'page_count':len(pages),
   'cuts_to_review':[p['page'] for p in pages if p['cut_before']=='low_ink_split_review_required']},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'pages':len(pages),'work':str(work)},ensure_ascii=True))

if __name__=='__main__':main()
