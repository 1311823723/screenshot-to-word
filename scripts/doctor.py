"""Read-only checks; does not install packages, start Word, or download models."""
import argparse, importlib.util, json, shutil, sys
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--mineru-exe');a=p.parse_args()
mods=['PIL','numpy','reportlab','docx','lxml','pypdfium2']
missing=[x for x in mods if importlib.util.find_spec(x) is None]
exe=a.mineru_exe or shutil.which('mineru-kit') or shutil.which('mineru')
word=None
if sys.platform=='win32':
 import winreg
 for hive in (winreg.HKEY_LOCAL_MACHINE,winreg.HKEY_CURRENT_USER):
  try:
   with winreg.OpenKey(hive,r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\WINWORD.EXE') as key:
    word=winreg.QueryValueEx(key,None)[0]
  except OSError:pass
report={'python':sys.executable,'version':sys.version.split()[0],'missing_helper_packages':missing,
        'mineru_executable':exe,'mineru_path_exists':bool(exe and Path(exe).is_file()),
        'word_registry_path':word,'word_path_exists':bool(word and Path(word).is_file()),
        'note':'Models, OCR quality, Word COM permissions and image-viewing ability still require actual verification.'}
print(json.dumps(report,ensure_ascii=True,indent=2))
sys.exit(1 if missing else 0)
