// Exact instructional diagrams, separate from the original hardware line art.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const modules = process.argv[process.argv.indexOf('--modules') + 1];
const require = createRequire(path.join(modules, '_parallax_artwork.cjs'));
const sharp = require('sharp');
const out = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../docs/assets/manual-design');
const ink = '#162B3A', blue = '#236A91', orange = '#C44D16', gray = '#69757D';
const text = (x,y,s,size=35,color=ink,anchor='middle') => `<text x="${x}" y="${y}" text-anchor="${anchor}" font-family="Microsoft YaHei,SimHei,sans-serif" font-size="${size}" fill="${color}">${s}</text>`;
const rect = (x,y,w,h,color='white',stroke=ink,sw=3) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="7" fill="${color}" stroke="${stroke}" stroke-width="${sw}"/>`;
const line = (x1,y1,x2,y2,color=ink,sw=4,extra='') => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${sw}" ${extra}/>`;
const arrow = (x1,y1,x2,y2,color=ink) => {
  const a=Math.atan2(y2-y1,x2-x1), n=17;
  return line(x1,y1,x2,y2,color,6)+`<path d="M ${x2-n*Math.cos(a-.48)} ${y2-n*Math.sin(a-.48)} L ${x2} ${y2} L ${x2-n*Math.cos(a+.48)} ${y2-n*Math.sin(a+.48)}" fill="none" stroke="${color}" stroke-width="6"/>`;
};
// The asymmetric L-shaped target makes orientation and overlap easy to judge.
const target = (x,y,kind,ghost=false) => `<path d="M ${x-37} ${y-40} h 37 v 24 h 37 v 56 h -74 Z" fill="${kind==='heat'?'url(#heat)':'none'}" stroke="${kind==='heat'?orange:blue}" stroke-width="${kind==='heat'?3:7}" ${ghost?'stroke-dasharray="9 7" opacity=".32"':''}/>`;
const defs = `<defs><pattern id="heat" width="13" height="13" patternUnits="userSpaceOnUse"><rect width="13" height="13" fill="#FBE1CC"/><path d="M -3 3 L 3 -3 M 0 13 L 13 0 M 10 16 L 16 10" stroke="${orange}" stroke-width="2"/></pattern></defs>`;
async function save(name,height,body) {
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="${height}" viewBox="0 0 1000 ${height}">${defs}<rect width="1000" height="${height}" fill="white"/>${body}</svg>`;
  fs.writeFileSync(path.join(out,`parallax-${name}.svg`),svg);
  await sharp(Buffer.from(svg)).resize({width:2400}).png().toFile(path.join(out,`parallax-${name}.png`));
}

// Top view, two parallel optical axes and the same centred target at two depths.
let origin='';
for (const [ox,near] of [[0,true],[510,false]]) {
  const ty=near?290:130, left=ox+155, right=ox+335, tx=ox+245;
  origin+=text(tx,50,near?'近距离目标':'远距离目标',40);
  origin+=line(left,500,left,105,gray,2,'stroke-dasharray="10 8"')+line(right,500,right,105,gray,2,'stroke-dasharray="10 8"');
  origin+=line(left,500,tx,ty,blue,5)+line(right,500,tx,ty,orange,5);
  origin+=rect(tx-30,ty-20,60,40,'#EDF2F5',ink,3);
  origin+=`<circle cx="${left}" cy="500" r="23" fill="white" stroke="${blue}" stroke-width="6"/><circle cx="${right}" cy="500" r="23" fill="url(#heat)" stroke="${orange}" stroke-width="4"/>`;
  origin+=text(left,565,'可见光',34,blue)+text(right,565,'热像',34,orange);
  origin+=text(tx,630,near?'两路观察方向差较大':'两路观察方向差较小',34);
}
await save('principle',670,origin);

const cameraCases = [
  ['X偏移 增大','摄像头向下',0,55], ['X偏移 减小','摄像头向上',0,-55],
  ['Y偏移 增大','摄像头向右',65,0], ['Y偏移 减小','摄像头向左',-65,0],
];
const thermalCases = [
  ['热像X 增大','热像向左',-65,0], ['热像X 减小','热像向右',65,0],
  ['热像Y 增大','热像向上',0,-55], ['热像Y 减小','热像向下',0,55],
];
async function directions(name,cases,moving) {
  let body='';
  for (let j=0;j<cases.length;j++) {
    const [label,move,dx,dy]=cases[j], x=20+(j%2)*500,y=15+Math.floor(j/2)*365,cx=x+230,cy=y+165;
    body+=text(cx,y+35,label,39)+rect(x+20,y+64,420,205,'white','#BCC7CE',2);
    body+=target(cx,cy,moving==='camera'?'heat':'camera');
    body+=target(cx,cy,moving==='camera'?'camera':'heat',true);
    body+=target(cx+dx,cy+dy,moving==='camera'?'camera':'heat');
    // Arrow uses an uncluttered screen edge, with same motion as the target.
    const ax=dx===0?cx+145:cx, ay=dx===0?cy:cy+76;
    body+=arrow(ax-dx*.35,ay-dy*.35,ax+dx*.65,ay+dy*.65,moving==='camera'?blue:orange);
    body+=text(cx,y+320,move,36,moving==='camera'?blue:orange);
  }
  body+=line(80,758,160,758,blue,7)+text(177,770,'可见光轮廓',33,ink,'start');
  body+=rect(570,740,65,30,'url(#heat)',orange,3)+text(655,770,'热像热区',33,ink,'start');
  await save(name,800,body);
}
await directions('camera-directions',cameraCases,'camera');
await directions('thermal-directions',thermalCases,'heat');

// A consistent example: camera starts lower-right, X decrease moves it up,
// then Y decrease moves it left. No assumed numeric step or invented UI screenshot.
let worked='';
for (const [index,label,dx,dy] of [[0,'观察重影',90,55],[1,'减小 X偏移',90,0],[2,'减小 Y偏移',0,0]]) {
  const y=index*245;
  worked+=text(30,y+47,`0${index+1}`,39,ink,'start')+text(130,y+47,label,38,ink,'start');
  worked+=rect(430,y+15,520,205,'white','#BCC7CE',2);
  worked+=target(650,y+117,'heat')+target(650+dx,y+117+dy,'camera');
  if(index===0) worked+=text(130,y+111,'轮廓偏右下',34,gray,'start');
  if(index===1) worked+=arrow(830,y+175,830,y+85,blue)+text(130,y+111,'先向上对齐',34,blue,'start');
  if(index===2) worked+=arrow(865,y+166,775,y+166,blue)+text(130,y+111,'再向左重合',34,blue,'start');
}
await save('worked-example',740,worked);
console.log('Generated four parallax SVG sources and print PNGs.');
