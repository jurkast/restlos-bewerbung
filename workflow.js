// 0.12: reminders at start, export cleanup, editable e-mail text and job-ad suggestions.
// Extends existing functions like studio.js and letter-tools.js do.
let remindersShown=false,exportItems=null,jobSuggestion=null;

// ---- defaults for new fields (keep in sync with forms.py / delivery.py)
const workflowEnsure=ensureForms;
ensureForms=function(){workflowEnsure();for(const a of state.applications){a.form.mailSubject??='';a.form.mailText??='';}};
function defaultMailSubject(a){let p=(a.position||'').trim(),kind=a.initiative?'Initiativbewerbung':'Bewerbung';return p?kind+' als '+p:kind;}
function defaultMailText(a){let p=(a.position||'').trim();if(a.initiative)return 'anbei erhalten Sie meine Initiativbewerbung'+(p?' als '+p:'')+'. Ich würde mich freuen, Ihr Team zu unterstützen, und stehe Ihnen für Rückfragen gern zur Verfügung.\n\nÜber die Gelegenheit zu einem persönlichen Gespräch freue ich mich.';return 'anbei erhalten Sie meine Bewerbungsunterlagen'+(p?' für die Position als '+p:'')+'.\n\nÜber die Gelegenheit zu einem persönlichen Gespräch freue ich mich.';}

