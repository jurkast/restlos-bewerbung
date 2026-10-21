"""Local CV variants, attachment transforms, document audit and writing checks."""
import copy,re,base64,subprocess,tempfile
from pathlib import Path
CV_KEYS=('title','summary','experience','education','skills','languages','projects','hobbies')
ARTICLES={'der','die','das','den','dem','des'}
CLAUSE_STARTS={'ich','sie','er','es','wir','ihr','man','mich','mir','ihnen','ihre','ihr','mein','meine','meinen','meiner','meinem','unser','unsere','unseren','diese','dieser','dieses','dies','sich','auch','gerade'}
FIELD_LABELS={'letter':'Anschreiben','recipient':'Empfängeranschrift','title':'Berufsbezeichnung','summary':'Kurzprofil','experience':'Berufserfahrung','education':'Ausbildung','skills':'Kenntnisse','languages':'Sprachen','projects':'Projekte & Engagement','hobbies':'Interessen'}
LEGAL_FORMS=r'\b(gmbh|mbh|ag|kg|ohg|gbr|ug|haftungsbeschränkt|e\.?\s?v|e\.?\s?k|se|co|ltd|inc|llc|kgaa|stiftung|und|&)\b'
def company_words(name):
 cleaned=re.sub(LEGAL_FORMS,' ',name.lower());return [w for w in re.findall(r'[\wäöüß]+',cleaned) if len(w)>=3]
def cv_profile(p,a):
 result=copy.deepcopy(p)
 if a.get('cv') is not None:
  result.update(a['cv'])
  for k in ('experience','education','skills','languages'):result['form'][k]['mode']='text'
 return result

def validate_studio(p,a):
 cv=a.get('cv')
 if cv is not None and (not isinstance(cv,dict) or set(cv)!=set(CV_KEYS) or any(not isinstance(v,str) for v in cv.values())):raise ValueError('Ungültige eigene Lebenslauffassung.')
 d=a['design'];d.setdefault('photoScale',100);d.setdefault('spacing',100);d.setdefault('breakBefore',[])
 for key,lo,hi in [('photoScale',50,100),('spacing',75,130)]:
  if type(d[key]) not in (int,float) or not lo<=d[key]<=hi:raise ValueError('Ungültige Layoutgröße.')
 if not isinstance(d['breakBefore'],list) or any(k not in CV_KEYS for k in d['breakBefore']):raise ValueError('Ungültige Seitenumbrüche.')
 edits=a.setdefault('attachmentEdits',{})
 if not isinstance(edits,dict):raise ValueError('Ungültige Anlagenbearbeitung.')
 for name,rows in edits.items():
  if not isinstance(name,str) or not isinstance(rows,list) or not 1<=len(rows)<=300:raise ValueError('Ungültige Anlagenseiten.')
  for row in rows:
   if not isinstance(row,dict) or type(row.get('index'))!=int or row['index']<0 or row.get('rotation') not in (0,90,180,270):raise ValueError('Ungültige Anlagenseite.')

def attachment_pdf(a,rel,dest):
 from storage import resolve
 from pypdf import PdfReader,PdfWriter
 path=resolve(rel)
 if not path.is_file() or path.is_symlink():raise ValueError('Anlage fehlt oder ist verknüpft: '+path.name)
 reader=PdfReader(path)
 if reader.is_encrypted:raise ValueError('Bitte eine PDF ohne Passwort verwenden.')
 rows=a.get('attachmentEdits',{}).get(rel,[{'index':i,'rotation':0} for i in range(len(reader.pages))])
 writer=PdfWriter()
 for row in rows:
  if row['index']>=len(reader.pages):raise ValueError('Die Seitenzahl einer Anlage hat sich geändert. Bitte die Seitenbearbeitung zurücksetzen.')
  page=copy.deepcopy(reader.pages[row['index']]);page.rotate(row['rotation']);writer.add_page(page)
 writer.write(str(dest));writer.close()

def missing_documents(profile):
 from storage import DATA
 return [{'id':d['id'],'name':d['name'],'category':d['category'],'path':d['path']} for d in profile['documents'] if not (DATA/d['path']).is_file() or (DATA/d['path']).is_symlink()]

