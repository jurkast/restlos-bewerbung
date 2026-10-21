"""Local profile storage, migration and private document library."""
import os,json,uuid,re,shutil,zipfile,hashlib,threading,time
from datetime import datetime
from pathlib import Path
from forms import materialize,validate_forms
ROOT=Path(__file__).resolve().parent
# Serialises file changes between the GUI thread and background PDF generation.
STORE_LOCK=threading.RLock()
# Set by load() when data.json was unreadable and a fallback copy was used.
RECOVERED=''
def app_version():
 try:return (ROOT/'VERSION').read_text().strip()
 except OSError:return '0.0.0'
DATA=Path(os.environ.get('RESTLOS_DATA_DIR',str(Path.home()/'Documents/Restlos Bewerbung'))).resolve()
LEGACY=Path(os.environ.get('RESTLOS_LEGACY_DIR',str(Path.home()/'.local/share/bewerbungsatelier')))
CATEGORIES=['Lebenslauf','Anschreiben','Zeugnisse','Zertifikate','Sonstiges','Fotos']
PROFILE_FIELDS=['name','title','email','phone','address','experience','education','skills','languages']
def ident(): return str(uuid.uuid4())
def new_application():
 return dict(id=ident(),company='',position='',recipient='',location='',date=__import__('datetime').datetime.now().strftime('%d.%m.%Y'),salutation='Sehr geehrte Damen und Herren,',job='',motivation='',evidence='',letter='',status='Entwurf',template='Seitenleiste',attachments=[])
def new_profile(label='Neues Profil'):
 return dict(id=ident(),label=label,folder='',profile={k:'' for k in PROFILE_FIELDS},applications=[new_application()],documents=[],dictionary=[])
def activate(s,pid=None):
 p=next((p for p in s['profiles'] if p['id']==(pid or s['selectedProfile'])),s['profiles'][0]);s['selectedProfile']=p['id'];s['profile']=p['profile'];s['applications']=p['applications'];return s
def initial():
 p=new_profile('Mein Profil');return validate(activate(dict(version=2,selectedProfile=p['id'],profiles=[p])))
def selected(s): return next(p for p in s['profiles'] if p['id']==s['selectedProfile'])
def clean(t): return re.sub(r'[^\w .-]','_',t).strip(' .')[:70] or 'Unbenannt'
def private_dir(p): p.mkdir(parents=True,exist_ok=True,mode=0o700);p.chmod(0o700);return p
def write(path,data):
 private_dir(path.parent);tmp=path.with_name(path.name+'.'+uuid.uuid4().hex[:6]+'.tmp');tmp.write_text(data,encoding='utf-8');tmp.chmod(0o600);tmp.replace(path)
def write_changed(path,data):
 # Skip unchanged files: saving happens after every typing pause.
 try:
  if path.read_text(encoding='utf-8')==data:return False
 except (OSError,UnicodeDecodeError):pass
 write(path,data);return True
def file_hash(path):
 with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def resolve(rel):
 p=(DATA/rel).resolve()
 if not p.is_relative_to(DATA): raise ValueError('Ungültiger Dokumentpfad.')
 return p

def validate(s):
 if not isinstance(s,dict) or s.get('version')!=2 or not isinstance(s.get('profiles'),list) or not s['profiles']: raise ValueError('Ungültiges Restlos-Profilformat.')
 ids=set()
 for p in s['profiles']:
  if not isinstance(p,dict) or not re.fullmatch(r'[a-zA-Z0-9_-]+',p.get('id','')) or p['id'] in ids: raise ValueError('Ungültige Profil-ID.')
  ids.add(p['id'])
  if not isinstance(p.get('label'),str) or not isinstance(p.get('folder'),str): raise ValueError('Ungültiger Profilname.')
  if p['folder'] and Path(p['folder']).name!=p['folder']: raise ValueError('Ungültiger Profilordner.')
  if not isinstance(p.get('profile'),dict) or any(not isinstance(p['profile'].get(k),str) for k in PROFILE_FIELDS): raise ValueError('Ungültige Profildaten.')
  if not isinstance(p.get('applications'),list) or not p['applications']: raise ValueError('Jedes Profil braucht eine Bewerbung.')
  validate_forms(p['profile'])
  aids=set()
  for a in p['applications']:
   if not isinstance(a,dict) or not re.fullmatch(r'[a-zA-Z0-9_-]+',a.get('id','')) or a['id'] in aids: raise ValueError('Ungültige Bewerbungs-ID.')
   aids.add(a['id'])
   validate_forms(p['profile'],a)
   materialize(p['profile'],a)
   if any(not isinstance(a.get(k),type(v)) for k,v in new_application().items()): raise ValueError('Ungültige Bewerbung.')
   if any(not isinstance(n,str) for n in a['attachments']): raise ValueError('Ungültige Anlagen.')
  if not isinstance(p.get('documents'),list) or not isinstance(p.get('dictionary'),list) or any(not isinstance(w,str) for w in p['dictionary']): raise ValueError('Ungültige Dokumentliste.')
  for d in p['documents']:
   if not isinstance(d,dict) or any(not isinstance(d.get(k),str) for k in ('id','name','category','path')) or d['category'] not in CATEGORIES: raise ValueError('Ungültiges Dokument.')
   if not d['path'].startswith('Profile/'+p['folder']+'/'): raise ValueError('Dokument liegt außerhalb des Profils.')
   resolve(d['path'])
  paths={d['path'] for d in p['documents']}
  if p['profile'].get('signature') and p['profile']['signature'] not in paths:raise ValueError('Die Unterschrift fehlt in der Profilablage.')
  if p['profile'].get('photo') and p['profile']['photo'] not in paths: raise ValueError('Das Foto fehlt in der Profilablage.')
  if any(n not in paths for a in p['applications'] for n in a['attachments']): raise ValueError('Eine Anlage fehlt in der Profilbibliothek.')
 if s.get('selectedProfile') not in ids: raise ValueError('Aktives Profil fehlt.')
 return activate(s)

