"""Produce a report bound to final files, keeping mechanical evidence and agent attestations distinct."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
import argparse,json,hashlib
from collections import Counter
import pypdfium2 as P

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser()
 for arg in ('docx','pdf','qa-report','build-report','reviews','attestation','out'):ap.add_argument('--'+arg,required=True)
 ap.add_argument('--make-template',action='store_true');a=ap.parse_args()
 docx=Path(a.docx);pdf=Path(a.pdf);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 doc_hash=digest(docx);pdf_hash=digest(pdf)
 build=json.loads(Path(a.build_report).read_text(encoding='utf-8-sig'));qa=json.loads(Path(a.qa_report).read_text(encoding='utf-8-sig'))
 reviews=json.loads(Path(a.reviews).read_text(encoding='utf-8-sig'))
 if a.make_template:
  target=Path(a.attestation)
  if target.exists():raise SystemExit('Attestation exists; do not overwrite completed checks')
  target.write_text(json.dumps({'docx_sha256':doc_hash,'pdf_sha256':pdf_hash,'source_tables_compared':False,
   'mixed_tables_preserved':False,'invented_content_checked':False,'toc_page_numbers_checked':False,
   'visual_pages_reviewed':[],'review_dispositions':[{'item_index':i,'status':'pending','evidence':''} for i in range(len(build.get('review_items',[])))],
   'known_source_issues':[],'unresolved_output_issues':[]},ensure_ascii=False,indent=2),encoding='utf-8')
  print('Attestation template created; unchecked fields must be completed after actual source/render review.');return
 att=json.loads(Path(a.attestation).read_text(encoding='utf-8-sig'));fail=[]
 for key in ('pages','tables','pictures','toc_links','blank_page_candidates','field_error_pages','replacement_characters','inconsistent_table_rows','out_of_page_text'):
  if key not in qa:fail.append('Required QA evidence is missing: '+key)
 if qa.get('docx_sha256')!=doc_hash or qa.get('pdf_sha256')!=pdf_hash:fail.append('QA report is not bound to current final files; rerun QA')
 if att.get('docx_sha256')!=doc_hash or att.get('pdf_sha256')!=pdf_hash:fail.append('Review attestation is stale for these files')
 if build.get('inputs_sha256',{}).get('reviews')!=digest(a.reviews):fail.append('Content review differs from the review used during build')
 for key in ('blank_page_candidates','field_error_pages','inconsistent_table_rows','out_of_page_text'):
  if qa.get(key):fail.append('Mechanical check requires correction: '+key)
 if qa.get('replacement_characters'):fail.append('Replacement characters require source inspection')
 for key in ('source_tables_compared','mixed_tables_preserved','invented_content_checked','toc_page_numbers_checked'):
  if att.get(key) is not True:fail.append('Agent source/visual check incomplete: '+key)
 pages=len(P.PdfDocument(str(pdf)))
 if sorted(set(att.get('visual_pages_reviewed',[])))!=list(range(1,pages+1)):fail.append('Not every final PDF page was reviewed')
 dispositions=att.get('review_dispositions',[])
 if sorted(x.get('item_index',-1) for x in dispositions)!=list(range(len(build.get('review_items',[])))):fail.append('Build review items are not fully accounted for')
 for item in dispositions:
  if item.get('status') not in ('resolved','source_limitation') or not item.get('evidence'):fail.append('Unresolved build review item: '+str(item.get('item_index')))
 known=att.get('known_source_issues',[])
 for issue in known:
  if not issue.get('source_location') or not issue.get('description'):fail.append('Known source issue lacks source location/description')
 for title in build.get('unmatched_source_toc',[]):
  if not any(issue.get('title')==title for issue in known):fail.append('Missing source TOC entry lacks documented source limitation: '+title)
 if att.get('unresolved_output_issues'):fail.append('Output defects remain unresolved')
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 with ZipFile(docx) as z:xml=E.fromstring(z.read('word/document.xml'))
 tables=xml.findall('.//w:tbl',ns)
 expected=Counter((x['output_table_index'],x['output_row'],x['col']) for x in build.get('cell_images',[]))
 for (ti,ri,ci),count in expected.items():
  actual=0
  if 1<=ti<=len(tables):
   rows=tables[ti-1].findall('w:tr',ns)
   if 0<=ri<len(rows):
    col=0
    for cell in rows[ri].findall('w:tc',ns):
     span=cell.find('w:tcPr/w:gridSpan',ns);width=int(span.get('{'+ns['w']+'}val')) if span is not None else 1
     if col==ci:actual=len(cell.findall('.//w:drawing',ns));break
     col+=width
  if actual<count:fail.append(f'Source cell images missing from final native table {ti}, row {ri}, col {ci}')
 counters={'pages':pages,'native_tables':len(xml.findall('.//w:tbl',ns)),'image_objects':len(xml.findall('.//w:drawing',ns)),
  'toc_links':len(xml.xpath('//w:hyperlink[starts-with(@w:anchor,"_Toc")]',namespaces=ns))}
 if build.get('source_toc_entries') and not counters['toc_links']:fail.append('Source has a TOC but final document has no refreshed TOC links')
 report={'schema_version':1,'status':'needs_revision' if fail else 'accepted_with_source_limitations' if known else 'accepted_with_agent_attestation',
  'docx_sha256':doc_hash,'pdf_sha256':pdf_hash,'final_counters':counters,'blocking_findings':fail,
  'mechanical_evidence':qa,'agent_attestation':att,'source_review_sha256':digest(a.reviews),
  'limitations':'Source comparison and page viewing are agent attestations, not automatic proof of semantic accuracy. Re-run after any artifact changes.'}
 (out/'最终验收报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 lines=['# 交付与待核对说明','',f"状态：{report['status']}",f"Word SHA256：{doc_hash}",'',
  f"最终文件：{pages} 页，{counters['native_tables']} 张原生表格，{counters['image_objects']} 个图片对象，{counters['toc_links']} 条目录链接。",'',
  '## 源资料限制','']
 if known:
  for issue in known:lines.append('- '+issue.get('title','')+'；来源：'+issue.get('source_location','')+'；'+issue.get('description',''))
 else:lines.append('本轮记录中没有已知源资料限制；这不表示逐字自动校对无误。')
 lines.extend(['','## 未通过项','']+[('- '+x) for x in fail] if fail else ['','## 未通过项','','机械检查及本轮代理核验记录未列出待整改项。'])
 (out/'交付与待核对说明.md').write_text('\n'.join(lines),encoding='utf-8')
 print(json.dumps({'status':report['status'],'counts':counters,'blocking_findings':fail},ensure_ascii=True))
 if fail:raise SystemExit(2)

if __name__=='__main__':main()
