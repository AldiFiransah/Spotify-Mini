const audio=new Audio(), $=id=>document.getElementById(id);
const DEF="data:image/svg+xml,"+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#2d2450"/><text x="50" y="62" font-size="44" text-anchor="middle" fill="#a78bfa">♪</text></svg>');
let lagu=[],tampil=[],idx=-1,acak=false,ulang=false,ctx,an,data;
$("cover").src=DEF;

$("folder").onchange=e=>{
  lagu=[...e.target.files].filter(f=>/\.(mp3|flac|wav|ogg|m4a|opus)$/i.test(f.name)).map(f=>({file:f,url:URL.createObjectURL(f),judul:f.name.replace(/\.[^.]+$/,""),artis:"Artis tidak diketahui",cover:DEF}));
  lagu.sort((a,b)=>a.judul.localeCompare(b.judul));
  filter(); lagu.forEach(baca);
};
function baca(l){
  if(!window.jsmediatags)return;
  jsmediatags.read(l.file,{onSuccess:({tags})=>{
    if(tags.title)l.judul=tags.title;
    if(tags.artist)l.artis=tags.artist;
    if(tags.picture)l.cover=URL.createObjectURL(new Blob([new Uint8Array(tags.picture.data)],{type:tags.picture.format}));
    renderList(); if(tampil[idx]===l)info(l);
  },onError:()=>{}});
}
function filter(){
  const q=$("cari").value.toLowerCase(),s=tampil[idx];
  tampil=lagu.filter(l=>(l.judul+" "+l.artis).toLowerCase().includes(q));
  idx=s?tampil.indexOf(s):-1; renderList();
}
$("cari").oninput=filter;
function renderList(){
  const ul=$("list"); ul.innerHTML="";
  tampil.forEach((l,i)=>{
    const li=document.createElement("li"); li.tabIndex=0; if(i===idx)li.className="on";
    const im=new Image(); im.src=l.cover; im.alt="";
    const d=document.createElement("div"), b=document.createElement("b"), s=document.createElement("small");
    b.textContent=l.judul; s.textContent=l.artis; d.append(b,s); li.append(im,d);
    li.onclick=()=>putar(i); li.onkeydown=e=>{if(e.key==="Enter")putar(i)};
    ul.appendChild(li);
  });
}
function info(l){
  $("judul").textContent=l.judul; $("artis").textContent=l.artis; $("cover").src=l.cover;
  $("amb").style.setProperty("--img",`url("${l.cover}")`); document.title=l.judul+" · Pemutar Musik";
  if("mediaSession" in navigator)navigator.mediaSession.metadata=new MediaMetadata({title:l.judul,artist:l.artis,artwork:[{src:l.cover}]});
}
function viz(){
  if(ctx)return;
  ctx=new AudioContext(); const src=ctx.createMediaElementSource(audio);
  an=ctx.createAnalyser(); an.fftSize=128; src.connect(an); an.connect(ctx.destination);
  data=new Uint8Array(an.frequencyBinCount); gambar();
}
function gambar(){
  requestAnimationFrame(gambar);
  const c=$("viz"),g=c.getContext("2d"),w=c.width=c.clientWidth,h=c.height=c.clientHeight;
  an.getByteFrequencyData(data); const n=Math.floor(data.length*.75),bw=w/n;
  g.fillStyle="#c4b5fd";
  for(let i=0;i<n;i++){const v=data[i]/255*h; g.fillRect(i*bw+1,h-v,bw-2,v);}
}
function putar(i){
  if(!tampil.length)return;
  viz(); if(ctx.state==="suspended")ctx.resume();
  idx=(i+tampil.length)%tampil.length; const l=tampil[idx];
  audio.src=l.url; audio.play(); info(l); renderList();
}
const berikut=()=>putar(acak?Math.floor(Math.random()*tampil.length):idx+1);
const toggle=()=>{if(idx<0)return putar(0);audio.paused?audio.play():audio.pause()};
$("play").onclick=toggle; $("next").onclick=berikut; $("prev").onclick=()=>putar(idx-1);
$("acak").onclick=()=>{acak=!acak;$("acak").classList.toggle("aktif",acak)};
$("ulang").onclick=()=>{ulang=!ulang;$("ulang").classList.toggle("aktif",ulang)};
audio.onplay=()=>{$("play").textContent="⏸"};
audio.onpause=()=>{$("play").textContent="▶"};
audio.onended=()=>ulang?putar(idx):berikut();
const fmt=s=>isFinite(s)?Math.floor(s/60)+":"+String(Math.floor(s%60)).padStart(2,"0"):"0:00";
audio.ontimeupdate=()=>{$("now").textContent=fmt(audio.currentTime);$("seek").value=audio.duration?audio.currentTime/audio.duration*100:0};
audio.onloadedmetadata=()=>$("dur").textContent=fmt(audio.duration);
$("seek").oninput=e=>{if(audio.duration)audio.currentTime=e.target.value/100*audio.duration};
audio.volume=.8; $("vol").oninput=e=>audio.volume=e.target.value;
document.onkeydown=e=>{
  if(e.target.tagName==="INPUT"&&e.target.type!=="range")return;
  const k=e.key.toLowerCase();
  if(k===" "){e.preventDefault();toggle()}
  else if(k==="n")berikut(); else if(k==="p")putar(idx-1);
  else if(k==="s")$("acak").click(); else if(k==="r")$("ulang").click();
  else if(e.key==="ArrowRight")audio.currentTime+=5; else if(e.key==="ArrowLeft")audio.currentTime-=5;
};
if("mediaSession" in navigator){
  const m=navigator.mediaSession;
  m.setActionHandler("play",toggle); m.setActionHandler("pause",toggle);
  m.setActionHandler("nexttrack",berikut); m.setActionHandler("previoustrack",()=>putar(idx-1));
}
