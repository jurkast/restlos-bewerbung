import os,sys,tempfile,json
from pathlib import Path
work=Path(tempfile.mkdtemp(prefix='restlos-size-'));os.environ['RESTLOS_DATA_DIR']=str(work/'data');os.environ['RESTLOS_UPDATE_DIR']=str(work/'updates');os.environ['RESTLOS_LEGACY_DIR']=str(work/'none');sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app,storage,updates
from PIL import Image,ImageDraw
im=Image.new('RGBA',(400,100));ImageDraw.Draw(im).line([(10,80),(50,10),(100,70),(380,40)],fill='black',width=4);im.save(work/'sign.png')
s=storage.initial();d=storage.document_copy(s,work/'sign.png','Sonstiges');s['profile']['signature']=d['path'];s['applications'].append(storage.new_application());storage.persist(s);updates.save_config('jurkast/restlos-bewerbung',False)
from PySide6.QtWidgets import QApplication,QMainWindow
from PySide6.QtCore import QTimer
original=QMainWindow.show;results=[]
def show(w):
 original(w);pg=w.centralWidget().page()
 def run():
  pg.runJavaScript("(()=>{page='editor';step='text';render();let slider=$('signatureScale');slider.value=65;slider.dispatchEvent(new Event('input'));let value=app().design.signatureScale;let label=$('signatureScaleValue').textContent;let first=current;current=state.applications[1].id;render();let other=Number($('signatureScale').value);current=first;render();flush();return JSON.stringify({value,label,other,restored:Number($('signatureScale').value)});})()",lambda v:results.append(json.loads(v)))
 QTimer.singleShot(1600,run);QTimer.singleShot(4200,QApplication.instance().quit)
QMainWindow.show=show;app.launch();assert results==[{'value':65,'label':'65 %','other':100,'restored':65}],results
s=storage.load();a=s['applications'][0];assert a['design']['signatureScale']==65
from personal import signature_image
from pdf_export import make_pdf
from word_export import make_docx
from docx import Document
from pypdf import PdfReader
from pypdf.generic import ContentStream
for scale in (25,65,100,150):
 a['design']['signatureScale']=scale;stream,width,height=signature_image(s['profile'],a)
 assert abs(width-150*scale/100)<.01 and abs(height-37.5*scale/100)<.01
 pdf=work/f'{scale}.pdf';make_pdf(s,a,pdf,kind='letter',attachments=False);reader=PdfReader(pdf)
 matrices=[args for page in reader.pages for args,op in ContentStream(page.get_contents(),reader).operations if op==b'cm']
 assert any(abs(float(x[0])-width)<.01 and abs(float(x[3])-height)<.01 for x in matrices)
 doc=work/f'{scale}.docx';make_docx(s,a,doc,kind='letter');shape=Document(doc).inline_shapes[0];assert abs(shape.width.pt-width)<.01 and abs(shape.height.pt-height)<.01
for bad in (0,151,True,float('nan')):
 a['design']['signatureScale']=bad
 try:storage.validate(s);raise AssertionError('Invalid scale accepted')
 except ValueError:pass
a['design'].pop('signatureScale');storage.validate(s);assert a['design']['signatureScale']==100
print('PASS: Slider, Bewerbungstrennung, Speicherung, exakte PDF-/Word-Maße bei 25/65/100/150 %, Grenzen und Altprofile')
