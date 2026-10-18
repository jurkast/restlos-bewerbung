"""Local-only snapshots and readiness checks. No applicant data is uploaded."""
import json,zipfile,uuid,shutil
from datetime import datetime
from pathlib import Path
from storage import DATA,validate,private_dir

def snapshot_before_update():
 data=DATA/'data.json'
 if not data.exists():return
 raw=data.read_bytes();state=validate(json.loads(raw))
 for profile in state['profiles']:
  for document in profile['documents']:
   original=DATA/document['path']
   if not original.is_file() or original.is_symlink():raise ValueError('Die Sicherung konnte nicht erstellt werden: Originaldatei fehlt oder ist verknüpft: '+document['name'])
 folder=private_dir(DATA/'Sicherungen')
 dest=folder/('Vor-Update-'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'-'+uuid.uuid4().hex[:6]+'.zip');temp=dest.with_suffix('.tmp')
 try:
  with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
   z.writestr('data.json',raw)
   for profile in state['profiles']:
    root=DATA/'Profile'/profile['folder']
    for f in root.rglob('*'):
     if f.is_file() and not f.is_symlink():z.write(f,str(f.relative_to(DATA)))
  temp.chmod(0o600);temp.replace(dest)
 except Exception:
  temp.unlink(missing_ok=True);raise
 return str(dest)

def readiness(s):
 return [{'label':'PDF-Vorschau','ok':bool(shutil.which('pdftoppm'))},
 {'label':'Texterkennung (Tesseract)','ok':bool(shutil.which('tesseract'))},
 {'label':'Deutsches Wörterbuch','ok':Path('/usr/share/hunspell/de_DE.dic').exists()},
 {'label':'Name im aktuellen Profil','ok':bool(s['profile']['name'].strip())},
 {'label':'E-Mail im aktuellen Profil','ok':bool(s['profile']['email'].strip())}]
