"""Local, paginated application PDFs with independent sidebar flow."""
import sys,tempfile,threading
from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'lib'))
from reportlab.platypus import SimpleDocTemplate,BaseDocTemplate,Frame,PageTemplate,Paragraph,Spacer,Image,PageBreak,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,Color,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader,PdfWriter
from storage import resolve
from forms import materialize
from photos import cropped
from personal import details,signature_image
from studio import cv_profile,attachment_pdf
TEMPLATES={
 'Seitenleiste':dict(side=True,accent='#167c77',style='soft'),
 'Graphit':dict(side=True,accent='#455477',style='soft'),
 'Sand':dict(side=True,accent='#8f6b3e',style='soft'),
 'Nordlicht':dict(side=True,accent='#174a65',style='dark'),
 'Elegant':dict(side=True,accent='#5b4178',style='stripe'),
 'Kontur':dict(side=True,accent='#3d6453',style='outline'),
 'Studio':dict(side=True,accent='#ad4e3f',style='block'),
 'Klar':dict(side=False,accent='#243447',style='plain'),
 'Modern':dict(side=False,accent='#187b79',style='line'),
 'Klassisch':dict(side=False,accent='#383838',style='classic'),
 'Horizont':dict(side=False,accent='#234d72',style='banner'),
 'Editorial':dict(side=False,accent='#954b37',style='editorial')}
SIDEBARS={k:v for k,v in TEMPLATES.items() if v['side']}
LABELS={'summary':'Kurzprofil','experience':'Berufserfahrung','education':'Ausbildung & Weiterbildung','projects':'Projekte & Engagement','skills':'Kenntnisse','languages':'Sprachen','hobbies':'Interessen'}
LOCK=threading.RLock()

def settings(a):
 conf=TEMPLATES.get(a['template'],TEMPLATES['Seitenleiste']).copy();conf['accent']=a.get('design',{}).get('accent') or conf['accent'];return conf

def fonts():
 for name,file in [('Restlos','DejaVuSans.ttf'),('RestlosBold','DejaVuSans-Bold.ttf'),('RestlosSerif','DejaVuSerif.ttf'),('RestlosSerifBold','DejaVuSerif-Bold.ttf')]:
  if name not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))

def styles(a,light_text=False):
 d=a['design'];serif=d['font']=='Serif' or a['template']=='Klassisch';font='RestlosSerif' if serif else 'Restlos';bold=font+'Bold';color=HexColor(settings(a)['accent']);size=d['size'];spacing=d.get('spacing',100)/100
 body=ParagraphStyle('body',fontName=font,fontSize=size,leading=size*1.52*spacing,spaceAfter=10*spacing,textColor=HexColor('#253843'),splitLongWords=True)
 return {'body':body,'small':ParagraphStyle('small',parent=body,fontSize=8.5,leading=13,spaceAfter=12),
 'side':ParagraphStyle('side',parent=body,fontSize=9,leading=14,textColor=white if light_text else HexColor('#253843')),
 'sidehead':ParagraphStyle('sidehead',parent=body,fontName=bold,fontSize=9,leading=14,spaceBefore=15,spaceAfter=8,textColor=white if light_text else color,keepWithNext=True),
 'name':ParagraphStyle('name',parent=body,fontName=bold,fontSize=26,leading=32,textColor=color,spaceAfter=12),
 'role':ParagraphStyle('role',parent=body,fontName=bold,fontSize=12,leading=18,spaceAfter=16),
 'section':ParagraphStyle('section',parent=body,fontName=bold,fontSize=12,leading=18,textColor=color,spaceBefore=15*spacing,spaceAfter=9*spacing,keepWithNext=True),
 'station':ParagraphStyle('station',parent=body,fontName=bold,spaceAfter=6,keepWithNext=True)}

def para(text,style):return Paragraph(escape(str(text)).replace('\n','<br/>'),style)
def photo(p,a,width=130):
 if not p.get('photo') or not a['design']['photo'] or not resolve(p['photo']).is_file():return []
 width*=a['design'].get('photoScale',100)/100
 image=Image(cropped(p),width=width,height=width*(1.25 if p['photoSettings']['shape']=='portrait' else 1));image.hAlign='LEFT';return [image,Spacer(1,10)]
def blocks(story,text,style):
 for block in text.split('\n\n'):
  if block.strip():story.append(para(block,style))