def audit_documents(s):
 return [dict(d,profileId=p['id'],profileLabel=p['label']) for p in s['profiles'] for d in missing_documents(p)]

def repair_document(profile,document_id,source):
 from storage import DATA,resolve
 import shutil
 document=next(d for d in profile['documents'] if d['id']==document_id)
 target=resolve(document['path']);raw=DATA/document['path'];source=Path(source)
 if raw.is_symlink() or target.exists():raise ValueError('Die Datei ist vorhanden oder verknüpft. Sie wird nicht überschrieben.')
 if not source.is_file() or source.is_symlink():raise ValueError('Bitte eine reguläre Datei auswählen.')
 if source.suffix.lower()!=target.suffix.lower():raise ValueError('Bitte denselben Dateityp auswählen: '+target.suffix)
 if source.stat().st_size>100*1024**2:raise ValueError('Die Ersatzdatei darf höchstens 100 MB groß sein.')
 if target.suffix.lower()=='.pdf':
  from pypdf import PdfReader
  reader=PdfReader(source)
  if reader.is_encrypted:raise ValueError('Bitte eine PDF ohne Passwort auswählen.')
 elif target.suffix.lower() in ('.png','.jpg','.jpeg','.webp'):
  from PIL import Image
  with Image.open(source) as im:im.verify()
 target.parent.mkdir(parents=True,exist_ok=True)
 with source.open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
 target.chmod(0o600)
 return document['name']

def text_advice(text):
 issues=[]
 def issue(start,end,message,replacement=None):issues.append(dict(start=start,end=end,original=text[start:end],message=message,replacement=replacement))
 for m in re.finditer(r'\b([\wÄÖÜäöüß]+)(\s+)\1\b',text,re.I):
  word=m.group(1).lower()
  if word in ARTICLES:
   # „…, die die Abteilung …“ is correct German; only flag without a preceding comma.
   if re.search(r',\s*$',text[:m.start()]):continue
   issue(*m.span(),'„'+m.group(1)+' '+m.group(1)+'“ – bitte prüfen. Korrekt ist das z. B. nach einem Komma („…, die die …“).')
  else:issue(*m.span(),'Wort direkt wiederholt – bitte prüfen.',m.group(1))
 for m in re.finditer(r'(?<=\S) {2,}(?=\S)',text):issue(*m.span(),'Mehrere Leerzeichen.', ' ')
 for phrase in ('Ich bin mir sicher das','Ich hoffe das','Ich bin davon überzeugt das'):
  for m in re.finditer(r'\b'+re.escape(phrase)+r'\b(?=\s+(\S+))?',text,re.I):
   following=(m.group(1) or '').strip('.,;:!?')
   fixed=re.sub(r' das$',', dass',m.group(),flags=re.I)
   if following.lower() in CLAUSE_STARTS:issue(*m.span(),'Hier wird der Nebensatz mit „dass“ eingeleitet.',fixed)
   elif following[:1].isupper():continue  # „Ich hoffe das Beste“: Artikel vor einem Nomen
   elif following:issue(*m.span(),'Bitte prüfen: Leitet „das“ hier einen Nebensatz ein, schreibe „, dass“.')
 for m in re.finditer(r'\bIch freue mich darauf Sie\b',text,re.I):issue(*m.span(),'Vor der folgenden Infinitivgruppe steht ein Komma.',re.sub(r' Sie$',', Sie',m.group(),flags=re.I))
 for m in re.finditer(r'[^.!?\n]+[.!?]?',text):
  if len(m.group().split())>30:issue(*m.span(),'Langer Satz: über 30 Wörter. Prüfe, ob du ihn aufteilen kannst.')
 for phrase in ('hiermit bewerbe ich mich','mit großem interesse','teamfähig und belastbar'):
  for m in re.finditer(re.escape(phrase),text,re.I):issue(*m.span(),'Allgemeine Formulierung: Ergänze einen konkreten Bezug oder ein Beispiel.')
 sentences={}
 for m in re.finditer(r'[^.!?\n]+[.!?]',text):
  key=m.group().strip().lower()
  if key in sentences:issue(*m.span(),'Dieser Satz kommt mehrfach vor.')
  sentences[key]=True
 return issues

