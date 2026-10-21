let signaturePreview='';
const beforeSignatureReceive=receive;
receive=function(msg){
 if(msg.type==='signature_preview'){
  if(msg.profileId!==state.selectedProfile)return;
  signaturePreview=msg.image;
  if($('signatureImage')){$('signatureImage').src='data:image/png;base64,'+msg.image;$('signatureImage').hidden=!msg.image;}
  return;
 }
 if(msg.type==='load')signaturePreview='';
 beforeSignatureReceive(msg);
 if(msg.type==='load'){if(state.profile.signature)bridge('signature_preview');}
};
const beforeSignatureSwitch=switchProfile;
switchProfile=function(id){signaturePreview='';beforeSignatureSwitch(id);if(state.profile.signature)bridge('signature_preview');};
const beforeSignatureLetter=letterEditor;
letterEditor=function(){return beforeSignatureLetter()+signatureCard();};
function signatureCard(){let p=state.profile;return `<div class="card"><h2>Deine Unterschrift</h2><p class="hint">Tippe deinen Namen ein, zeichne selbst oder lade ein Bild deiner Unterschrift hoch. Sie erscheint im Anschreiben zwischen Grußformel und Name. Die Bilddatei wird lokal unter „Sonstiges“ im Profil abgelegt.</p>${p.signature?`<img id="signatureImage" ${signaturePreview?'':'hidden'} src="${signaturePreview?'data:image/png;base64,'+signaturePreview:''}" alt="Deine Unterschrift" style="max-width:${200*(app().design.signatureScale??100)/100}px;max-height:${60*(app().design.signatureScale??100)/100}px;background:white;padding:8px"><label class="check-line"><input type="checkbox" ${app().design.signature!==false?'checked':''} onchange="setDesign('signature',this.checked)"> Unterschrift in dieser Bewerbung verwenden</label><label class="field"><span>Größe im Anschreiben: <strong id="signatureScaleValue">${app().design.signatureScale??100} %</strong></span><input id="signatureScale" type="range" min="25" max="150" step="5" value="${app().design.signatureScale??100}" oninput="resizeSignature(Number(this.value))"></label><div class="actions"><button onclick="resizeSignature(65)">Kompakt · 65 %</button><button onclick="resizeSignature(100)">Originalgröße · 100 %</button></div><p class="hint">Die Größe gilt nur für diese Bewerbung. Die Dokumentvorschau rechts zeigt das Ergebnis; PDF und Word übernehmen dieselbe Größe.</p>`:''}<div class="actions"><button onclick="openSignatureEditor()">${p.signature?'Unterschrift ersetzen':'Unterschrift hinzufügen'}</button>${p.signature?`<button onclick="state.profile.signature='';signaturePreview='';changed();render()">Unterschrift aus Profil entfernen</button>`:''}</div><p class="hint">Die Unterschrift gilt für dieses Profil. Das Entfernen aus dem Profil bewahrt die Originaldatei in der Ablage.</p></div>`;}

function resizeSignature(value){
 if(!Number.isFinite(value)||value<25||value>150)return;
 app().design.signatureScale=value;
 if($('signatureScale'))$('signatureScale').value=value;
 if($('signatureScaleValue'))$('signatureScaleValue').textContent=value+' %';
 let image=$('signatureImage');if(image){image.style.maxWidth=(200*value/100)+'px';image.style.maxHeight=(60*value/100)+'px';}
 changed();
}