def sections(story,p,a,st,keys):
 for key in keys:
  if not p.get(key,'').strip():continue
  if key in a['design'].get('breakBefore',[]):story.append(PageBreak())
  story.append(para(LABELS[key],st['section']))
  if key in ('experience','education'):
   for block in p[key].split('\n\n'):
    lines=block.split('\n');story.append(para(lines[0],st['station'] if len(lines)>1 else st['body']))
    if len(lines)>1:blocks(story,'\n'.join(lines[1:]),st['body'])
  else:blocks(story,p[key],st['body'])

def page_footer(c,doc,p,color):
 c.setFont('Restlos',8);c.setFillColor(HexColor('#63737b'));c.drawRightString(551,26,str(doc.page))

def letter_pdf(p,a,path):
 st=styles(a);conf=settings(a);story=[para(p['name'] or 'Dein Name',st['name']),para(' · '.join(filter(None,[p['email'],p['phone']]))+'\n'+p['address'],st['small'])]
 blocks(story,a['recipient'] or a['company'],st['body']);story.append(Spacer(1,8));story.append(para(', '.join(filter(None,[a['location'],a['date']])),st['small']))
 story.append(para('Bewerbung als '+(a['position'] or 'Position'),st['role']));blocks(story,a['salutation'],st['body']);blocks(story,a['letter'],st['body']);ending=[para('Mit freundlichen Grüßen',st['body']),Spacer(1,8)]
 if p.get('signature') and a['design'].get('signature',True) and resolve(p['signature']).is_file():
  stream,w,h=signature_image(p,a);im=Image(stream,width=w,height=h);im.hAlign='LEFT';ending.extend([im,Spacer(1,5)])
 ending.append(para(p['name'],st['body']));story.append(KeepTogether(ending))
 def background(c,d):
  if conf['style'] not in ('plain','classic'):
   c.setStrokeColor(HexColor(conf['accent']));c.setLineWidth(3);c.line(46,813,550,813)
  page_footer(c,d,p,conf['accent'])
 SimpleDocTemplate(str(path),pagesize=(595.28,841.89),leftMargin=46,rightMargin=46,topMargin=44,bottomMargin=48).build(story,onFirstPage=background,onLaterPages=background)

