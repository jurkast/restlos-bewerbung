from email.message import EmailMessage
from email.policy import SMTP
from pypdf import PdfReader
from pathlib import Path
import re

def pdf_report(path,s,a):
 r=PdfReader(path);warnings=[]
 if Path(path).stat().st_size>5*1024**2:warnings.append('Die Datei ist größer als 5 MB. Prüfe die Vorgaben des Empfängers.')
 if re.search(r'\[[^\]]+\]|\bTODO\b|\bXXX\b',a['letter']):warnings.append('Im Anschreiben stehen möglicherweise noch Platzhalter.')
 if not s['profile']['name'].strip():warnings.append('Der Name fehlt.')
 if not a['company'].strip() or not a['position'].strip():warnings.append('Firma oder Position fehlt.')
 if a['form']['letterMode']=='form' and (not a['motivation'].strip() or not a['evidence'].strip()):warnings.append('Einstieg oder Erfahrung im Anschreiben fehlt.')
 text_pages=sum(bool((p.extract_text() or '').strip()) for p in r.pages)
 if text_pages<len(r.pages):warnings.append('Einige Seiten enthalten nur Bilder. Das ist bei gescannten Anlagen möglich.')
 return {'type':'export_report','path':str(path),'pages':len(r.pages),'mb':round(Path(path).stat().st_size/1024**2,2),'textPages':text_pages,'warnings':warnings}

def mail_draft(path,pdf,s,a):
 msg=EmailMessage(policy=SMTP);recipient=str(a.get('recipientEmail') or '').strip()
 if recipient:msg['To']=recipient
 if s['profile']['email'].strip():msg['From']=s['profile']['email'].strip()
 position=a['position'].strip()
 msg['Subject']='Bewerbung als '+position if position else 'Bewerbung';msg['X-Unsent']='1'
 msg.set_content(a['salutation']+'\n\nanbei erhalten Sie meine Bewerbungsunterlagen'+(' für die Position als '+position if position else '')+'.\n\nÜber die Gelegenheit zu einem persönlichen Gespräch freue ich mich.\n\nMit freundlichen Grüßen\n'+s['profile']['name'])
 msg.add_attachment(Path(pdf).read_bytes(),maintype='application',subtype='pdf',filename=('Bewerbung_'+re.sub(r'[^\w-]+','_',s['profile']['name'].strip()).strip('_')).rstrip('_')+'.pdf')
 Path(path).write_bytes(msg.as_bytes())