// ---- 1. reminders when the program starts
function addDays(day,n){let d=new Date(day+'T12:00:00');d.setDate(d.getDate()+n);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function reminderItems(){
 let today=localDay(),soon=addDays(today,3),items=[];
 for(const p of state.profiles)for(const a of p.applications){
  if(['Zusage','Absage'].includes(a.status))continue;let t=a.tracking||{};
  for(const [k,label] of [['deadline','Bewerbungsfrist'],['followup','Wiedervorlage']]){
   let v=t[k];if(!v||v>soon||(k==='deadline'&&a.status!=='Entwurf'))continue;
   let when=v<today?'überfällig seit '+displayDay(v):v===today?'heute':'am '+displayDay(v);
   items.push({profile:p.id,profileLabel:p.label,app:a.id,title:a.position||'Neue Bewerbung',company:a.company,label,when,overdue:v<today,day:v});
  }
 }
 return items.sort((x,y)=>x.day.localeCompare(y.day));
}
function showReminders(){
 let items=reminderItems();if(!items.length)return;
 let several=state.profiles.length>1;
 modalBox('reminders',`<h2>Heute wichtig</h2><p class="hint">Fristen und Wiedervorlagen, die fällig sind oder in den nächsten drei Tagen anstehen.</p>${items.map((x,i)=>`<div class="issue ${x.overdue?'warn':'good'}"><strong>${esc(x.label)} ${esc(x.when)}</strong><p>${esc(x.title)}${x.company?' · '+esc(x.company):''}${several?' · Profil: '+esc(x.profileLabel):''}</p><button onclick="openReminder(${i})">Bewerbung öffnen</button></div>`).join('')}<div class="actions"><button class="primary" onclick="$('reminders').remove()">Später</button></div>`);
 window.reminderList=items;
}
function openReminder(i){let x=window.reminderList[i];$('reminders')?.remove();if(state.selectedProfile!==x.profile)switchProfile(x.profile);current=x.app;page='editor';step='stelle';render();}

// ---- 2. export cleanup (on the backup page)
function exportsCard(){
 let body=exportItems===null?'<p class="hint">Jeder Export ist eine datierte Momentaufnahme. Mit der Zeit sammeln sich viele Fassungen an.</p><button onclick="bridge(\'exports_scan\')">Exporte prüfen</button>'
 :!exportItems.length?'<p class="issue good">In diesem Profil gibt es noch keine Exporte.</p>'
 :(()=>{let total=exportItems.reduce((s,x)=>s+x.removableMb,0),files=exportItems.reduce((s,x)=>s+x.removable.length,0);
   return exportItems.map(x=>`<div class="attachment"><span><b>${esc(x.label)}</b><br><span class="small">${x.files} Dateien · ${String(x.mb).replace('.',',')} MB${x.removable.length?' · davon '+x.removable.length+' ältere Fassungen ('+String(x.removableMb).replace('.',',')+' MB)':''}</span></span>${x.removable.length?`<button onclick="cleanExports(['${x.applicationId}'])">Aufräumen</button>`:''}</div>`).join('')
   +(files?`<div class="actions"><button class="primary" onclick="cleanExports(null)">Alle älteren Fassungen löschen (${String(Math.round(total*100)/100).replace('.',',')} MB)</button></div>`:'<p class="issue good">Keine älteren Fassungen vorhanden.</p>');})();
 return `<div class="card"><h2>Exporte aufräumen</h2>${body}<p class="hint">Gelöscht werden nur ältere Exporte im Ordner „Exporte“ der Bewerbungen dieses Profils. Die neueste Fassung je Art (Mappe, Lebenslauf, Anschreiben, E-Mail …) bleibt immer erhalten. Originaldokumente und Sicherungen werden nicht angefasst.</p></div>`;
}
function cleanExports(ids){let n=(exportItems||[]).filter(x=>!ids||ids.includes(x.applicationId)).reduce((s,x)=>s+x.removable.length,0);if(!n)return;if(confirm(n+' ältere Export-Datei(en) endgültig löschen? Die neueste Fassung je Art bleibt erhalten.'))bridge('exports_clean',{applications:ids});}
const workflowBackup=backup;
backup=function(){return workflowBackup()+exportsCard();};

// ---- 3. editable e-mail text (check & export step)
function mailFields(){
 let a=app(),f=a.form;
 return `<div class="form-grid" style="margin:12px 0">${formInput('af-mailSubject','Betreff der E-Mail',f.mailSubject,"editApplicationForm('mailSubject',this.value)",{placeholder:defaultMailSubject(a),wide:true})}</div>${formInput('af-mailText','Text der E-Mail (zwischen Anrede und Grußformel)',f.mailText||defaultMailText(a),"editApplicationForm('mailText',this.value)",{multi:true,rows:5})}<p class="hint">Anrede („${esc(a.salutation)}“), „Mit freundlichen Grüßen“ und dein Name werden automatisch ergänzt. ${f.mailText.trim()?'<button onclick="editApplicationForm(\'mailText\',\'\');render()">Standardtext verwenden</button>':''}</p>`;
}

// ---- 4. suggestions from the job advertisement (step "Stelle")
const JOB_LABELS={position:'Position',company:'Unternehmen',contact:'Ansprechperson',street:'Straße',postcode:'Postleitzahl',city:'Ort des Unternehmens',recipientEmail:'E-Mail für die Bewerbung',deadline:'Bewerbungsfrist'};
function jobCurrent(a,k){return k==='position'||k==='company'?a[k]:k==='recipientEmail'?(a.recipientEmail||''):k==='deadline'?a.tracking.deadline:a.form[k];}
function showJobSuggestion(msg){
 let a=app(),keys=Object.keys(JOB_LABELS).filter(k=>msg.fields[k]);jobSuggestion=msg;
 if(!keys.length){toast('In der Stellenanzeige wurden keine eindeutigen Angaben erkannt. Bitte trage sie selbst ein.');return;}
 let textMode=a.form.recipientMode==='text';
 modalBox('jobSuggest',`<h2>Angaben aus der Stellenanzeige</h2><p class="hint">Bitte prüfen. Leere Felder sind vorausgewählt; bereits ausgefüllte werden nur überschrieben, wenn du sie anhakst.${textMode?' Die Anschrift wird in die frei geschriebene Empfängeranschrift übernommen.':''}</p>${keys.map(k=>{let cur=jobCurrent(a,k)||'';return `<div class="import-field"><label><input type="checkbox" id="job-use-${k}" ${cur.trim()?'':'checked'}> ${JOB_LABELS[k]}${cur.trim()&&cur!==msg.fields[k]?` <span class="small">(bisher: ${esc(cur)})</span>`:''}</label><input id="job-${k}" type="${k==='deadline'?'date':'text'}" value="${esc(msg.fields[k])}"></div>`}).join('')}<div class="actions"><button class="primary" onclick="applyJobSuggestion()">Ausgewählte Angaben übernehmen</button><button onclick="$('jobSuggest').remove()">Abbrechen</button></div>`);
}
function applyJobSuggestion(){
 let a=app(),f=a.form,take=k=>$('job-use-'+k)?.checked?$('job-'+k).value.trim():null;
 for(const k of ['position','company']){let v=take(k);if(v!==null)a[k]=v;}
 let v=take('recipientEmail');if(v!==null)a.recipientEmail=v;
 v=take('deadline');if(v!==null&&/^\d{4}-\d{2}-\d{2}$/.test(v))a.tracking.deadline=v;
 let address={};for(const k of ['contact','street','postcode','city']){let x=take(k);if(x!==null)address[k]=x;}
 if(f.recipientMode==='form')Object.assign(f,address);
 else if(Object.keys(address).length){let lines=[a.company,address.contact,address.street,[address.postcode,address.city].filter(Boolean).join(' ')].filter(x=>x&&x.trim());a.recipient=lines.join('\n');if(address.contact)f.contact=address.contact;}
 $('jobSuggest').remove();compileForms();changed();render();toast('Angaben übernommen. Bitte die Anrede und Empfängeranschrift kurz prüfen.');
}

const workflowBody=editorBody;
editorBody=function(){
 let html=workflowBody();
 if(step==='stelle'){let jobField=field('a','job','Stellenanzeige',true,'Füge die Stellenanzeige hier als Text ein. Sie bleibt lokal gespeichert.');html=html.replace(jobField,jobField+`<div class="actions" style="margin:-4px 0 14px"><button onclick="flush();bridge('job_parse')" ${app().job.trim()?'':'disabled'}>Angaben aus der Anzeige übernehmen</button><span class="small">Erkennt Firma, Position, Ansprechperson, Anschrift, E-Mail und Frist – lokal, ohne Internet.</span></div>`);}
 if(step==='check')html=html.replace(`<button onclick="bridge('export_mail')">E-Mail-Datei mit PDF-Anhang speichern</button>`,mailFields()+`<button onclick="bridge('export_mail')">E-Mail-Datei mit PDF-Anhang speichern</button>`);
 return html;
};
const workflowUpdate=update;
update=function(scope,key,value){workflowUpdate(scope,key,value);if(scope==='a'&&key==='job'){let b=document.querySelector('button[onclick^="flush();bridge(\'job_parse\')"]');if(b)b.disabled=!value.trim();}};

const workflowReceive=receive;
receive=function(msg){
 if(msg.type==='job_parse'){if(msg.profileId===state.selectedProfile&&msg.applicationId===current)showJobSuggestion(msg);return;}
 if(msg.type==='exports_scan'){if(msg.profileId===state.selectedProfile){exportItems=msg.items;if(page==='backup')render();}return;}
 workflowReceive(msg);
 if(msg.type==='load'){exportItems=null;if(!remindersShown){remindersShown=true;setTimeout(showReminders,400);}}
};