def absorb(s):
 # The editor sends active aliases as well as all other profiles.
 p=selected(s);p['profile']=s['profile'];p['applications']=s['applications'];return validate(s)
def profile_dir(p):
 if not p['folder']: p['folder']=clean(p['label'])+'_'+p['id'][:8]
 path=private_dir(DATA/'Profile'/p['folder'])
 for n in CATEGORIES+['Bewerbungen']: private_dir(path/n)
 return path

def application_dir(p,a):
 # Stable ID keeps links intact if company or title changes.
 base=profile_dir(p)/'Bewerbungen'
 name=clean((a['company'] or 'Neue Bewerbung')+' - '+(a['position'] or 'Entwurf'))+'_'+a['id'][:8]
 old=a.get('folder','')
 if not old:
  matches=list(base.glob('*_'+a['id'][:8]))
  if len(matches)==1: old=matches[0].name
 if old and Path(old).name!=old: raise ValueError('Ungültiger Bewerbungsordner.')
 if old and old!=name and (base/old).exists() and not (base/name).exists(): (base/old).rename(base/name)
 a['folder']=name
 path=private_dir(base/name)
 for n in ['Anschreiben','Lebenslauf','Deckblatt','Anlagen','Exporte']: private_dir(path/n)
 return path

def existing_application_dir(p,a):
 # Locate by stable ID without creating or renaming (for background work).
 if not p.get('folder'):return None
 base=DATA/'Profile'/p['folder']/'Bewerbungen'
 matches=list(base.glob('*_'+a['id'][:8])) if base.is_dir() else []
 return matches[0] if len(matches)==1 and matches[0].is_dir() and not matches[0].is_symlink() else None

def document_copy(s,source,category):
 if category not in CATEGORIES: raise ValueError('Unbekannte Kategorie.')
 p=selected(s);source=Path(source);folder=profile_dir(p)/category
 # Re-selecting the same file returns the existing copy instead of a duplicate.
 digest=file_hash(source)
 for d in p['documents']:
  if d['category']!=category or Path(d['path']).suffix.lower()!=source.suffix.lower():continue
  try:
   existing=resolve(d['path'])
   if existing.is_file() and not existing.is_symlink() and existing.stat().st_size==source.stat().st_size and file_hash(existing)==digest:return d
  except (OSError,ValueError):continue
 name=clean(source.stem)+source.suffix.lower();target=folder/name
 if target.exists(): target=folder/(clean(source.stem)+'_'+uuid.uuid4().hex[:6]+source.suffix.lower())
 shutil.copyfile(source,target);target.chmod(0o600)
 d=dict(id=ident(),name=source.name,category=category,path=str(target.relative_to(DATA)));p['documents'].append(d);return d

def attachment_state(a):
 # Changes to the list, page edits or the original files require new copies.
 rows=[]
 for rel in a['attachments']:
  try:st=resolve(rel).stat();rows.append([rel,st.st_size,st.st_mtime_ns])
  except (OSError,ValueError):rows.append([rel,None,None])
 return hashlib.sha256(json.dumps([rows,a.get('attachmentEdits',{})],sort_keys=True).encode()).hexdigest()

