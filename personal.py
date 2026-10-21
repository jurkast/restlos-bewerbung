"""Optional CV details and local signature images."""
from datetime import date
from io import BytesIO
FIELDS={'birthDate':'Geburtsdatum','birthPlace':'Geburtsort','maritalStatus':'Familienstand','nationality':'Staatsangehörigkeit'}
def details(p):
 rows=[]
 for key,label in FIELDS.items():
  value=p.get(key,'').strip()
  if key=='birthDate' and value:value=date.fromisoformat(value).strftime('%d.%m.%Y')
  if value:rows.append(label+': '+value)
 return '\n'.join(rows)
def signature_image(p,a=None):
 from storage import resolve
 from PIL import Image,ImageOps
 with Image.open(resolve(p['signature'])) as original:
  if original.width*original.height>30000000:raise ValueError('Unterschrift: Bild ist zu groß.')
  im=ImageOps.exif_transpose(original).convert('RGBA');im.thumbnail((1200,600))
  out=BytesIO();im.save(out,format='PNG');out.seek(0)
  width=min(150,45*im.width/im.height);height=width*im.height/im.width
  scale=a.get('design',{}).get('signatureScale',100)/100 if a else 1
  return out,width*scale,height*scale


def save_created_signature(s,encoded):
 import base64,binascii,tempfile
 from pathlib import Path
 from PIL import Image
 from storage import document_copy
 prefix='data:image/png;base64,'
 if not isinstance(encoded,str) or not encoded.startswith(prefix) or len(encoded)>4000000:raise ValueError('Ungültiges Unterschriftbild.')
 try:raw=base64.b64decode(encoded[len(prefix):],validate=True)
 except (ValueError,binascii.Error):raise ValueError('Ungültige Bilddaten.')
 with Image.open(BytesIO(raw)) as source:
  if source.format!='PNG' or source.width>2400 or source.height>1000:raise ValueError('Unterschriftbild ist zu groß oder hat ein falsches Format.')
  im=source.convert('RGBA');bounds=im.getchannel('A').getbbox()
  if not bounds:raise ValueError('Bitte zuerst eine Unterschrift eingeben oder zeichnen.')
  im=im.crop(bounds)
  from PIL import ImageOps
  im=ImageOps.expand(im,border=10,fill=(255,255,255,0))
  with tempfile.TemporaryDirectory(prefix='restlos-signature-') as td:
   file=Path(td)/'Unterschrift.png';im.save(file)
   document=document_copy(s,file,'Sonstiges')
 s['profile']['signature']=document['path']
 return document
