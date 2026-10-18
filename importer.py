"""Conservative, local document extraction. Never silently apply inferred data."""
import re,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from pypdf import PdfReader

def extract(path,progress=None):
 path=Path(path);ext=path.suffix.lower()
 if path.stat().st_size>40*1024**2:raise ValueError('Bitte eine Datei mit höchstens 40 MB wählen.')
 if ext=='.pdf':
  r=PdfReader(path)
  if r.is_encrypted:raise ValueError('Bitte eine PDF ohne Passwort verwenden.')
  if len(r.pages)>100:raise ValueError('Für den Import bitte höchstens 100 PDF-Seiten verwenden.')
  from ocr import recognize_page
  parts=[];scans=0
  for i,page in enumerate(r.pages):
   value=page.extract_text(extraction_mode='layout') or ''
   if len(value.strip())<30:
    scans+=1
    if scans>20:raise ValueError('Bitte Dokumente mit mehr als 20 gescannten Seiten für den Import aufteilen.')
    if progress:progress('Texterkennung: PDF-Seite '+str(i+1)+' von '+str(len(r.pages)))
    value=recognize_page(path,i+1) or value
   parts.append(value)
  text='\n\n'.join(parts)
 elif ext in ('.docx','.odt'):
  with zipfile.ZipFile(path) as z:
   name='word/document.xml' if ext=='.docx' else 'content.xml'
   if z.getinfo(name).file_size>15*1024**2:raise ValueError('Dokumentinhalt ist zu groß.')
   root=ET.fromstring(z.read(name));tag='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p' if ext=='.docx' else '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p'
   text='\n'.join(''.join(el.itertext()) for el in root.iter(tag))
 elif ext in ('.png','.jpg','.jpeg','.webp','.tif','.tiff'):
  from ocr import recognize_image
  if progress:progress('Texterkennung läuft lokal …')
  text=recognize_image(path)
 elif ext=='.txt':
  try:text=path.read_text(encoding='utf-8-sig')
  except UnicodeDecodeError:text=path.read_text(encoding='cp1252')
 else:raise ValueError('Unterstützt werden PDF, DOCX, ODT, TXT und Bilddateien.')
 if not text.strip():raise ValueError('Es wurde kein lesbarer Text erkannt. Bitte eine schärfere, gerade ausgerichtete Vorlage verwenden. Das Original bleibt in der Dokumentablage.')
 return text[:150000]

def suggest(text,category='Lebenslauf'):
 lines=[re.sub(r'\s{2,}',' ',x).strip() for x in text.splitlines() if x.strip()]
 fields={};notes=[]
 email=re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text)
 if email:fields['email']=email.group()
 for line in lines:
  phone=re.search(r'(?:Telefon|Tel\.?|Mobil|Phone)\s*:?\s*([+\d][\d ()/.-]{6,})',line,re.I)
  if not phone:phone=re.match(r'^((?:\+49|0049|0)[\d ()/.-]{7,})$',line)
  if phone:fields['phone']=phone.group(1).strip();break
 if category=='Lebenslauf':
  excluded=['lebenslauf','curriculum vitae','kontakt','persönliche daten','profil','bewerbung','berufserfahrung']
  for line in lines[:10]:
   candidate=re.sub(r'^(?:Name|Vor- und Nachname)\s*:\s*','',line,flags=re.I)
   if line.lower() not in excluded and re.fullmatch(r'[A-ZÄÖÜ][a-zäöüßéèà-]+(?: [A-ZÄÖÜ][a-zäöüßéèà-]+){1,3}',candidate):fields['name']=candidate;notes.append('Der Name ist eine Vermutung aus den ersten Zeilen.');break
  for i,line in enumerate(lines):
   if re.search(r'\b\d{5}\s+[A-ZÄÖÜ]',line):
    fields['address']=('\n'.join(lines[max(0,i-1):i+1]) if i and re.search(r'\d',lines[i-1]) else line);break
  headings={'experience':['berufserfahrung','beruflicher werdegang','berufliche erfahrung','praktische erfahrung'],'education':['ausbildung','bildung','schulbildung','ausbildung & weiterbildung','studium'],'skills':['kenntnisse','fähigkeiten','kompetenzen','it-kenntnisse','kenntnisse und fähigkeiten'],'languages':['sprachen','sprachkenntnisse']}
  current=None;parts={}
  for line in lines:
   hit=next((k for k,hs in headings.items() if line.lower().rstrip(':') in hs),None)
   if hit:current=hit;parts.setdefault(hit,[]);continue
   if line.lower().rstrip(':') in ['hobbys','interessen','referenzen','persönliche daten','kontakt']:current=None
   if current:parts[current].append(line)
  fields.update({k:'\n'.join(v) for k,v in parts.items() if v})
 if category=='Anschreiben':
  match=re.search(r'((?:Sehr geehrte[^\n]+|Guten Tag[^\n]+))\n(.*)',text,re.S)
  if match:
   fields['salutation']=match.group(1).strip();body=re.split(r'Mit freundlichen Grüßen|Freundliche Grüße|Beste Grüße',match.group(2),flags=re.I)[0];fields['letter']=body.strip()
  else:fields['letter']=text.strip();notes.append('Keine eindeutige Anrede erkannt: Der gesamte Text wird zur Auswahl angeboten.')
  pos=re.search(r'Bewerbung\s+(?:als|um(?: die Stelle als)?)\s+([^\n]+)',text,re.I)
  if pos:fields['position']=pos.group(1).strip()
 notes.append('Texterkennung, Spalten und ungewöhnliche Überschriften können Fehler verursachen. Prüfe jeden Vorschlag vor der Übernahme.')
 return dict(fields=fields,notes=notes,text=text)
