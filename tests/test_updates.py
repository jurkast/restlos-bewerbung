import os,sys,json,hashlib,zipfile,subprocess,shutil,copy,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];temporary=tempfile.TemporaryDirectory(prefix='restlos-update-test-');work=Path(temporary.name);base=work/'base';base.mkdir();(base/'VERSION').write_text('0.6.0');os.environ['RESTLOS_BASE_DIR']=str(base)
os.environ['RESTLOS_UPDATE_DIR']=str(work/'updates');os.environ['RESTLOS_DATA_DIR']=str(work/'data');os.environ['RESTLOS_LEGACY_DIR']=str(work/'none')
sys.path.insert(0,str(root))
import app,storage,updates as u,reliability
u.ROOT=base
key=work/'test-private.pem'
subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(key)],check=True)
subprocess.run(['openssl','pkey','-in',str(key),'-pubout','-out',str(base/'update-public.pem')],check=True)
s=storage.initial();s['profile']['name']='LOKALE TESTPERSON';storage.persist(s)
original=(storage.DATA/'data.json').read_bytes();secret=storage.DATA/'nur-lokal.txt';secret.write_text('Nicht veröffentlichen')
def release(v='0.7.0',unsafe=False):
 archive=work/('restlos-bewerbung-'+v+'.zip')
 with zipfile.ZipFile(archive,'w') as z:
  for p,data in {'app.py':'# Synthetic update fixture; not a real release','index.html':'test','VERSION':v,'lib/PySide6/__init__.py':'# test'}.items():z.writestr(p,data)
  if unsafe:z.writestr('../escape.txt','bad')
 m={'application':'restlos-bewerbung','architecture':'amd64','version':v,'minimum_base':'0.6.0','archive':archive.name,'size':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
 manifest=work/'manifest.json';manifest.write_text(json.dumps(m));sig=work/'manifest.sig';subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(key),'-rawin','-in',str(manifest),'-out',str(sig)],check=True)
 return manifest,sig,archive
u.save_config('jurkast/restlos-bewerbung',True)
m,sig,z=release();message=u.stage(m,sig,z,reliability.snapshot_before_update);assert '0.7.0' in message;assert (storage.DATA/'data.json').read_bytes()==original;assert secret.read_text()=='Nicht veröffentlichen'
backups=list((storage.DATA/'Sicherungen').glob('*.zip'));assert len(backups)>=1
with zipfile.ZipFile(backups[-1]) as backup:assert json.loads(backup.read('data.json'))['profiles'][0]['profile']['name']=='LOKALE TESTPERSON';assert backup.testzip() is None
assert u.choose_launch().name=='0.7.0';assert (u.HOME/'launch-pending.json').exists()
# Emulate the new app reporting a successful startup.
oldroot=u.ROOT;u.ROOT=u.HOME/'versions/0.7.0';u.startup_ready();u.ROOT=oldroot;assert not (u.HOME/'launch-pending.json').exists()
# A startup failure falls back and disables automatic retries.
u.write(u.HOME/'launch-pending.json',{'version':'0.7.0','pid':99999999});assert u.choose_launch()==u.BASE;assert not u.config()['automatic'];assert not (u.HOME/'current.json').exists()
# Failed backup must not activate an update.
def badbackup():raise OSError('Sicherung fehlgeschlagen')
try:u.stage(m,sig,z,badbackup);raise AssertionError('backup error ignored')
except OSError:pass
assert not (u.HOME/'current.json').exists()
# Tampered signature is rejected.
sig.write_bytes(b'0'*64)
try:u.stage(m,sig,z,lambda:None);raise AssertionError('bad signature accepted')
except ValueError:pass
# Signed archive with traversal is still rejected.
m,sig,z=release('0.8.0',True)
try:u.stage(m,sig,z,lambda:None);raise AssertionError('unsafe zip accepted')
except ValueError:pass
assert not (work/'escape.txt').exists()
# Changed download is rejected before extraction.
m,sig,z=release('0.8.0');z.write_bytes(z.read_bytes()+b'tampered')
try:u.stage(m,sig,z,lambda:None);raise AssertionError('bad digest accepted')
except ValueError:pass
assert u.allowed_url('https://github.com/jurkast/restlos-bewerbung') and not u.allowed_url('http://github.com/x') and not u.allowed_url('https://evil.test/x')
# No applicant content is needed by the download transport.
requested=[]
def fake_fetch(url,dest,limit):
 requested.append(url)
 if url.endswith('.json'):shutil.copy2(m,dest)
 elif url.endswith('.sig'):shutil.copy2(sig,dest)
 else:raise OSError('test offline')
u.fetch=fake_fetch;r=u.check(lambda:None);assert not r['ok'];assert all('LOKALE' not in x for x in requested);assert not (u.HOME/'current.json').exists()
print('PASS signed staging, local backup, unchanged originals, activation handshake, failed startup rollback, backup failure, invalid signature/hash/path, offline failure')

temporary.cleanup()
