"""Require source-grounded table decisions; heuristic warnings are not semantic proof."""
from lxml import html as H

def table_hazards(markup):
 tree=H.fromstring(markup);cells=tree.xpath('.//td|.//th');rows=tree.xpath('.//tr')
 flags=[]
 if tree.xpath('.//img|.//svg|.//canvas|.//object'):flags.append('html_contains_visual_elements')
 if len(rows)>1:
  data=[c for row in rows[1:] for c in row.xpath('./td|./th')]
  if data and sum(not c.text_content().strip() for c in data)/len(data)>.35:flags.append('many_empty_body_cells_check_for_missing_images')
 text=tree.text_content()
 if any(x in text for x in ('监控','应用资源','数据库资源','测试结果','Year','Consensus')):
  flags.append('verify_table_content_against_source_not_ocr_label')
 return flags

def validate_review(review,markup):
 if not review or review.get('source_checked') is not True:
  raise ValueError('Table source review is missing; inspect the original crop before building')
 if not str(review.get('evidence','')).strip():raise ValueError('Source review must describe what the source actually shows')
 decision=review.get('decision')
 if decision not in ('native_table','figure','omit_artifact'):raise ValueError('Source review decision is still pending or invalid')
 visual=review.get('visual_content')
 if visual not in ('none','present'):raise ValueError('Declare whether source table cells contain pictures')
 if decision=='native_table':
  images=review.get('cell_images',[])
  if visual=='present' and not images:raise ValueError('Source table contains pictures: cell_images is required; empty cells are not a replacement')
  if visual=='none' and images:raise ValueError('Conflicting visual_content and cell_images')
  if H.fromstring(markup).xpath('.//img|.//svg|.//canvas|.//object') and not images:
   raise ValueError('HTML visual elements would be lost by text_content; provide source crops for cells')
 return decision
