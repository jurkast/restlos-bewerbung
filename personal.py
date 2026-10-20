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
def signature_image(p):
 from storage import resolve
 from PIL import Image,ImageOps
 with Image.open(resolve(p['signature'])) as original:
  if original.width*original.height>30000000:raise ValueError('Unterschrift: Bild ist zu groß.')
  im=ImageOps.exif_transpose(original).convert('RGBA');im.thumbnail((1200,600))
  out=BytesIO();im.save(out,format='PNG');out.seek(0)
  width=min(150,45*im.width/im.height);height=width*im.height/im.width
  return out,width,height