def sync_attachments(a,ap):
 from studio import attachment_pdf
 folder=ap/'Anlagen';manifest=folder/'.zugeordnet.json';stamp=folder/'.anlagen-state'
 linked={str(i+1).zfill(2)+'-'+Path(n).name for i,n in enumerate(a['attachments'])}
 state=attachment_state(a)
 write_changed(folder/'Verzeichnis.txt','\n'.join(a['attachments']))
 try:unchanged=stamp.read_text()==state and all((folder/n).is_file() for n in linked)
 except OSError:unchanged=False
 if unchanged:return
 try:previous=json.loads(manifest.read_text()) if manifest.exists() else []
 except ValueError:previous=[]
 complete=True
 for index,rel in enumerate(a['attachments']):
  src=resolve(rel);dst=folder/(str(index+1).zfill(2)+'-'+src.name)
  if not src.is_file() or src.is_symlink():complete=False;continue
  temporary=folder/('.'+uuid.uuid4().hex[:8]+'.tmp.pdf')
  try:attachment_pdf(a,rel,temporary);temporary.chmod(0o600);temporary.replace(dst)
  finally:temporary.unlink(missing_ok=True)
 # Remove only managed copies no longer linked to this application.
 for name in previous:
  old=folder/Path(name).name
  if old.is_file() and old.name not in linked: old.unlink()
 write(manifest,json.dumps(sorted(linked)))
 if complete:write(stamp,state)
 else:stamp.unlink(missing_ok=True)

def snapshot_data(target):
 # data.previous.json keeps a state at least 15 minutes older than the current one,
 # and one copy per day is kept for two weeks (form data only, files stay in place).
 if not target.exists():return
 previous=DATA/'data.previous.json'
 try:
  if not previous.exists() or time.time()-previous.stat().st_mtime>900:shutil.copy2(target,previous);previous.chmod(0o600)
  daily=private_dir(DATA/'Sicherungen'/'Täglich');today=daily/('data-'+datetime.now().strftime('%Y-%m-%d')+'.json')
  if not today.exists():shutil.copy2(target,today);today.chmod(0o600)
  for old in sorted(daily.glob('data-*.json'))[:-14]:old.unlink()
 except OSError:pass

def pdf_digest(p,a):
 return hashlib.sha256(json.dumps([app_version(),p['profile'],{k:v for k,v in a.items() if k not in ('tracking','aiDraft','letterHistory','folder')}],sort_keys=True).encode()).hexdigest()

def generate_documents(s,background=False):
 """Create Anschreiben/Lebenslauf/Deckblatt PDFs for changed applications of the active profile.
 PDFs are built in a temporary folder first; only the final move holds STORE_LOCK."""
 import tempfile
 from pdf_export import make_pdf
 p=selected(s)
 for a in p['applications']:
  digest=pdf_digest(p,a)
  with STORE_LOCK:
   folder=existing_application_dir(p,a) if background else application_dir(p,a)
   if folder is None:continue
   stamp=folder/'.pdf-state'
   try:
    if stamp.read_text()==digest:continue
   except OSError:pass
  kinds=[('letter','Anschreiben/Anschreiben.pdf'),('cv','Lebenslauf/Lebenslauf.pdf')]+([('cover','Deckblatt/Deckblatt.pdf')] if a.get('design',{}).get('cover') else [])
  with tempfile.TemporaryDirectory(prefix='restlos-pdf-') as td:
   built=[]
   for kind,name in kinds:
    tmp=Path(td)/(kind+'.pdf');make_pdf(s,a,tmp,kind,False);built.append((tmp,name))
   with STORE_LOCK:
    folder=existing_application_dir(p,a) if background else application_dir(p,a)
    if folder is None:continue
    for tmp,name in built:
     dest=folder/name;private_dir(dest.parent);part=dest.with_name('.'+uuid.uuid4().hex[:8]+'.tmp.pdf')
     shutil.copyfile(tmp,part);part.chmod(0o600);part.replace(dest)
    write(folder/'.pdf-state',digest)

def persist(s,active_id=None,generate=True):
 """Save all profiles. Only changed files are rewritten. generate=True also builds the
 document PDFs synchronously; the app normally does that in the background instead."""
 with STORE_LOCK:
  absorb(s);private_dir(DATA)
  for p in s['profiles']:
   profile_dir(p)
   for a in p['applications']:
    ap=application_dir(p,a);write_changed(ap/'Bewerbung.json',json.dumps(a,ensure_ascii=False,indent=2))
    write_changed(ap/'Anschreiben/Anschreiben.txt',a['salutation']+'\n\n'+a['letter']+'\n\nMit freundlichen Grüßen\n'+p['profile']['name'])
    cv=__import__('studio').cv_profile(p['profile'],a)
    write_changed(ap/'Lebenslauf/Lebenslauf.txt','\n\n'.join(cv[k] for k in PROFILE_FIELDS)+'\n\n'+__import__('personal').details(cv))
    sync_attachments(a,ap)
  for p in s['profiles']: write_changed(profile_dir(p)/'Profil.json',json.dumps(p,ensure_ascii=False,indent=2))
  target=DATA/'data.json';content=json.dumps({k:v for k,v in s.items() if k not in ('profile','applications')},ensure_ascii=False,indent=2)
  snapshot_data(target)
  write_changed(target,content)
 if generate:generate_documents(s)
 return s

