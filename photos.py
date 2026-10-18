from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw
from storage import resolve

def cropped(profile):
 path=resolve(profile['photo'])
 with Image.open(path) as source:
  source.load();im=ImageOps.exif_transpose(source).convert('RGB')
 settings=profile.get('photoSettings',{});shape=settings.get('shape','portrait');ratio=0.8 if shape=='portrait' else 1
 w,h=im.size;zoom=float(settings.get('zoom',1));cw=min(w,h*ratio)/zoom;ch=cw/ratio
 left=(w-cw)*float(settings.get('x',.5));top=(h-ch)*float(settings.get('y',.5))
 im=im.crop((round(left),round(top),round(left+cw),round(top+ch))).resize((640,800) if shape=='portrait' else (640,640),Image.Resampling.LANCZOS)
 if shape=='round':
  im=im.convert('RGBA');mask=Image.new('L',im.size,0);ImageDraw.Draw(mask).ellipse((0,0,im.width-1,im.height-1),fill=255);im.putalpha(mask)
 data=BytesIO();im.save(data,format='PNG');data.seek(0);return data
