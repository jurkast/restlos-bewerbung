let signatureEditor=null;
const signatureStyles=[['Restlosallura','Fließend'],['Restlosgreatvibes','Elegant'],['Restloscaveat','Handschrift']];
function openSignatureEditor(){
 signatureEditor={profile:state.selectedProfile,application:current,mode:'type',name:state.profile.name||'',font:0,color:'#182633',strokes:[],active:null,ready:false,saving:false};
 modalBox('signatureEditor',`<style>#signatureEditor [data-font][aria-pressed="true"]{border-color:#167c77;background:#e7f5f1;color:#153d3c}</style><div class="actions" style="justify-content:space-between"><h2>Deine Unterschrift gestalten</h2><button onclick="closeSignatureEditor()" aria-label="Schließen">×</button></div><p class="hint">Eintippen, selbst zeichnen oder ein Bild auswählen. Erst beim Einfügen wird die neue Unterschrift im Profil gespeichert.</p><div class="steps" id="signatureTabs">${[['type','Eintippen'],['draw','Zeichnen'],['upload','Hochladen']].map(([k,t])=>`<button data-mode="${k}" onclick="signatureMode('${k}')">${t}</button>`).join('')}</div><div id="signatureControls"></div><div id="signaturePaper" style="background:white;border:1px solid #cbdad9;border-radius:12px;padding:12px;margin:16px 0"><canvas id="signatureCanvas" width="1200" height="360" aria-label="Zeichenfläche für deine Unterschrift" style="width:100%;height:auto;display:block;touch-action:none"></canvas></div><p id="signatureHint" class="hint" role="status"></p><div class="actions" style="justify-content:flex-end"><button onclick="closeSignatureEditor()">Abbrechen</button><button id="signatureInsert" class="primary" disabled onclick="insertSignature()">Unterschrift einfügen</button></div>`);
 signatureMode('type');
 signatureFontsReady.then(()=>{if(!signatureEditor)return;signatureEditor.ready=true;drawSignature();}).catch(()=>{if($('signatureHint'))$('signatureHint').textContent='Schriftarten konnten nicht geladen werden. Zeichnen und Hochladen bleiben verfügbar.';});
 const canvas=$('signatureCanvas');
 const point=e=>{let r=canvas.getBoundingClientRect();return [Math.max(0,Math.min(1200,(e.clientX-r.left)*1200/r.width)),Math.max(0,Math.min(360,(e.clientY-r.top)*360/r.height))];};
 canvas.onpointerdown=e=>{let c=signatureEditor;if(!c||c.mode!=='draw'||c.saving||e.button!==0)return;e.preventDefault();canvas.setPointerCapture(e.pointerId);c.active={id:e.pointerId,points:[point(e)]};drawSignature();};
 canvas.onpointermove=e=>{let c=signatureEditor;if(!c?.active||c.active.id!==e.pointerId)return;c.active.points.push(point(e));drawSignature();};
 const finish=e=>{let c=signatureEditor;if(!c?.active||c.active.id!==e.pointerId)return;c.strokes.push(c.active.points);c.active=null;drawSignature();};
 canvas.onpointerup=finish;canvas.onpointercancel=finish;canvas.onlostpointercapture=finish;
}
function closeSignatureEditor(){if(signatureEditor?.saving)return;$('signatureEditor')?.remove();signatureEditor=null;}
function signatureMode(mode){let c=signatureEditor;if(!c||c.saving)return;c.mode=mode;c.active=null;
 document.querySelectorAll('#signatureTabs button').forEach(b=>{b.classList.toggle('active',b.dataset.mode===mode);b.setAttribute('aria-pressed',b.dataset.mode===mode);});
 $('signaturePaper').hidden=mode==='upload';$('signatureInsert').hidden=mode==='upload';
 let colors=`<div class="actions"><span>Farbe</span>${[['#182633','Dunkel'],['#214caa','Blau'],['#ad2626','Rot']].map(([v,t])=>`<button aria-label="${t}" onclick="setSignatureColor('${v}')" style="border-color:${v};color:${v}">${t}</button>`).join('')}<label>Eigene Farbe <input aria-label="Eigene Farbe" type="color" value="${c.color}" oninput="setSignatureColor(this.value)"></label></div>`;
 $('signatureControls').innerHTML=mode==='type'?`<label class="field"><span>Dein Name</span><input id="signatureName" maxlength="120" value="${esc(c.name)}" oninput="signatureEditor.name=this.value;drawSignature()"></label><div class="form-grid">${signatureStyles.map(([f,label],i)=>`<button aria-pressed="${i===c.font}" data-font="${i}" onclick="signatureEditor.font=${i};document.querySelectorAll('[data-font]').forEach(b=>b.setAttribute('aria-pressed',Number(b.dataset.font)===${i}));drawSignature()"><span style="font-family:${f};font-size:32px">Unterschrift</span><br>${label}</button>`).join('')}</div>${colors}`:mode==='draw'?`${colors}<div class="actions" style="margin-top:12px"><button onclick="signatureEditor.strokes.pop();drawSignature()">Letzten Strich zurücknehmen</button><button onclick="signatureEditor.strokes=[];signatureEditor.active=null;drawSignature()">Zeichenfläche leeren</button></div>`:`<p>Wähle ein Bild deiner Unterschrift (PNG, JPG oder WebP), möglichst eng zugeschnitten und mit weißem oder transparentem Hintergrund.</p><button class="primary" onclick="uploadSignature()">Bilddatei auswählen und übernehmen</button><p class="hint">Die Originaldatei wird in die lokale Profilablage kopiert. Brichst du die Dateiauswahl ab, bleibt deine bisherige Unterschrift erhalten.</p>`;
 drawSignature();
}
function setSignatureColor(color){if(signatureEditor&&!signatureEditor.saving){signatureEditor.color=color;drawSignature();}}
function drawSignature(){let c=signatureEditor,canvas=$('signatureCanvas');if(!c||!canvas)return;let ctx=canvas.getContext('2d');ctx.clearRect(0,0,1200,360);ctx.fillStyle=c.color;ctx.strokeStyle=c.color;ctx.lineWidth=5;ctx.lineCap='round';ctx.lineJoin='round';
 if(c.mode==='type'&&c.ready&&c.name.trim()){
  let family=signatureStyles[c.font][0],size=130;ctx.font=`${size}px ${family}`;let width=ctx.measureText(c.name.trim()).width;if(width>1080)size*=1080/width;ctx.font=`${size}px ${family}`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(c.name.trim(),600,180);
 }
 if(c.mode==='draw')for(let stroke of [...c.strokes,...(c.active?[c.active.points]:[])]){if(!stroke.length)continue;ctx.beginPath();ctx.moveTo(...stroke[0]);if(stroke.length===1){ctx.arc(stroke[0][0],stroke[0][1],2.5,0,Math.PI*2);ctx.fill();}else{for(let p of stroke.slice(1))ctx.lineTo(...p);ctx.stroke();}}
 let valid=c.mode==='type'?c.ready&&!!c.name.trim():c.mode==='draw'&&c.strokes.length>0;
 $('signatureInsert').disabled=!valid||c.saving;
 $('signatureHint').textContent=c.saving?'Unterschrift wird lokal gespeichert …':c.mode==='type'?(c.ready?'Vorschau deiner Unterschrift. Die Schriftarten sind im Programm enthalten.':'Schriftarten werden geladen …'):c.mode==='draw'?'Unterschreibe in der weißen Fläche mit Maus, Trackpad oder Finger.':'Deine vorhandene Unterschrift wird erst nach Auswahl eines gültigen Bildes ersetzt.';
}
function validSignatureContext(){let c=signatureEditor;if(!c||c.profile!==state.selectedProfile||c.application!==current){toast('Bitte die Unterschrift in der ursprünglichen Bewerbung erneut öffnen.');return false;}return true;}
function uploadSignature(){if(!validSignatureContext())return;signatureEditor.upload=true;bridge('signature');}
function insertSignature(){if(!validSignatureContext()||signatureEditor.saving||$('signatureInsert').disabled)return;let image=$('signatureCanvas').toDataURL('image/png');signatureEditor.saving=true;drawSignature();bridge('signature_create',{image});}
const signatureMakerReceive=receive;
receive=function(msg){
 if(msg.type==='load'&&signatureEditor&&(signatureEditor.saving||signatureEditor.upload)){$('signatureEditor')?.remove();signatureEditor=null;}
 if(msg.type==='error'&&signatureEditor){signatureEditor.saving=false;drawSignature();}
 signatureMakerReceive(msg);
};
