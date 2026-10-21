// 0.11: automatic salutation, list of enclosures, place/date/signature below the CV,
// DIN 5008 letter layout and "restart to update". Extends existing functions like studio.js does.
const LETTER_DEFAULT_SALUTATION='Sehr geehrte Damen und Herren,';
const LETTER_PARTICLES=new Set(['von','van','de','der','den','zu','vom','zur','ten','ter','di','da','del','le','la']);

// Keep in sync with letters.py (salutation_for / contact_person / document_label).
function salutationFor(contact){
 let m=/^\s*(Frau|Herrn?)\s+(.+?)\s*,?\s*$/.exec(contact||'');if(!m)return LETTER_DEFAULT_SALUTATION;
 let tokens=m[2].split(/\s+/),titles=tokens.filter(t=>/^(Prof|Professor|Dr)\b/.test(t)),names=tokens.filter(t=>!t.endsWith('.')&&!titles.includes(t));
 if(!names.length)return LETTER_DEFAULT_SALUTATION;
 let start=names.findIndex((t,i)=>LETTER_PARTICLES.has(t.toLowerCase())&&i<names.length-1);if(start<0)start=names.length-1;
 return (m[1]==='Frau'?'Sehr geehrte Frau ':'Sehr geehrter Herr ')+[...titles,names.slice(start).join(' ')].join(' ')+',';
}
function contactPerson(a){if(a.form.recipientMode==='form')return a.form.contact||'';return (a.recipient||'').split('\n').find(l=>/^\s*(Frau|Herrn?)\b/.test(l))||'';}
function documentLabel(name){let stem=String(name).replace(/\.[^./]*$/,'').replace(/_[0-9a-f]{6}$/,'');return stem.replace(/_/g,' ').replace(/\s+/g,' ').trim()||name;}
function attachmentLinesFor(a){
 let own=a.form.attachmentText||'';if(own.trim())return own.split('\n').map(x=>x.trim()).filter(Boolean);
 let names=Object.fromEntries((activeProfile()?.documents||[]).map(d=>[d.path,d.name])),lines=['Lebenslauf'];
 for(let rel of a.attachments){let label=documentLabel(names[rel]||rel.split('/').pop());if(!lines.includes(label))lines.push(label);}
 return lines;
}

const letterToolsEnsure=ensureForms;
ensureForms=function(){letterToolsEnsure();for(const a of state.applications){let d=a.design,af=a.form;d.attachmentList??=true;d.cvSignature??=false;d.letterLayout??='standard';af.attachmentText??='';af.salutationMode??=(['',LETTER_DEFAULT_SALUTATION].includes((a.salutation||'').trim())?'auto':'text');}};
const letterToolsCompile=compileForms;
compileForms=function(){letterToolsCompile();for(const a of state.applications)if(a.form.salutationMode==='auto')a.salutation=salutationFor(contactPerson(a));};

function setSalutationMode(mode){let a=app();a.form.salutationMode=mode;compileForms();changed();render();}
function salutationControls(){
 let a=app(),auto=a.form.salutationMode==='auto',contact=contactPerson(a);
 return `<div class="field"><span>Anrede</span><div class="steps" style="margin:6px 0 8px"><button class="${auto?'active':''}" onclick="setSalutationMode('auto')">Automatisch</button><button class="${auto?'':'active'}" onclick="setSalutationMode('text')">Eigene Anrede</button></div>${auto?`<div class="issue good">${esc(a.salutation)}</div><p class="hint">${contact.trim()?`Abgeleitet aus „${esc(contact)}“.`:'Trage unter „Stelle“ eine Ansprechperson wie „Frau Dr. Müller“ oder „Herr Schmidt“ ein, dann wird die Anrede persönlich.'}</p>`:`<input id="a-salutation" value="${esc(a.salutation)}" oninput="update('a','salutation',this.value)">`}</div>`;
}
function attachmentListCard(){
 let a=app(),on=a.design.attachmentList,lines=attachmentLinesFor(a),own=(a.form.attachmentText||'').trim();
 return `<div class="card"><h2>Anlagenverzeichnis</h2><p class="hint">Unter deinem Namen wird aufgelistet, was der Bewerbung beiliegt. Die Liste folgt automatisch den Anlagen dieser Bewerbung.</p><label class="check-line"><input type="checkbox" ${on?'checked':''} onchange="setDesign('attachmentList',this.checked);render()"> Anlagenverzeichnis im Anschreiben anzeigen</label>${on?`<div class="issue"><strong>Anlagen</strong><br>${lines.map(esc).join('<br>')}</div>${formInput('af-attachmentText','Eigene Liste (optional, eine Anlage pro Zeile – ersetzt die automatische Liste)',a.form.attachmentText,"editApplicationForm('attachmentText',this.value)",{multi:true,rows:3,placeholder:'Leer lassen für die automatische Liste'})}${own?'<button onclick="editApplicationForm(\'attachmentText\',\'\');render()">Automatische Liste verwenden</button>':''}`:''}</div>`;
}
const letterToolsLetter=letterEditor;
letterEditor=function(){return letterToolsLetter().replace(field('a','salutation','Anrede'),salutationControls())+attachmentListCard();};

