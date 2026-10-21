"""Canonical conversion of form data into document text; legacy text stays intact."""
SECTIONS=('experience','education','skills','languages')
def ensure(p,a=None):
 f=p.setdefault('form',{})
 f.setdefault('contactMode','form' if not p.get('address','').strip() else 'text')
 for k in ('street','postcode','city','country'):f.setdefault(k,'')
 for key in SECTIONS:f.setdefault(key,{'mode':'form' if not p.get(key,'').strip() else 'text','rows':[]})
 for k in ('summary','projects','hobbies','photo','birthDate','birthPlace','maritalStatus','nationality','signature'):p.setdefault(k,'')
 p.setdefault('photoSettings',{'zoom':1,'x':0.5,'y':0.5,'shape':'portrait'})
 if a is not None:
  a.setdefault('tracking',{'deadline':'','followup':'','sent':'','notes':''})
  af=a.setdefault('form',{})
  af.setdefault('recipientMode','form' if not a.get('recipient','').strip() else 'text')
  af.setdefault('letterMode','form' if not a.get('letter','').strip() else 'text')
  for k in ('contact','street','postcode','city','fit','availability'):af.setdefault(k,'')
  af.setdefault('closing','Über die Gelegenheit zu einem persönlichen Gespräch freue ich mich.')
  a.setdefault('design',{'accent':'','font':'Sans','size':10,'photo':True,'cover':False,'order':['summary','experience','education','projects','skills','languages','hobbies']})
  a['design'].setdefault('signature',True)
  a['design'].setdefault('signatureScale',100)
  # 0.11: enclosure list, place/date/signature below the CV, DIN 5008 letter layout.
  a['design'].setdefault('attachmentList',True)
  a['design'].setdefault('cvSignature',False)
  a['design'].setdefault('letterLayout','standard')
  af.setdefault('attachmentText','')
  # Existing own salutations stay; the neutral default follows the contact person.
  af.setdefault('salutationMode','auto' if a.get('salutation','').strip() in ('','Sehr geehrte Damen und Herren,') else 'text')
 return f

def date_text(value):
 if not value:return ''
 parts=value.split('-')
 return parts[1]+'/'+parts[0] if len(parts)==2 and len(parts[0])==4 else value

def materialize(p,a=None):
 f=ensure(p,a)
 if f['contactMode']=='form':p['address']='\n'.join(x for x in [f['street'].strip(),' '.join(x for x in [f['postcode'].strip(),f['city'].strip()] if x),f['country'].strip()] if x)
 for key in SECTIONS:
  section=f[key]
  if section['mode']!='form':continue
  rows=[]
  for row in section['rows']:
   if key in ('experience','education'):
    period=' – '.join(x for x in [date_text(row.get('start','')),'heute' if row.get('current') else date_text(row.get('end',''))] if x)
    title=' · '.join(x.strip() for x in [period,row.get('title',''),row.get('organization',''),row.get('city','')] if x.strip())
    value='\n'.join(x for x in [title,row.get('details','').strip()] if x)
   else:value=' – '.join(x.strip() for x in [row.get('name',''),row.get('level','')] if x.strip())
   if value:rows.append(value)
  p[key]=('\n\n' if key in ('experience','education') else '\n').join(rows)
 if a is not None:
  af=a['form']
  if af['recipientMode']=='form':a['recipient']='\n'.join(x.strip() for x in [a['company'],af['contact'],af['street'],' '.join(x for x in [af['postcode'],af['city']] if x)] if x.strip())
  if af.get('salutationMode')=='auto':
   from letters import salutation_for,contact_person
   a['salutation']=salutation_for(contact_person(a))
  if af['letterMode']=='form':a['letter']='\n\n'.join(x.strip() for x in [a['motivation'],a['evidence'],af['fit'],af['availability'],af['closing']] if x.strip())
 return p

