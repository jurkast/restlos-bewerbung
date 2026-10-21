// 0.13: unsolicited applications ("Initiativbewerbung"). A tick under "Stelle" makes position,
// job ad and recipient optional: the check still points out what is missing, but as a hint.
const initiativeEnsure=ensureForms;
ensureForms=function(){initiativeEnsure();for(const a of state.applications)a.initiative??=false;};

function setInitiative(on){let a=app();a.initiative=on;changed();render();}
function initiativeBox(){
 let on=!!app().initiative;
 return `<label class="check-line" style="margin-top:0"><input type="checkbox" ${on?'checked':''} onchange="setInitiative(this.checked)"> <span><b>Initiativbewerbung</b> – ich bewerbe mich ohne konkrete Stellenausschreibung</span></label>${on?'<p class="issue good">Position, Stellenanzeige und Empfängeranschrift sind jetzt optional. Beim Prüfen weist Restlos auf fehlende Angaben nur noch hin. Der Betreff lautet „Initiativbewerbung“ oder „Initiativbewerbung als …“.</p>':''}`;
}

const initiativeBody=editorBody;
editorBody=function(){
 let html=initiativeBody(),a=app();
 if(step==='stelle'){
  html=html.replace('<p class="hint">Mit einer konkreten Stelle wird aus deinem Profil eine persönliche Bewerbung.</p>','<p class="hint">Mit einer konkreten Stelle wird aus deinem Profil eine persönliche Bewerbung.</p>'+initiativeBox());
  if(a.initiative){
   html=html.replace(field('a','position','Beworbene Position'),field('a','position','Wunschposition oder Bereich (optional)',false,'Zum Beispiel: Lager und Logistik'));
   html=html.replace('<span>Stellenanzeige</span>','<span>Stellenanzeige (bei einer Initiativbewerbung meist leer)</span>');
  }
 }
 return html;
};

// Simple checklist on "Prüfen & Export".
const initiativeChecks=checks;
checks=function(){
 let out=initiativeChecks(),a=app();
 if(!a.initiative)return out;
 return out.map(([ok,text])=>text==='Unternehmen und Position müssen ausgefüllt sein.'
  ?[true,'Initiativbewerbung: '+(a.company.trim()?'Unternehmen „'+a.company.trim()+'“':'kein Unternehmen')+(a.position.trim()?', Wunschposition „'+a.position.trim()+'“':', keine Position')+' – beides ist optional.']:[ok,text]);
};

// Example library: suggest the examples for unsolicited applications first.
const initiativeLibrary=openAnswerLibrary;
openAnswerLibrary=function(field=''){initiativeLibrary(field);if(app().initiative&&!answerFilters.situation&&answerExamples.some(x=>x.situation==='Initiativbewerbung')){filterAnswers('situation','Initiativbewerbung');if($('answerSituation'))$('answerSituation').value='Initiativbewerbung';}};

// Draft from own sentences: no position needed for unsolicited applications.
const initiativeDraft=draft;
draft=function(){
 let a=app();if(!a.initiative||a.position.trim())return initiativeDraft();
 if(!a.motivation.trim()||!a.evidence.trim()){toast('Bitte Motivation und passende Erfahrung ergänzen.');return;}
 window.proposed=a.motivation.trim()+'\n\n'+a.evidence.trim()+'\n\nGern erläutere ich Ihnen in einem persönlichen Gespräch, wie ich meine Erfahrung bei Ihnen einbringen kann.';
 $('draftArea').innerHTML='<p class="hint" style="margin-top:18px">Vorschlag ausschließlich aus deiner Motivation und Erfahrung:</p><div class="issue">'+esc(window.proposed).replace(/\n/g,'<br>')+'</div><button class="primary" onclick="acceptDraft()">Diesen Entwurf übernehmen</button>';
};

// Check before export: required items and optional hints are shown separately.
function checkIssue(x){return `<div class="issue ${x.level==='hint'?'':'warn'}">${esc(x.message)} <button onclick="jumpStudio('${x.step}','${x.field}')">Zum Abschnitt</button></div>`;}
const initiativeReceive=receive;
receive=function(msg){
 if(msg.type==='studio_check'&&msg.token===studioCheckToken&&msg.profileId===state.selectedProfile&&msg.applicationId===current){
  let must=msg.issues.filter(x=>x.level!=='hint'),hints=msg.issues.filter(x=>x.level==='hint'),a=app();
  modalBox('studioCheck',`<h2>Bewerbungscheck${a.initiative?' · Initiativbewerbung':''}</h2><p>${msg.pages!==null?`${msg.pages} Seiten · ${msg.mb} MB`:'Die vollständige Mappe konnte nicht erzeugt werden.'}</p><p class="hint">Hinweise sind keine automatische inhaltliche Freigabe. Firmennamen werden mit anderen Bewerbungen dieses Profils und der Empfängeranschrift verglichen.</p>${must.length?'<h3>Bitte prüfen</h3>'+must.map(checkIssue).join(''):'<p class="issue good">Alle notwendigen Angaben sind vorhanden.</p>'}${hints.length?'<h3>Hinweise (optional)</h3>'+hints.map(checkIssue).join(''):''}<div class="actions"><button onclick="$('studioCheck').remove();studioPending=null">Schließen</button>${studioPending?`<button class="primary" onclick="performCheckedExport()">${must.length?'Geprüft – Export fortsetzen':'Export fortsetzen'}</button>`:''}</div>`);
  return;
 }
 initiativeReceive(msg);
};
