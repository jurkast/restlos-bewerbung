"""Signed GitHub release updates, staged per user; no privileged package changes."""
import os,json,re,hashlib,subprocess,tempfile,shutil,zipfile,stat,time
from pathlib import Path
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.parse import urlparse
from urllib.error import HTTPError,URLError
ROOT=Path(__file__).resolve().parent
BASE=Path(os.environ.get('RESTLOS_BASE_DIR',str(ROOT))).resolve()
HOME=Path(os.environ.get('RESTLOS_UPDATE_DIR',str(Path.home()/'.local/share/restlos-bewerbung-updates')))
DEFAULT_REPO='jurkast/restlos-bewerbung'

def version(v):
 if not isinstance(v,str) or not re.fullmatch(r'\d+\.\d+\.\d+',v):raise ValueError('Ungültige Versionsnummer.')
 return tuple(map(int,v.split('.')))
def current_version():return (ROOT/'VERSION').read_text().strip()
def private(p):p.mkdir(parents=True,exist_ok=True,mode=0o700);return p
def write(path,data):
 private(path.parent);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2));tmp.chmod(0o600);tmp.replace(path)
def read(path,default):
 try:return json.loads(path.read_text())
 except (OSError,ValueError):return default

def config():return {'repository':DEFAULT_REPO,'automatic':True,**read(HOME/'settings.json',{})}
def save_config(repo,automatic):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo) or any(x in ('.','..') for x in repo.split('/')):raise ValueError('Bitte GitHub-Benutzer/Repository eingeben, zum Beispiel jurkast/restlos-bewerbung.')
 write(HOME/'settings.json',{'repository':repo,'automatic':bool(automatic)})
def status():
 active=read(HOME/'current.json',{})
 return {'version':current_version(),'config':config(),'pending':active.get('version','') if active.get('version')!=current_version() else '',**read(HOME/'status.json',{})}

def allowed_url(url):
 u=urlparse(url)
 return u.scheme=='https' and u.hostname in ('github.com','release-assets.githubusercontent.com','objects.githubusercontent.com') and not u.username and not u.password
