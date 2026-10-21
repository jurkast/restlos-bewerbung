"""Local OCR. Originals are never uploaded or modified."""
import shutil,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageOps

def recognize_image(source):
 executable=shutil.which('tesseract')
 if not executable:raise ValueError('Texterkennung fehlt. Bitte Restlos über das Installationspaket installieren; es ergänzt Tesseract und das deutsche Wörterbuch.')
 with tempfile.TemporaryDirectory(prefix='restlos-ocr-') as td:
  dest=Path(td)/'image.png'
  with Image.open(source) as im:
   if im.width*im.height>40000000:raise ValueError('Das Bild ist zu groß für die Texterkennung (maximal 40 Megapixel).')
   ImageOps.exif_transpose(im).convert('RGB').save(dest)
  result=subprocess.run([executable,str(dest),'stdout','-l','deu+eng','--psm','3'],capture_output=True,text=True,timeout=90)
  if result.returncode:raise ValueError('Texterkennung fehlgeschlagen. Prüfe, ob die deutschen und englischen Tesseract-Sprachdaten installiert sind.')
  return result.stdout.strip()

def recognize_page(path,page):
 with tempfile.TemporaryDirectory(prefix='restlos-page-') as td:
  prefix=Path(td)/'scan'
  result=subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-scale-to','3000','-png',str(path),str(prefix)],capture_output=True,timeout=45)
  if result.returncode:raise ValueError('Die PDF-Seite konnte nicht für die Texterkennung gelesen werden.')
  return recognize_image(prefix.with_suffix('.png'))