def application_check(s,a,check_size=True):
 from forms import materialize
 from storage import selected,resolve
 from pdf_export import make_pdf
 materialize(s['profile'],a);p=cv_profile(s['profile'],a);issues=[]
 def add(text,step='stelle',field=''):issues.append(dict(message=text,step=step,field=field))
 for key,label in [('name','Name'),('email','E-Mail'),('phone','Telefon'),('address','Adresse')]:
  if not p.get(key,'').strip():add(label+' fehlt.','profile',key)
 if p.get('email') and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',p['email']):add('E-Mail-Adresse bitte prüfen.','profile','email')
 for key,label in [('company','Unternehmen'),('position','Position'),('recipient','Empfänger')]:
  if not a.get(key,'').strip():add(label+' fehlt.','stelle',key)
 texts=[('text','letter',a['letter']),('stelle','recipient',a['recipient'])]+[('cv',k,p.get(k,'')) for k in CV_KEYS]
 for step,key,text in texts:
  if re.search(r'\[[^\]]+\]|\bTODO\b|\bXXX\b',text):add('Möglicher Platzhalter in „'+FIELD_LABELS.get(key,key)+'“.',step,key)
  for m in re.finditer(r'(\d{2})/(\d{4})\s*[–-]\s*(\d{2})/(\d{4})',text):
   if not 1<=int(m[1])<=12 or not 1<=int(m[3])<=12 or m[2]+m[1]>m[4]+m[3]:add('Ungültiger oder rückwärts laufender Zeitraum in „'+FIELD_LABELS.get(key,key)+'“: '+m.group()+'.',step,key)
 for other in s['applications']:
  company=other.get('company','').strip()
  if len(company)>3 and company.lower()!=a['company'].strip().lower() and company.lower() in a['letter'].lower():add('Im Anschreiben steht auch das Unternehmen „'+company+'“. Bitte prüfen.','text','letter')
 words=company_words(a['company'])
 if words and a['recipient'] and not any(w in a['recipient'].lower() for w in words):add('Unternehmen und Empfängeranschrift stimmen möglicherweise nicht überein.','stelle','recipient')
 if not a['letter'].strip():add('Anschreibentext fehlt.','text','letter')
 if a['design'].get('letterLayout')=='din5008':
  from letters import recipient_lines
  if len(recipient_lines(a))>6:add('Die Empfängeranschrift hat mehr als 6 Zeilen und passt so nicht vollständig ins Adressfeld nach DIN 5008.','stelle','recipient')
 for d in missing_documents(selected(s)):add('Datei fehlt oder ist verknüpft: '+d['name'],'documents')
 for rel in a['attachments']:
  if not resolve(rel).is_file():add('Zugeordnete Anlage fehlt: '+Path(rel).name,'documents')
 report={'issues':issues,'mb':None,'pages':None}
 if check_size:
  try:
   with tempfile.TemporaryDirectory() as td:
    path=Path(td)/'check.pdf';make_pdf(s,a,path)
    from pypdf import PdfReader
    report.update(mb=round(path.stat().st_size/1024**2,2),pages=len(PdfReader(path).pages))
    if path.stat().st_size>5*1024**2:add('Die Gesamtmappe ist größer als 5 MB. Bitte die Vorgaben des Empfängers prüfen.','anlagen')
  except Exception as e:add('Mappe konnte nicht vollständig erstellt werden: '+str(e),'anlagen')
 return report

def render_pages(path,start=0,count=1,scale=900):
 from pypdf import PdfReader
 total=len(PdfReader(path).pages)
 if not total or start<0 or start>=total:raise ValueError('Ungültige Vorschauseite.')
 with tempfile.TemporaryDirectory() as td:
  result=subprocess.run(['pdftoppm','-f',str(start+1),'-l',str(min(total,start+count)),'-scale-to',str(scale),'-png',str(path),str(Path(td)/'page')],capture_output=True,timeout=60)
  if result.returncode:raise ValueError('Seitenvorschau konnte nicht erstellt werden.')
  images=sorted(Path(td).glob('page-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
  return {'count':total,'start':start,'pages':[base64.b64encode(p.read_bytes()).decode() for p in images]}
