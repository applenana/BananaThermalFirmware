// Native SVG illustrations for the Word/PDF manuals; not product photographs.
// Run with the Codex bundled Node runtime and package directory.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const moduleDir = args[args.indexOf('--modules') + 1];
if (!moduleDir) throw new Error('Pass --modules <absolute bundled node_modules>');
const require = createRequire(path.join(moduleDir, '_manual_artwork.cjs'));
const sharp = require('sharp');
const out = path.join(root, 'docs/assets/manual-design');
fs.mkdirSync(out, { recursive: true });
const ink = '#162B3A', orange = '#F0642A', blue = '#236A91';
const svg = (w,h,body) => `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">${body}</svg>`;
const rect=(x,y,w,h,fill,stroke='none',rx=0,sw=2)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
const text=(x,y,s,size=24,color=ink,weight=400)=>`<text x="${x}" y="${y}" font-family="Calibri,Arial,sans-serif" font-size="${size}" font-weight="${weight}" fill="${color}">${s}</text>`;
const line=(x1,y1,x2,y2,color=ink,sw=3,dash='')=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${sw}" ${dash?`stroke-dasharray="${dash}"`:''}/>`;
const circle=(x,y,r,fill,stroke='none',sw=2)=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
const colors=['#17133F','#283682','#226C99','#30A7A1','#A1C958','#F5D653','#F3A13F','#E86B32','#CC3340','#8E1D57'];
function thermal(x,y,w,h) {
  let s='';
  for(let j=0;j<24;j++) for(let i=0;i<32;i++) {
    const v=Math.min(.999, .08+.65*Math.exp(-((i-20)**2/53+(j-9)**2/36))+.25*Math.exp(-((i-8)**2/110+(j-17)**2/45)));
    s+=rect(x+i*w/32,y+j*h/24,w/32+.4,h/24+.4,colors[Math.floor(v*colors.length)]);
  }
  return s;
}
function device(x,y,w,h,rocker=false) {
  let s=rect(x+8,y+14,w,h,'#E4EAF0','none',19);
  s+=rect(x,y,w,h,'#FAFCFD',ink,18,4);
  s+=rect(x+13,y+13,w-26,h-26,'#EAF0F4',ink,12,2);
  s+=rect(x+w*.22,y-14,w*.1,14,ink,'none',3);
  s+=rect(x+w*.61,y-13,w*.07,13,ink,'none',3)+rect(x+w*.73,y-13,w*.07,13,ink,'none',3);
  if(rocker) s+=rect(x+w*.37,y-15,w*.17,15,orange,'none',3);
  s+=thermal(x+27,y+28,w-54,h-56);
  s+=line(x+w*.5-15,y+h*.5,x+w*.5+15,y+h*.5,'#FFFFFF',2);
  s+=line(x+w*.5,y+h*.5-15,x+w*.5,y+h*.5+15,'#FFFFFF',2);
  return s;
}
let standard=device(38,182,365,274)+device(468,120,406,305)+device(939,58,430,323,true);
standard+=text(156,512,'2.4',31,ink,700)+text(616,512,'2.8',31,ink,700)+text(1090,512,'3.2',31,ink,700);
await save('cover-standard',svg(1410,580,standard));
let dual=device(130,120,800,420,true);
dual+=rect(1000,158,245,320,'#FAFCFD',ink,22,4);
for(const y of [235,370]) dual+=circle(1122,y,47,'#EAF0F4',ink,3)+circle(1122,y,27,ink)+circle(1114,y-9,7,'#FFFFFF');
dual+=text(1025,535,'THERMAL + RGB',27,ink,700);
await save('cover-dual',svg(1410,620,dual));

const key=(x,y,label,w=125)=>rect(x,y,w,76,'#162B3A','none',12)+text(x+22,y+49,label,31,'#FFFFFF',700);
let flow='';
for(const [i,label] of ['A+B','A / B','A+B','A / B','A+B'].entries()) {
  const x=35+i*270;
  flow+=circle(x+63,29,19,i===0?orange:blue)+text(x+57,36,String(i+1),20,'#FFFFFF',700);
  flow+=key(x,75,label);
  if(i<4) flow+=line(x+147,113,x+236,113,'#B2C2CC',4)+`<path d="M${x+225},104 l12,9 -12,9" fill="none" stroke="#B2C2CC" stroke-width="4"/>`;
}
await save('menu-flow',svg(1390,195,flow));

let view=rect(20,20,1020,555,'#F1F5F8','none',18)+thermal(46,45,850,505);
view+=rect(927,45,32,505,'none',ink,0,2);
for(let i=0;i<10;i++) view+=rect(928,46+i*50.3,30,50.4,colors[9-i]);
view+=text(969,67,'MAX',20)+text(969,548,'MIN',20);
view+=line(470,290,510,290,'#FFFFFF',3)+line(490,270,490,310,'#FFFFFF',3);
view+=circle(490,290,22,'none','#FFFFFF',2);
view+=circle(660,235,14,'#FFFFFF',ink,3);
view+=line(454,326,476,305,orange,3)+circle(433,345,24,orange)+text(425,354,'1',25,'#FFFFFF',700);
view+=line(695,208,673,225,orange,3)+circle(719,190,24,orange)+text(711,199,'2',25,'#FFFFFF',700);
view+=circle(1007,296,24,orange)+text(999,305,'3',25,'#FFFFFF',700);
await save('thermal-view',svg(1080,600,view));

let alarm=rect(0,0,1400,420,'#FFFFFF');
alarm+=line(100,35,100,340,'#8CA0AD',2)+line(100,340,1340,340,'#8CA0AD',2);
alarm+=line(100,135,1340,135,orange,2,'12 10')+line(100,230,1340,230,blue,2,'12 10');
alarm+=text(24,145,'60°C',27,orange,700)+text(24,240,'58°C',27,blue,700);
alarm+=`<path d="M110,292 C210,290 240,140 340,100 C450,40 550,70 640,105 C730,140 810,165 900,205 C980,242 1080,278 1190,280 L1335,280" fill="none" stroke="${ink}" stroke-width="7" stroke-linecap="round"/>`;
alarm+=circle(298,135,10,orange)+circle(956,230,10,blue);
alarm+=text(205,391,'01',27,orange,700)+text(537,391,'02',27,orange,700)+text(945,391,'03',27,blue,700);
await save('alarm-hysteresis',svg(1400,420,alarm));

let alignment='';
for(let i=0;i<3;i++) {
  const x=18+i*464;
  alignment+=rect(x,15,430,280,'#F2F6F8','none',12);
  alignment+=rect(x+120,86,115,115,'none',orange,14,5);
  alignment+=rect(x+(i===0?161:i===1?144:120),i===0?104:86,i===0?83:115,i===0?83:115,'none',blue,14,5);
  alignment+=circle(x+30,45,17,ink)+text(x+24,51,String(i+1),18,'#FFFFFF',700);
}
await save('alignment',svg(1400,330,alignment));

async function save(name,data) {
  fs.writeFileSync(path.join(out,name+'.svg'),data);
  await sharp(Buffer.from(data)).resize({width:2400}).png().toFile(path.join(out,name+'.png'));
}