def validate_forms(p,a=None):
 f=ensure(p,a)
 from personal import FIELDS
 from datetime import date
 if any(not isinstance(p[k],str) for k in (*FIELDS,'signature')):raise ValueError('Ungültige persönliche Angaben.')
 if p['birthDate']:
  try:birth=date.fromisoformat(p['birthDate'])
  except ValueError:raise ValueError('Bitte ein gültiges Geburtsdatum eingeben.')
  if birth>date.today():raise ValueError('Das Geburtsdatum darf nicht in der Zukunft liegen.')
 if a is not None and (type(a['design']['signatureScale']) not in (int,float) or not 25<=a['design']['signatureScale']<=150):raise ValueError('Die Unterschriftgröße muss zwischen 25 und 150 Prozent liegen.')
 if a is not None and not isinstance(a['design']['signature'],bool):raise ValueError('Ungültige Unterschriftoption.')
 if f['contactMode'] not in ('form','text') or any(not isinstance(f[k],str) for k in ('street','postcode','city','country')):raise ValueError('Ungültige Kontaktfelder.')
 for key in SECTIONS:
  sec=f[key]
  if not isinstance(sec,dict) or sec.get('mode') not in ('form','text') or not isinstance(sec.get('rows'),list):raise ValueError('Ungültige Formulareinträge.')
  for row in sec['rows']:
   if not isinstance(row,dict) or any(not isinstance(v,bool if k=='current' else str) for k,v in row.items()):raise ValueError('Ungültiger Eintrag.')
 settings=p['photoSettings']
 if not isinstance(p['photo'],str) or not isinstance(settings,dict):raise ValueError('Ungültiges Foto.')
 for key,lo,hi in [('zoom',1,3),('x',0,1),('y',0,1)]:
  value=settings.get(key)
  if isinstance(value,bool) or not isinstance(value,(int,float)) or not lo<=value<=hi:raise ValueError('Ungültiger Fotoausschnitt.')
 if settings.get('shape') not in ('portrait','square','round'):raise ValueError('Ungültige Fotoform.')
 if a is not None:
  from studio import validate_studio
  validate_studio(p,a)
  tracking=a['tracking']
  if not isinstance(tracking,dict) or any(not isinstance(tracking.get(k),str) for k in ('deadline','followup','sent','notes')):raise ValueError('Ungültige Bewerbungsplanung.')
  from datetime import date
  for key in ('deadline','followup','sent'):
   if tracking[key]:
    try:date.fromisoformat(tracking[key])
    except ValueError:raise ValueError('Bitte ein gültiges Datum für die Bewerbungsplanung eingeben.')
  af=a['form'];d=a['design']
  if af.get('recipientMode') not in ('form','text') or af.get('letterMode') not in ('form','text'):raise ValueError('Ungültiger Eingabemodus.')
  if any(not isinstance(af.get(k),str) for k in ('contact','street','postcode','city','fit','availability','closing','attachmentText')):raise ValueError('Ungültige Anschreibenfelder.')
  if af.get('salutationMode') not in ('auto','text'):raise ValueError('Ungültiger Anredemodus.')
  if any(not isinstance(d.get(k),bool) for k in ('attachmentList','cvSignature')):raise ValueError('Ungültige Dokumentoption.')
  if d.get('letterLayout') not in ('standard','din5008'):raise ValueError('Ungültiges Briefformat.')
  import re
  if d.get('accent') and not re.fullmatch(r'#[0-9a-fA-F]{6}',d['accent']):raise ValueError('Ungültige Farbe.')
  if d.get('font') not in ('Sans','Serif') or d.get('size') not in (9,10,11):raise ValueError('Ungültige Schrift.')
  if not isinstance(d.get('photo'),bool) or not isinstance(d.get('cover'),bool):raise ValueError('Ungültige Dokumentoption.')
  order=d.get('order',[])
  if not isinstance(order,list) or set(order)!=set(['summary','experience','education','projects','skills','languages','hobbies']) or len(order)!=7:raise ValueError('Ungültige Abschnittsreihenfolge.')
