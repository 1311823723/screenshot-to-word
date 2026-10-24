from pathlib import Path
import argparse,collections,json
from common import plain,children
from content_guard import table_hazards

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--result',required=True);ap.add_argument('--work',required=True);ap.add_argument('--pages');a=ap.parse_args()
 data=json.loads(Path(a.result).read_text(encoding='utf-8-sig'));out=Path(a.work);out.mkdir(parents=True,exist_ok=True)
 inventory=[];counts=collections.Counter();candidates=[];reviews=[];lines=['# OCR 结构索引','页号是裁切片段号；block 是识别结果 index。原图判断优先于类型标签。','']
 pages=json.loads(Path(a.pages).read_text(encoding='utf-8-sig')) if a.pages else None
 if pages:(out/'source_review').mkdir(exist_ok=True)
 previous=None
 for page in data['pages']:
  pn=page['page_idx']+1;lines.extend([f'## 片段 {pn}',''])
  for block in page.get('blocks',[]):
   typ=block['type'];idx=block['index'];counts[typ]+=1
   item={'page':pn,'block_index':idx,'type':typ,'bbox':block.get('bbox'),'continues_prev':block.get('continues_prev',False)}
   if typ=='table':
    item['table_html']=[x.get('content','') for x in children(block) if x.get('type')=='table_body']
    item['captions']=[plain(x) for x in children(block) if x.get('type')=='table_caption']
    flags=[flag for markup in item['table_html'] for flag in table_hazards(markup)]
    item['hazards']=flags
    crop_path=None
    if pages and block.get('bbox'):
     from PIL import Image
     source=pages[pn-1];im=Image.open(source['path']);w,h=im.size;box=block['bbox']
     if max(box)<=2:box=[v*(w if i%2==0 else h) for i,v in enumerate(box)]
     crop_path=out/'source_review'/f'p{pn:03d}_b{idx:03d}.png'
     im.crop((max(0,int(box[0])-20),max(0,int(box[1])-20),min(w,int(box[2])+20),min(h,int(box[3])+20))).save(crop_path)
    reviews.append({'page':pn,'block_index':idx,'decision':'pending','source_checked':False,'evidence':'',
     'visual_content':'unknown','cell_images':[],'source_crop':str(crop_path) if crop_path else None,'hazards':flags})
    summary=' | '.join(item['captions']) or '(原生表格候选，HTML 见 inventory.json)'
    if block.get('continues_prev') or (previous and previous['type']=='table' and previous['page']!=pn):
     candidates.append({'page':pn,'block_index':idx,'previous':previous,'model_continues_prev':bool(block.get('continues_prev')),
                        'action':'核对原图和列语义，再决定是否加入 table_joins'})
   elif typ in ('image','chart','figure'):
    item['children']=children(block);summary='(图像候选，需检查裁框与完整性)'
   else:item['text']=plain(block);summary=item['text']
   inventory.append(item);lines.append(f'- block {idx} / {typ}: {summary}')
   if typ not in ('header','footer','page_number'):previous={'page':pn,'block_index':idx,'type':typ}
  lines.append('')
 result={'page_count':len(data['pages']),'block_counts':dict(counts),'table_join_candidates':candidates,'blocks':inventory}
 (out/'inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'inventory.md').write_text('\n'.join(lines),encoding='utf-8')
 template=out/'content_review.template.json'
 if not template.exists():template.write_text(json.dumps({'schema_version':1,'table_reviews':reviews},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'pages':len(data['pages']),'counts':dict(counts),'join_candidates':len(candidates)},ensure_ascii=True))

if __name__=='__main__':main()
