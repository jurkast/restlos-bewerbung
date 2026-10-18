#!/usr/bin/python3
import sys,os,json,tempfile,subprocess,base64,uuid,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'lib'))
from storage import *
from pdf_export import make_pdf
from importer import extract,suggest
from spelling import Speller
from pypdf import PdfReader

def launch():
 from concurrent.futures import ThreadPoolExecutor
 from PySide6.QtWidgets import QApplication,QMainWindow,QFileDialog,QMessageBox
 from PySide6.QtWebEngineWidgets import QWebEngineView
 from PySide6.QtWebEngineCore import QWebEnginePage,QWebEngineScript,QWebEngineUrlRequestInterceptor
 from PySide6.QtCore import QUrl,QTimer,QObject,Signal,QLockFile
 from PySide6.QtGui import QIcon,QDesktopServices
 qapp=QApplication(sys.argv);qapp.setApplicationName('Restlos Bewerbung');qapp.setDesktopFileName('restlos-bewerbung');qapp.setWindowIcon(QIcon(str(ROOT/'icon.svg')))
 private_dir(DATA);lock=QLockFile(str(DATA/'.restlos.lock'))
 if not lock.tryLock(100):
  QMessageBox.information(None,'Restlos Bewerbung','Dieses Datenverzeichnis ist bereits in einem Restlos-Fenster geöffnet.');return
 class Result(QObject): ready=Signal(dict)
 class LocalOnly(QWebEngineUrlRequestInterceptor):
  def interceptRequest(self,info):
   if info.requestUrl().scheme() not in ('file','data','about','qrc'):info.block(True)
 class Page(QWebEnginePage):
  def javaScriptConsoleMessage(self,level,message,line,source):
   if message.startswith('RESTLOS:'):self.owner.message(message[8:])
  def acceptNavigationRequest(self,url,kind,is_main):
   return (url.isLocalFile() and Path(url.toLocalFile()).resolve().is_relative_to(ROOT)) or url.toString()=='about:blank'
 class Window(QMainWindow):
  def closeEvent(self,event):
   if getattr(self,'closing',False):event.accept();return
   event.ignore()
   self.owner.web.page().runJavaScript("bridge('save_and_close');")
 class App:
  def __init__(self):
   self.updatepool=ThreadPoolExecutor(max_workers=1);self.updateBusy=False;self.aipool=ThreadPoolExecutor(max_workers=1);self.aiBusy=False;self.pool=ThreadPoolExecutor(max_workers=1);self.spellpool=ThreadPoolExecutor(max_workers=1);self.result=Result();self.result.ready.connect(self.emit);self.speller=None
   self.win=Window();self.win.owner=self;self.win.setWindowTitle('Restlos Bewerbung');self.win.resize(1460,950)
   self.web=QWebEngineView();page=Page(self.web);page.owner=self;self.web.setPage(page)
   self.interceptor=LocalOnly(page);page.profile().setUrlRequestInterceptor(self.interceptor)
   script=QWebEngineScript();script.setInjectionPoint(QWebEngineScript.DocumentCreation);script.setWorldId(QWebEngineScript.MainWorld);script.setSourceCode("window.atelierSend=function(message){console.log('RESTLOS:'+message);};")
   page.scripts().insert(script);self.win.setCentralWidget(self.web);self.web.setUrl(QUrl.fromLocalFile(str(ROOT/'index.html')));self.win.show()
  def emit(self,data):
   if data.get('type')=='updates':self.updateBusy=False
   if data.get('type') in ('ai_result','ai_error') and not data.get('busy'):self.aiBusy=False
   self.web.page().runJavaScript('receive('+json.dumps(data,ensure_ascii=False)+')')
  def state(self,s):
   from photos import cropped
   photo=s['profile'].get('photo')
   self.emit({'type':'load','data':s,'root':str(DATA),'folder':str(profile_dir(selected(s))),'photoPreview':base64.b64encode(cropped(s['profile']).getvalue()).decode() if photo else ''})
  def notice(self,text):self.emit({'type':'notice','text':text})
  def task(self,fn,pool=None):
   def run():
    try:self.result.ready.emit(fn())
    except Exception as e:self.result.ready.emit({'type':'error','text':str(e)})
   (pool or self.pool).submit(run)
  def check_updates(self):
   if self.updateBusy:return
   self.updateBusy=True
   self.emit({'type':'update_progress','text':'Updates werden geprüft und gegebenenfalls im Hintergrund vorbereitet …'})
   def work():
    from updates import check
    from reliability import snapshot_before_update
    try:return {'type':'updates',**check(snapshot_before_update)}
    except Exception as e:return {'type':'updates','message':str(e),'ok':False}
   self.task(work,self.updatepool)
  def message(self,message):
   try:
    req=json.loads(message);action=req['action']
    if action=='load':
     s=load();persist(s,generate=False);self.state(s);return
    s=absorb(req['data']);p=selected(s);a=next((x for x in s['applications'] if x['id']==req['id']),s['applications'][0])
    if action=='startup_ready':
     from updates import startup_ready,config
     startup_ready()
     if not hasattr(self,'updateTimer'):
      self.updateTimer=QTimer(self.win);self.updateTimer.setInterval(6*60*60*1000);self.updateTimer.timeout.connect(lambda:self.check_updates() if config()['automatic'] else None);self.updateTimer.start()
      if config()['automatic']:QTimer.singleShot(3000,self.check_updates)
     return
    if action=='update_status':
     from updates import status
     from reliability import readiness
     self.emit({'type':'update_status',**status(),'readiness':readiness(s)});return
    if action=='update_settings':
     from updates import save_config,status
     save_config(req.get('repository','').strip(),req.get('automatic',True));self.emit({'type':'update_status',**status()});self.notice('Update-Einstellungen gespeichert.');return
    if action=='update_check':self.check_updates();return
    if action=='update_rollback':
     from updates import rollback,status
     rollback();self.emit({'type':'update_status',**status()});return
    if action=='save_and_close':
     persist(s,a['id']);self.win.closing=True;self.win.close();return
    if action=='ai_models':
     def status():
      try:
       from assistant_local import models
       return {'type':'ai_models','models':models()}
      except Exception as e:return {'type':'ai_models','models':[],'error':str(e)}
     self.task(status,self.aipool);return
    if action=='ai_generate':
     if self.aiBusy:self.emit({'type':'ai_error','text':'Es läuft bereits eine Texterstellung. Bitte den Abschluss abwarten.','busy':True,'requestId':req.get('requestId')});return
     self.aiBusy=True
     def generate_text():
      context={'profileId':p['id'],'applicationId':a['id'],'requestId':req.get('requestId')}
      try:
       from assistant_local import generate
       return {'type':'ai_result',**context,**generate(s,a,req.get('model',''))}
      except Exception as e:return {'type':'ai_error',**context,'text':str(e)}
     self.task(generate_text,self.aipool);return
    if action=='export_prompt':
     from assistant_local import prompt
     text=prompt(s,a);persist(s,a['id']);dest=application_dir(p,a)/'Exporte'/('Texthilfe-Prompt_'+uuid.uuid4().hex[:8]+'.txt');write(dest,text);self.notice('Prompt lokal gespeichert: '+str(dest));return
    if action=='photo':
     source,_=QFileDialog.getOpenFileName(self.win,'Bewerbungsfoto auswählen',str(Path.home()),'Bilder (*.jpg *.jpeg *.png *.webp)')
     if not source:return
     from PIL import Image
     if Path(source).stat().st_size>20*1024**2:raise ValueError('Bitte ein Bild unter 20 MB verwenden.')
     with Image.open(source) as im:
      if im.width*im.height>30000000:raise ValueError('Bitte ein Bild mit höchstens 30 Megapixeln verwenden.')
      im.load()
     d=document_copy(s,source,'Fotos');s['profile']['photo']=d['path'];s['profile']['photoSettings']={'zoom':1,'x':0.5,'y':0.5,'shape':'portrait'};persist(s,a['id']);self.state(s);return
    if action=='photo_preview':
     from photos import cropped
     self.emit({'type':'photo_preview','profileId':s['selectedProfile'],'image':base64.b64encode(cropped(s['profile']).getvalue()).decode() if s['profile']['photo'] else ''});return
    if action=='save':persist(s,a['id']);self.emit({'type':'saved'});return
    if action=='spell':
     def check():
      if self.speller is None:self.speller=Speller()
      ignore=p['dictionary']+p['profile']['name'].split()+a['company'].split()
      return {'type':'spell','profileId':p['id'],'field':req['field'],'text':req['text'],'issues':self.speller.check(req['text'],ignore)}
     self.task(check,self.spellpool);return
    if action=='preview':
     def preview():
      with tempfile.TemporaryDirectory() as td:
       path=Path(td)/'preview.pdf';make_pdf(s,a,path,req.get('kind','all'),False)
       count=len(PdfReader(path).pages)
       proc=subprocess.run(['pdftoppm','-f','1','-l','12','-scale-to','1050','-png',str(path),str(Path(td)/'page')],capture_output=True,timeout=45)
       if proc.returncode:raise ValueError('PDF-Vorschau konnte nicht gerendert werden.')
       pages=sorted(Path(td).glob('page-*.png'),key=lambda f:int(f.stem.split('-')[-1]))
       return {'type':'preview','token':req.get('token'),'count':count,'pages':[base64.b64encode(f.read_bytes()).decode() for f in pages]}
     self.task(preview);return
    if action=='new_profile':
     persist(s,generate=False);label=req.get('label','Neues Profil').strip() or 'Neues Profil';np=new_profile(label);s['profiles'].append(np);activate(s,np['id']);persist(s);self.state(s);return
    if action=='open_folder':
     persist(s,a['id']);dest=application_dir(p,a) if req.get('application') else profile_dir(p);QDesktopServices.openUrl(QUrl.fromLocalFile(str(dest)));return
    if action=='duplicate_application':
     import copy
     persist(s,a['id']);clone=copy.deepcopy(a);clone['id']=ident();clone.pop('folder',None);clone.pop('aiDraft',None);clone.pop('letterHistory',None);clone['tracking']={'deadline':'','followup':'','sent':'','notes':''};clone['status']='Entwurf';clone['company']=(clone['company']+' – Kopie').strip();s['applications'].append(clone);persist(s,clone['id']);self.state(s);self.notice('Kopie angelegt. Firma und Empfänger vor dem Versand anpassen.');return
    if action in ('export_word','export_mail'):
     persist(s,a['id']);folder=application_dir(p,a)/'Exporte';stamp=__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+'_'+uuid.uuid4().hex[:4]
     if action=='export_word':
      from word_export import make_docx
      kind=req.get('kind','cv');dest=folder/({'cv':'Lebenslauf','letter':'Anschreiben','cover':'Deckblatt'}[kind]+'_'+stamp+'.docx');make_docx(s,a,dest,kind)
     else:
      from delivery import mail_draft
      pdf=folder/('Bewerbung_'+stamp+'.pdf');make_pdf(s,a,pdf);pdf.chmod(0o600);dest=folder/('E-Mail-Entwurf_'+stamp+'.eml');mail_draft(dest,pdf,s,a)
     dest.chmod(0o600);self.notice('Gespeichert: '+str(dest)+('\nEs wurde keine E-Mail versendet.' if action=='export_mail' else '\nWord-Ausgabe als bearbeitbare einspaltige Fassung.'));return
    if action=='export':
     persist(s,a['id']);kind=req.get('kind','all');prefix={'all':'Bewerbungsmappe','cv':'Lebenslauf','letter':'Anschreiben','cover':'Deckblatt'}[kind]
     timestamp=__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S');dest=application_dir(p,a)/'Exporte'/(prefix+'_'+timestamp+'_'+uuid.uuid4().hex[:4]+'.pdf')
     make_pdf(s,a,dest,kind);dest.chmod(0o600);self.emit(__import__('delivery').pdf_report(dest,s,a));return
    if action in ('attach','import'):
     category=req.get('category','Zeugnisse' if action=='attach' else 'Lebenslauf')
     if category not in CATEGORIES:raise ValueError('Unbekannte Kategorie.')
     files,_=QFileDialog.getOpenFileNames(self.win,'Dokumente hinzufügen',str(Path.home()),'Dokumente (*.pdf *.docx *.odt *.txt *.png *.jpg *.jpeg *.webp *.tif *.tiff);;Alle Dateien (*)')
     if not files:return
     imported=[]
     for f in files:
      if action=='attach' and Path(f).suffix.lower()!='.pdf':raise ValueError('Zum Zusammenführen der Mappe bitte PDF-Anlagen wählen. Andere Formate können in der Dokumentablage gespeichert werden.')
      if Path(f).suffix.lower()=='.pdf':
       r=PdfReader(f)
       if r.is_encrypted:raise ValueError('Bitte PDFs ohne Passwort wählen.')
     for f in files:
      d=document_copy(s,f,category);imported.append(d)
      if action=='attach':a['attachments'].append(d['path'])
     persist(s,a['id']);self.state(s)
     if req.get('extract') and imported:
      d=imported[0]
      def imported_text():return {'type':'import','document':d,'profileId':p['id'],'applicationId':a['id'],**suggest(extract(resolve(d['path']),lambda text:self.result.ready.emit({'type':'progress','text':text})),category)}
      self.task(imported_text)
     else:self.notice(str(len(imported))+' Dokument(e) automatisch im Profilordner abgelegt.')
     return
    if action=='analyze_document':
     d=next(d for d in p['documents'] if d['id']==req['document'])
     self.task(lambda:{'type':'import','document':d,'profileId':p['id'],'applicationId':a['id'],**suggest(extract(resolve(d['path']),lambda text:self.result.ready.emit({'type':'progress','text':text})),d['category'])});return
    if action=='open_document':
     d=next(d for d in p['documents'] if d['id']==req['document']);QDesktopServices.openUrl(QUrl.fromLocalFile(str(resolve(d['path']))));return
    if action=='backup':
     dest,_=QFileDialog.getSaveFileName(self.win,'Vollständige Sicherung',str(Path.home()/'Restlos-Bewerbung-Sicherung.zip'),'ZIP-Dateien (*.zip)')
     if dest:backup(s,Path(dest));self.notice('Alle Profile, Dokumente und Bewerbungen wurden gesichert.')
     return
    if action=='restore':
     src,_=QFileDialog.getOpenFileName(self.win,'Sicherung wiederherstellen',str(Path.home()),'ZIP-Dateien (*.zip)')
     if src and QMessageBox.question(self.win,'Sicherung wiederherstellen','Alle Profile durch die Sicherung ersetzen? Der aktuelle Bestand wird vorher vollständig gesichert.')==QMessageBox.Yes:self.state(restore(src))
     return
   except Exception as e:
    if isinstance(locals().get('req'),dict) and req.get('action')=='ai_generate':self.emit({'type':'ai_error','text':str(e),'requestId':req.get('requestId')})
    else:self.emit({'type':'error','text':str(e)})
 instance=App();qapp.exec();instance.updatepool.shutdown(wait=True);instance.aipool.shutdown(wait=True);instance.pool.shutdown(wait=True);instance.spellpool.shutdown(wait=True)
if __name__=='__main__':launch()
