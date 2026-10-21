#!/usr/bin/env python3
"""Build signed runtime ZIP and DEB from an explicit source/runtime whitelist."""
import argparse,hashlib,json,re,shutil,subprocess,tempfile,zipfile
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path,required=True,help='Directory with lib/ and native/');parser.add_argument('--key',type=Path,required=True,help='Private Ed25519 key, outside source tree');parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];v=(root/'VERSION').read_text().strip()
if not re.fullmatch(r'\d+\.\d+\.\d+',v):raise SystemExit('Invalid version')
if args.key.resolve().is_relative_to(root):raise SystemExit('Keep the private signing key outside the program source tree.')
args.output.mkdir(parents=True,exist_ok=True)
# Explicit source file types; never include profiles, data folders, logs or private keys.
files=[p for p in root.iterdir() if p.is_file() and (p.suffix in ('.py','.js','.html','.md','.svg','.sh') or p.name in ('VERSION','update-public.pem','requirements.txt','LICENSE'))]
with tempfile.TemporaryDirectory(prefix='restlos-release-') as td:
 stage=Path(td)/'package';app=stage/'opt/restlos-bewerbung';app.mkdir(parents=True)
 for p in files:shutil.copy2(p,app/p.name)
 for name in ('lib','native'):
  source=args.runtime/name
  if not source.is_dir():raise SystemExit('Missing runtime '+str(source))
  shutil.copytree(source,app/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 archive=args.output/('restlos-bewerbung-'+v+'.zip')
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for p in sorted(app.rglob('*')):
   if p.is_symlink():raise SystemExit('Unexpected symlink: '+str(p))
   if p.is_file():z.write(p,str(p.relative_to(app)))
 with archive.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 manifest={'application':'restlos-bewerbung','architecture':'amd64','version':v,'minimum_base':'0.6.0','archive':archive.name,'size':archive.stat().st_size,'sha256':digest}
 m=args.output/'restlos-update.json';m.write_text(json.dumps(manifest,indent=2)+'\n');sig=args.output/'restlos-update.sig'
 subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(args.key),'-rawin','-in',str(m),'-out',str(sig)],check=True)
 subprocess.run(['openssl','pkeyutl','-verify','-pubin','-inkey',str(root/'update-public.pem'),'-rawin','-in',str(m),'-sigfile',str(sig)],check=True)
 control=stage/'DEBIAN';control.mkdir();(control/'control').write_text('Package: restlos-bewerbung\nVersion: '+v+'\nSection: office\nPriority: optional\nArchitecture: amd64\nMaintainer: Restlos Bewerbung <local@localhost>\nDepends: python3 (>= 3.12), openssl, fonts-dejavu-core, poppler-utils, libegl1, libopengl0, libnss3, libxkbcommon0, libxcb-cursor0, libasound2t64, libhunspell-1.7-0, hunspell-de-de | hunspell-de-de-frami, tesseract-ocr, tesseract-ocr-deu, tesseract-ocr-eng\nDescription: Lokales Bewerbungsstudio mit signierten Programmupdates\n Formulare, Fotos, Vorlagen, PDF und Word, OCR, Bewerbungsplanung\n und optionale lokale KI. Persoenliche Dateien bleiben lokal.\n')
 bindir=stage/'usr/bin';bindir.mkdir(parents=True);launcher=bindir/'restlos-bewerbung';launcher.write_text('#!/bin/sh\nexec "/opt/restlos-bewerbung/Restlos Bewerbung starten.sh" "$@"\n');launcher.chmod(0o755)
 desktops=stage/'usr/share/applications';desktops.mkdir(parents=True);(desktops/'restlos-bewerbung.desktop').write_text('[Desktop Entry]\nType=Application\nName=Restlos Bewerbung\nComment=Profile und Bewerbungen lokal verwalten\nExec=restlos-bewerbung\nIcon=restlos-bewerbung\nTerminal=false\nCategories=Office;\nStartupWMClass=Restlos Bewerbung\n')
 icons=stage/'usr/share/icons/hicolor/scalable/apps';icons.mkdir(parents=True);shutil.copy2(root/'icon.svg',icons/'restlos-bewerbung.svg')
 subprocess.run(['dpkg-deb','--root-owner-group','-Zxz','-z3','--build',str(stage),str(args.output/('restlos-bewerbung_'+v+'_amd64.deb'))],check=True)
print('Created signed release '+v+' in '+str(args.output))
