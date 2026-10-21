import os,sys,tempfile,json
from pathlib import Path
work=Path(tempfile.mkdtemp(prefix='restlos09-test-'))
os.environ['RESTLOS_DATA_DIR']=str(work/'data');os.environ['RESTLOS_UPDATE_DIR']=str(work/'updates');os.environ['RESTLOS_LEGACY_DIR']=str(work/'none')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app,storage,updates
updates.save_config('jurkast/restlos-bewerbung',False)
s=storage.initial();s['profile']['name']='Mara Weiß';storage.persist(s)
from PySide6.QtWidgets import QMainWindow,QApplication,QFileDialog
from PySide6.QtCore import QTimer
from PIL import Image,ImageDraw
im=Image.new('RGBA',(300,90));ImageDraw.Draw(im).line([(10,60),(40,10),(60,70),(240,40)],fill='black',width=4);im.save(work/'upload.png')
QFileDialog.getOpenFileName=staticmethod(lambda *a:(str(work/'upload.png'),''))
original=QMainWindow.show;results=[]
def show(w):
 original(w);pg=w.centralWidget().page()
 def js(code):pg.runJavaScript(code)
 QTimer.singleShot(1500,lambda:js("page='editor';step='text';render();openSignatureEditor();"))
 def typed():
  pg.runJavaScript("JSON.stringify({fonts:signatureEditor.ready,enabled:!$('signatureInsert').disabled,modes:document.querySelectorAll('#signatureTabs button').length})",lambda v:results.append(json.loads(v)))
  pg.runJavaScript("(()=>{let c=signatureEditor,images=[];for(let i=0;i<3;i++){c.font=i;drawSignature();images.push($('signatureCanvas').toDataURL())}c.name=' ';drawSignature();let empty=$('signatureInsert').disabled;closeSignatureEditor();let cancelled=!state.profile.signature;openSignatureEditor();return JSON.stringify({distinct:new Set(images).size,empty,cancelled});})()",lambda v:results.append(json.loads(v)))
  w.grab().save(str(work/'typed.png'));js("signatureEditor.font=1;setSignatureColor('#214caa');insertSignature();")
 QTimer.singleShot(3200,typed)
 def drawn():
  pg.runJavaScript("JSON.stringify({saved:!!state.profile.signature,closed:!$('signatureEditor'),preview:!!signaturePreview})",lambda v:results.append(json.loads(v)))
  js("openSignatureEditor();signatureMode('draw');window.blankDisabled=$('signatureInsert').disabled;let c=$('signatureCanvas'),r=c.getBoundingClientRect();c.dispatchEvent(new PointerEvent('pointerdown',{pointerId:1,button:0,clientX:r.left+20,clientY:r.top+80}));c.dispatchEvent(new PointerEvent('pointermove',{pointerId:1,clientX:r.left+80,clientY:r.top+20}));c.dispatchEvent(new PointerEvent('pointerup',{pointerId:1,clientX:r.left+80,clientY:r.top+20}));")
 # Synthetic pointer capture may fail without a physical pointer: test helper supplies valid capture semantics.
 QTimer.singleShot(4500,lambda:js("HTMLCanvasElement.prototype.setPointerCapture=function(){}"))
 QTimer.singleShot(4800,drawn)
 def checks():
  pg.runJavaScript("JSON.stringify({blank:window.blankDisabled,strokes:signatureEditor.strokes.length,enabled:!$('signatureInsert').disabled})",lambda v:results.append(json.loads(v)))
  js("signatureEditor.strokes.pop();drawSignature();window.undoEmpty=$('signatureInsert').disabled;signatureEditor.strokes=[[[30,200],[80,40],[100,220],[500,90]]];drawSignature();insertSignature();")
 QTimer.singleShot(5800,checks)
 def upload():
  pg.runJavaScript("JSON.stringify({undo:window.undoEmpty,count:activeProfile().documents.length})",lambda v:results.append(json.loads(v)))
  js("openSignatureEditor();signatureMode('upload');uploadSignature();")
 QTimer.singleShot(7300,upload)
 def finish():
  pg.runJavaScript("JSON.stringify({count:activeProfile().documents.length,preview:!!signaturePreview,closed:!$('signatureEditor')})",lambda v:results.append(json.loads(v)))
 QTimer.singleShot(9000,finish);QTimer.singleShot(9800,QApplication.instance().quit)
QMainWindow.show=show;app.launch()
print(results)
assert results[0]=={'fonts':True,'enabled':True,'modes':3}
assert results.pop(1)=={'distinct':3,'empty':True,'cancelled':True}
assert results[1]=={'saved':True,'closed':True,'preview':True}
assert results[2]=={'blank':True,'strokes':1,'enabled':True}
assert results[3]=={'undo':True,'count':2}
assert results[4]=={'count':3,'preview':True,'closed':True}
s=storage.load();a=s['applications'][0]
from pdf_export import make_pdf
from word_export import make_docx
from pypdf import PdfReader
from docx import Document
for i,d in enumerate(s['profiles'][0]['documents']):
 s['profile']['signature']=d['path'];make_pdf(s,a,work/f'signature-{i}.pdf',kind='letter',attachments=False);make_docx(s,a,work/f'signature-{i}.docx',kind='letter')
 assert sum(len(p.images) for p in PdfReader(work/f'signature-{i}.pdf').pages)==1
 assert len(Document(work/f'signature-{i}.docx').inline_shapes)==1
from personal import save_created_signature
import base64,io
im=Image.new('RGBA',(20,20));b=io.BytesIO();im.save(b,format='PNG')
for data in ('broken','data:image/png;base64,!!!','data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()):
 try:save_created_signature(s,data);raise AssertionError('Invalid input accepted')
 except (ValueError,OSError):pass
print('PASS: drei Modi, Schriftladen, Zeichnen, Rückgängig, Leerschutz, Persistenz, Upload, PDF/Word und ungültige Eingaben')
print(work)
