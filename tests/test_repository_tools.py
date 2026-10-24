"""Check public demo and release tooling without OCR, network or Office."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,unittest,zipfile

ROOT=Path(__file__).resolve().parents[1]

class RepositoryTools(unittest.TestCase):
 def test_demo_is_synthetic_and_still_requires_source_review(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'demo'
   result=subprocess.run([sys.executable,str(ROOT/'examples/make_demo.py'),'--output',str(out)],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr)
   review=json.loads((out/'content_review.json').read_text(encoding='utf-8'))['table_reviews'][0]
   self.assertIs(review['source_checked'],False);self.assertEqual(review['decision'],'pending')
   self.assertTrue(review['cell_images'])
   manifest=json.loads((out/'source_manifest.json').read_text(encoding='utf-8'))
   self.assertIs(manifest['synthetic'],True);self.assertIs(manifest['ocr_executed'],False)
   self.assertEqual(manifest['sources'][0]['sha256'],hashlib.sha256((out/'source.png').read_bytes()).hexdigest())

 def test_archive_is_reproducible_source_only_and_self_contained(self):
  with tempfile.TemporaryDirectory() as tmp:
   command=[sys.executable,str(ROOT/'scripts/package_skill.py'),'--output',tmp]
   first=subprocess.run(command,capture_output=True,text=True);self.assertEqual(first.returncode,0,first.stderr)
   archive=next(Path(tmp).glob('*.zip'));before=archive.read_bytes()
   second=subprocess.run(command,capture_output=True,text=True);self.assertEqual(second.returncode,0,second.stderr)
   self.assertEqual(before,archive.read_bytes())
   with zipfile.ZipFile(archive) as z:
    names=z.namelist();self.assertIn('screenshot-to-word/SKILL.md',names)
    self.assertIn('screenshot-to-word/README.md',names)
    self.assertIn('screenshot-to-word/examples/README.md',names)
    manifest=json.loads(z.read('screenshot-to-word/RELEASE_MANIFEST.json'))
    for name,digest in manifest['source_files'].items():self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(),digest)
    for name in names:
     self.assertNotIn('/work/',name);self.assertNotIn('/.git/',name);self.assertNotIn('__pycache__',name)
     self.assertNotIn(Path(name).suffix.lower(),{'.png','.jpg','.docx','.pdf','.zip','.pyc'})

if __name__=='__main__':unittest.main()
