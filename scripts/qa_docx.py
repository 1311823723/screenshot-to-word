"""Render every page and perform mechanical checks; visual/content review is still required."""
from pathlib import Path
from zipfile import ZipFile
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from lxml import etree as E
import pypdfium2 as P

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--docx',required=True);ap.add_argument('--pdf',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 if (out/'qa_report.json').exists():raise SystemExit('QA directory already used; choose a new directory to avoid stale page images')
 document=P.PdfDocument(a.pdf);texts=[];blank=[];outside=[]
 for i in range(len(document)):
  page=document[i];tp=page.get_textpage();text=tp.get_text_range();texts.append(text)
  bitmap=page.render(scale=1.6).to_pil();bitmap.save(out/f'page-{i+1:03d}.png')
  ink=float((np.asarray(bitmap.convert('L'))<220).mean())
  if len(text.strip())<5 and ink<.003:blank.append(i+1)
  w,h=page.get_size();bad=0
  for j in range(tp.count_chars()):
   left,bottom,right,top=tp.get_charbox(j)
   if left < -1 or right > w+1 or bottom < -1 or top > h+1:bad+=1
  if bad:outside.append({'page':i+1,'characters':bad})
 for start in range(0,len(document),6):
  sheet=Image.new('RGB',(1800,1700),'#d0d0d0');draw=ImageDraw.Draw(sheet)
  for k in range(min(6,len(document)-start)):
   im=Image.open(out/f'page-{start+k+1:03d}.png');im.thumbnail((590,810));x=k%3*600;y=k//3*850
   sheet.paste(im,(x,y+30));draw.text((x+10,y+7),str(start+k+1),fill='black')
  sheet.save(out/f'contact-{start//6+1:02d}.jpg',quality=90)
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 with ZipFile(a.docx) as z:xml=E.fromstring(z.read('word/document.xml'))
 fields=xml.xpath('//w:instrText/text()',namespaces=ns);tables=xml.findall('.//w:tbl',ns)
 widths=[];badgrids=[]
 for ti,table in enumerate(tables):
  cols=table.findall('w:tblGrid/w:gridCol',ns);width=sum(int(x.get('{'+ns['w']+'}w')) for x in cols);widths.append(width)
  for ri,row in enumerate(table.findall('w:tr',ns)):
   logical=0;cellwidth=0
   for cell in row.findall('w:tc',ns):
    span=cell.find('w:tcPr/w:gridSpan',ns);logical+=int(span.get('{'+ns['w']+'}val')) if span is not None else 1
    tcw=cell.find('w:tcPr/w:tcW',ns);cellwidth+=int(tcw.get('{'+ns['w']+'}w')) if tcw is not None else 0
   if logical!=len(cols) or cellwidth!=width:badgrids.append({'table':ti+1,'row':ri+1,'logical_columns':logical,'row_width':cellwidth,'grid_width':width})
 report={'pages':len(document),'tables':len(tables),'pictures':len(xml.findall('.//w:drawing',ns)),
  'toc_fields':[x for x in fields if 'TOC ' in x],
  'toc_links':len(xml.xpath('//w:hyperlink[starts-with(@w:anchor,"_Toc")]',namespaces=ns)),
  'blank_page_candidates':blank,'field_error_pages':[i+1 for i,t in enumerate(texts) if 'Error! Reference source not found' in t or '错误!未找到' in t],
  'replacement_characters':sum(t.count('\ufffd') for t in texts),'table_grid_widths':sorted(set(widths)),
  'inconsistent_table_rows':badgrids,'out_of_page_text':outside,
  'status':'Mechanical checks only. Inspect all page images and verify source content separately.'}
 report['docx_sha256']=hashlib.sha256(Path(a.docx).read_bytes()).hexdigest()
 report['pdf_sha256']=hashlib.sha256(Path(a.pdf).read_bytes()).hexdigest()
 (out/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'final_text.txt').write_text('\n\n'.join(f'=== PAGE {i+1} ===\n{t}' for i,t in enumerate(texts)),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=True))

if __name__=='__main__':main()
