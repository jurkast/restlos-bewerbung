import os,sys,json,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
test_temp=tempfile.TemporaryDirectory(prefix='restlos-examples-')
work=Path(test_temp.name)
os.environ['RESTLOS_DATA_DIR']=str((work/'data').resolve())
os.environ['RESTLOS_LEGACY_DIR']=str((work/'none').resolve())
os.environ['RESTLOS_UPDATE_DIR']=str((work/'updates').resolve())
sys.path.insert(0,str(root))
import app,storage,updates
updates.save_config('jurkast/restlos-bewerbung',False)
s=storage.initial();storage.persist(s)
from PySide6.QtWidgets import QApplication,QMainWindow
from PySide6.QtCore import QTimer
original=QMainWindow.show;results=[]
script=r'''(()=>{let checks=[];function ok(c,label){if(!c)throw Error(label);checks.push(label)}
window.confirm=()=>true;
page='editor';step='text';render();
ok(answerExamples.length===66,'66 Beispiele');ok(new Set(answerExamples.map(x=>x.text)).size===66,'Keine doppelten Texte');
ok(document.querySelectorAll('button[onclick^="openAnswerLibrary"]').length===5,'Alle fünf Abschnitte');
openAnswerLibrary('motivation');filterAnswers('category','IT & Software');filterAnswers('situation','Quereinstieg');
ok(matchingAnswers().some(x=>x.category==='IT & Software')&&matchingAnswers().some(x=>x.situation==='Quereinstieg'),'Beruf und Situation kombinieren');
filterAnswers('search','UNAUFFINDBAR');ok(matchingAnswers().length===0&&$('answerResults').textContent.includes('Keine passenden'),'Leere Suche');
app().company='Muster & <Partner>';app().position='Fachkraft';app().motivation='Mein eigener Einstieg.';compileForms();
chooseAnswer('ex001');ok(answerContext.values.includes('Muster & <Partner>'),'Firmenname vorausgefüllt');ok($('answerApply').disabled,'Unvollständige Angaben gesperrt');
answerContext.names.forEach((n,i)=>{if(!answerContext.values[i])setAnswerValue(i,'die Planung von Terminen')});
let filled=$('answerPreview').value;ok(!$('answerApply').disabled&&!/\[[^\]]+\]/.test(filled),'Platzhalter ersetzt');
applyAnswer();ok(app().motivation==='Mein eigener Einstieg.\n\n'+filled,'Anhängen erhält Text');ok(app().letterHistory[0].motivation==='Mein eigener Einstieg.','Vorherige Fassung erhalten');
chooseAnswer('ex001');answerContext.names.forEach((n,i)=>setAnswerValue(i,'Meine Angabe'));$('answerOperation').value='replace';$('answerPreview').value='Mein neuer Einstieg.';applyAnswer();ok(app().motivation==='Mein neuer Einstieg.','Abschnitt ersetzen');
showLetterHistory();restoreLetter(0);ok(app().motivation.startsWith('Mein eigener Einstieg.\n\n'),'Verlauf wiederherstellen');
for(let key of ['evidence','fit','availability','closing']){chooseAnswer(answerExamples.find(x=>x.field===key).id);answerContext.names.forEach((n,i)=>setAnswerValue(i,'Passende Angabe'));$('answerPreview').value='Prüftext '+key;applyAnswer();ok(answerTarget(app(),key).includes('Prüftext '+key),'Zielabschnitt '+key)}
chooseAnswer('ex001');answerContext.names.forEach((n,i)=>setAnswerValue(i,'Text'));let oldProfile=state.selectedProfile;state.selectedProfile='different';applyAnswer();ok(!!$('answerFill'),'Profilwechsel blockiert');state.selectedProfile=oldProfile;
let oldCurrent=current;current='missing';applyAnswer();ok(!!$('answerFill'),'Bewerbungswechsel blockiert');current=oldCurrent;
app().motivation='Zwischenzeitlich geändert';applyAnswer();ok(app().motivation==='Zwischenzeitlich geändert','Neuere Eingabe geschützt');$('answerFill').remove();
letterMode('text');app().letter='Freier Ausgangstext';render();ok(document.querySelectorAll('button[onclick^="openAnswerLibrary"]').length===1,'Bibliothek im Freitext');
chooseAnswer(answerExamples.find(x=>x.field==='closing').id);applyAnswer();ok(app().form.letterMode==='text'&&app().letter.startsWith('Freier Ausgangstext\n\n'),'Freitext anhängen ohne Moduswechsel');
chooseAnswer(answerExamples.find(x=>x.field==='closing').id);$('answerOperation').value='replace';window.confirm=()=>false;applyAnswer();ok(app().letter.startsWith('Freier Ausgangstext'),'Ersetzen abbrechen');window.confirm=()=>true;$('answerPreview').value='Abschließender Testtext';applyAnswer();ok(app().letter==='Abschließender Testtext','Freitext ersetzen');
chooseAnswer('ex001');answerContext.names.forEach((n,i)=>setAnswerValue(i,'<img src=x onerror=alert(1)> & "Zitat"'));ok(!document.querySelector('#answerFill img'),'Angaben sicher als Text');$('answerFill').remove();
flush();answerFilters={field:'',category:'',situation:'',search:''};openAnswerLibrary('');return JSON.stringify({checks,letter:app().letter,history:app().letterHistory.length});})()'''
def show(w):
 original(w);pg=w.centralWidget().page()
 def run():
  def done(v):
   print('RESULT',v,flush=True)
   if v:results.append(json.loads(v))
   QTimer.singleShot(1200,lambda:w.grab().save(str((work/'library.png').resolve())))
  pg.runJavaScript(script,done)
 QTimer.singleShot(1800,run)
 QTimer.singleShot(6500,QApplication.instance().quit)
QMainWindow.show=show;app.launch()
assert results,'JavaScript test failed'
s=storage.load();assert s['applications'][0]['letter']=='Abschließender Testtext';assert len(s['applications'][0]['letterHistory'])>0
from pdf_export import make_pdf
from pypdf import PdfReader
pdf=(work/'letter.pdf');make_pdf(s,s['applications'][0],pdf,kind='letter',attachments=False)
assert 'Abschließender Testtext' in '\n'.join(p.extract_text() for p in PdfReader(pdf).pages)
print('PASS UI + Speicherung + PDF',len(results[0]['checks']))
