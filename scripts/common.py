import html,re

def textof(obj):
 if isinstance(obj,str):return obj
 if isinstance(obj,list):return ''.join(textof(x) for x in obj)
 if isinstance(obj,dict):return textof(obj.get('content',''))
 return ''

def plain(value):
 text=html.unescape(textof(value)).replace('\u00a0',' ')
 # Only literal symbol substitutions; structural formulae remain for review.
 for old,new in [(r'\%', '%'),(r'\leq','≤'),(r'\geq','≥'),(r'\times','×'),(r'\bullet','•')]:text=text.replace(old,new)
 text=re.sub(r'(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])','',text)
 return text.strip()

def location(page,block):return (int(page['page_idx'])+1,int(block['index']))

def children(block):
 result=block.get('content',[])
 return [x for x in result if isinstance(x,dict)] if isinstance(result,list) else []