class Redirect(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if not allowed_url(newurl):raise ValueError('Update-Download wurde an eine unerwartete Adresse umgeleitet.')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def fetch(url,dest,limit):
 if not allowed_url(url):raise ValueError('Ungültige Update-Adresse.')
 try:
  with build_opener(Redirect()).open(Request(url,headers={'User-Agent':'Restlos-Bewerbung-Updater/0.6'}),timeout=20) as response,dest.open('wb') as output:
   total=0;started=time.monotonic()
   while True:
    block=response.read(1024*1024)
    if not block:break
    total+=len(block)
    if time.monotonic()-started>600:raise ValueError('Der Download hat zu lange gedauert. Bitte später erneut versuchen.')
    if total>limit:raise ValueError('Die Update-Datei überschreitet die erlaubte Größe.')
    output.write(block)
 except HTTPError as e:
  if e.code==404:raise ValueError('Noch kein passendes öffentliches Update-Release gefunden.') from e
  raise ValueError('GitHub ist momentan nicht erreichbar (HTTP '+str(e.code)+').') from e
 except (URLError,TimeoutError) as e:raise ValueError('Die Updatequelle ist momentan nicht erreichbar. Deine installierte Version bleibt nutzbar.') from e

def verify(manifest,signature):
 result=subprocess.run(['openssl','pkeyutl','-verify','-pubin','-inkey',str(BASE/'update-public.pem'),'-rawin','-in',str(manifest),'-sigfile',str(signature)],capture_output=True,timeout=10)
 if result.returncode:raise ValueError('Die Update-Signatur ist ungültig. Es wird nichts installiert.')
 m=json.loads(manifest.read_text())
 if m.get('application')!='restlos-bewerbung' or m.get('architecture')!='amd64':raise ValueError('Das Update passt nicht zu Restlos Bewerbung auf diesem Rechner.')
 version(m['version']);version(m['minimum_base'])
 if version(m['minimum_base'])>version((BASE/'VERSION').read_text().strip()):raise ValueError('Dieses Update benötigt einmalig ein neueres DEB-Installationspaket.')
 if not re.fullmatch(r'restlos-bewerbung-\d+\.\d+\.\d+\.zip',m.get('archive','')) or not re.fullmatch(r'[a-f0-9]{64}',m.get('sha256','')):raise ValueError('Ungültige Update-Beschreibung.')
 if type(m.get('size'))!=int or not 0<m['size']<1024**3:raise ValueError('Ungültige Update-Größe.')
 return m

def extract(archive,target):
 with zipfile.ZipFile(archive) as z:
  entries=z.infolist();names=set()
  if len(entries)>30000 or sum(i.file_size for i in entries)>2*1024**3:raise ValueError('Das Update ist zu groß.')
  for i in entries:
   p=Path(i.filename);kind=stat.S_IFMT(i.external_attr>>16)
   if p.is_absolute() or '..' in p.parts or '\\' in i.filename or i.filename in names or kind not in (0,stat.S_IFREG,stat.S_IFDIR):raise ValueError('Unsicherer Pfad im Update.')
   names.add(i.filename)
  for i in entries:
   dest=target/i.filename
   if i.is_dir():private(dest);continue
   private(dest.parent)
   with z.open(i) as src,dest.open('wb') as out:shutil.copyfileobj(src,out)
   dest.chmod(0o700 if i.external_attr>>16&0o111 else 0o600)
 for required in ('app.py','index.html','VERSION','lib/PySide6/__init__.py'):
  if not (target/required).is_file():raise ValueError('Das Update ist unvollständig: '+required)

def stage(manifest,signature,archive,before_activate):
 m=verify(manifest,signature)
 if version(m['version'])<=version(current_version()):return 'Restlos ist auf dem aktuellen Stand.'
 active=read(HOME/'current.json',{})
 if active.get('version')==m['version']:return 'Version '+m['version']+' ist bereit und wird beim nächsten Start verwendet.'
 if active.get('version') and version(active['version'])>version(m['version']):return 'Eine neuere Version ist bereits vorbereitet.'
 with archive.open('rb') as source:digest=hashlib.file_digest(source,'sha256').hexdigest()
 if archive.stat().st_size!=m['size'] or digest!=m['sha256']:raise ValueError('Die Update-Datei ist beschädigt oder verändert. Es wird nichts installiert.')
 private(HOME)
 if shutil.disk_usage(HOME).free<3*1024**3:raise ValueError('Für ein sicheres Update werden mindestens 3 GB freier Speicher benötigt.')
 with tempfile.TemporaryDirectory(prefix='staging-',dir=HOME) as td:
  target=Path(td)/'app';private(target);extract(archive,target)
  if (target/'VERSION').read_text().strip()!=m['version']:raise ValueError('Die Versionsangabe im Update stimmt nicht überein.')
  shutil.copy2(manifest,target/'release.json');shutil.copy2(signature,target/'release.sig')
  before_activate()
  dest=private(HOME/'versions')/m['version']
  if dest.exists():shutil.rmtree(dest)
  target.rename(dest)
  write(HOME/'current.json',{'version':m['version'],'previous':active.get('version','')})
 return 'Version '+m['version']+' ist geprüft und bereit. Sie startet automatisch beim nächsten Öffnen von Restlos.'

def check(before_activate):
 cfg=config();repo=cfg['repository'];save_config(repo,cfg['automatic'])
 base='https://github.com/'+repo+'/releases/latest/download/'
 private(HOME)
 try:
  with tempfile.TemporaryDirectory(prefix='download-',dir=HOME) as td:
   tmp=Path(td);manifest=tmp/'restlos-update.json';signature=tmp/'restlos-update.sig'
   fetch(base+manifest.name,manifest,64000);fetch(base+signature.name,signature,256);m=verify(manifest,signature)
   if version(m['version'])<=version(current_version()):message='Restlos ist auf dem aktuellen Stand.'
   elif read(HOME/'current.json',{}).get('version')==m['version']:message='Version '+m['version']+' ist bereits für den nächsten Start bereit.'
   else:
    archive=tmp/m['archive'];fetch(base+m['archive'],archive,m['size']);message=stage(manifest,signature,archive,before_activate)
  write(HOME/'status.json',{'message':message,'checked':time.strftime('%d.%m.%Y %H:%M'),'ok':True})
 except Exception as e:write(HOME/'status.json',{'message':str(e),'checked':time.strftime('%d.%m.%Y %H:%M'),'ok':False})
 return status()

def rollback():
 active=read(HOME/'current.json',{});previous=active.get('previous','')
 if previous and (HOME/'versions'/previous/'app.py').is_file():write(HOME/'current.json',{'version':previous})
 else:(HOME/'current.json').unlink(missing_ok=True)
 cfg=config();save_config(cfg['repository'],False)
 (HOME/'launch-pending.json').unlink(missing_ok=True)
 write(HOME/'status.json',{'message':'Zur vorherigen Version zurückgeschaltet. Automatische Updates sind vorerst ausgeschaltet. Bitte Restlos neu starten.','ok':True})

def startup_ready():
 pending=read(HOME/'launch-pending.json',{})
 if pending.get('version')==current_version():(HOME/'launch-pending.json').unlink(missing_ok=True)
 try:prune_versions()
 except OSError:pass

def prune_versions():
 """Each prepared version needs about 1 GB. Keep only the running, the active
 and the previous version (for rollback); remove older ones."""
 folder=HOME/'versions'
 if not folder.is_dir():return []
 active=read(HOME/'current.json',{})
 keep={current_version(),active.get('version',''),active.get('previous','')}
 if ROOT.parent.resolve()==folder.resolve():keep.add(ROOT.name)
 pending=read(HOME/'launch-pending.json',{}).get('version')
 if pending:keep.add(pending)
 removed=[]
 for entry in folder.iterdir():
  if entry.name in keep or entry.is_symlink() or not entry.is_dir():continue
  try:version(entry.name)
  except ValueError:continue
  shutil.rmtree(entry);removed.append(entry.name)
 return removed

def choose_launch():
 active=read(HOME/'current.json',{});v=active.get('version')
 if not v:return BASE
 try:
  if version(v)<=version((BASE/'VERSION').read_text().strip()):return BASE
  pending=read(HOME/'launch-pending.json',{})
  if pending.get('version')==v:
   # A live process is not a failed startup.
   pid=pending.get('pid')
   if isinstance(pid,int):
    try:os.kill(pid,0);return BASE
    except ProcessLookupError:pass
   rollback();return choose_launch()
  target=HOME/'versions'/v;m=verify(target/'release.json',target/'release.sig')
  if m['version']!=v or (target/'VERSION').read_text().strip()!=v:raise ValueError('Versionsprüfung fehlgeschlagen.')
  write(HOME/'launch-pending.json',{'version':v,'pid':os.getpid()});return target
 except Exception as e:
  rollback();write(HOME/'status.json',{'message':'Update konnte nicht gestartet werden: '+str(e)+'. Installierte Version wird verwendet.','ok':False});return BASE
