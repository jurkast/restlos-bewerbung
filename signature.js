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
function signatureCard(){let p=state.profile;return `<div class="card"><h2>Deine Unterschrift</h2><p class="hint">Lade deine Unterschrift als PNG, JPG oder WebP hoch – möglichst eng zugeschnitten, mit transparentem oder weißem Hintergrund. Sie erscheint im Anschreiben zwischen Grußformel und Name. Die Bilddatei wird lokal unter „Sonstiges“ im Profil abgelegt.</p>${p.signature?`<img id="signatureImage" ${signaturePreview?'':'hidden'} src="${signaturePreview?'data:image/png;base64,'+signaturePreview:''}" alt="Deine Unterschrift" style="max-width:240px;max-height:90px;background:white;padding:8px"><label class="check-line"><input type="checkbox" ${app().design.signature!==false?'checked':''} onchange="setDesign('signature',this.checked)"> Unterschrift in dieser Bewerbung verwenden</label>`:''}<div class="actions"><button onclick="bridge('signature')">${p.signature?'Unterschrift ersetzen':'Unterschrift hinzufügen'}</button>${p.signature?`<button onclick="state.profile.signature='';signaturePreview='';changed();render()">Unterschrift aus Profil entfernen</button>`:''}</div><p class="hint">Die Unterschrift gilt für dieses Profil. Das Entfernen aus dem Profil bewahrt die Originaldatei in der Ablage.</p></div>`;}
