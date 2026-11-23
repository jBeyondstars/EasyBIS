"use strict";
const $ = id => document.getElementById(id);
const paths = {
  save:'M4 4h13l3 3v13H4z M8 4v6h8V4 M8 20v-7h8v7',
  download:'M12 3v12m-5-5 5 5 5-5 M4 15v5h16v-5',
  shield:'M12 2 4 5v6c0 5 4 8 8 11 4-3 8-6 8-11V5z',
  swords:'m3 3 4 1 12 12-3 3L4 7z M14 19l5-5m-2 4 4 3 M21 3l-4 1-4 4m-4 5-5 5 2 2 5-5 M4 15l5 5',
  grid:'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  grip:'M9 5h.2m5.8 0h.2M9 12h.2m5.8 0h.2M9 19h.2m5.8 0h.2'
};
function icon(name) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('viewBox','0 0 24 24');
  svg.setAttribute('aria-hidden','true');
  const path = document.createElementNS(svg.namespaceURI,'path');
  for (const [key,value] of Object.entries({d:paths[name],fill:'none',stroke:'currentColor','stroke-linecap':'round','stroke-linejoin':'round','stroke-width':name==='grip'?3.5:1.6})) path.setAttribute(key,value);
  svg.append(path);
  return svg;
}
document.querySelectorAll('[data-icon]').forEach(el=>el.replaceWith(icon(el.dataset.icon)));
const classNames={WARRIOR:'Guerrier',PALADIN:'Paladin',HUNTER:'Chasseur',ROGUE:'Voleur',PRIEST:'Prêtre',SHAMAN:'Chaman',MAGE:'Mage',WARLOCK:'Démoniste',DRUID:'Druide'};
const specNames={'Arms':'Armes','Fury':'Fureur','Protection':'Protection','Holy':'Sacré','Retribution':'Vindicte','Beast Mastery':'Maîtrise des bêtes','Marksmanship':'Précision','Survival':'Survie','Assassination':'Assassinat','Subtlety':'Finesse','Shadow':'Ombre','Elemental':'Élémentaire','Enhancement':'Amélioration','Restoration':'Restauration','Arcane':'Arcanes','Fire':'Feu','Frost':'Givre','Affliction':'Affliction','Demonology':'Démonologie','Destruction':'Destruction','Balance':'Équilibre','Feral (Bear)':'Farouche (ours)','Feral (Cat)':'Farouche (félin)'};
const slots={head:'Tête',neck:'Cou',shoulder:'Épaules',back:'Dos',chest:'Torse',wrist:'Poignets',hands:'Mains',waist:'Taille',legs:'Jambes',feet:'Pieds',finger:'Doigts',trinket:'Bijoux',main:'Main droite',off:'Main gauche',ranged:'À distance'};
const colors=['#9d9d9d','#f2ede8','#56d552','#4da5ff','#c380ff','#ffa346','#e8ce86'];
const D=window.BIS_DATA;
const storageKey='easybis-editor-v1';
let selection={cls:'ROGUE',spec:'2',side:'a',mode:'pve',slot:'head'};
let scoreOverrides={};
let edits={}, dirty=false,dragIndex=null,toastTimer;
const profileKey=()=>[selection.cls,selection.spec,selection.mode,selection.side].join(':');
function el(tag,txt,cls){const n=document.createElement(tag);if(txt!=null)n.textContent=txt;if(cls)n.className=cls;return n}
function photo(id){
  const img=new Image();img.alt='';img.draggable=false;
  const path=D.items[id]?.icon;
  img.src=path||'helm.webp';
  img.onerror=()=>{img.onerror=null;img.src='helm.webp'};
  return img;
}
function choices(select,entries,value){select.replaceChildren(...entries.map(([id,name])=>new Option(name,id)));select.value=value}
function getOrder(key,slot){
  const base=D.profiles[key]?.[slot]||[], valid=new Set(base.map(p=>p.id));
  const order=[];
  for(const id of edits[key]?.[slot]||[]) if(valid.delete(id))order.push(id);
  return [...order,...valid];
}
function markDirty(){dirty=true;$('status').textContent='Modifications à enregistrer'}
function move(from,to){
  const key=profileKey(),s=selection.slot,ids=getOrder(key,s);
  if(!Number.isInteger(from)||to<0||from<0||from>=ids.length||to>=ids.length||from===to)return;
  ids.splice(to,0,ids.splice(from,1)[0]);
  (edits[key]??={})[s]=ids;
  markDirty();render();return ids[to];
}
function hideTip(){$('tip').hidden=true}
function showTip(target,item,duel){
  if(dragIndex!==null)return;
  const tip=$('tip');
  tip.replaceChildren(el('strong',item.name));
  tip.style.setProperty('--quality',colors[item.quality]||'#eee');
  const lines=item.lines||[];
  const equipmentLine=lines.findIndex((line,i)=>i>0&&line===item.type);
  for(const [i,line] of lines.entries()){
    if(line===item.name||i===equipmentLine)continue;
    if(i===equipmentLine-1){
      const pair=el('div',null,'tip-pair');pair.append(el('span',line),el('span',item.type));tip.append(pair);
    }else{
      const cls=/^(Equip:|Use:|Équip|Utilis|Set:|\(\d\) Set\s*:)/i.test(line)?'effect':line.startsWith('Item Level')?'item-level':'';
      tip.append(el('div',line,cls));
    }
  }
  if(!item.lines?.length)tip.append(el('div',item.type));
  if(duel)tip.append(el('div',duel,'item-level'));
  tip.hidden=false;
  const rect=target.getBoundingClientRect();
  tip.style.left=Math.max(4,Math.min(rect.left+32,innerWidth-tip.offsetWidth-8))+'px';
  tip.style.top=(rect.bottom+tip.offsetHeight+10<innerHeight?rect.bottom+6:Math.max(4,rect.top-tip.offsetHeight-6))+'px';
}
function scoreSettings(key,slot,pick){
  const saved=scoreOverrides[key]?.[slot]?.[pick.id];
  return {
    showScore:!pick.option&&(pick.score!=null||!!pick.bis)&&saved?.showScore!==false,
    tied:saved?.tied===true
  };
}
function scoreCell(pick,item){
  const key=profileKey(),slot=selection.slot;
  const settings=scoreSettings(key,slot,pick);
  const cell=el('div',null,'score'+(pick.bis?' top':''));
  if(pick.option)cell.append(el('span',pick.option,'score-value'));
  const value=el('div',null,'score-value');
  value.append(el('span',pick.bis?'BIS':pick.score==null?'—':(pick.score>100?'+':'')+(pick.score-100)+' %'));
  if(pick.score!=null){
    const track=el('span',null,'track'),bar=el('b');
    bar.style.width=Math.max(0,Math.min(100,pick.score))+'%';
    track.append(bar);value.append(track);
  }
  value.hidden=!settings.showScore;
  cell.append(value);
  for(const [field,label,description] of [
    ['showScore','Score','Afficher le score'],
    ['tied','Tied','Marquer comme ex æquo']
  ]){
    const control=el('label',null,'score-toggle'),input=el('input');
    input.type='checkbox';input.checked=settings[field];
    input.disabled=field==='showScore'&&(!!pick.option||(pick.score==null&&!pick.bis));
    control.title=input.disabled?'Aucun score fourni par EasyBIS':description;
    input.setAttribute('aria-label',description+' · '+item.name);
    input.onchange=()=>{
      settings[field]=input.checked;
      const profile=scoreOverrides[key]??={};
      (profile[slot]??={})[pick.id]=settings;
      value.hidden=!settings.showScore;
      markDirty();
    };
    control.append(input,document.createTextNode(label));cell.append(control);
  }
  return cell;
}
function rowFor(id,index,picks,ids){
  const item=D.items[id],pick=picks.find(p=>p.id===id),row=el('li',null,'row');
  row.draggable=true;row.style.setProperty('--quality',colors[item.quality]||'#eee');
  const rank=el('div',null,'rank'),moves=el('div',null,'moves');
  for(const [step,label,sign] of [[-1,'Monter','▴'],[1,'Descendre','▾']]){
    const btn=el('button',sign);btn.disabled=index+step<0||index+step>=ids.length;
    btn.setAttribute('aria-label',label+' '+item.name);btn.title=label;
    btn.onclick=()=>{move(index,index+step);$('list').children[index+step].querySelector('.obj').focus()};
    moves.append(btn);
  }
  rank.append(icon('grip'),moves,el('span',String(index+1).padStart(2,'0')));
  const obj=el('div',null,'obj');obj.tabIndex=0;
  obj.setAttribute('aria-describedby','tip');
  const details=el('div');details.append(el('strong',item.name),el('span',item.type,'sub'));obj.append(photo(id),details);
  obj.onmouseenter=obj.onfocus=()=>showTip(obj,item,pick.duel);
  obj.onmouseleave=obj.onblur=hideTip;
  obj.onclick=()=>showTip(obj,item,pick.duel);
  const score=scoreCell(pick,item);
  const source=el('div',null,'source');source.append(el('small',pick.sourceType||item.sourceType),el('span',pick.source||item.source||'Source inconnue'));
  row.append(rank,obj,score,source);
  row.ondragstart=e=>{dragIndex=index;hideTip();row.classList.add('dragging');e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',String(id))};
  row.ondragover=e=>{if(dragIndex!==null){e.preventDefault();row.classList.add('over');e.dataTransfer.dropEffect='move'}};
  row.ondragleave=()=>row.classList.remove('over');
  row.ondrop=e=>{e.preventDefault();const from=dragIndex;dragIndex=null;row.classList.remove('over');move(from,index)};
  row.ondragend=()=>{dragIndex=null;document.querySelectorAll('.over,.dragging').forEach(r=>r.classList.remove('over','dragging'))};
  return row;
}
const doneKey=(cls,id)=>`easybis-spec-done:${cls}:${id}`;
function specDone(cls,id){
  try{return localStorage.getItem(doneKey(cls,id))==='1'}
  catch{return false}
}
function render(){
  hideTip();
  const {cls,spec,side,mode,slot}=selection,key=profileKey(),profile=D.profiles[key]||{},specs=D.classes[cls];
  choices($('spec'),specs.map(s=>[s.id,(specNames[s.name]||s.name)+(specDone(cls,s.id)?' ✓ Done':'')]),spec);
  $('done').checked=specDone(cls,spec);
  $('cls').value=cls;$('side').value=side;
  document.querySelectorAll('[data-mode]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.mode===mode));
  const nav=document.querySelector('nav');nav.replaceChildren();
  for(const [s,name] of Object.entries(slots)){
    const ids=getOrder(key,s),b=el('button');b.setAttribute('aria-current',s===slot);
    b.append(ids.length?photo(ids[0]):el('span','', 'nav-fallback'),el('span',name),el('small',String(ids.length)));
    b.onclick=()=>{selection.slot=s;render()};nav.append(b);
  }
  $('slot-select').value=slot;
  const ids=getOrder(key,slot);
  $('slot-name').textContent=slots[slot];$('count').textContent=ids.length+(ids.length===1?' objet':' objets');
  $('profile-label').textContent=[classNames[cls],$('spec').selectedOptions[0]?.text,mode==='pve'?'PvE':'PvP'].join(' · ');
  $('slot-image').replaceChildren(...(ids.length?[photo(ids[0])]:[]));
  $('list').replaceChildren(...ids.map((id,i)=>rowFor(id,i,profile[slot],ids)));
  if(!ids.length)$('list').append(el('li','Aucun objet classé pour cet emplacement avec ce profil.','empty'));
}
function toast(message){clearTimeout(toastTimer);$('toast').textContent=message;$('toast').hidden=false;toastTimer=setTimeout(()=>$('toast').hidden=true,4000)}
function restore(){
  try{
    const saved=JSON.parse(localStorage.getItem(storageKey)||'null');
    if(!saved)return;
    if(saved.version!==D.version){toast('Les données Easy BIS ont changé. Le classement actuel a été chargé.');return}
    if(saved.scoreOverrides && typeof saved.scoreOverrides==='object')scoreOverrides=saved.scoreOverrides;
    if(saved.edits && typeof saved.edits==='object'){
      for(const [key,order] of Object.entries(saved.edits)){
        if(!D.profiles[key]||!order||typeof order!=='object')continue;
        edits[key]={};
        for(const [s,ids] of Object.entries(order))if(slots[s]&&Array.isArray(ids))edits[key][s]=ids.filter(Number.isInteger);
      }
    }
    const v=saved.selection;
    if(v&&slots[v.slot]&&D.profiles[[v.cls,v.spec,v.mode,v.side].join(':')])selection=v;
    $('status').textContent='Classements enregistrés chargés';
  }catch{toast('Lecture de la sauvegarde locale impossible.')}
}
function save(){
  edits[profileKey()]??={};
  try{
    localStorage.setItem(storageKey,JSON.stringify({version:D.version,selection,edits,scoreOverrides}));dirty=false;
    $('status').textContent='Enregistré dans ce navigateur';toast('Classements enregistrés.');
  }catch{toast('Sauvegarde locale indisponible. Utilise Exporter JSON.')}
}
function exportLists(){
  const profiles=[...new Set([...Object.keys(edits),...Object.keys(scoreOverrides).filter(k=>D.profiles[k]),profileKey()])].map(key=>{
    const [cls,spec,mode,side]=key.split(':');
    return {class:cls,specId:Number(spec),spec:D.classes[cls].find(s=>String(s.id)===spec).name,mode,faction:side==='a'?'Alliance':'Horde',
      slots:Object.fromEntries(Object.keys(slots).map(s=>[s,getOrder(key,s).map((id,i)=>{
        const pick=D.profiles[key][s].find(p=>p.id===id);
        return {rank:i+1,id,name:D.items[id].name,...(pick.option?{option:pick.option}:{}),...scoreSettings(key,s,pick)};
      })]))};
  });
  const today=new Date();
  const out={format:'easybis-personal-rankings',schemaVersion:1,dataVersion:D.version,phase:0,level:60,exportedAt:today.toISOString(),profiles};
  const url=URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{type:'application/json'}));
  const link=el('a');link.href=url;link.download='easybis-classements-'+today.toISOString().slice(0,10)+'.json';document.body.append(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);toast(profiles.length+' profil'+(profiles.length>1?'s exportés.':' exporté.'));
}
choices($('cls'),Object.entries(classNames).filter(([key])=>D.classes[key]),selection.cls);
choices($('slot-select'),Object.entries(slots),selection.slot);
restore();
$('cls').onchange=e=>{selection.cls=e.target.value;selection.spec=String(D.classes[selection.cls][0].id);render()};
for(const [id,field] of [['spec','spec'],['side','side'],['slot-select','slot']])$(id).onchange=e=>{selection[field]=e.target.value;render()};
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{selection.mode=b.dataset.mode;render()});
$('done').onchange=()=>{
  const key=doneKey(selection.cls,selection.spec);
  try{
    if($('done').checked)localStorage.setItem(key,'1');
    else localStorage.removeItem(key);
  }catch{toast('Impossible de mémoriser le statut dans ce navigateur.')}
  render();
};
$('save').onclick=save;$('export').onclick=exportLists;
document.addEventListener('keydown',e=>{if(e.key==='Escape')hideTip()});
document.addEventListener('scroll',hideTip,true);
window.addEventListener('resize',hideTip);
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue=''}});
render();
