"""Validate public Skill structure and repository hygiene, without OCR downloads."""
from pathlib import Path
import ast,re,sys
import yaml

def main():
 root=Path(__file__).resolve().parents[1];text=(root/'SKILL.md').read_text(encoding='utf-8-sig')
 match=re.match(r'^---\s*\n(.*?)\n---\s*\n',text,re.S)
 if not match:raise SystemExit('SKILL.md needs YAML frontmatter')
 meta=yaml.safe_load(match[1]);name=meta.get('name','');description=meta.get('description','')
 assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name) and len(name)<=64,'Invalid Skill name'
 assert name==root.name,'Skill folder name must match frontmatter name'
 assert isinstance(description,str) and 0<len(description)<=1024,'Invalid description'
 assert len(meta.get('compatibility',''))<=500,'Compatibility is too long'
 assert meta.get('metadata',{}).get('version')==(root/'VERSION').read_text().strip(),'Version mismatch'
 for required in ('README.md','CONTRIBUTING.md','scripts/requirements.txt','references/environment.md','tests/test_regressions.py'):
  assert (root/required).is_file(),required
 skip={'.git','.venv','venv','__pycache__','work','outputs','dist','.pytest_cache'}
 files=[p for p in root.rglob('*') if p.is_file() and not(set(p.relative_to(root).parts)&skip)]
 forbidden={'.docx','.xlsx','.pdf','.png','.jpg','.jpeg','.zip','.pyc','.pem','.key'}
 for p in files:
  assert p.suffix.lower() not in forbidden,'Non-source/private artifact: '+str(p.relative_to(root))
  assert p.stat().st_size<1024*1024,'Unexpected large file: '+str(p.relative_to(root))
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p))
  if p.suffix in ('.yaml','.yml'):yaml.safe_load(p.read_text(encoding='utf-8-sig'))
  if p.suffix=='.md':
   for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
    if '://' in link or link.startswith('#'):continue
    assert (p.parent/link.split('#')[0]).exists(),f'Broken local link in {p.name}: {link}'
 interface=yaml.safe_load((root/'agents/openai.yaml').read_text(encoding='utf-8'))['interface']
 assert '$'+name in interface['default_prompt'],'Default prompt must name the Skill'
 assert 25<=len(interface['short_description'])<=64,'UI description length'
 print(f'Validated {name}: metadata, Python syntax, YAML, links and {len(files)} source files.')
 print('No OCR/Office run or semantic source review was performed by this check.')

if __name__=='__main__':main()
