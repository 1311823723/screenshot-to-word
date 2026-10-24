"""Regression fixtures for observed content-loss and stale-report failure modes."""
import sys,json,tempfile,unittest,hashlib,subprocess
from pathlib import Path
from zipfile import ZipFile
from PIL import Image,ImageDraw
from lxml import etree as E
from reportlab.pdfgen import canvas
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_docx import Builder

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
HTML='<table><tr><td>Mode</td><td>Monitoring</td></tr><tr><td>INFO</td><td></td></tr></table>'
class Regressions(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)
  im=Image.new('RGB',(400,300),'white');d=ImageDraw.Draw(im);d.rectangle((5,5,395,295),outline='black');d.line((200,220,240,160,280,200,340,100),fill='blue',width=4);im.save(self.base/'source.png')
  self.pages=[{'page':1,'source':'source.png','path':str(self.base/'source.png'),'width':400,'height':300,'start':0,'end':300}]
  self.data={'pages':[{'page_idx':0,'blocks':[{'type':'table','index':0,'bbox':[0,0,1,1],'content':[{'type':'table_body','content':HTML}]}]}]}
 def tearDown(self):self.temp.cleanup()
 def review(self,**overrides):
  result={'page':1,'block_index':0,'source_checked':True,'decision':'native_table','visual_content':'none','evidence':'Fixture source was inspected','cell_images':[]};result.update(overrides);return result
 def build(self,review):
  return Builder(self.data,self.pages,{'title':'Regression fixture','_reviews':{'table_reviews':[review]}})
 def test_pending_source_review_blocks_generation(self):
  with self.assertRaisesRegex(ValueError,'source review'):Builder(self.data,self.pages,{'title':'Fixture'}).run()
 def test_code_preserves_whitespace_entities_and_literal_backslashes(self):
  literal='    if (ready) {\n\tString label = "中 文 &lt;";\n        String pattern = "\\times";\n    }\n'
  data={'pages':[{'page_idx':0,'blocks':[{'type':'code','index':0,'content':[{'type':'code_body','content':literal}]}]}]}
  builder=Builder(data,self.pages,{'title':'Code fixture'});doc=builder.run()
  self.assertEqual(doc.paragraphs[0].text,literal)
  self.assertEqual(doc.paragraphs[0].paragraph_format.first_line_indent,0)
  self.assertEqual(len(builder.report['code_blocks']),1)
 def test_mixed_table_cannot_become_empty_cells(self):
  with self.assertRaisesRegex(ValueError,'cell_images'):self.build(self.review(visual_content='present')).run()
 def test_continuation_caption_does_not_break_table_join(self):
  import copy
  data=copy.deepcopy(self.data);pages=self.pages*3;reviews=[]
  for n in range(3):
   if n:data['pages'].append(copy.deepcopy(data['pages'][0]))
   data['pages'][n]['page_idx']=n
   reviews.append(self.review(page=n+1))
  data['pages'][1]['blocks'][0]['content'].append({'type':'table_caption','index':1,'content':'Table caption'})
  cfg={'title':'Fixture','_reviews':{'table_reviews':reviews},'table_joins':[{'page':2,'block_index':0,'reason':'Fixture continuation'},{'page':3,'block_index':0,'reason':'Fixture continuation'}]}
  builder=Builder(data,pages,cfg);doc=builder.run()
  self.assertEqual(len(doc.tables),1)
  self.assertEqual(len(doc.tables[0].rows),6)
  self.assertEqual(sum(p.text=='Table caption' for p in doc.paragraphs),1)
 def test_source_figure_does_not_become_invented_year_table(self):
  data=json.loads(json.dumps(self.data));data['pages'][0]['blocks'][0]['content'][0]['content']='<table><tr><td>Year</td><td>2017</td><td>Consensus</td></tr></table>'
  builder=Builder(data,self.pages,{'title':'Fixture','_reviews':{'table_reviews':[self.review(decision='figure',visual_content='present')]}})
  doc=builder.run();self.assertEqual(len(doc.tables),0);self.assertEqual(len(doc.inline_shapes),1)
  # The same words may be valid elsewhere: no keyword deletion rule is used.
  builder=Builder(data,self.pages,{'title':'Fixture','_reviews':{'table_reviews':[self.review()]}})
  self.assertEqual(len(builder.run().tables),1)
 def test_final_audit_catches_missing_cell_image_even_when_total_is_unchanged(self):
  review=self.review(visual_content='present',cell_images=[{'row':1,'col':1,'bbox':[.5,.3,.95,.9],'evidence':'Fixture chart in logical cell'}])
  builder=self.build(review);doc=builder.run();self.assertEqual(len(doc.tables[0].cell(1,1)._tc.xpath('.//w:drawing')),1)
  docx=self.base/'result.docx';doc.save(docx)
  reviews=self.base/'reviews.json';reviews.write_text(json.dumps({'table_reviews':[review]}),encoding='utf-8')
  report=builder.report;report['inputs_sha256']={'reviews':hashlib.sha256(reviews.read_bytes()).hexdigest()}
  build=self.base/'build.json';build.write_text(json.dumps(report),encoding='utf-8')
  pdf=self.base/'result.pdf';c=canvas.Canvas(str(pdf));c.drawString(50,700,'Fixture audit file, not an Office rendering');c.save()
  qa=self.base/'qa.json';att=self.base/'att.json'
  def bind():
   dh=hashlib.sha256(docx.read_bytes()).hexdigest();ph=hashlib.sha256(pdf.read_bytes()).hexdigest()
   qa.write_text(json.dumps({'docx_sha256':dh,'pdf_sha256':ph,'pages':1,'tables':1,'pictures':1,'toc_links':0,
    'blank_page_candidates':[],'field_error_pages':[],'replacement_characters':0,'inconsistent_table_rows':[],'out_of_page_text':[]}),encoding='utf-8')
   att.write_text(json.dumps({'docx_sha256':dh,'pdf_sha256':ph,'source_tables_compared':True,'mixed_tables_preserved':True,
    'invented_content_checked':True,'toc_page_numbers_checked':True,'visual_pages_reviewed':[1],
    'review_dispositions':[],'known_source_issues':[],'unresolved_output_issues':[]}),encoding='utf-8')
  command=[sys.executable,str(Path(__file__).resolve().parents[1]/'scripts/finalize_delivery.py'),
   '--docx',str(docx),'--pdf',str(pdf),'--qa-report',str(qa),'--build-report',str(build),'--reviews',str(reviews),'--attestation',str(att),'--out',str(self.base/'delivery')]
  bind();passed=subprocess.run(command,capture_output=True,text=True);self.assertEqual(passed.returncode,0,passed.stderr)
  drawing=doc.tables[0].cell(1,1)._tc.xpath('.//w:drawing')[0]
  drawing.getparent().remove(drawing);doc.add_paragraph().add_run()._r.append(drawing);doc.save(docx)
  self.assertEqual(len(doc.inline_shapes),1);bind()
  failed=subprocess.run(command,capture_output=True,text=True);self.assertEqual(failed.returncode,2,failed.stderr)
  final=json.loads((self.base/'delivery/最终验收报告.json').read_text(encoding='utf-8'))
  self.assertTrue(any('cell images missing' in x for x in final['blocking_findings']))
  # A subsequent file change also invalidates the QA/attestation hashes.
  doc.add_paragraph('A final edit after acceptance');doc.save(docx)
  subprocess.run(command,capture_output=True,text=True)
  final=json.loads((self.base/'delivery/最终验收报告.json').read_text(encoding='utf-8'))
  self.assertTrue(any('stale' in x or 'current final files' in x for x in final['blocking_findings']))

if __name__=='__main__':unittest.main()