def cv_pdf(p,a,path):
 conf=settings(a);dark=conf['style']=='dark';st=styles(a,dark);accent=HexColor(conf['accent']);light=Color(.93+.07*accent.red,.93+.07*accent.green,.93+.07*accent.blue)
 if not conf['side']:
  story=[]
  if conf['style']=='banner':story.append(Spacer(1,22))
  story+=photo(p,a,96)
  story+=[para(p['name'] or 'Dein Name',st['name'])]
  if p['title']:story.append(para(p['title'],st['role']))
  story.append(para(' · '.join(filter(None,[p['email'],p['phone']]))+'\n'+p['address'],st['small']))
  if details(p):story.append(para(details(p),st['small']))
  sections(story,p,a,st,a['design']['order'])
  def bg(c,d):
   if conf['style']=='banner':
    c.setFillColor(accent);c.rect(0,805,595,37,fill=1,stroke=0)
   elif conf['style']=='editorial':
    c.setFillColor(accent);c.rect(22,44,4,754,fill=1,stroke=0);c.setFillColor(light);c.rect(570,44,8,754,fill=1,stroke=0)
   elif conf['style']=='line':c.setStrokeColor(accent);c.setLineWidth(3);c.line(46,811,550,811)
   page_footer(c,d,p,conf['accent'])
  SimpleDocTemplate(str(path),pagesize=(595.28,841.89),leftMargin=46,rightMargin=46,topMargin=44,bottomMargin=48).build(story,onFirstPage=bg,onLaterPages=bg);return
 left=photo(p,a)
 contact='\n'.join(filter(None,[p['email'],p['phone'],p['address']]))
 for title,text in [('KONTAKT',contact),('PERSÖNLICHES',details(p)),('KENNTNISSE',p['skills']),('SPRACHEN',p['languages'])]:
  if text.strip():left.append(para(title,st['sidehead']));blocks(left,text,st['side'])
 if not left:left=[para('KONTAKT',st['sidehead'])]
 main=[para('LEBENSLAUF',st['small']),para(p['name'] or 'Dein Name',st['name'])]
 if p['title']:main.append(para(p['title'],st['role']))
 sections(main,p,a,st,[k for k in a['design']['order'] if k not in ('skills','languages')])
 def bg(c,d):
  c.setFillColor(accent if dark else light);c.setStrokeColor(accent)
  if conf['style']=='dark':c.rect(0,0,193,842,fill=1,stroke=0)
  elif conf['style']=='outline':c.roundRect(22,44,168,754,10,fill=0,stroke=1)
  elif conf['style']=='stripe':c.rect(22,44,168,754,fill=1,stroke=0);c.setFillColor(accent);c.rect(22,44,5,754,fill=1,stroke=0)
  elif conf['style']=='block':c.rect(22,44,168,754,fill=1,stroke=0);c.setFillColor(accent);c.rect(22,797,535,12,fill=1,stroke=0)
  else:c.roundRect(22,44,168,754,12,fill=1,stroke=0);c.setFillColor(accent);c.roundRect(22,804,168,8,4,fill=1,stroke=0)
  c.setStrokeColor(light);c.line(216,44,557,44);page_footer(c,d,p,conf['accent'])
 with tempfile.TemporaryDirectory() as td:
  for name,story,x,width,fn in [('left',left,34,144,bg),('right',main,210,353,lambda c,d:None)]:
   doc=BaseDocTemplate(str(Path(td)/(name+'.pdf')),pagesize=(595.28,841.89));doc.addPageTemplates(PageTemplate(id='body',frames=[Frame(x,61,width,724,leftPadding=6,rightPadding=6,topPadding=6,bottomPadding=6)],onPage=fn));doc.build(story)
  l=PdfReader(Path(td)/'left.pdf');r=PdfReader(Path(td)/'right.pdf');w=PdfWriter()
  for i in range(max(len(l.pages),len(r.pages))):
   if i<len(l.pages):page=l.pages[i]
   else:
    from reportlab.pdfgen import canvas
    buf=BytesIO();c=canvas.Canvas(buf,pagesize=(595.28,841.89));bg(c,type('Page',(),{'page':i+1})());c.save();buf.seek(0);page=PdfReader(buf).pages[0]
   if i<len(r.pages):page.merge_page(r.pages[i])
   w.add_page(page)
  w.write(str(path));w.close()

def cover_pdf(p,a,path):
 st=styles(a);accent=HexColor(settings(a)['accent']);story=[Spacer(1,52),para('BEWERBUNG',st['small']),para(a['position'] or 'Deine Position',st['name']),para(a['company'],st['role']),Spacer(1,24)]+photo(p,a,142)+[Spacer(1,20),para(p['name'] or 'Dein Name',st['name']),para(' · '.join(filter(None,[p['email'],p['phone']]))+'\n'+p['address'],st['body'])]
 def bg(c,d):c.setFillColor(accent);c.rect(0,0,15,842,fill=1,stroke=0);c.setStrokeColor(accent);c.line(48,810,547,810)
 SimpleDocTemplate(str(path),pagesize=(595.28,841.89),leftMargin=52,rightMargin=52,topMargin=48,bottomMargin=48).build(story,onFirstPage=bg,onLaterPages=bg)

def make_pdf(s,a,path,kind='all',attachments=True):
 if kind not in ('all','letter','cv','cover'):raise ValueError('Unbekanntes Dokumentformat.')
 with LOCK:
  p=s['profile'];materialize(p,a);fonts()
  with tempfile.TemporaryDirectory() as td:
   files=[]
   # Cover is optional; it precedes the letter, CV and attachments.
   for key,include,fn in [('cover',kind=='cover' or kind=='all' and a['design']['cover'],cover_pdf),('letter',kind in ('all','letter'),letter_pdf),('cv',kind in ('all','cv'),cv_pdf)]:
    if include:
     file=Path(td)/(key+'.pdf');fn(cv_profile(p,a) if key=='cv' else p,a,file);files.append(file)
   if kind=='all' and attachments:
    for i,rel in enumerate(a['attachments']):
     file=Path(td)/('attachment-'+str(i)+'.pdf');attachment_pdf(a,rel,file);files.append(file)
   writer=PdfWriter()
   for f in files:writer.append(str(f))
   writer.add_metadata({'/Title':('Lebenslauf' if kind=='cv' else 'Bewerbung')+' – '+p['name'],'/Author':p['name']});writer.write(str(path));writer.close()
