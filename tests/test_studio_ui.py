import os,sys,tempfile,json
from pathlib import Path
work=Path(tempfile.mkdtemp(prefix='restlos-studio-ui-'));os.environ['RESTLOS_DATA_DIR']=str(work/'data');os.environ['RESTLOS_UPDATE_DIR']=str(work/'updates');os.environ['RESTLOS_LEGACY_DIR']=str(work/'none');sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app,storage,updates
from reportlab.pdfgen import canvas
source=work/'zeugnis.pdf';c=canvas.Canvas(str(source))
for i in range(3):c.drawString(60,700,'Seite '+str(i+1));c.showPage()
c.save();s=storage.initial();s['profile']['name']='Mara Muster';s['profile']['experience']='Gemeinsame Erfahrung';s['profile']['form']['experience']['mode']='text';a=s['applications'][0];a['motivation']='Ich hoffe das ich ich helfen kann.';d=storage.document_copy(s,source,'Zeugnisse');a['attachments']=[d['path']];missing=storage.document_copy(s,source,'Zertifikate');storage.resolve(missing['path']).unlink();s['applications'].append(storage.new_application());storage.persist(s);updates.save_config('jurkast/restlos-bewerbung',False)
from PySide6.QtWidgets import QApplication,QMainWindow,QFileDialog
from PySide6.QtCore import QTimer
QFileDialog.getOpenFileName=staticmethod(lambda *args:(str(source),''))
original=QMainWindow.show;results=[]
def show(w):
 original(w);pg=w.centralWidget().page()
 def js(code):pg.runJavaScript(code)
 def collect(code):pg.runJavaScript('JSON.stringify('+code+')',lambda value:results.append(json.loads(value)))
 QTimer.singleShot(1400,lambda:js("window.confirm=()=>true;page='editor';step='cv';render();toggleOwnCV(true);$('cv-experience').value='Eigene Erfahrung';$('cv-experience').dispatchEvent(new Event('input'));"))
 QTimer.singleShot(3000,lambda:collect("{own:app().cv.experience,base:state.profile.experience,other:!!state.applications[1].cv}"))
 QTimer.singleShot(3300,lambda:js("step='anlagen';render();openAttachmentPages(0);"))
 def edit():
  collect("{count:studioPageEditor.count,thumbnails:Object.keys(studioPageEditor.images).length}")
  js("studioPageEditor.rows=[{index:2,rotation:90},{index:0,rotation:0}];saveAttachmentPages();step='check';render();bridge('export',{kind:'all'});")
 QTimer.singleShot(5500,edit)
 def check():
  collect("{gate:!!$('studioCheck'),pending:studioPending?.action,hints:$('studioCheck').textContent.includes('fehlt')}")
  js("$('studioCheck').remove();studioPending=null;openPacket();")
 QTimer.singleShot(7800,check)
 def packet():
  collect("{packet:!!document.querySelector('#studioPacket img'),navigation:$('studioPacket').textContent.includes('Seite 1 von')}")
  w.grab().save(str(work/'packet.png'));js("$('studioPacket').remove();studioPacket=null;page='documents';render();bridge('studio_audit');")
 QTimer.singleShot(10000,packet)
 def repair():
  collect("{missing:studioAudit.length,repair:!!$('studioAudit').querySelector('button')}")
  js("bridge('studio_repair',{document:studioAudit[0].id});")
 QTimer.singleShot(11300,repair)
 def text():
  collect("{repaired:studioAudit.length}");js("page='editor';step='text';render();bridge('studio_text');")
 QTimer.singleShot(13200,text)
 def advice():
  collect("{suggestions:studioText.issues.length}");js("applyTextAdvice(0);")
 QTimer.singleShot(14500,advice)
 def final():
  collect("{corrected:app().letter.includes('dass')||!app().letter.includes('ich ich'),history:app().letterHistory.length,mode:app().form.letterMode}");js("$('studioText')?.remove();step='design';render();setDesign('spacing',120);setDesign('photoScale',75);setCVBreak('experience',true);flush();")
 QTimer.singleShot(16000,final);QTimer.singleShot(18000,QApplication.instance().quit)
QMainWindow.show=show;app.launch();print(results)
assert results[0]=={'own':'Eigene Erfahrung','base':'Gemeinsame Erfahrung','other':False}
assert results[1]=={'count':3,'thumbnails':3}
assert results[2]=={'gate':True,'pending':'export','hints':True}
assert results[3]=={'packet':True,'navigation':True}
assert results[4]=={'missing':1,'repair':True} and results[5]=={'repaired':0}
assert results[6]['suggestions']>=2 and results[7]['corrected'] and results[7]['history']>=1 and results[7]['mode']=='text'
s=storage.load();assert s['applications'][0]['design']['spacing']==120 and s['applications'][0]['design']['photoScale']==75;assert s['applications'][0]['cv']['experience']=='Eigene Erfahrung';assert not list(storage.DATA.glob('Profile/*/Bewerbungen/*/Exporte/*.pdf'))
print('PASS: Alle sechs Bereiche im Desktop, Exportprüfung, echte Reparatur, Textübernahme/Verlauf, Persistenz.');print(work)