def migrate(old,legacy):
 s=initial();p=selected(s);p['profile']=old['profile'];p['applications']=old['applications'];activate(s);profile_dir(p)
 mapping={}
 for a in p['applications']:
  for name in a['attachments']:
   if name not in mapping:
    source=legacy/'attachments'/Path(name).name
    if not source.exists(): raise ValueError('Alte Anlage fehlt: '+name)
    mapping[name]=document_copy(s,source,'Zeugnisse')['path']
  a['attachments']=[mapping[n] for n in a['attachments']]
 return validate(s)

def read_state(path):
 return validate(json.loads(path.read_text(encoding='utf-8')))

def load():
 global RECOVERED
 RECOVERED=''
 if (DATA/'data.json').exists():
  try:return read_state(DATA/'data.json')
  except (OSError,ValueError) as error:
   # Keep the damaged file and fall back to the newest readable copy.
   daily=sorted((DATA/'Sicherungen'/'Täglich').glob('data-*.json'),reverse=True) if (DATA/'Sicherungen'/'Täglich').is_dir() else []
   for candidate in [DATA/'data.previous.json',*daily]:
    try:s=read_state(candidate)
    except (OSError,ValueError):continue
    broken=DATA/('data.defekt-'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'.json')
    shutil.copy2(DATA/'data.json',broken);broken.chmod(0o600)
    shutil.copy2(candidate,DATA/'data.json')
    RECOVERED='Die Datei data.json war beschädigt ('+str(error)+'). Restlos hat den Stand aus „'+candidate.name+'“ geladen. Die beschädigte Datei liegt als „'+broken.name+'“ im Datenordner. Bitte die letzten Änderungen prüfen.'
    return s
   raise ValueError('Die Bewerbungsdaten (data.json) sind beschädigt und es wurde keine lesbare Ausweichkopie gefunden: '+str(error)+'. Eine ZIP-Sicherung kann über „Sicherung & Daten → Wiederherstellen“ eingespielt werden.') from error
 if (LEGACY/'data.json').exists():
  old=json.loads((LEGACY/'data.json').read_text());s=migrate(old,LEGACY);persist(s);return s
 return initial()

def backup(s,dest):
 persist(s,generate=False)
 temp=Path(str(dest)+'.tmp')
 with STORE_LOCK,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
  z.write(DATA/'data.json','data.json')
  for p in s['profiles']:
   for f in profile_dir(p).rglob('*'):
    if f.is_file() and not f.is_symlink():z.write(f,str(f.relative_to(DATA)))
 temp.chmod(0o600);temp.replace(dest)

def raw_backup(dest):
 temp=Path(str(dest)+'.tmp')
 try:
  with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
   for name in ('data.json','data.previous.json'):
    if (DATA/name).is_file():z.write(DATA/name,name)
   if (DATA/'Profile').is_dir():
    for f in (DATA/'Profile').rglob('*'):
     if f.is_file() and not f.is_symlink():z.write(f,str(f.relative_to(DATA)))
  temp.chmod(0o600);temp.replace(dest)
 except Exception:
  temp.unlink(missing_ok=True);raise

def restore(source):
 # Validate all paths before changing anything; keep a complete pre-restore backup.
 with STORE_LOCK,zipfile.ZipFile(source) as z:
  if sum(i.file_size for i in z.infolist())>2*1024**3: raise ValueError('Die Sicherung ist größer als 2 GB.')
  for i in z.infolist():
   if Path(i.filename).is_absolute() or '..' in Path(i.filename).parts or (i.external_attr>>16)&0o170000==0o120000: raise ValueError('Unsicherer Pfad in der Sicherung.')
  raw=json.loads(z.read('data.json'))
  if raw.get('version')!=2: raise ValueError('Bitte eine Restlos-Sicherung der Version 0.2 verwenden. Alte Daten werden beim ersten Start automatisch übernommen.')
  s=validate(raw)
  for p in s['profiles']:
   for d in p['documents']:
    if d['path'] not in z.namelist(): raise ValueError('Dokument fehlt in der Sicherung: '+d['name'])
  private_dir(DATA)
  if (DATA/'data.json').exists() or (DATA/'Profile').is_dir():
   # Raw copy without validation, so restoring also works when the current data are damaged.
   raw_backup(private_dir(DATA/'Sicherungen')/('Vor-Wiederherstellung-'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'-'+uuid.uuid4().hex[:6]+'.zip'))
  for i in z.infolist():
   if i.is_dir():continue
   if i.filename!='data.json' and not i.filename.startswith('Profile/'):continue
   path=resolve(i.filename);private_dir(path.parent);path.write_bytes(z.read(i));path.chmod(0o600)
 persist(s,generate=False);return s