function letterLayoutCard(){
 let d=app().design,din=d.letterLayout==='din5008',sig=!!activeProfile()?.profile?.signature;
 return `<div class="card"><h2>Briefformat und Abschluss</h2><label class="field"><span>Format des Anschreibens</span><select onchange="setDesign('letterLayout',this.value);render();previewOverride='letter';requestPreview()"><option value="standard" ${din?'':'selected'}>Restlos-Vorlage</option><option value="din5008" ${din?'selected':''}>DIN 5008 (Fensterumschlag)</option></select></label><p class="hint">${din?'Die Anschrift steht im Adressfeld für Fensterumschläge (DIN lang/C6), das Datum rechts, mit Falz- und Lochmarken am Rand. Höchstens 6 Zeilen Empfängeranschrift. Die Word-Ausgabe bleibt einspaltig.':'Das Anschreiben folgt der gewählten Vorlage.'}</p><label class="check-line"><input type="checkbox" ${d.cvSignature?'checked':''} onchange="setDesign('cvSignature',this.checked);render()"> Ort, Datum ${sig?'und Unterschrift ':''}unter dem Lebenslauf</label>${d.cvSignature?`<p class="hint">Ort und Datum kommen aus „Stelle“ (${esc([app().location,app().date].filter(x=>x?.trim()).join(', ')||'bitte ergänzen')}).${sig?'':' Eine Unterschrift fügst du unter „Anschreiben → Deine Unterschrift“ hinzu.'}</p>`:''}<div class="actions"><button onclick="previewOverride='letter';requestPreview()">Anschreiben ansehen</button><button onclick="previewOverride=null;requestPreview()">Lebenslauf ansehen</button></div></div>`;
}
const letterToolsBody=editorBody;
editorBody=function(){let html=letterToolsBody();if(step==='design')html+=letterLayoutCard();return html;};

// Restart to activate a prepared update without leaving the program by hand.
function restartForUpdate(){if(confirm('Restlos speichert alles, schließt sich und startet sofort mit Version '+(updateInfo.pending||'')+'. Fortfahren?'))bridge('update_restart');}
function paintUpdateBanner(){
 let pending=updateInfo?.pending,el=$('updateBanner');
 if(!pending){el?.remove();return;}
 if(!el){el=document.createElement('div');el.id='updateBanner';el.setAttribute('role','status');el.style.cssText='position:fixed;right:22px;bottom:22px;z-index:60;background:#14323a;color:#fff;padding:14px 16px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.25);display:flex;gap:12px;align-items:center;max-width:460px;font-size:13px';document.body.appendChild(el);}
 el.innerHTML=`<span>Update auf Version <b>${esc(pending)}</b> ist bereit.</span><button class="primary" onclick="restartForUpdate()">Jetzt neu starten und aktualisieren</button>`;
}
const letterToolsSettings=settingsPage;
settingsPage=function(){let html=letterToolsSettings();if(!updateInfo.pending)return html;return html.replace('Du kannst jetzt normal weiterarbeiten.</div>','Du kannst jetzt normal weiterarbeiten oder direkt aktualisieren.</div><div class="actions"><button class="primary" onclick="restartForUpdate()">Jetzt neu starten und aktualisieren</button></div>');};
const letterToolsReceive=receive;
receive=function(msg){letterToolsReceive(msg);if(['update_status','updates','load'].includes(msg.type))paintUpdateBanner();};
