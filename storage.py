"""Local profile storage, migration and private document library."""
import os,json,uuid,re,shutil,tempfile,zipfile,hashlib
from pathlib import Path
from forms import ensure,materialize,validate_forms
ROOT=Path(__file__).resolve().parent
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
 private_dir(path.parent);tmp=path.with_name(path.name+'.tmp');tmp.write_text(data,encoding='utf-8');tmp.chmod(0o600);tmp.replace(path)
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

def document_copy(s,source,category):
 if category not in CATEGORIES: raise ValueError('Unbekannte Kategorie.')
 p=selected(s);source=Path(source);folder=profile_dir(p)/category
 name=clean(source.stem)+source.suffix.lower();target=folder/name
 if target.exists(): target=folder/(clean(source.stem)+'_'+uuid.uuid4().hex[:6]+source.suffix.lower())
 shutil.copyfile(source,target);target.chmod(0o600)
 d=dict(id=ident(),name=source.name,category=category,path=str(target.relative_to(DATA)));p['documents'].append(d);return d

def persist(s,active_id=None,generate=True):
 absorb(s);private_dir(DATA)
 for p in s['profiles']:
  folder=profile_dir(p);write(folder/'Profil.json',json.dumps(p,ensure_ascii=False,indent=2))
  for a in p['applications']:
   ap=application_dir(p,a);write(ap/'Bewerbung.json',json.dumps(a,ensure_ascii=False,indent=2))
   write(ap/'Anschreiben/Anschreiben.txt',a['salutation']+'\n\n'+a['letter']+'\n\nMit freundlichen Grüßen\n'+p['profile']['name'])
   write(ap/'Lebenslauf/Lebenslauf.txt','\n\n'.join(p['profile'][k] for k in PROFILE_FIELDS)+'\n\n'+__import__('personal').details(p['profile']))
   manifest=ap/'Anlagen/.zugeordnet.json'
   previous=json.loads(manifest.read_text()) if manifest.exists() else []
   write(ap/'Anlagen/Verzeichnis.txt','\n'.join(a['attachments']))
   for rel in a['attachments']:
    src=resolve(rel);dst=ap/'Anlagen'/src.name
    if not src.exists(): raise ValueError('Anlage fehlt: '+src.name)
    if not dst.exists() or src.stat().st_mtime>dst.stat().st_mtime: shutil.copyfile(src,dst);dst.chmod(0o600)
   # Remove only managed copies no longer linked to this application.
   linked={Path(n).name for n in a['attachments']}
   for name in previous:
    old=ap/'Anlagen'/Path(name).name
    if old.is_file() and old.name not in linked: old.unlink()
   write(manifest,json.dumps(sorted(linked)))
 for p in s['profiles']: write(profile_dir(p)/'Profil.json',json.dumps(p,ensure_ascii=False,indent=2))
 target=DATA/'data.json'
 if target.exists(): shutil.copy2(target,DATA/'data.previous.json')
 write(target,json.dumps({k:v for k,v in s.items() if k not in ('profile','applications')},ensure_ascii=False,indent=2))
 if generate:
  from pdf_export import make_pdf
  p=selected(s)
  for a in p['applications']:
   folder=application_dir(p,a)
   digest=hashlib.sha256(json.dumps(['0.8.0',p['profile'],{k:v for k,v in a.items() if k not in ('tracking','aiDraft','letterHistory')}],sort_keys=True).encode()).hexdigest()
   stamp=folder/'.pdf-state'
   if stamp.exists() and stamp.read_text()==digest: continue
   for kind,name in [('letter','Anschreiben/Anschreiben.pdf'),('cv','Lebenslauf/Lebenslauf.pdf')]+([('cover','Deckblatt/Deckblatt.pdf')] if a.get('design',{}).get('cover') else []):
    dest=folder/name;tmp=dest.with_suffix('.tmp.pdf');make_pdf(s,a,tmp,kind,False);tmp.chmod(0o600);tmp.replace(dest)
   write(stamp,digest)
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

def load():
 if (DATA/'data.json').exists(): return validate(json.loads((DATA/'data.json').read_text()))
 if (LEGACY/'data.json').exists():
  old=json.loads((LEGACY/'data.json').read_text());s=migrate(old,LEGACY);persist(s);return s
 return initial()

def backup(s,dest):
 persist(s,generate=False)
 temp=Path(str(dest)+'.tmp')
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
  z.write(DATA/'data.json','data.json')
  for p in s['profiles']:
   for f in profile_dir(p).rglob('*'):
    if f.is_file() and not f.is_symlink():z.write(f,str(f.relative_to(DATA)))
 temp.chmod(0o600);temp.replace(dest)

def restore(source):
 # Validate all paths before changing anything; keep a complete pre-restore backup.
 with zipfile.ZipFile(source) as z:
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
  if (DATA/'data.json').exists():
   backup(load(),DATA/('Vor-Wiederherstellung-'+uuid.uuid4().hex[:8]+'.zip'))
  for i in z.infolist():
   if i.is_dir():continue
   if i.filename!='data.json' and not i.filename.startswith('Profile/'):continue
   path=resolve(i.filename);private_dir(path.parent);path.write_bytes(z.read(i));path.chmod(0o600)
 persist(s,generate=False);return s
