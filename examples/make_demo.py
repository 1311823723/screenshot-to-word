"""Generate public synthetic inputs without OCR, Office or private source material."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import argparse,json,hashlib

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
 out=Path(args.output).resolve()
 if (out/'pages.json').exists():raise SystemExit('Demo exists; choose a new output directory')
 out.mkdir(parents=True,exist_ok=True)
 image=Image.new('RGB',(1200,1600),'white');draw=ImageDraw.Draw(image);font=ImageFont.load_default(size=28)
 draw.text((100,100),'Synthetic monitoring example',font=font,fill='black')
 draw.text((100,230),'1 Example results',font=font,fill='black')
 draw.rectangle((100,350,1100,760),outline='black',width=3)
 draw.line((400,350,400,760),fill='black',width=3);draw.line((100,420,1100,420),fill='black',width=3)
 for pos,label in [((130,370),'Mode'),((430,370),'Monitoring'),((130,490),'INFO')]:draw.text(pos,label,font=font,fill='black')
 draw.line((450,700,1060,700),fill='gray',width=2);draw.line((450,450,450,700),fill='gray',width=2)
 draw.line((460,670,550,610,640,640,730,520,820,570,910,470,1040,500),fill='blue',width=6)
 draw.text((100,900),'Fictional demo. No real measurements.',font=font,fill='black')
 source=out/'source.png';image.save(source)
 pages=[{'page':1,'source':source.name,'source_path':str(source),'path':str(source),'width':1200,'height':1600,'start':0,'end':1600}]
 result={'pages':[{'page_idx':0,'blocks':[
  {'type':'doc_title','index':0,'content':[{'type':'text','content':'Synthetic monitoring example'}]},
  {'type':'paragraph_title','index':1,'content':[{'type':'text','content':'1 Example results'}]},
  {'type':'table','index':2,'bbox':[100/1200,350/1600,1100/1200,760/1600],
   'content':[{'type':'table_body','content':'<table><tr><td>Mode</td><td>Monitoring</td></tr><tr><td>INFO</td><td></td></tr></table>'}]},
  {'type':'text','index':3,'content':[{'type':'text','content':'Fictional demo. No real measurements.'}]}]}]}
 review={'schema_version':1,'table_reviews':[{'page':1,'block_index':2,'decision':'pending','source_checked':False,'evidence':'',
  'visual_content':'present','cell_images':[{'row':1,'col':1,'source_page':1,'bbox':[430/1200,440/1600,1080/1200,730/1600],
  'evidence':'Verify the chart crop against source.png before approval'}]}]}
 config=json.loads((Path(__file__).parent/'document.example.json').read_text(encoding='utf-8'))
 manifest={'synthetic':True,'ocr_executed':False,'sources':[{'name':source.name,'width':1200,'height':1600,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}]}
 for name,value in [('pages.json',pages),('result.json',result),('content_review.json',review),('document.json',config),('source_manifest.json',manifest)]:
  (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Synthetic demo created. Inspect source.png and finish the pending source review before building.')

if __name__=='__main__':main()
