"""Build a deterministic source-only Skill archive, never bundling local work."""
from pathlib import Path
import argparse,hashlib,json,zipfile

ROOT_FILES={'SKILL.md','README.md','CONTRIBUTING.md','CHANGELOG.md','VERSION','requirements-dev.txt','.gitignore','.gitattributes','LICENSE','LICENSE.txt'}
FOLDERS={'scripts','references','agents','docs','examples','tests','.github'}
SUFFIXES={'.py','.ps1','.txt','.md','.json','.yaml','.yml'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];out=Path(a.output).resolve()
 if any(out==root/x or root/x in out.parents for x in FOLDERS):raise SystemExit('Output must not be inside a source directory')
 version=(root/'VERSION').read_text().strip();files=[]
 for p in root.rglob('*'):
  if not p.is_file():continue
  parts=p.relative_to(root).parts
  if '__pycache__' in parts or any(part.startswith('.') and part!='.github' for part in parts[1:]):continue
  if len(parts)==1 and p.name in ROOT_FILES:files.append(p)
  elif parts[0] in FOLDERS and p.suffix in SUFFIXES:files.append(p)
 files.sort(key=lambda p:p.relative_to(root).as_posix())
 payload={root.name+'/'+p.relative_to(root).as_posix():p.read_bytes() for p in files}
 manifest={'version':version,'source_files':{name:hashlib.sha256(data).hexdigest() for name,data in payload.items()}}
 payload[root.name+'/RELEASE_MANIFEST.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8')
 out.mkdir(parents=True,exist_ok=True);target=out/f'{root.name}-{version}.zip'
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for name,data in payload.items():
   info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,data)
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  for name,data in payload.items():assert z.read(name)==data
 digest=hashlib.sha256(target.read_bytes()).hexdigest()
 target.with_suffix('.zip.sha256').write_text(digest+'  '+target.name+'\n',encoding='utf-8')
 print(json.dumps({'archive':str(target),'source_files':len(files),'sha256':digest},ensure_ascii=True))
 print('Development archive; publication/license decisions and full runtime checks remain separate.')

if __name__=='__main__':main()
