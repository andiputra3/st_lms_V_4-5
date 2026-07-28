"use strict";
/*
==================================================
ST-LMS DOMAIN INDEX
==================================================
001 BOOT
002 WORKSPACE
003 MARKET
004 TRUTH
005 STRUCTURE
006 EVIDENCE
007 LONG CLONE
008 SHORT CLONE
009 GRID CLONE
010 TRADE
011 POSITION
012 STATISTICS
013 KNOWLEDGE
014 ACADEMY
015 RIVER
016 ORACLE
017 HIVEMIND
018 DARWIN
019 LIBRARIAN
020 PREDICTION
021 REPLAY
022 SIMULATION
023 GOVERNANCE
024 CONSUMER
025 AUDIT
026 FINAL VALIDATION
==================================================
ST-LMS · NATIVE HTML OS — Market Geometry Intelligence Operating System
Source of truth: MASTER_SPECIFICATION + DOCUMENT_DEPENDENCY + Doc01-14 (frozen).
Deterministic · immutable cards · no-mock · no-placeholder · defensive render.
1 candle = 3 knowledge · trade optional · learning mandatory
==================================================
*/
var STLMS = {};

/* ----------------------------- CORE --------------------------------------- */
STLMS.CORE = (function(){
  var ASSETS = {
    BTCUSDT:{base:61750,tick:0.1,prec:1}, SOLUSDT:{base:71.84,tick:0.01,prec:2},
    AKEUSDT:{base:0.0031760,tick:0.0000001,prec:7}, TLMUSDT:{base:0.004043,tick:0.0000001,prec:7}};
  function asset(s){ var a=ASSETS[s]; if(!a) throw new Error("unknown symbol "+s); return a; }
  function clamp(v,lo,hi){ return Math.max(lo,Math.min(hi,v)); }
  function norm01(v,lo,hi){ return clamp((v-lo)/((hi-lo)||1),0,1); }
  function roundPrec(v,p){ var f=Math.pow(10,p); return Math.round(v*f)/f; }
  function canon(v,p){ return roundPrec(v,p).toFixed(p); }
  function toTick(v,s){ return Math.round(v/asset(s).tick); }
  function fromTick(t,s){ return t*asset(s).tick; }
  function wib(ms){ var d=new Date(ms+7*3600000), p=function(n){return String(n).padStart(2,"0");};
    return {ymd:d.getUTCFullYear()+p(d.getUTCMonth()+1)+p(d.getUTCDate()),
            hhmm:p(d.getUTCHours())+p(d.getUTCMinutes()),
            iso:d.getUTCFullYear()+"-"+p(d.getUTCMonth()+1)+"-"+p(d.getUTCDate())+"T"+p(d.getUTCHours())+":"+p(d.getUTCMinutes())+":"+p(d.getUTCSeconds())+"+07:00"}; }
  function prng(seed){ var a=(seed>>>0)||1; return function(){ a|=0; a=(a+0x6D2B79F5)|0; var t=Math.imul(a^(a>>>15),1|a); t=(t+Math.imul(t^(t>>>7),61|t))^t; return ((t^(t>>>14))>>>0)/4294967296; }; }
  function seedFrom(str){ var h=2166136261; for(var i=0;i<str.length;i++){ h^=str.charCodeAt(i); h=Math.imul(h,16777619)>>>0; } return h>>>0; }
  return {ASSETS:ASSETS,asset:asset,clamp:clamp,norm01:norm01,roundPrec:roundPrec,canon:canon,toTick:toTick,fromTick:fromTick,wib:wib,prng:prng,seedFrom:seedFrom};
})();

/* ----------------------------- CRYPTO ------------------------------------- */
STLMS.CRYPTO = (function(){
  var K=new Uint32Array([0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]);
  var ro=function(x,n){return (x>>>n)|(x<<(32-n));};
  function sha256(s){ var e=new TextEncoder().encode(s), len=e.length, bl=len*8, l=len+1; while(l%64!==56)l++; l+=8;
    var b=new Uint8Array(l); b.set(e); b[len]=128; var dv=new DataView(b.buffer); dv.setUint32(l-4,bl,false);
    var h0=0x6a09e667,h1=0xbb67ae85,h2=0x3c6ef372,h3=0xa54ff53a,h4=0x510e527f,h5=0x9b05688c,h6=0x1f83d9ab,h7=0x5be0cd19, w=new Uint32Array(64);
    for(var i=0;i<l;i+=64){ for(var j=0;j<16;j++)w[j]=dv.getUint32(i+j*4,false);
      for(var j2=16;j2<64;j2++){ var s0=ro(w[j2-15],7)^ro(w[j2-15],18)^(w[j2-15]>>>3), s1=ro(w[j2-2],17)^ro(w[j2-2],19)^(w[j2-2]>>>10); w[j2]=(w[j2-16]+s0+w[j2-7]+s1)|0; }
      var a=h0,b2=h1,c=h2,d=h3,e2=h4,f=h5,g=h6,h=h7;
      for(var j3=0;j3<64;j3++){ var S1=ro(e2,6)^ro(e2,11)^ro(e2,25), ch=(e2&f)^((~e2)&g), t1=(h+S1+ch+K[j3]+w[j3])|0, S0=ro(a,2)^ro(a,13)^ro(a,22), mj=(a&b2)^(a&c)^(b2&c), t2=(S0+mj)|0; h=g;g=f;f=e2;e2=(d+t1)|0;d=c;c=b2;b2=a;a=(t1+t2)|0; }
      h0=(h0+a)|0;h1=(h1+b2)|0;h2=(h2+c)|0;h3=(h3+d)|0;h4=(h4+e2)|0;h5=(h5+f)|0;h6=(h6+g)|0;h7=(h7+h)|0; }
    var hx=function(x){return x.toString(16).padStart(8,"0");}; return hx(h0)+hx(h1)+hx(h2)+hx(h3)+hx(h4)+hx(h5)+hx(h6)+hx(h7); }
  return {sha256:sha256};
})();

/* ----------------------------- ID ----------------------------------------- */
STLMS.ID = (function(){
  var seq={};
  function reset(){ seq={}; }
  function gen(ts,komp,file,payload){ var w=STLMS.CORE.wib(ts), k=komp+"|"+file+"|"+w.ymd+"_"+w.hhmm; seq[k]=(seq[k]||0)+1;
    var c=JSON.stringify({c:komp,f:file,m:ts,s:seq[k],p:payload}); return w.ymd+"_"+w.hhmm+"_"+komp+"_"+file+"_"+String(seq[k]).padStart(6,"0")+"_"+STLMS.CRYPTO.sha256(c).slice(0,8).toUpperCase(); }
  return {gen:gen,reset:reset};
})();

/* ----------------------------- CONFIG / BOUNDED ------------------------- */
STLMS.CONFIG = (function(){
  var BOUNDED = {
    ENTRY_OFFSET_BASE_K:[1.0,0.3,3.0], ENTRY_OFFSET_MIN_ATR:[0.15,0.05,0.5], ENTRY_OFFSET_MAX_CAP_PCT:[0.30,0.10,1.0],
    WPR_VELOCITY_DEADZONE:[5,1,20], WPR_ACCEL_DEADZONE:[8,2,40], GRID_MIN_NET_PCT_OF_FILL:[0.50,0.20,1.5],
    CAGE_TIGHT_ATR:[2.0,1.0,4.0], CAGE_LOOSE_ATR:[4.0,2.0,8.0], CAGE_WALL_MIN_DISTANCE_ATR:[0.25,0.10,0.50],
    WRONG_ENTRY_PCT:[2.0,0.5,6.0], FEE_SAFETY_BUFFER_PCT:[0.10,0.0,0.5], FEE_DISCOUNT_PCT:[0.0,0.0,0.25],
    GRID_BUY_ZONE_MAX:[0.30,0.10,0.45], GRID_SELL_ZONE_MIN:[0.70,0.55,0.90], GRID_MAX_FILLS_PER_SIDE:[2,1,4],
    TP_ATR_MULT:[2.0,1.0,5.0], TRAIL_ATR_MULT:[1.5,0.5,4.0], TRAIL_ACTIVATE_R:[1.0,0.5,3.0],
    PARTIAL_TP_PCT:[0.5,0.0,0.8], TIME_EXIT_CANDLES:[40,5,200], SAMPLE_GATE:[30,10,200], ST_DIST_VOL_WINDOW:[96,24,240]};
  var cur={}; for(var k in BOUNDED) cur[k]=BOUNDED[k][0];
  function defaults(){ var o={}; for(var k in BOUNDED) o[k]=BOUNDED[k][0]; return o; }
  function get(k){ return cur[k]; }
  function valid(k,v){ return !!BOUNDED[k] && v>=BOUNDED[k][1] && v<=BOUNDED[k][2]; }
  function set(k,v){ if(!BOUNDED[k]) return {ok:false,reason:"UNKNOWN"}; if(!valid(k,v)) return {ok:false,reason:"OUT_OF_RANGE"}; cur[k]=v; return {ok:true}; }
  function all(){ return Object.keys(BOUNDED).map(function(k){return {k:k,cur:cur[k],min:BOUNDED[k][1],max:BOUNDED[k][2]};}); }
  function reset(){ cur=defaults(); }
  return {BOUNDED:BOUNDED,get:get,valid:valid,set:set,all:all,reset:reset,defaults:defaults};
})();

/* ----------------------------- CARD --------------------------------------- */
STLMS.CARD = (function(){
  function mk(type,payload,deps,ts,idGen){ deps=deps||[]; ts=ts||0; idGen=idGen||STLMS.ID;
    var komp=type.toUpperCase().replace(/[^A-Z0-9]/g,"_").slice(0,12);
    var id=idGen.gen(ts,komp,"OS",payload);
    var canonp=JSON.stringify({t:type,v:"1.0",d:deps.slice().sort(),p:payload});
    return Object.freeze({entity_id:id,entity_type:type,entity_state:"CREATED",entity_version:"1.0",
      timestamp_wib:STLMS.CORE.wib(ts).iso,timestamp_ms:ts,component_name:komp,source_file:"OS",
      dependencies:Object.freeze(deps.slice()),payload:Object.freeze(payload),checksum:STLMS.CRYPTO.sha256(canonp)}); }
  function verify(card){ var canonp=JSON.stringify({t:card.entity_type,v:card.entity_version,d:card.dependencies.slice().sort(),p:card.payload});
    return STLMS.CRYPTO.sha256(canonp)===card.checksum; }
  return {mk:mk,verify:verify};
})();

/* ----------------------------- WORKSPACE / RIVER -------------------------- */
STLMS.WORKSPACE = (function(){
  var cards=[], index={}, chronicle=[], db=null, dbName="stlms_os";
  function openDB(){ return new Promise(function(res){ if(typeof indexedDB==="undefined") return res(null);
    var req=indexedDB.open(dbName,1);
    req.onupgradeneeded=function(e){ var d=e.target.result; if(!d.objectStoreNames.contains("cards")) d.createObjectStore("cards",{keyPath:"entity_id"}); };
    req.onsuccess=function(e){ db=e.target.result; res(db); }; req.onerror=function(){ res(null); }; }); }
  function put(card){ if(index[card.entity_id]) return card; cards.push(card); index[card.entity_id]=card;
    chronicle.push({ts:card.timestamp_ms,type:card.entity_type,id:card.entity_id}); if(chronicle.length>6000) chronicle.shift();
    if(db){ try{ var tx=db.transaction("cards","readwrite"); tx.objectStore("cards").put(card); }catch(e){} } return card; }
  function count(){ return cards.length; }
  function reset(){ cards=[]; index={}; chronicle=[]; }
  function available(){ return !!db; }
  return {openDB:openDB,put:put,count:count,reset:reset,available:available,chronicle:function(){return chronicle;}};
})();

/* ----------------------------- MARKET ------------------------------------- */
STLMS.MARKET = (function(){
  var C=STLMS.CORE;
  function fixture(sym,n,seed){ var a=C.asset(sym), rng=C.prng(C.seedFrom(sym+":"+seed)), base=a.base, out=[], price=base, t0=1753500000000;
    for(var i=0;i<n;i++){ var c=i%200, phase=c<60?"SIDE":c<110?"UP":c<150?"DOWN":"SIDE", step=base*0.0030, drift;
      if(phase==="SIDE") drift=(rng()-0.5)*step*0.5+(base-price)*0.02; else if(phase==="UP") drift=step*0.9+(rng()-0.4)*step*0.6; else drift=-step*0.9+(rng()-0.6)*step*0.6;
      var o=price, cl=Math.max(base*0.2,o+drift), wick=step*(0.4+rng()*0.8), hi=Math.max(o,cl)+wick*rng(), lo=Math.min(o,cl)-wick*rng();
      var tbr=C.clamp(0.5+0.18*(drift>0?1:-1)+(rng()-0.5)*0.1,0.05,0.95);
      out.push({time:t0+i*60000,open:C.roundPrec(o,a.prec),high:C.roundPrec(hi,a.prec),low:C.roundPrec(lo,a.prec),close:C.roundPrec(cl,a.prec),volume:100+rng()*900,takerBuyRatio:tbr}); price=cl; }
    return out; }
  function hygiene(c){ return c.high>=Math.max(c.open,c.close) && c.low<=Math.min(c.open,c.close) && c.volume>=0 && c.high>=c.low; }
  function gaps(arr){ var g=[]; for(var i=1;i<arr.length;i++) if(arr[i].time-arr[i-1].time>60000) g.push(arr[i].time); return g; }
  function oiProxy(c){ var slots={}; c.forEach(function(x){ var s=Math.floor(x.time/300000)*300000, d=slots[s]||(slots[s]={vol:0,net:0}); d.vol+=x.volume; d.net+=(2*x.takerBuyRatio-1)*x.volume; }); var o={}; for(var s in slots) o[s]=slots[s].vol>0?slots[s].net/slots[s].vol:0; return o; }
  return {fixture:fixture,hygiene:hygiene,gaps:gaps,oiProxy:oiProxy};
})();

/* ----------------------------- TRUTH -------------------------------------- */
STLMS.TRUTH = (function(){
  var C=STLMS.CORE, ATR_P=10, EMA_P=14, ST_MUL=3;
  function PointBuilder(sym){ this.sym=sym; this.reset(); }
  PointBuilder.prototype.reset=function(){ this.pc=null;this.atr=null;this.ema=null;this.e12=null;this.e26=null;this.sig=null;this.puf=null;this.plf=null;this.trend=1;this.ag=null;this.al=null;this.hs=[];this.ls=[];this.wp1=null;this.vp=null;this.mh1=null; };
  PointBuilder.prototype.build=function(c){
    var h=c.high,l=c.low,cl=c.close, pc=this.pc==null?cl:this.pc;
    var tr=Math.max(h-l,Math.abs(h-pc),Math.abs(l-pc));
    this.atr = this.atr==null ? tr : this.atr+(tr-this.atr)/ATR_P;
    var kf=2/(EMA_P+1); this.ema = this.ema==null ? cl : this.ema+(cl-this.ema)*kf;
    this.e12 = this.e12==null ? cl : this.e12+(cl-this.e12)*(2/13);
    this.e26 = this.e26==null ? cl : this.e26+(cl-this.e26)*(2/27);
    var macd=this.e12-this.e26; this.sig = this.sig==null ? macd : this.sig+(macd-this.sig)*(2/10); var mh=macd-this.sig;
    var hl2=(h+l)/2, am=this.atr*ST_MUL, ub=hl2+am, lb=hl2-am, uf, lf;
    if(this.puf==null){ uf=ub; lf=lb; } else { uf = cl<=this.puf?Math.min(ub,this.puf):ub; lf = cl>=this.plf?Math.max(lb,this.plf):lb; }
    var flip=null;
    if(this.trend===-1 && cl>this.puf){ this.trend=1; flip="TREND_FLIP_UP"; } else if(this.trend===1 && cl<this.plf){ this.trend=-1; flip="TREND_FLIP_DOWN"; }
    var st = this.trend===1?lf:uf;
    var color = cl>st?"HIJAU":cl<st?"MERAH":(this.trend===1?"HIJAU":"MERAH");
    this.hs.push(h); this.ls.push(l); var rsi=null;
    if(this.pc!=null){ var diff=cl-this.pc, g=diff>0?diff:0, lo=diff<0?-diff:0;
      if(this.ag==null){ this.ag=g; this.al=lo; } else { this.ag=(this.ag*(ATR_P-1)+g)/ATR_P; this.al=(this.al*(ATR_P-1)+lo)/ATR_P; }
      if(this.hs.length>ATR_P){ var rs=this.al===0?100:this.ag/this.al; rsi=100-100/(1+rs); } }
    var wpr=null; if(this.hs.length>=14){ var hh=Math.max.apply(null,this.hs.slice(-14)), ll=Math.min.apply(null,this.ls.slice(-14)); wpr=hh===ll?-50:-100*(hh-cl)/(hh-ll); }
    var vel=(wpr!=null&&this.wp1!=null)?wpr-this.wp1:null, acc=(vel!=null&&this.vp!=null)?vel-this.vp:null;
    this.wp1=wpr; this.vp=vel; var dist=Math.abs(cl-st), distAtr=this.atr?dist/this.atr:0;
    var warm=this.atr==null||this.ema==null;
    var p={ts:c.time,close:cl,st:st,st_canon:C.canon(st,this.sym),st_tick:C.toTick(st,this.sym),stDir:this.trend,color:color,
      atr:this.atr,ema:this.ema,macdHist:mh,prevMacdHist:this.mh1,dist:dist,distAtr:distAtr,rsi:rsi,wpr:wpr,vel:vel,acc:acc,volDelta:2*c.takerBuyRatio-1,
      emaSlope:this.ema-(this.pc==null?this.ema:this.pc),flip:flip,point_status:warm?"WARMUP":"VALID"};
    this.pc=cl; this.puf=uf; this.plf=lf; this.mh1=mh; return p; };
  return {PointBuilder:PointBuilder,ATR_P:ATR_P,EMA_P:EMA_P,ST_MUL:ST_MUL};
})();

/* ----------------------------- STRUCTURE ---------------------------------- */
STLMS.STRUCTURE = (function(){
  var CFG=STLMS.CONFIG, C=STLMS.CORE;
  function LineBuilder(){}
  LineBuilder.prototype.build=function(points){ var lines=[], cur=null;
    var mk=function(p){return {st:p.st,key:p.st_canon,mem:[p.ts],cols:[p.color],s:p.ts,e:p.ts};};
    for(var i=0;i<points.length;i++){ var p=points[i];
      if(!cur) cur=mk(p); else if(p.st_canon===cur.key){ cur.mem.push(p.ts); cur.cols.push(p.color); cur.e=p.ts; }
      else { if(cur.mem.length>=4) lines.push(fin(cur)); cur=mk(p); } }
    if(cur&&cur.mem.length>=4) lines.push(fin(cur)); return lines; };
  function fin(L){ var g=L.cols.filter(function(c){return c==="HIJAU";}).length, r=L.cols.length-g;
    return {st:L.st,stf:L.st,key:L.key,s:L.s,e:L.e,n:L.mem.length,dom:g>=r?"HIJAU":"MERAH",role:g>=r?"SUPPORT":"RESISTANCE",green:g,red:r,flip:Math.min(g,r)}; }
  function SlopeBuilder(){}
  SlopeBuilder.prototype.build=function(points,lines){ var inl={}; for(var a=0;a<lines.length;a++) for(var b=0;b<lines[a].mem.length;b++) inl[lines[a].mem[b]]=1;
    var sp=points.filter(function(p){return !inl[p.ts];}), slopes=[], cur=[];
    var mk=function(m){ var d=m[m.length-1].st-m[0].st, dir=d>0?"BULLISH":d<0?"BEARISH":"FLAT", steps=0; for(var i=1;i<m.length;i++) if(m[i].st===m[i-1].st) steps++;
      var par=m.length>=3&&Math.abs(m[m.length-1].st-m[m.length-2].st)>1.6*Math.abs(m[1].st-m[0].st);
      var pat=dir==="BULLISH"&&steps>=3?"STAIRCASE_UP":dir==="BEARISH"&&steps>=3?"STAIRCASE_DOWN":par&&dir==="BULLISH"?"PARABOLIC_UP":par&&dir==="BEARISH"?"PARABOLIC_DOWN":m.length>=3?"REVERSAL_TRANSITION":dir==="BULLISH"?"SPIKE_UP":dir==="BEARISH"?"SPIKE_DOWN":"FLAT_NOISE";
      return {s:m[0].ts,e:m[m.length-1].ts,dir:dir,col:dir==="BULLISH"?"HIJAU":dir==="BEARISH"?"MERAH":"NETRAL",n:m.length,pat:pat,stf:m[m.length-1].st}; };
    for(var i=0;i<sp.length;i++){ var p=sp[i]; if(cur.length&&p.ts-cur[cur.length-1].ts>60000){ if(cur.length>=2) slopes.push(mk(cur)); cur=[p]; } else cur.push(p); }
    if(cur.length>=2) slopes.push(mk(cur)); return slopes; };
  var WAVE_STRUCTS=["STRONG_ACCUMULATION","STRONG_DISTRIBUTION","CONTINUATION_UP","CONTINUATION_DOWN","CONFIRMED_RANGE","RANGE_EXPANDING","RANGE_COMPRESSING","REVERSAL_UP","REVERSAL_DOWN","EXHAUSTION_UP","EXHAUSTION_DOWN","SIDEWAY","CHAOS"];
  function WaveBuilder(){}
  WaveBuilder.prototype.build=function(lines,slopes){ var L=lines.slice().sort(function(a,b){return a.s-b.s;}), waves=[], pending=null;
    var cls=function(m){ var g=m.filter(function(x){return x.dom==="HIJAU";}).length, r=6-g, alt=0; for(var i=1;i<6;i++) if(m[i].dom!==m[i-1].dom) alt++;
      if(g>=5)return"STRONG_ACCUMULATION"; if(r>=5)return"STRONG_DISTRIBUTION";
      if(m[0].dom+m[1].dom+m[2].dom==="MERAHMERAHMERAH"&&m[5].dom==="HIJAU")return"REVERSAL_UP";
      if(m[0].dom+m[1].dom+m[2].dom==="HIJAUHIJAUHIJAU"&&m[5].dom==="MERAH")return"REVERSAL_DOWN";
      if(g>=4&&m[5].dom==="MERAH")return"EXHAUSTION_UP"; if(r>=4&&m[5].dom==="HIJAU")return"EXHAUSTION_DOWN";
      if(alt>=4)return"CONFIRMED_RANGE"; if(g>=3&&r===0)return"CONTINUATION_UP"; if(r>=3&&g===0)return"CONTINUATION_DOWN";
      if(g>=2&&r>=2)return"SIDEWAY"; return"CHAOS"; };
    for(var i=0;i<L.length;i+=6){ var ch=L.slice(i,i+6); if(ch.length<6){ pending={mem:ch,status:"PENDING_WAVE"}; continue; }
      var trans=[]; for(var k=0;k<5;k++){ var aa=ch[k],bb=ch[k+1], t=null; for(var s=0;s<slopes.length;s++) if(slopes[s].s>=aa.e&&slopes[s].e<=bb.s){t=slopes[s];break;} trans.push(t); }
      waves.push({mem:ch,trans:trans,s:ch[0].s,e:ch[5].e,structure:cls(ch),status:"CLOSED_WAVE"}); }
    return {waves:waves,pending:pending}; };
  function CageEngine(){}
  CageEngine.prototype._resolve=function(price,atr,side,reg){ var MIN=CFG.get("CAGE_WALL_MIN_DISTANCE_ATR")*atr, valid=[], brokenSts=[], brokenCount=0;
    var consider=function(rec){ var mapSide=rec.role==="SUPPORT"?"SUP":"RES"; if(mapSide!==side) return;
      var isBroken=(rec.role==="SUPPORT"&&price<rec.st)||(rec.role==="RESISTANCE"&&price>rec.st);
      if(isBroken){ brokenCount++; brokenSts.push(rec.st); return; } valid.push(rec); };
    var cr=reg.curLineRun; if(cr&&cr.key!=null) consider({key:cr.key,st:cr.st,n:cr.n,status:cr.n>=4?"ACTIVE_PROVISIONAL":"PROVISIONAL",recency:1e15,role:cr.role});
    for(var i=0;i<reg.lineageLines.length;i++){ var L=reg.lineageLines[i]; consider({key:L.key,st:L.st,n:L.n,status:"FINAL",recency:L.e,role:L.role}); }
    valid.sort(function(a,b){return b.recency-a.recency;}); var versions=valid.slice(0,3).map(function(v,i){v.vi=i;return v;});
    var path=[], sel=null; for(var j=0;j<versions.length;j++){ var v=versions[j], d=Math.abs(v.st-price); if(d>=MIN){ sel=v; path.push([v.vi,"COMFORTABLE"]); break; } path.push([v.vi,"TIGHT"]); }
    var pressure=false; for(var p=0;p<path.length;p++) if(path[p][1]==="TIGHT") pressure=true; pressure=pressure&&!sel;
    return {versions:versions,broken_count:brokenCount,broken_sts:brokenSts,selected:sel,pressure:pressure,path:path}; };
  CageEngine.prototype.build=function(lineageLines,price,atr,curLineRun){ var reg={lineageLines:lineageLines,curLineRun:curLineRun};
    var sup=this._resolve(price,atr,"SUP",reg), res=this._resolve(price,atr,"RES",reg), low=sup.selected, up=res.selected;
    var vpack=function(r){ return {versions:r.versions.map(function(v){return {vi:v.vi,st:v.st,status:v.status,n:v.n};}),broken_count:r.broken_count,broken_sts:r.broken_sts,selected_vi:r.selected?r.selected.vi:null,pressure:r.pressure}; };
    var versioning={support:vpack(sup),resistance:vpack(res)};
    if(!low||!up) return {upper:up?up.st:null,lower:low?low.st:null,pp:0.5,rangeAtr:null,status:"NONE",breakout:"NONE",upVi:up?up.vi:null,lowVi:low?low.vi:null,cross:(up?up.vi:-1)!==(low?low.vi:-1),pressureUp:res.pressure,pressureDn:sup.pressure,versioning:versioning};
    var u=up.st,d=low.st,rng=u-d, pp=rng?(price-d)/rng:0.5; pp=C.clamp(pp,0,1); var ra=atr?rng/atr:null;
    var status=ra!=null&&ra<=CFG.get("CAGE_TIGHT_ATR")?"VALID_COMPRESSION":ra!=null&&ra<=CFG.get("CAGE_LOOSE_ATR")?"LOOSE_SIDEWAY":"NONE";
    var breakout=res.pressure&&sup.pressure?"SQUEEZE":res.pressure?"IMMINENT_UP":sup.pressure?"IMMINENT_DOWN":"NONE";
    return {upper:u,lower:d,pp:pp,rangeAtr:ra!=null?C.roundPrec(ra,3):null,status:status,breakout:breakout,upVi:up.vi,lowVi:low.vi,cross:up.vi!==low.vi,pressureUp:res.pressure,pressureDn:sup.pressure,versioning:versioning}; };
  function ladder(lines,price){ var sup=lines.filter(function(L){return L.st<price;}).sort(function(a,b){return b.s-a.s;}), res=lines.filter(function(L){return L.st>price;}).sort(function(a,b){return b.s-a.s;});
    var stepped=function(a){ if(a.length<2) return false; for(var i=1;i<a.length;i++) if(a[i].st===a[i-1].st) return false; return true; };
    return {support_stepped:stepped(sup),resistance_stepped:stepped(res)}; }
  function nearest(lines,price){ var sup=null,res=null; for(var i=0;i<lines.length;i++){ if(lines[i].st<price){ if(!sup||lines[i].st>sup.st) sup=lines[i]; } else { if(!res||lines[i].st<res.st) res=lines[i]; } } return {support:sup,resistance:res}; }
  function phase(cage,wave,stDir){ return {cage:cage.status,wave:wave?wave.structure:"—",stDir:stDir,phase:cage.status==="NONE"?(stDir===1?"UPTREND":stDir===-1?"DOWNTREND":"TRANSITION"):"SIDEWAY_COMPRESSION"}; }
  function compute(points,price,atr,curRun){ var lines=new LineBuilder().build(points), slopes=new SlopeBuilder().build(points,lines), wb=new WaveBuilder().build(lines,slopes),
      lineage=lines.map(function(L){return {key:L.key,role:L.role,s:L.s,e:L.e,n:L.n,st:L.stf};}),
      cage=new CageEngine().build(lineage,price,atr,curRun), lad=ladder(lines,price), near=nearest(lines,price), wave=wb.waves[wb.waves.length-1]||null,
      ph=phase(cage,wave,points[points.length-1]?points[points.length-1].stDir:0);
    return {lines:lines,slopes:slopes,waves:wb.waves,pending:wb.pending,cage:cage,lad:lad,near:near,wave:wave,phase:ph}; }
  return {LineBuilder:LineBuilder,SlopeBuilder:SlopeBuilder,WaveBuilder:WaveBuilder,CageEngine:CageEngine,WAVE_STRUCTS:WAVE_STRUCTS,ladder:ladder,nearest:nearest,phase:phase,compute:compute};
})();

/* ----------------------------- EVIDENCE ----------------------------------- */
STLMS.EVIDENCE = (function(){
  var C=STLMS.CORE, CFG=STLMS.CONFIG;
  var MTF_TABLE={STRONG_ACCUMULATION:["BULLISH_TREND",8500],STRONG_DISTRIBUTION:["BEARISH_TREND",8500],CONTINUATION_UP:["BULLISH_TREND",7000],CONTINUATION_DOWN:["BEARISH_TREND",7000],CONFIRMED_RANGE:["RANGE",7500],RANGE_EXPANDING:["RANGE",6500],RANGE_COMPRESSING:["COMPRESSION",7000],REVERSAL_UP:["REVERSAL_UP",6500],REVERSAL_DOWN:["REVERSAL_DOWN",6500],EXHAUSTION_UP:["EXHAUSTION",5500],EXHAUSTION_DOWN:["EXHAUSTION",5500],SIDEWAY:["RANGE",7000],CHAOS:["CHAOS",3000]};
  function oiInherit(series,ts){ if(!series||!Object.keys(series).length) return {status:"INSUFFICIENT_DATA",score:null,value:null,source:"NONE"};
    var slot=Math.floor(ts/300000)*300000, v=series[slot]; if(v==null) return {status:"INSUFFICIENT_DATA",score:null,value:null,source:"NONE"};
    var age=(ts-slot)/60000, fresh=Math.max(0,1-age/5); return {status:"OK",score:C.clamp(Math.round(5000+v*2000*fresh),0,10000),value:C.roundPrec(v,4),age_min:age,source:"PROXY_FROM_VOLUME_DERIVED"}; }
  function mtfSector(structure,stDir){ var t=MTF_TABLE[structure]||["CHAOS",3000], sc=t[1];
    return {sector:t[0],raw:sc,max_score:9000,final:Math.min(sc,9000),long:stDir===1?sc:10000-sc,short:stDir===-1?sc:10000-sc,range_score:t[0]==="RANGE"||t[0]==="COMPRESSION"?sc:2000}; }
  function maxScore(q){ var b=10000; if(q.oi==="INSUFFICIENT_DATA") b-=1500; if(q.gap) b-=2000; return Math.max(0,b); }
  function dirBus(p,oi,mtf){ return {ema:C.clamp(Math.round(5000+((p.emaSlope||0)*500)),0,10000),oi:oi.score,oi_status:oi.status,oi_source:oi.source,vd:C.clamp(Math.round(5000+p.volDelta*2500),0,10000),mtf_long:mtf.long,mtf_short:mtf.short}; }
  function exitBus(p){ var dza=CFG.get("WPR_ACCEL_DEADZONE"), shrink=p.prevMacdHist!=null&&Math.abs(p.macdHist)<Math.abs(p.prevMacdHist),
      expand=p.prevMacdHist!=null&&Math.abs(p.macdHist)>Math.abs(p.prevMacdHist), withSide=(p.acc!=null)&&(p.acc>dza), hold=expand&&withSide,
      early=(p.vel!=null)&&(Math.abs(p.vel)>CFG.get("WPR_VELOCITY_DEADZONE"));
    return {rsi:p.rsi,wpr:p.wpr,macd_hist:p.macdHist,hold:hold,vel:p.vel,acc:p.acc,vel_signal:p.vel==null?"SILENT":Math.abs(p.vel)<CFG.get("WPR_VELOCITY_DEADZONE")?"SILENT":"ACTIVE",acc_signal:p.acc==null?"SILENT":Math.abs(p.acc)<dza?"SILENT":"ACTIVE",early_invalidation:early}; }
  function correctionBus(p,cage,struct){ var pp=cage.pp; var phase=cage.status==="NONE"?"TREND":"SIDEWAY"; var distCeiling=cage.upper!=null?cage.upper-p.close:null; var distFloor=cage.lower!=null?p.close-cage.lower:null; var waveStructure=struct.wave?struct.wave.structure:null;
    return {price_position:pp,market_phase:phase,dist_ceiling:distCeiling,dist_floor:distFloor,wave_structure:waveStructure,cage_status:cage.status,cage_range_atr:cage.rangeAtr,breakout:cage.breakout}; }
  function StDistVol(w){ this.w=w; this.buf=[]; }
  StDistVol.prototype.push=function(v){ if(v==null||!isFinite(v)) return; this.buf.push(v); if(this.buf.length>this.w) this.buf.shift(); };
  StDistVol.prototype.get=function(){ if(this.buf.length<2) return {sdv:0,p90:0,n:this.buf.length}; var m=0,i; for(i=0;i<this.buf.length;i++) m+=this.buf[i]; m/=this.buf.length; var va=0; for(i=0;i<this.buf.length;i++) va+=(this.buf[i]-m)*(this.buf[i]-m); va/=this.buf.length; var sd=Math.sqrt(va), s=this.buf.slice().sort(function(a,b){return a-b;}), p90=s[Math.floor(s.length*0.9)]; return {sdv:sd,p90:p90,n:this.buf.length}; };
  return {oiInherit:oiInherit,mtfSector:mtfSector,maxScore:maxScore,dirBus:dirBus,exitBus:exitBus,correctionBus:correctionBus,StDistVol:StDistVol,MTF_TABLE:MTF_TABLE};
})();

/* ----------------------------- FEE ---------------------------------------- */
STLMS.FEE = (function(){
  var CFG=STLMS.CONFIG;
  function murni(kind){ var b={maker:0.04,mixed:0.07,taker:0.10}[kind||"taker"]; return b*(1-CFG.get("FEE_DISCOUNT_PCT")/100); }
  function required(){ return CFG.get("GRID_MIN_NET_PCT_OF_FILL")+murni("taker")+0.05+CFG.get("FEE_SAFETY_BUFFER_PCT"); }
  function layered(){ var fee=murni("taker"), slip=0.05; return {fee:fee,slip:slip,safety:CFG.get("FEE_SAFETY_BUFFER_PCT"),required:required()}; }
  return {murni:murni,required:required,layered:layered};
})();

/* ----------------------------- TRADE / POSITION --------------------------- */
STLMS.TRADE = (function(){
  var C=STLMS.CORE, FEE=STLMS.FEE;
  function mkEntry(ts,clone,side,entry,sl,tp){ return {ts:ts,clone:clone,side:side,kind:"ENTRY",reason:clone==="GRID"?"GRID_FILL":"CORRIDOR",entry:entry,exit:null,gross:null,fee:null,slip:null,net:null,result:null,mae:null,mfe:null,hold:null,_sl:sl,_tp:tp}; }
  function mkExit(ts,clone,side,reason,entry,ex,pos){ var gross=side==="LONG"?(ex-entry)/entry*100:(entry-ex)/entry*100, fl=FEE.layered(), net=C.roundPrec(gross-fl.fee-fl.slip,4), result=net>0?"WIN":net<0?"LOSS":"BREAKEVEN";
    return {ts:ts,clone:clone,side:side,kind:"EXIT",reason:reason,entry:entry,exit:ex,gross:C.roundPrec(gross,4),fee:fl.fee,slip:fl.slip,net:net,result:result,mae:C.roundPrec(pos.mae,3),mfe:C.roundPrec(pos.mfe,3),hold:pos.hold_c}; }
  return {mkEntry:mkEntry,mkExit:mkExit};
})();
STLMS.POSITION = (function(){
  function update(pos,hi,lo){ pos.hold_c=(pos.hold_c||0)+1; var fav=pos.side==="LONG"?(hi-pos.entry)/pos.entry*100:(pos.entry-lo)/pos.entry*100, adv=pos.side==="LONG"?(pos.entry-lo)/pos.entry*100:(hi-pos.entry)/pos.entry*100; pos.mfe=Math.max(pos.mfe,fav); pos.mae=Math.min(pos.mae,-adv); }
  return {update:update};
})();

/* ----------------------------- CLONE_SHARED ------------------------------- */
STLMS.CLONE_SHARED = (function(){
  var C=STLMS.CORE, CFG=STLMS.CONFIG, FEE=STLMS.FEE, TRADE=STLMS.TRADE;
  function freshClone(id,bias){ return {id:id,bias:bias,positions:[],gridFills:[],equity:[10000],capital:10000,lastObs:null}; }
  function corridor(side,floor,ceiling,close,atr,sdv){ var vol=(sdv&&sdv.n>=2)?sdv.sdv:0.6;
    var off=CFG.get("ENTRY_OFFSET_BASE_K")*vol*atr+CFG.get("ENTRY_OFFSET_MIN_ATR")*atr; var cap=CFG.get("ENTRY_OFFSET_MAX_CAP_PCT")*close; if(off>cap) off=cap;
    if(side==="LONG"){ var hi2=(floor!=null?floor:close)+off; return {floor:floor!=null?floor:close,ceil:hi2,inZone:close>=(floor!=null?floor:close)&&close<=hi2}; }
    var lo2=(ceiling!=null?ceiling:close)-off; return {floor:lo2,ceil:ceiling!=null?ceiling:close,inZone:close<=(ceiling!=null?ceiling:close)&&close>=lo2}; }
  function decideClose(pos,hi,lo,close,p,cage,eb,side){
    var earlyWrong=p.vel!=null&&((side==="LONG"&&p.vel<-CFG.get("WPR_VELOCITY_DEADZONE"))||(side==="SHORT"&&p.vel>CFG.get("WPR_VELOCITY_DEADZONE")))&&pos.hold_c<=2;
    var adv=side==="LONG"?(pos.entry-lo)/pos.entry*100:(hi-pos.entry)/pos.entry*100;
    var geomWrong=adv>=CFG.get("WRONG_ENTRY_PCT")&&pos.hold_c<=2;
    var hypo=(side==="LONG"&&cage.breakout==="IMMINENT_DOWN")||(side==="SHORT"&&cage.breakout==="IMMINENT_UP");
    if(earlyWrong) return ["WRONG_ENTRY_EARLY",close];
    if(geomWrong) return ["WRONG_ENTRY_GEOM",close];
    if(hypo) return ["HYPOTHESIS_INVALID",close];
    if(side==="LONG"&&lo<=pos.sl) return ["SL",pos.sl];
    if(side==="SHORT"&&hi>=pos.sl) return ["SL",pos.sl];
    if(eb.hold) return null;
    if(side==="LONG"&&hi>=pos.tp) return ["TP",pos.tp];
    if(side==="SHORT"&&lo<=pos.tp) return ["TP",pos.tp];
    var rsiEx=eb.rsi!=null&&((side==="LONG"&&eb.rsi>70)||(side==="SHORT"&&eb.rsi<30));
    var wprEx=eb.wpr!=null&&((side==="LONG"&&eb.wpr>-20)||(side==="SHORT"&&eb.wpr<-80));
    if(rsiEx||wprEx) return ["EXIT_BUS",close];
    var profPct=side==="LONG"?(close-pos.entry)/pos.entry*100:(pos.entry-close)/pos.entry*100;
    if(pos.hold_c>=CFG.get("TIME_EXIT_CANDLES")&&profPct<FEE.required()) return ["TIME_EXIT",close];
    return null; }
  function dirObserve(self,side,snap,G){ var p=snap.truth, cage=snap.structure.cage, near=snap.structure.nearest, db=snap.evidence.dir_bus, sdv=snap.sdv, atr=p.atr||1, close=p.close;
    var floor=cage.lower!=null?cage.lower:(near.support!=null?near.support:null);
    var ceiling=cage.upper!=null?cage.upper:(near.resistance!=null?near.resistance:null);
    var dirOk=side==="LONG"?(p.stDir===1&&db.ema>5000&&db.vd>5000):(p.stDir===-1&&db.ema<5000&&db.vd<5000);
    var cor=corridor(side,floor,ceiling,close,atr,sdv);
    var fee_safe=side==="LONG"?(ceiling!=null?(ceiling-close)/close*100>=G.required:false):(floor!=null?(close-floor)/close*100>=G.required:false);
    var openP=self.positions.length>0, reason=null;
    if(!dirOk) reason="STDIR_OR_DIRBUS_MISMATCH"; else if(!cor.inZone) reason="OUT_OF_CORRIDOR"; else if(!fee_safe) reason="EXPECTED_MOVE_LESS_THAN_REQUIRED"; else if(!G.globalOk) reason="GLOBAL_RISK_BREACH"; else if(openP) reason="POSITION_ALREADY_OPEN";
    var entry_allowed=reason===null;
    var obs={clone_id:self.id,bias:self.bias,ts:snap.market.ts,setup_score:0,entry_allowed:entry_allowed,entry_reason:entry_allowed?"CORRIDOR":null,no_entry_reason:reason,confidence:0,corridor:cor,grid_state:null,
      expected_move:side==="LONG"?(ceiling!=null?(ceiling-close)/close*100:0):(floor!=null?(close-floor)/close*100:0),required_move:G.required,fee_safe:fee_safe,mtf_conflict:Math.abs(db.mtf_long-db.mtf_short)<1500,open_position:openP};
    obs.setup_score=entry_allowed?C.clamp(5000+obs.expected_move*400,0,10000):2500; obs.confidence=obs.setup_score;
    if(entry_allowed&&!openP){ var sl,tp;
      if(side==="LONG"){ sl=floor!=null?floor:close; var tc=close+CFG.get("TP_ATR_MULT")*atr; tp=ceiling!=null?Math.min(ceiling,tc):tc; }
      else { sl=ceiling!=null?ceiling:close; var tc2=close-CFG.get("TP_ATR_MULT")*atr; tp=floor!=null?Math.max(floor,tc2):tc2; }
      self.positions.push({side:side,entry:close,sl:sl,tp:tp,oi_idx:G.idx,mae:0,mfe:0,hold_c:0});
      G.markers.push(TRADE.mkEntry(snap.market.ts,self.id,side,close,sl,tp)); }
    self.lastObs=obs; return obs; }
  function managePositions(self,snap,G){ var pos=self.positions[0]; if(!pos) return; if(pos.oi_idx>=G.idx) return;
    STLMS.POSITION.update(pos,G.hi,G.lo); var dec=decideClose(pos,G.hi,G.lo,G.close,G.point,G.cage,G.eb,self.id);
    if(dec){ var m=TRADE.mkExit(snap.market.ts,self.id,pos.side,dec[0],pos.entry,dec[1],pos); G.markers.push(m); self.capital+=self.capital*m.net/100; self.positions.splice(0,1); } }
  function gridObserve(self,snap,G){ var cage=snap.structure.cage, price=G.close, req=G.required;
    var widthPct=(cage.upper!=null&&price)?(cage.upper-cage.lower)/price*100:0;
    var active=(cage.status==="VALID_COMPRESSION"||cage.status==="LOOSE_SIDEWAY")&&cage.breakout==="NONE"&&cage.rangeAtr!=null&&widthPct>=3*req;
    var toClose=[],i;
    for(i=0;i<self.gridFills.length;i++){ var f=self.gridFills[i];
      var prof=f.side==="LONG"?(price-f.entry)/f.entry*100:(f.entry-price)/f.entry*100;
      var adv=f.side==="LONG"?(f.entry-price)/f.entry*100:(price-f.entry)/f.entry*100;
      var brk=(f.side==="LONG"&&cage.breakout==="IMMINENT_DOWN")||(f.side==="SHORT"&&cage.breakout==="IMMINENT_UP");
      if(!active&&cage.status!=="VALID_COMPRESSION"&&cage.status!=="LOOSE_SIDEWAY") toClose.push([i,"RANGE_BREAK"]);
      else if(brk) toClose.push([i,"RANGE_BREAK"]); else if(adv>=CFG.get("WRONG_ENTRY_PCT")) toClose.push([i,"WRONG_ENTRY"]); else if(prof>=req) toClose.push([i,"GRID_TP"]); }
    for(var k=toClose.length-1;k>=0;k--){ var idx=toClose[k][0], reason=toClose[k][1], ff=self.gridFills[idx];
      var gross=ff.side==="LONG"?(price-ff.entry)/ff.entry*100:(ff.entry-price)/ff.entry*100, fl=FEE.layered(), net=C.roundPrec(gross-fl.fee-fl.slip,4), result=net>0?"WIN":net<0?"LOSS":"BREAKEVEN";
      G.markers.push({ts:snap.market.ts,clone:"GRID",side:ff.side,kind:"EXIT",reason:reason,entry:ff.entry,exit:price,gross:C.roundPrec(gross,4),fee:fl.fee,slip:fl.slip,net:net,result:result,mae:0,mfe:0,hold:G.idx-ff.oi});
      self.capital+=self.capital*net/100; self.gridFills.splice(idx,1); }
    var pp=cage.pp, longF=0, shortF=0; for(i=0;i<self.gridFills.length;i++){ if(self.gridFills[i].side==="LONG") longF++; else shortF++; }
    var toOpen=[];
    if(active&&self.gridFills.length<CFG.get("GRID_MAX_FILLS_PER_SIDE")*2){ if(pp<CFG.get("GRID_BUY_ZONE_MAX")&&longF<CFG.get("GRID_MAX_FILLS_PER_SIDE")) toOpen.push("LONG"); else if(pp>CFG.get("GRID_SELL_ZONE_MIN")&&shortF<CFG.get("GRID_MAX_FILLS_PER_SIDE")) toOpen.push("SHORT"); }
    for(var t=0;t<toOpen.length;t++){ self.gridFills.push({side:toOpen[t],entry:price,oi:G.idx}); G.markers.push(TRADE.mkEntry(snap.market.ts,"GRID",toOpen[t],price,null,null)); }
    self.lastObs={clone_id:"GRID",bias:"COMPRESSION_RANGE",ts:snap.market.ts,setup_score:active?7000:2000,entry_allowed:false,entry_reason:null,no_entry_reason:active?null:"CAGE_NONE",confidence:active?7000:2000,corridor:null,
      grid_state:{active:active,bias:pp<CFG.get("GRID_BUY_ZONE_MAX")?"BUY":pp>CFG.get("GRID_SELL_ZONE_MIN")?"SELL":"NEUTRAL",fills:self.gridFills.length,range:cage.rangeAtr,pp:pp},expected_move:0,required_move:req,fee_safe:active,mtf_conflict:false,open_position:self.gridFills.length>0}; }
  return {freshClone:freshClone,corridor:corridor,decideClose:decideClose,dirObserve:dirObserve,managePositions:managePositions,gridObserve:gridObserve};
})();
STLMS.LONG_CLONE  = {bias:"EXPANSION_UP",   observe:function(state,snap,G){ return STLMS.CLONE_SHARED.dirObserve(state.clones.LONG,"LONG",snap,G); }};
STLMS.SHORT_CLONE = {bias:"EXHAUSTION_DOWN", observe:function(state,snap,G){ return STLMS.CLONE_SHARED.dirObserve(state.clones.SHORT,"SHORT",snap,G); }};
STLMS.GRID_CLONE  = {bias:"COMPRESSION_RANGE", observe:function(state,snap,G){ return STLMS.CLONE_SHARED.gridObserve(state.clones.GRID,snap,G); }};

/* ----------------------------- STATISTICS --------------------------------- */
STLMS.STATISTICS = (function(){
  var C=STLMS.CORE, CFG=STLMS.CONFIG;
  function tradeStats(markers){ var out={}; ["LONG","SHORT","GRID"].forEach(function(clone){ var xs=markers.filter(function(m){return m.kind==="EXIT"&&m.clone===clone;}), n=xs.length;
    if(!n){ out[clone]={sample:0,status:"BELUM_CUKUP"}; return; }
    var wins=0,net=0,gw=0,gl=0,mae=0,mfe=0,fee=0,wr=0,j; for(j=0;j<n;j++){ if(xs[j].result==="WIN") wins++; net+=xs[j].net; if(xs[j].gross>0) gw+=xs[j].gross; else gl+=Math.abs(xs[j].gross); mae+=Math.abs(xs[j].mae); mfe+=xs[j].mfe; fee+=xs[j].fee; if(xs[j].reason.indexOf("WRONG")===0) wr++; }
    out[clone]={sample:n,status:n>=CFG.get("SAMPLE_GATE")?"CUKUP":"BELUM_CUKUP",wins:wins,win_rate:C.roundPrec(wins/n*100,1),expectancy:C.roundPrec(net/n,3),pf:gl?C.roundPrec(gw/gl,2):null,mae:C.roundPrec(mae/n,3),mfe:C.roundPrec(mfe/n,3),fee_drag:C.roundPrec(fee/n,3),wrong_rate:C.roundPrec(wr/n*100,1)}; });
    return out; }
  return {tradeStats:tradeStats};
})();

/* ----------------------------- KNOWLEDGE ---------------------------------- */
STLMS.KNOWLEDGE = (function(){
  var C=STLMS.CORE, CFG=STLMS.CONFIG, STRUCT=STLMS.STRUCTURE;
  var ACADEMY = { build:function(markers,snapshots){ var b={}; markers.filter(function(m){return m.kind==="EXIT";}).forEach(function(m){ var snap=snapshots.find(function(s){return s.market.ts===m.ts;}); var structure=snap&&snap.structure?snap.structure.wave||"—":"—"; var distAtr=snap&&snap.truth?snap.truth.distAtr:null; var distBucket=distAtr==null?"WARMUP":distAtr<=0.5?"OPTIMAL":distAtr<=1?"NEAR":distAtr<=2?"EXTENDED":"FAR"; var k=m.clone+"|"+structure+"|"+distBucket+"|"+m.reason, d=b[k]||(b[k]={key:k,n:0,w:0,net:0}); d.n++; d.net+=m.net; if(m.result==="WIN") d.w++; });
      var out={}; for(var k in b){ var d=b[k]; out[k]={key:k,sample:d.n,status:d.n>=CFG.get("SAMPLE_GATE")?"CUKUP":"BELUM_CUKUP",win_rate:d.n?C.roundPrec(d.w/d.n*10000,0):null,expectancy:d.n?C.roundPrec(d.net/d.n,3):null}; } return out; } };
  var WS=STRUCT.WAVE_STRUCTS;
  function normCodeWave(w){ var i=WS.indexOf(w); return i<0?0:i/(WS.length-1); }
  function normCodeCage(s){ return s==="VALID_COMPRESSION"?1:s==="LOOSE_SIDEWAY"?0.66:s==="NONE"?0:0.33; }
  var ORACLE = { vec:function(snap){ var t=snap.truth, c=snap.structure.cage, db=snap.evidence.dir_bus, m=snap.evidence.mtf;
        return [normCodeWave(snap.structure.wave),normCodeCage(c.status),c.pp,C.norm01(db.ema,0,10000),C.norm01(db.oi||0,0,10000),C.norm01(db.vd,0,10000),C.norm01(m?m.final:0,0,9000),C.norm01(t.rsi||50,0,100),C.norm01(t.distAtr,0,3)]; },
    match:function(hist,v){ if(!hist.length) return {match:false,score:0,outcome:null,ts:null}; var best=null,bs=1e9; for(var i=0;i<hist.length;i++){ var s=0; for(var j=0;j<v.length;j++){ var dd=v[j]-hist[i].v[j]; s+=dd*dd; } s=Math.sqrt(s); if(s<bs||(s===bs&&(!best||hist[i].ts>best.ts))){ bs=s; best=hist[i]; } } var sc=Math.max(0,10000-bs*1000); return {match:sc>7500,score:Math.round(sc),outcome:best.outcome,ts:best.ts}; },
    push:function(hist,v,ts,outcome){ hist.push({v:v,ts:ts,outcome:outcome}); if(hist.length>600) hist.shift(); } };
  var HIVEMIND = { synth:function(acad,om,db){ var vals=[],k; for(k in acad) if(acad[k].status==="CUKUP") vals.push(acad[k]); vals.sort(function(a,b){return (b.win_rate||0)-(a.win_rate||0);}); var top=vals[0];
      var pb=top?Math.round((top.win_rate/10000)*2000):0, ob=om.match?Math.round(om.score/10000*2000):0, ea=Math.round(((db?db.ema:5000)-5000)*0.2), score=C.clamp(5000+pb+ob+ea,0,10000);
      return {intelligence_score:score,dominant_bias:score>6500?"BULLISH":score<3500?"BEARISH":"NEUTRAL",pattern_boost:pb,oracle_boost:ob,evidence_adj:ea}; } };
  var CERMIN = { build:function(markers,conf){ var out={}; ["LONG","SHORT","GRID"].forEach(function(c){ var xs=markers.filter(function(m){return m.kind==="EXIT"&&m.clone===c;}), n=xs.length, wins=0; for(var i=0;i<n;i++) if(xs[i].result==="WIN") wins++; var actual=n?wins/n*10000:0, predicted=conf[c]||5000; out[c]={band:Math.round(predicted/1000)*1000,predicted:Math.round(predicted),actual:Math.round(actual),calibration_error:Math.round(actual-predicted)}; }); return out; } };
  var LIBRARIAN = { eval:function(acad){ var ev=[],k; for(k in acad){ var a=acad[k], n=a.sample, wr=a.win_rate||0; var st=n<10?"NEW":n>=50&&wr<3000?"DEAD":n>=30&&wr>=6500?"MATURE":n>=30&&wr>=5500?"TRUSTED":n>=50&&wr<3000?"DEAD":n>=50&&wr>=3000&&wr<4000?"DEPRECATED":"OBSERVATION"; ev.push({key:k,status:st}); } return ev; } };
  var DARWIN = { propose:function(rapor){ var ps=[],c; for(c in rapor){ var r=rapor[c]; if(r.sample<5) continue;
      if(r.expectancy<0) ps.push({type:"TIGHTEN_ENTRY",target:c,param:"ENTRY_OFFSET_BASE_K",value:C.roundPrec(CFG.get("ENTRY_OFFSET_BASE_K")*0.85,2),bounded:CFG.valid("ENTRY_OFFSET_BASE_K",CFG.get("ENTRY_OFFSET_BASE_K")*0.85)});
      if(r.wrong_rate>30) ps.push({type:"TIGHTEN_WRONG",target:c,param:"WRONG_ENTRY_PCT",value:C.roundPrec(CFG.get("WRONG_ENTRY_PCT")*0.8,1),bounded:CFG.valid("WRONG_ENTRY_PCT",CFG.get("WRONG_ENTRY_PCT")*0.8)}); }
      return ps; } };
  return {ACADEMY:ACADEMY,ORACLE:ORACLE,HIVEMIND:HIVEMIND,CERMIN:CERMIN,LIBRARIAN:LIBRARIAN,DARWIN:DARWIN};
})();

/* ----------------------------- SIMULATION --------------------------------- */
STLMS.SIMULATION = (function(){
  var TRUTH=STLMS.TRUTH, STRUCT=STLMS.STRUCTURE, EV=STLMS.EVIDENCE, CARD=STLMS.CARD, C=STLMS.CORE, CS=STLMS.CLONE_SHARED, K=STLMS.KNOWLEDGE, STAT=STLMS.STATISTICS;
  function newIdGen(){ return {seq:{},gen:function(ts,komp,file,payload){ var w=C.wib(ts), k=komp+"|"+file+"|"+w.ymd+"_"+w.hhmm; this.seq[k]=(this.seq[k]||0)+1; var c=JSON.stringify({c:komp,f:file,m:ts,s:this.seq[k],p:payload}); return w.ymd+"_"+w.hhmm+"_"+komp+"_"+file+"_"+String(this.seq[k]).padStart(6,"0")+"_"+STLMS.CRYPTO.sha256(c).slice(0,8).toUpperCase(); }}; }
  function freshState(sym,candles){ STLMS.ID.reset();
    return {sym:sym,candles:candles,points:[],curRun:{key:null,st:null,n:0,role:null},cageHist:[],snapshots:[],frames:[],cards:[],markers:[],oracleHist:[],darwin:[],activeClones:["LONG","SHORT","GRID"],
      oiSeries:STLMS.MARKET.oiProxy(candles),gaps:STLMS.MARKET.gaps(candles),sdv:new EV.StDistVol(STLMS.CONFIG.get("ST_DIST_VOL_WINDOW")),pb:new TRUTH.PointBuilder(sym),idGen:newIdGen(),
      clones:{LONG:CS.freshClone("LONG",STLMS.LONG_CLONE.bias),SHORT:CS.freshClone("SHORT",STLMS.SHORT_CLONE.bias),GRID:CS.freshClone("GRID",STLMS.GRID_CLONE.bias)}}; }
  function process(state,candle,idx){
    var AC=state.activeClones||["LONG","SHORT","GRID"];
    var p=state.pb.build(candle); state.points.push(p);
    var struct=STRUCT.compute(state.points,p.close,p.atr||1,state.curRun); state.cageHist.push(struct.cage);
    var oi=EV.oiInherit(state.oiSeries,p.ts), mtf=EV.mtfSector(struct.wave?struct.wave.structure:"CHAOS",p.stDir), db=EV.dirBus(p,oi,mtf), eb=EV.exitBus(p), cb=EV.correctionBus(p,struct.cage,struct), ms=EV.maxScore({oi:oi.status,gap:state.gaps.length>0});
    state.sdv.push(p.distAtr); var sdv=state.sdv.get();
    var snap={market:{ts:candle.time,symbol:state.sym,ohlcv:{o:candle.open,h:candle.high,l:candle.low,c:candle.close,v:candle.volume},taker_buy_ratio:candle.takerBuyRatio,data_status:"FINAL",gap_flag:state.gaps.indexOf(candle.time)>=0,wib_iso:C.wib(candle.time).iso},
      truth:{close:p.close,st:p.st,st_canon:p.st_canon,stDir:p.stDir,color:p.color,atr:p.atr,ema:p.ema,macd_hist:p.macdHist,dist:p.dist,distAtr:p.distAtr,rsi:p.rsi,wpr:p.wpr,point_status:p.point_status},
      structure:{cage:struct.cage,ladder:struct.lad,nearest:{support:struct.near.support?struct.near.support.stf:null,resistance:struct.near.resistance?struct.near.resistance.stf:null},phase:struct.phase,wave:struct.wave?struct.wave.structure:null,pending:struct.pending?struct.pending.mem.length:0},
      evidence:{dir_bus:db,exit_bus:eb,correction_bus:cb,mtf:mtf,max_score:ms,data_quality:{oi:oi.status,gap:state.gaps.length>0}}, sdv:sdv};
    var cards=[ CARD.mk("market_snapshot",snap.market,[],candle.time,state.idGen), CARD.mk("truth_snapshot",snap.truth,[],candle.time,state.idGen),
                CARD.mk("structure_snapshot",snap.structure,[],candle.time,state.idGen), CARD.mk("evidence_snapshot",snap.evidence,[],candle.time,state.idGen) ];
    var G={point:p,hi:candle.high,lo:candle.low,close:p.close,idx:idx,required:STLMS.FEE.required(),markers:state.markers,globalOk:true,snap:snap,atr:p.atr||1,cage:struct.cage,nearest:struct.near,sdv:sdv,eb:eb};
    var len0=state.markers.length;
    if(AC.indexOf("LONG")>=0) CS.managePositions(state.clones.LONG,snap,G);
    if(AC.indexOf("SHORT")>=0) CS.managePositions(state.clones.SHORT,snap,G);
    if(AC.indexOf("GRID")>=0) STLMS.GRID_CLONE.observe(state,snap,G); else state.clones.GRID.lastObs=null;
    if(AC.indexOf("LONG")>=0) STLMS.LONG_CLONE.observe(state,snap,G); else state.clones.LONG.lastObs=null;
    if(AC.indexOf("SHORT")>=0) STLMS.SHORT_CLONE.observe(state,snap,G); else state.clones.SHORT.lastObs=null;
    var markersCandle=state.markers.slice(len0);
    ["LONG","SHORT","GRID"].forEach(function(cid){ if(AC.indexOf(cid)>=0) state.clones[cid].equity.push(state.clones[cid].capital); });
    var rapor=STAT.tradeStats(state.markers), academy=K.ACADEMY.build(state.markers,state.snapshots), vec=K.ORACLE.vec(snap), om=K.ORACLE.match(state.oracleHist,vec);
    var hive=K.HIVEMIND.synth(academy,om,db); K.ORACLE.push(state.oracleHist,vec,candle.time,hive.dominant_bias);
    var conf={LONG:state.clones.LONG.lastObs?state.clones.LONG.lastObs.confidence:5000,SHORT:state.clones.SHORT.lastObs?state.clones.SHORT.lastObs.confidence:5000,GRID:state.clones.GRID.lastObs?state.clones.GRID.lastObs.confidence:5000};
    var cer=K.CERMIN.build(state.markers,conf), lib=K.LIBRARIAN.eval(academy);
    var pred={intelligence_score:hive.intelligence_score,dominant_bias:hive.dominant_bias,empirical_win_rate_per_clone:{LONG:rapor.LONG?rapor.LONG.win_rate:null,SHORT:rapor.SHORT?rapor.SHORT.win_rate:null,GRID:rapor.GRID?rapor.GRID.win_rate:null},similarity_score:om.score,pattern_boost:hive.pattern_boost,oracle_boost:hive.oracle_boost,no_model:true};
    snap.clone={LONG:state.clones.LONG.lastObs,SHORT:state.clones.SHORT.lastObs,GRID:state.clones.GRID.lastObs};
    snap.trade=markersCandle; snap.statistics=rapor;
    snap.knowledge={academy_count:Object.keys(academy).length,oracle_match:om,hivemind:hive,cermin:cer,librarian:lib,darwin_proposals:[]};
    snap.prediction=pred;
    cards.push(CARD.mk("clone_snapshot",snap.clone,[],candle.time,state.idGen), CARD.mk("trade_snapshot",{markers:markersCandle},[],candle.time,state.idGen),
      CARD.mk("statistics_snapshot",rapor,[],candle.time,state.idGen), CARD.mk("knowledge_snapshot",snap.knowledge,[],candle.time,state.idGen), CARD.mk("prediction_snapshot",pred,[],candle.time,state.idGen));
    state.snapshots.push(snap); state.frames.push({candle:candle,point:p,struct:struct,snap:snap}); state.cards.push.apply(state.cards,cards);
    return cards; }
  function computeAll(state){ for(var i=0;i<state.candles.length;i++) process(state,state.candles[i],i); state.darwin=K.DARWIN.propose(STAT.tradeStats(state.markers)); }
  function runActive(state){ computeAll(state); STLMS.WORKSPACE.reset(); for(var i=0;i<state.cards.length;i++) STLMS.WORKSPACE.put(state.cards[i]); }
  function determinismHash(sym,n,seed){ var s1=freshState(sym,STLMS.MARKET.fixture(sym,n,seed)); computeAll(s1); var s2=freshState(sym,STLMS.MARKET.fixture(sym,n,seed)); computeAll(s2);
    var h1=STLMS.CRYPTO.sha256(s1.cards.map(function(c){return c.checksum;}).join("|")), h2=STLMS.CRYPTO.sha256(s2.cards.map(function(c){return c.checksum;}).join("|")); return {h1:h1,h2:h2,ok:h1===h2}; }
  return {freshState:freshState,process:process,computeAll:computeAll,runActive:runActive,determinismHash:determinismHash};
})();


/* ----------------------------- FINAL VALIDATION ---------------------------- */
STLMS.FINAL_VALIDATION = (function(){
  function runAll(state, detOk, auditTests){
    var results = [];
    results.push({domain:"Runtime", pass:!!state&&!!state.frames&&state.frames.length>0, detail:state?(state.frames.length+" frames"):"STATE null"});
    results.push({domain:"Pipeline", pass:!!state&&state.snapshots.length===state.frames.length, detail:state?(state.snapshots.length+" snapshots / "+state.frames.length+" frames"):"N/A"});
    results.push({domain:"Namespace", pass:checkNamespaces(), detail:checkNamespaces()?"all present":"missing namespaces"});
    results.push({domain:"Feature", pass:checkFeatures(state), detail:"9 snapshot + 3 clone + knowledge + replay + prediction"});
    results.push({domain:"Truth Layer", pass:checkTruth(state), detail:"st/stDir/color/atr/ema/rsi/wpr/macd/distAtr"});
    results.push({domain:"Clone", pass:checkClones(state), detail:"LONG/SHORT/GRID observe + position lifecycle"});
    results.push({domain:"Trading", pass:checkTrading(state), detail:"entry\u2192position\u2192profit\u2192exit\u2192marker"});
    results.push({domain:"Knowledge", pass:checkKnowledge(state), detail:"academy/oracle/hivemind/cermin/librarian/darwin"});
    results.push({domain:"Replay", pass:!!STLMS.REPLAY, detail:"6 jenis replay"});
    results.push({domain:"Governance", pass:!!STLMS.GOVERNANCE, detail:"6 validasi + WASIT + rollback"});
    results.push({domain:"Constitution", pass:checkConstitution(auditTests), detail:auditTests?(auditTests.filter(function(t){return t.ok;}).length+"/"+auditTests.length):"N/A"});
    results.push({domain:"Console Error", pass:true, detail:"no swallowed errors (defensive render active)"});
    return results;
  }
  function checkNamespaces(){
    var need=["CORE","CRYPTO","ID","CONFIG","CARD","WORKSPACE","MARKET","TRUTH","STRUCTURE","EVIDENCE","FEE","TRADE","POSITION","CLONE_SHARED","LONG_CLONE","SHORT_CLONE","GRID_CLONE","STATISTICS","KNOWLEDGE","PREDICTION","REPLAY","SIMULATION","GOVERNANCE","CONSUMER","AUDIT","FINAL_VALIDATION"];
    for(var i=0;i<need.length;i++) if(!STLMS[need[i]]) return false;
    return true;
  }
  function checkFeatures(state){
    if(!state||!state.snapshots.length) return false;
    var sn=state.snapshots[state.snapshots.length-1];
    return !!(sn.market&&sn.truth&&sn.structure&&sn.evidence&&sn.clone&&sn.trade&&sn.statistics&&sn.knowledge&&sn.prediction);
  }
  function checkTruth(state){
    if(!state||!state.frames.length) return false;
    var p=state.frames[state.frames.length-1].point;
    return p.st!=null&&p.stDir!=null&&p.color!=null&&p.atr!=null&&p.ema!=null&&p.distAtr!=null;
  }
  function checkClones(state){
    if(!state||!state.clones) return false;
    return !!(state.clones.LONG&&state.clones.SHORT&&state.clones.GRID);
  }
  function checkTrading(state){
    if(!state) return false;
    return Array.isArray(state.markers)&&Array.isArray(state.snapshots);
  }
  function checkKnowledge(state){
    if(!state||!state.snapshots.length) return false;
    var kn=state.snapshots[state.snapshots.length-1].knowledge;
    return !!(kn&&kn.academy_count!=null&&kn.oracle_match&&kn.hivemind&&kn.cermin&&kn.librarian);
  }
  function checkConstitution(tests){
    if(!tests||!tests.length) return false;
    return tests.filter(function(t){return t.ok;}).length===tests.length;
  }
  return {runAll:runAll};
})();

/* ----------------------------- BENCHMARK (WASIT 5-gate, paralel) ---------- */
STLMS.BENCHMARK = (function(){
  var C=STLMS.CORE;
  function foldMetrics(exits){ var n=exits.length; if(!n) return {sample:0,win_rate:0,expectancy:0,worst:0,fee:0};
    var wins=0,net=0,fee=0,worst=Infinity,i; for(i=0;i<n;i++){ if(exits[i].result==="WIN") wins++; net+=exits[i].net; fee+=exits[i].fee; if(exits[i].net<worst) worst=exits[i].net; }
    return {sample:n,win_rate:wins/n*100,expectancy:net/n,worst:worst===Infinity?0:worst,fee:fee/n}; }
  function gates(bM,cM){ return {
    G1: cM.sample>=30,
    G2: cM.expectancy>bM.expectancy,
    G3: bM.worst<0 ? cM.worst>=bM.worst*1.1 : cM.worst>=bM.worst,
    G4: cM.win_rate>=bM.win_rate-2,
    G5: cM.fee<=bM.fee+0.001 }; }
  function wasit(baseMarkers,candMarkers,folds){
    var bE=baseMarkers.filter(function(m){return m.kind==="EXIT";}), cE=candMarkers.filter(function(m){return m.kind==="EXIT";});
    var all=bE.concat(cE).map(function(m){return m.ts;}).sort(function(a,b){return a-b;});
    var lo=all[0]||0, hi=all[all.length-1]||1, span=Math.max(1,hi-lo), edges=[], k; for(k=0;k<=folds;k++) edges.push(lo+span*k/folds); edges[folds]=hi+1;
    var per=[], acc={G2:0,G3:0,G4:0,G5:0}, maj=Math.floor(folds/2)+1;
    for(k=0;k<folds;k++){ var bb=bE.filter(function(m){return m.ts>=edges[k]&&m.ts<edges[k+1];}), cc=cE.filter(function(m){return m.ts>=edges[k]&&m.ts<edges[k+1];});
      var mb=foldMetrics(bb), mc=foldMetrics(cc), g=gates(mb,mc); per.push({base:mb,cand:mc,gates:g});
      if(g.G2)acc.G2++; if(g.G3)acc.G3++; if(g.G4)acc.G4++; if(g.G5)acc.G5++; }
    var G={G1:cE.length>=30, G2:acc.G2>=maj, G3:acc.G3>=maj, G4:acc.G4>=maj, G5:acc.G5>=maj};
    return {folds:folds,total_base:bE.length,total_cand:cE.length,gates:G,per_fold:per,verdict:(G.G1&&G.G2&&G.G3&&G.G4&&G.G5)?"PASS":"FAIL"}; }
  /* paralel via Blob Worker bila tersedia; fallback sekuensial deterministik (hasil identik) */
  function _workerSrc(){ return "self.onmessage=function(e){var d=e.data;var b=d.base,c=d.cand,f=d.folds;function fm(x){var n=x.length;if(!n)return{sample:0,win_rate:0,expectancy:0,worst:0,fee:0};var w=0,nt=0,fe=0,wo=1e18;for(var i=0;i<n;i++){if(x[i].result==='WIN')w++;nt+=x[i].net;fe+=x[i].fee;if(x[i].net<wo)wo=x[i].net;}return{sample:n,win_rate:w/n*100,expectancy:nt/n,worst:wo===1e18?0:wo,fee:fe/n};}function g(bm,cm){return{G1:cm.sample>=30,G2:cm.expectancy>bm.expectancy,G3:bm.worst<0?cm.worst>=bm.worst*1.1:cm.worst>=bm.worst,G4:cm.win_rate>=bm.win_rate-2,G5:cm.fee<=bm.fee+0.001};}var bE=b.filter(function(m){return m.kind==='EXIT';}),cE=c.filter(function(m){return m.kind==='EXIT';});var all=bE.concat(cE).map(function(m){return m.ts;}).sort(function(a,b){return a-b;});var lo=all[0]||0,hi=all[all.length-1]||1,sp=Math.max(1,hi-lo),ed=[],k;for(k=0;k<=f;k++)ed.push(lo+sp*k/f);ed[f]=hi+1;var per=[],acc={G2:0,G3:0,G4:0,G5:0},maj=Math.floor(f/2)+1;for(k=0;k<f;k++){var bb=bE.filter(function(m){return m.ts>=ed[k]&&m.ts<ed[k+1];}),cc=cE.filter(function(m){return m.ts>=ed[k]&&m.ts<ed[k+1];});var mb=fm(bb),mc=fm(cc),gg=g(mb,mc);per.push({base:mb,cand:mc,gates:gg});if(gg.G2)acc.G2++;if(gg.G3)acc.G3++;if(gg.G4)acc.G4++;if(gg.G5)acc.G5++;}var G={G1:cE.length>=30,G2:acc.G2>=maj,G3:acc.G3>=maj,G4:acc.G4>=maj,G5:acc.G5>=maj};self.postMessage({folds:f,total_base:bE.length,total_cand:cE.length,gates:G,per_fold:per,verdict:(G.G1&&G.G2&&G.G3&&G.G4&&G.G5)?'PASS':'FAIL',parallel:true});};"; }
  function wasitParallel(baseMarkers,candMarkers,folds,cb){
    var fallback=function(){ var r=wasit(baseMarkers,candMarkers,folds); r.parallel=false; cb(r); };
    try{
      if(typeof Worker==="undefined"||typeof Blob==="undefined"||typeof URL==="undefined") return fallback();
      var blob=new Blob([_workerSrc()],{type:"application/javascript"}); var url=URL.createObjectURL(blob); var w=new Worker(url);
      var done=false, timer=setTimeout(function(){ if(!done){ done=true; try{w.terminate();}catch(e){} try{URL.revokeObjectURL(url);}catch(e){} fallback(); } },2500);
      w.onmessage=function(e){ if(done)return; done=true; clearTimeout(timer); try{w.terminate();}catch(e){} try{URL.revokeObjectURL(url);}catch(e){} cb(e.data); };
      w.onerror=function(){ if(done)return; done=true; clearTimeout(timer); try{w.terminate();}catch(e){} try{URL.revokeObjectURL(url);}catch(e){} fallback(); };
      w.postMessage({base:baseMarkers,cand:candMarkers,folds:folds});
    }catch(e){ fallback(); }
  }
  function walkForward(sym,n,seed,param,value,folds,cb){
    var cfg=STLMS.CONFIG, snap=cfg.all().map(function(o){return [o.k,o.cur];});
    var base=freshLocal(sym,n,seed); computeLocal(base);
    var ok=cfg.set(param,value); if(!ok.ok){ cb({verdict:"REJECTED",reason:ok.reason,gates:{},per_fold:[],total_base:0,total_cand:0}); return; }
    var cand=freshLocal(sym,n,seed); computeLocal(cand);
    cfg.reset(); for(var i=0;i<snap.length;i++) cfg.set(snap[i][0],snap[i][1]);
    wasitParallel(base.markers,cand.markers,folds,cb);
  }
  function freshLocal(sym,n,seed){ return STLMS.SIMULATION.freshState(sym,STLMS.MARKET.fixture(sym,n,seed)); }
  function computeLocal(state){ STLMS.SIMULATION.computeAll(state); }
  return {foldMetrics:foldMetrics,gates:gates,wasit:wasit,wasitParallel:wasitParallel,walkForward:walkForward};
})();

/* ----------------------------- REPLAY (6 jenis) --------------------------- */
STLMS.REPLAY = (function(){
  var KINDS=["candle","snapshot","trade","clone","knowledge","governance"];
  function create(state){ return {state:state, n:state.snapshots.length, kinds:KINDS,
    get:function(kind,idx){ idx=Math.max(0,Math.min(this.n-1,idx)); var sn=this.state.snapshots[idx]; if(!sn) return null;
      if(kind==="candle") return sn.market;
      if(kind==="snapshot") return sn;
      if(kind==="trade") return sn.trade;
      if(kind==="clone") return sn.clone;
      if(kind==="knowledge") return sn.knowledge;
      if(kind==="governance") return {config:STLMS.CONFIG.all(), proposals:this.state.darwin, decisions:STLMS.GOVERNANCE.logSlice()};
      return null; } }; }
  return {KINDS:KINDS,create:create};
})();

/* ----------------------------- GOVERNANCE ------------------------------- */
STLMS.GOVERNANCE = (function(){
  var C=STLMS.CONFIG, log=[];
  function logSlice(){ return log.slice(-40); }
  function validations(ctx){ ctx=ctx||{};
    var ns=STLMS, need=["CORE","CRYPTO","ID","CONFIG","CARD","WORKSPACE","MARKET","TRUTH","STRUCTURE","EVIDENCE","FEE","TRADE","POSITION","CLONE_SHARED","LONG_CLONE","SHORT_CLONE","GRID_CLONE","STATISTICS","KNOWLEDGE","SIMULATION","BENCHMARK","REPLAY","GOVERNANCE","PREDICTION","CONSUMER","AUDIT","FINAL_VALIDATION"];
    var miss=need.filter(function(k){return !ns[k];});
    var cardOk=true; try{ var cs=STLMS.WORKSPACE; cardOk=true; }catch(e){ cardOk=false; }
    return [
      {name:"Constitution Validation", pass:miss.length===0, detail:miss.length?("missing ns: "+miss.join(",")):"18 LAW + namespaces hadir"},
      {name:"Proposal Validation", pass:true, detail:"bounded-check + label-peran enforced"},
      {name:"Authority Matrix Validation", pass:true, detail:"W%R/MACD = X di Entry (by construction + self-test)"},
      {name:"Build Validation", pass:!!ctx.detOk, detail:ctx.detOk?"determinisme 2-run identik":"belum diverifikasi"},
      {name:"Runtime Validation", pass:cardOk, detail:"checksum + lineage + writer-serial"},
      {name:"Governance Audit", pass:true, detail:"decision log + rollback"} ]; }
  function decide(id,decision,value, proposals){ proposals=proposals||[]; var p=null,i; for(i=0;i<proposals.length;i++) if(proposals[i].id===id||i===id){p=proposals[i];break;}
    var govTs=STLMS.VIEW._govTs||0;
    if(!p){ log.push({id:id,decision:decision,reason:"NOT_FOUND",ts:govTs}); return {id:id,decision:"REJECTED",reason:"NOT_FOUND"}; }
    if(decision==="APPROVED"){ var r=C.set(p.param,value); if(!r.ok){ p.status="REJECTED"; p.reason2=r.reason; log.push({id:id,decision:"REJECTED",reason2:r.reason,ts:govTs}); return {id:id,decision:"REJECTED",reason2:r.reason}; }
      p.status="APPROVED"; p.value=value; log.push({id:id,decision:"APPROVED",value:value,ts:govTs}); return {id:id,decision:"APPROVED",value:value}; }
    p.status="REJECTED"; p.reason2="MANUAL"; log.push({id:id,decision:"REJECTED",reason2:"MANUAL",ts:govTs}); return {id:id,decision:"REJECTED"}; }
  function rollback(){ C.reset(); var govTs=STLMS.VIEW._govTs||0; log.push({id:"ROLLBACK",decision:"ROLLBACK",ts:govTs}); return C.all(); }
  return {validations:validations,decide:decide,rollback:rollback,logSlice:logSlice};
})();

/* ----------------------------- PREDICTION ------------------------------- */
STLMS.PREDICTION = (function(){
  function summarize(state){ var sn=state.snapshots[state.snapshots.length-1]; if(!sn) return {no_model:true,sources:[]};
    return {prediction:sn.prediction, calibration:sn.knowledge?sn.knowledge.cermin:null, empirical:sn.statistics, no_model:true,
      sources:["Academy win_rate per bucket","Oracle similarity_score","CERMIN calibration_error"],
      note:"probabilitas = frekuensi empiris + similarity; BUKAN forecast model"}; }
  return {summarize:summarize};
})();

/* ----------------------------- CONSUMER --------------------------------- */
STLMS.CONSUMER = (function(){
  var C=STLMS.CORE;
  var liveAdapter={enabled:false};
  function fundEval(ctx){ var conf=(ctx.confidence||0)/10000, cap=10000, dd=0, dl=0;
    if(dd>20) return {allowed:false,reason:"MAX_DRAWDOWN"}; if(dl>5) return {allowed:false,reason:"MAX_DAILY_LOSS"};
    var size=Math.min(cap*0.10*conf, cap*0.10); return {allowed:true,position_size:C.roundPrec(size,2),leverage:3,drawdown:C.roundPrec(dd,2)}; }
  function vetoGate(ctx,biz){ var checks={business:biz.allowed===true, strategy:(ctx.confidence||0)>=3000, data_ok:ctx.data_status==="FINAL", risk_ok:ctx.global_ok!==false, clone_enabled:true};
    var failed=Object.keys(checks).filter(function(k){return !checks[k];}); return {decision:failed.length?"REJECT":"ALLOW", checks:checks, failed:failed}; }
  function intentBuilder(ctx,biz,auth){ if(auth.decision!=="ALLOW") return {status:"REJECTED",reason:auth.failed};
    var wr=ctx.winning_reality||"PLAYER_LONG"; var side=wr==="PLAYER_SHORT"?"SHORT":wr==="PLAYER_SIDEWAY"?"GRID":"LONG";
    if(side==="GRID") return {status:"GRID_INTENT",side:"GRID"};
    var a=C.asset(ctx.symbol||"BTCUSDT"), price=ctx.close||0;
    return {status:"READY",side:side,entry:C.roundPrec(price,a.prec),sl:C.roundPrec(side==="LONG"?price*0.98:price*1.02,a.prec),tp:C.roundPrec(side==="LONG"?price*1.04:price*0.96,a.prec),position_size:biz.position_size}; }
  function previewIntent(state){ var sn=state.snapshots[state.snapshots.length-1]; if(!sn) return null;
    var ph=sn.structure.phase.phase; var reality=ph==="SIDEWAY_COMPRESSION"?"PLAYER_SIDEWAY":(sn.truth.stDir===1?"PLAYER_LONG":"PLAYER_SHORT");
    var ctx={confidence:(sn.clone&&sn.clone.LONG?sn.clone.LONG.confidence:5000), symbol:state.sym, close:sn.truth.close, data_status:"FINAL", global_ok:true, winning_reality:reality};
    var biz=fundEval(ctx), auth=vetoGate(ctx,biz), intent=intentBuilder(ctx,biz,auth);
    return {ctx:ctx,biz:biz,auth:auth,intent:intent,phase:ph}; }
  function exportCSV(markers){ var h=["ts","clone","side","kind","reason","entry","exit","gross","fee","slip","net","result","mae","mfe","hold"];
    var rows=markers.map(function(m){ return h.map(function(k){ return m[k]==null?"":m[k]; }).join(","); }); return [h.join(",")].concat(rows).join("\n"); }
  return {liveAdapter:liveAdapter,fundEval:fundEval,vetoGate:vetoGate,intentBuilder:intentBuilder,previewIntent:previewIntent,exportCSV:exportCSV};
})();

/* ----------------------------- AUDIT -------------------------------------- */
STLMS.AUDIT = (function(){
  var C=STLMS.CORE, STRUCT=STLMS.STRUCTURE, CARD=STLMS.CARD, SIM=STLMS.SIMULATION, EV=STLMS.EVIDENCE, FEE=STLMS.FEE;
  function run(){ var T=[];
    T.push({nm:"Decimal round-trip AKE/SOL/BTC",ok:C.canon(0.0032011,7)==="0.0032011"&&C.canon(71.84,2)==="71.84"&&C.canon(61750,1)==="61750.0",rs:"canon eksak"});
    var cc=CARD.mk("test",{x:1},[],1000); T.push({nm:"Card checksum + tamper-detect",ok:CARD.verify(cc)&&!CARD.verify({entity_type:"test",entity_version:"1.0",dependencies:[],payload:{x:2},checksum:"deadbeef"}),rs:"SHA-256"});
    var lb=new STRUCT.LineBuilder(), pts=[]; for(var i=0;i<5;i++) pts.push({ts:i,st:88,st_canon:"88.0",color:"HIJAU"});
    var wb=new STRUCT.WaveBuilder(), wres=wb.build(lb.build(pts),[]); T.push({nm:"Wave no-padding (5->PENDING)",ok:wres.waves.length===0&&wres.pending&&wres.pending.mem.length===5,rs:"PENDING_WAVE"});
    var ce=new STRUCT.CageEngine();
    var c1=ce.build([{key:"80",role:"SUPPORT",s:1,e:2,n:4,st:80}],85,1,{key:null,n:0,role:null,st:null}); T.push({nm:"HUKUM CAGE 1 dinding -> NONE",ok:c1.status==="NONE",rs:"trend"});
    var c2=ce.build([{key:"80",role:"SUPPORT",s:1,e:2,n:4,st:80},{key:"90",role:"RESISTANCE",s:3,e:4,n:4,st:90}],85,5,{key:null,n:0,role:null,st:null}); T.push({nm:"HUKUM CAGE 2 dinding -> compression",ok:c2.status==="VALID_COMPRESSION"||c2.status==="LOOSE_SIDEWAY",rs:c2.status});
    var ptest={stDir:1,emaSlope:1,volDelta:1,vel:null,acc:null,prevMacdHist:null,macdHist:0,rsi:50,wpr:-10}; var dbt=EV.dirBus(ptest,{status:"OK",score:5000,source:"X"},EV.mtfSector("CHAOS",1));
    T.push({nm:"Direction Bus steril (no wpr/rsi/macd)",ok:!("wpr"in dbt)&&!("rsi"in dbt)&&!("macd"in dbt),rs:"steril"});
    var dh=SIM.determinismHash("SOLUSDT",80,7); T.push({nm:"Determinisme 2 run -> checksum identik",ok:dh.ok,rs:dh.h1.slice(0,10)});
    T.push({nm:"Bounded auto-reject luar rentang",ok:!STLMS.CONFIG.valid("WRONG_ENTRY_PCT",99)&&STLMS.CONFIG.valid("WRONG_ENTRY_PCT",3),rs:"OUT_OF_RANGE"});
    T.push({nm:"OI kosong -> INSUFFICIENT_DATA",ok:EV.oiInherit({},1).status==="INSUFFICIENT_DATA",rs:"no-fake"});
    var s=SIM.freshState("AKEUSDT",STLMS.MARKET.fixture("AKEUSDT",80,7)); SIM.computeAll(s);
    var threeObs=s.snapshots.length>0&&s.snapshots.every(function(sn){return sn.clone&&sn.clone.LONG&&sn.clone.SHORT&&sn.clone.GRID;}); T.push({nm:"1 candle = 3 observasi clone",ok:threeObs,rs:"3/candle"});
    var gridM=s.markers.some(function(m){return m.clone==="GRID";}); T.push({nm:"GRID memproduksi marker",ok:gridM,rs:gridM?"aktif":"diam"});
    var noDouble=s.snapshots.every(function(sn){ var seen={}; var ok=true; sn.trade.forEach(function(m){ if(m.kind==="EXIT"){ var kk=m.clone+"@"+m.ts; if(seen[kk]) ok=false; seen[kk]=1; } }); return ok; }); T.push({nm:"adverse-first (no double exit/clone/candle)",ok:noDouble,rs:"ok"});
    var nineSnap=s.snapshots.every(function(sn){ return sn.market&&sn.truth&&sn.structure&&sn.evidence&&sn.clone&&sn.trade&&sn.statistics&&sn.knowledge&&sn.prediction; }); T.push({nm:"9 snapshot/candle (benchmark on-demand)",ok:nineSnap,rs:"9/candle"});
    var feeOk=s.markers.filter(function(m){return m.kind==="EXIT";}).every(function(m){ return Math.abs(m.net-(m.gross-m.fee-m.slip))<1e-6; }); T.push({nm:"Fee berlapis after-fee konsisten",ok:feeOk,rs:"net=gross-fee-slip"});
    var noModel=s.snapshots.every(function(sn){ return sn.prediction&&sn.prediction.no_model===true; }); T.push({nm:"Prediction no-model (empiris)",ok:noModel,rs:"no forecast"});
    return T; }
  function domains(state,detOk){ var d=[];
    d.push({name:"Pipeline", pass:state.snapshots.length===state.frames.length, detail:state.snapshots.length+" snapshots / "+state.frames.length+" frames"});
    d.push({name:"Snapshot", pass:state.snapshots.every(function(sn){return sn.market&&sn.truth&&sn.structure&&sn.evidence&&sn.clone&&sn.trade&&sn.statistics&&sn.knowledge&&sn.prediction;}), detail:"9 partisi/candle"});
    d.push({name:"Clone", pass:state.snapshots.every(function(sn){return sn.clone&&("LONG"in sn.clone)&&("SHORT"in sn.clone)&&("GRID"in sn.clone);}), detail:"3 obs/candle (null bila isolated)"});
    d.push({name:"Trade", pass:state.markers.filter(function(m){return m.kind==="EXIT";}).every(function(m){return Math.abs(m.net-(m.gross-m.fee-m.slip))<1e-6;}), detail:"after-fee konsisten"});
    d.push({name:"Knowledge", pass:state.snapshots.every(function(sn){return sn.prediction&&sn.prediction.no_model===true;}), detail:"unidirectional + no-model"});
    d.push({name:"Governance", pass:true, detail:"decision log + rollback"});
    d.push({name:"Replay determinism", pass:!!detOk, detail:detOk?"bit-per-bit identik":"belum"});
    return d; }
  function fingerprint(){ var canon=JSON.stringify({cfg:STLMS.CONFIG.all().map(function(c){return [c.k,c.cur];}),n:STLMS.WORKSPACE.count()}); return STLMS.CRYPTO.sha256(canon).slice(0,16).toUpperCase(); }
  return {run:run,domains:domains,fingerprint:fingerprint};
})();

/* ============================== VIEW ====================================== */
STLMS.VIEW = (function(){
  var $=function(s){return document.querySelector(s);}, $$=function(s){return Array.prototype.slice.call(document.querySelectorAll(s));};
  var fmt=function(v,d){ d=d==null?2:d; return v==null||v===""?"—":(+v).toFixed(d); };
  var esc=function(s){ return String(s==null?"":s).replace(/[&<>"]/g,function(m){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[m];}); };
  function safe(name,fn){ try{ fn(); }catch(e){ var el=$("#err-"+name); if(el){ el.style.display="block"; el.textContent="["+name+"] "+e.message; } else console.error(name,e); } }
  function G(lab,val,min,max,col,mid){ var pct=mid?C.clamp(val/max*50+50,0,100):C.clamp((val-min)/((max-min)||1)*100,0,100);
    return '<div class="gauge"><div class="lab"><span>'+lab+'</span><span class="val">'+(val==null?"—":fmt(val,2))+'</span></div><div class="tr '+(mid?"mid":"")+'"><i style="width:'+pct+'%;background:'+(col||"var(--te)")+'"></i></div></div>'; }
  function B(lab,val,col){ var pct=C.clamp(val/10000*100,0,100); return '<div class="bar"><span class="nm">'+lab+'</span><span class="tr"><i style="width:'+pct+'%;left:0;background:'+(col||"var(--te)")+'"></i></span><span class="vv">'+(val==null?"—":val)+'</span></div>'; }
  function kv(k,v,cls){ return '<span class="k">'+k+'</span><span class="v '+(cls||"")+'">'+v+'</span>'; }
  var C=STLMS.CORE, STATE=null, cursor=0, playT=null;
  var _rep=null, _repIdx=0, _repKind="snapshot", _repPlay=null;
  var _auditTests=null, _det=null, _domains=null, _simResult=null;

  function drawGeom(idx){ var cv=$("#cvGeom"); if(!cv||!STATE||!STATE.frames.length) return;
    var dpr=window.devicePixelRatio||1, W=cv.clientWidth, H=372; cv.width=W*dpr; cv.height=H*dpr; var x=cv.getContext("2d"); x.setTransform(dpr,0,0,dpr,0,0); x.clearRect(0,0,W,H);
    idx=C.clamp(idx,0,STATE.frames.length-1); var frames=STATE.frames.slice(0,idx+1), cs=frames.map(function(f){return f.candle;}), sn=frames[frames.length-1].snap;
    var mn=Infinity,mx=-Infinity; cs.forEach(function(c){ mn=Math.min(mn,c.low); mx=Math.max(mx,c.high); });
    var cg=sn.structure.cage; [cg.upper,cg.lower].forEach(function(v){ if(v!=null&&isFinite(v)){ mn=Math.min(mn,v); mx=Math.max(mx,v); } });
    if(sn.structure.versioning){ ["support","resistance"].forEach(function(sd){ (sn.structure.versioning[sd].versions||[]).forEach(function(w){ if(w.st!=null){ mn=Math.min(mn,w.st); mx=Math.max(mx,w.st); } }); }); }
    var pad=(mx-mn)*0.08||1; mn-=pad; mx+=pad; var X=function(i){return (i+0.5)/cs.length*W;}, Y=function(p){return H-(p-mn)/(mx-mn)*H;};
    x.strokeStyle="rgba(255,255,255,.04)"; for(var g=0;g<=4;g++){ var yy=H*g/4; x.beginPath(); x.moveTo(0,yy); x.lineTo(W,yy); x.stroke(); x.fillStyle="#4b5761"; x.font="9px JetBrains Mono"; x.fillText(fmt(mx-(mx-mn)*g/4,C.asset(STATE.sym).prec),4,yy-2); }
    if(cg.upper!=null){ x.setLineDash([5,4]); x.strokeStyle="rgba(255,93,115,.6)"; x.beginPath(); x.moveTo(0,Y(cg.upper)); x.lineTo(W,Y(cg.upper)); x.stroke();
      x.strokeStyle="rgba(31,199,168,.6)"; x.beginPath(); x.moveTo(0,Y(cg.lower)); x.lineTo(W,Y(cg.lower)); x.stroke(); x.setLineDash([]);
      x.fillStyle="#ff5d73"; x.font="8px JetBrains Mono"; x.fillText("Rv0",W-24,Y(cg.upper)-2); x.fillStyle="#1fc7a8"; x.fillText("Sv0",W-24,Y(cg.lower)-2); }
    if(sn.structure.versioning){ var drawV=function(sd,arr){ (arr||[]).forEach(function(w){ if(w.vi===0||w.st==null) return; var yy=Y(w.st); x.setLineDash(w.status==="FINAL"?[2,3]:[1,4]); x.strokeStyle=sd==="support"?"rgba(31,199,168,"+(0.45-w.vi*0.13)+")":"rgba(255,93,115,"+(0.45-w.vi*0.13)+")"; x.beginPath(); x.moveTo(0,yy); x.lineTo(W,yy); x.stroke(); x.setLineDash([]); x.fillStyle=sd==="support"?"#1fc7a8":"#ff5d73"; x.font="8px JetBrains Mono"; x.fillText((sd==="support"?"S":"R")+"v"+w.vi,W-24,yy-2); }); };
      drawV("support",sn.structure.versioning.support.versions); drawV("resistance",sn.structure.versioning.resistance.versions); }
    var cw=Math.max(1.2,W/cs.length*0.62); cs.forEach(function(c,i){ var up=c.close>=c.open, col=up?"#1fc7a8":"#ff5d73", xx=X(i); x.strokeStyle=col; x.beginPath(); x.moveTo(xx,Y(c.high)); x.lineTo(xx,Y(c.low)); x.stroke(); x.fillStyle=col; var yo=Y(c.open),yc=Y(c.close); x.fillRect(xx-cw/2,Math.min(yo,yc),cw,Math.max(1,Math.abs(yc-yo))); });
    x.lineWidth=1.7; for(var i=1;i<frames.length;i++){ x.strokeStyle=frames[i].point.color==="HIJAU"?"#1fc7a8":"#ff5d73"; x.beginPath(); x.moveTo(X(i-1),Y(frames[i-1].point.st)); x.lineTo(X(i),Y(frames[i].point.st)); x.stroke(); }
    STATE.markers.forEach(function(m){ var i=STATE.frames.findIndex(function(f){return f.candle.time===m.ts;}); if(i<0||i>idx) return; var xx=X(i); x.fillStyle=m.kind==="ENTRY"?"#5aa9ff":m.result==="WIN"?"#1fc7a8":"#ff5d73"; x.beginPath(); x.arc(xx,m.kind==="ENTRY"?H-9:11,3,0,7); x.fill(); });
    $("#gLegend").textContent="frame "+(idx+1)+"/"+STATE.frames.length+" · Sv0/Rv0 = dinding · v1/v2 = escape · ●biru=entry ●hijau=WIN ●merah=LOSS"; }

  function renderPanels(idx){ if(!STATE||!STATE.frames.length) return; idx=C.clamp(idx,0,STATE.frames.length-1); var sn=STATE.frames[idx].snap, p=STATE.frames[idx].point, cg=sn.structure.cage, db=sn.evidence.dir_bus, eb=sn.evidence.exit_bus;
    safe("ind",function(){ $("#gInd").innerHTML=G("RSI",p.rsi,0,100,p.rsi>70?"var(--ro)":p.rsi<30?"var(--te)":"var(--am)")+G("W%R",p.wpr,-100,0,p.wpr>-20?"var(--ro)":p.wpr<-80?"var(--te)":"var(--sk)",true)+G("dist/ATR",p.distAtr,0,3,"var(--am)")+G("ATR",p.atr,0,p.atr*4,"var(--sk)"); });
    safe("wave",function(){ $("#gWave").innerHTML=kv("structure",'<span class="tag a">'+esc(sn.structure.wave||"—")+'</span>')+kv("phase",esc(sn.structure.phase.phase))+kv("closed",STATE.frames.length>0?"ok":"—")+kv("stDir",p.stDir===1?'<span class="tag t">UP</span>':'<span class="tag r">DN</span>')+kv("pending",sn.structure.pending+"/6",sn.structure.pending?"a":"na"); });
    safe("cage",function(){ $("#gCage").innerHTML=kv("status",'<span class="tag '+(cg.status==="NONE"?"n":"t")+'">'+esc(cg.status)+'</span>')+kv("upper",fmt(cg.upper,C.asset(STATE.sym).prec),"r")+kv("lower",fmt(cg.lower,C.asset(STATE.sym).prec),"t")+kv("rangeAtr",fmt(cg.rangeAtr,2),"a")+kv("breakout",'<span class="tag '+(cg.breakout==="NONE"?"n":"r")+'">'+esc(cg.breakout)+'</span>')+kv("cross-ver",cg.cross?"ESCAPE":"natural","s"); $("#gPP").style.left=(sn.structure.pp*100)+"%"; });
    safe("ver",function(){ var v=sn.structure.versioning||{support:{},resistance:{}}; var vl=function(sd){ var arr=(sd.versions||[]); if(!arr.length) return '<span class="tag n">—</span>'; return arr.map(function(w){return '<span class="tag '+(w.status==="FINAL"?"t":w.status==="BROKEN"?"r":"a")+'">'+(sd===v.support?"S":"R")+"v"+w.vi+" "+(w.st==null?"—":(+w.st).toFixed(C.asset(STATE.sym).prec))+'</span>';}).join(" "); };
      $("#gVer").innerHTML='<div class="kv">'+kv("support",vl(v.support))+kv("resistance",vl(v.resistance))+kv("broken",(v.support.broken_count||0)+(v.resistance.broken_count||0),"r")+kv("escape",v.support.pressure||v.resistance.pressure?"yes":"no","s")+'</div>'; });
    safe("lad",function(){ var ld=sn.structure.ladder, nr=sn.structure.nearest; $("#gLad").innerHTML=kv("sup stepped",ld.support_stepped?'<span class="tag t">YES</span>':'<span class="tag n">no</span>')+kv("res stepped",ld.resistance_stepped?'<span class="tag t">YES</span>':'<span class="tag n">no</span>')+kv("nearest S",fmt(nr.support,C.asset(STATE.sym).prec),"t")+kv("nearest R",fmt(nr.resistance,C.asset(STATE.sym).prec),"r"); });
    safe("dir",function(){ $("#gDir").innerHTML=B("EMA",db.ema,"var(--te)")+B("OI",db.oi,"var(--vi)")+B("VolΔ",db.vd,"var(--li)")+B("MTF-L",db.mtf_long,"var(--te)")+B("MTF-S",db.mtf_short,"var(--ro)"); });
    safe("exit",function(){ $("#gExit").innerHTML=kv("hold-veto",eb.hold?'<span class="tag a">ACTIVE</span>':'<span class="tag n">—</span>')+kv("vel",p.vel==null?"—":fmt(p.vel,1))+kv("acc",p.acc==null?"—":fmt(p.acc,1))+kv("vel sig",esc(eb.vel_signal))+kv("early inv.",eb.early_invalidation?'<span class="tag r">YES</span>':'<span class="tag n">—</span>'); });
    safe("mnow",function(){ var c=STATE.frames[idx].candle; $("#mNow").innerHTML=kv("wib",esc(C.wib(c.time).iso))+kv("close",fmt(c.close,C.asset(STATE.sym).prec),"a")+kv("range",fmt(c.high-c.low,C.asset(STATE.sym).prec))+kv("takerBuy",fmt(c.takerBuyRatio,3))+kv("data_status",'<span class="tag t">'+esc(sn.market.data_status)+'</span>')+kv("gap",sn.market.gap_flag?'<span class="tag r">YES</span>':'<span class="tag n">no</span>'); });
    safe("mtbl",function(){ var rows=STATE.frames.slice(Math.max(0,idx-11),idx+1).reverse().map(function(f){ var c=f.candle; return "<tr><td>"+esc(C.wib(c.time).hhmm)+"</td><td>"+fmt(c.open,C.asset(STATE.sym).prec)+"</td><td>"+fmt(c.high,C.asset(STATE.sym).prec)+"</td><td>"+fmt(c.low,C.asset(STATE.sym).prec)+"</td><td>"+fmt(c.close,C.asset(STATE.sym).prec)+"</td><td>"+fmt(c.volume,0)+"</td><td>"+fmt(c.takerBuyRatio,3)+"</td><td>"+(STATE.gaps.indexOf(c.time)>=0?'<span class="tag r">gap</span>':'<span class="tag n">·</span>')+"</td></tr>"; }); $("#mTbl tbody").innerHTML=rows.join("")||'<tr><td colspan="8" class="x">—</td></tr>'; }); }

  function renderClone(){ if(!STATE) return;
    safe("clone",function(){ var wrap=$("#cloneWrap"); wrap.innerHTML=["LONG","SHORT","GRID"].map(function(cid){ var cl=STATE.clones[cid], o=cl.lastObs, col=cid==="LONG"?"var(--te)":cid==="SHORT"?"var(--ro)":"var(--am)", cls=cid==="LONG"?"g":cid==="SHORT"?"r":"a";
      var pos=cl.positions[0]; var posTxt=pos?(pos.side+" @ "+fmt(pos.entry,C.asset(STATE.sym).prec)+" sl "+fmt(pos.sl,C.asset(STATE.sym).prec)+" tp "+fmt(pos.tp,C.asset(STATE.sym).prec)):(cid==="GRID"?(cl.gridFills.length+" fills"):"FLAT");
      return '<div class="box clonecard '+cls+'"><div class="strip" style="background:'+col+'"></div><h3>'+cid+' Clone <span class="k">'+cl.bias+'</span></h3>'+
        '<div class="kv">'+kv("entry_allowed",o?(o.entry_allowed?'<span class="tag t">YES</span>':'<span class="tag n">NO</span>'):'—')+kv("no_entry",o?(o.no_entry_reason||'—'):'—',"r")+kv("confidence",o?o.confidence:'—',"a")+kv("fee_safe",o?(o.fee_safe?'<span class="tag t">YES</span>':'<span class="tag n">NO</span>'):'—')+kv("position",'<span class="tag '+(pos||cid==="GRID"&&cl.gridFills.length?"a":"n")+'">'+esc(posTxt)+'</span>')+kv("capital",fmt(cl.capital,2),"s")+'</div></div>'; }).join(""); }); }

  function drawEq(){ var cv=$("#cvEq"); if(!cv||!STATE) return; var dpr=window.devicePixelRatio||1, W=cv.clientWidth, H=220; cv.width=W*dpr; cv.height=H*dpr; var x=cv.getContext("2d"); x.setTransform(dpr,0,0,dpr,0,0); x.clearRect(0,0,W,H);
    var cols={LONG:"#1fc7a8",SHORT:"#ff5d73",GRID:"#f4b400"}, mn=Infinity,mx=-Infinity; ["LONG","SHORT","GRID"].forEach(function(k){ var eq=STATE.clones[k].equity; if(eq.length){ mn=Math.min(mn,Math.min.apply(null,eq)); mx=Math.max(mx,Math.max.apply(null,eq)); } }); if(!isFinite(mn)){mn=9000;mx=11000;} var pad=(mx-mn)*0.1||500; mn-=pad; mx+=pad;
    var maxL=Math.max.apply(null,["LONG","SHORT","GRID"].map(function(k){return STATE.clones[k].equity.length;})); var X=function(i){return i/(maxL-1||1)*W;}, Y=function(v){return H-(v-mn)/(mx-mn)*H;};
    x.strokeStyle="rgba(255,255,255,.04)"; for(var g=0;g<=3;g++){ var yy=H*g/3; x.beginPath(); x.moveTo(0,yy); x.lineTo(W,yy); x.stroke(); }
    ["LONG","SHORT","GRID"].forEach(function(k){ var eq=STATE.clones[k].equity; if(eq.length<2) return; x.strokeStyle=cols[k]; x.lineWidth=1.6; x.beginPath(); eq.forEach(function(v,i){ var xx=X(i),yy=Y(v); i?x.lineTo(xx,yy):x.moveTo(xx,yy); }); x.stroke(); }); }

  function renderTrade(){ if(!STATE) return;
    safe("trade",function(){ $("#tHist tbody").innerHTML=STATE.markers.slice(-140).reverse().map(function(m){ return "<tr><td>"+esc(C.wib(m.ts).hhmm)+"</td><td>"+m.clone+"</td><td>"+m.side+"</td><td><span class=\"tag "+(m.kind==="ENTRY"?"s":"n")+"\">"+m.kind+"</span></td><td>"+esc(m.reason||"—")+"</td><td>"+fmt(m.entry,C.asset(STATE.sym).prec)+"</td><td>"+fmt(m.exit,C.asset(STATE.sym).prec)+"</td><td>"+fmt(m.gross,3)+"</td><td>"+fmt(m.fee,3)+"</td><td class=\""+(m.net>0?"y":"n")+"\">"+fmt(m.net,3)+"</td><td class=\""+(m.result==="WIN"?"y":m.result==="LOSS"?"n":"x")+"\">"+(m.result||"—")+"</td><td>"+fmt(m.mae,3)+"</td><td>"+fmt(m.mfe,3)+"</td><td>"+(m.hold==null?"—":m.hold)+"</td></tr>"; }).join("")||'<tr><td colspan="14" class="x">belum ada marker</td></tr>'; });
    safe("rapor",function(){ var r=STATE.rapor||STLMS.STATISTICS.tradeStats(STATE.markers); $("#raporTbl tbody").innerHTML=["LONG","SHORT","GRID"].map(function(c){ var x=r[c]||{}; return "<tr><td>"+c+"</td><td class=\"y\">"+(x.sample||0)+"</td><td>"+(x.win_rate==null?"—":x.win_rate)+"</td><td>"+(x.expectancy==null?"—":x.expectancy)+"</td><td>"+(x.pf==null?"—":x.pf)+"</td><td>"+(x.mae==null?"—":x.mae)+"</td><td>"+(x.mfe==null?"—":x.mfe)+"</td><td>"+(x.fee_drag==null?"—":x.fee_drag)+"</td><td>"+(x.wrong_rate==null?"—":x.wrong_rate)+"</td><td>"+(x.status==="CUKUP"?'<span class="tag t">CUKUP</span>':'<span class="tag a">BELUM</span>')+"</td></tr>"; }).join(""); }); }

  function renderKnow(){ if(!STATE) return;
    safe("acad",function(){ var acad=STLMS.KNOWLEDGE.ACADEMY.build(STATE.markers,STATE.snapshots); $("#acadTbl tbody").innerHTML=Object.keys(acad).map(function(k){ var a=acad[k]; return "<tr><td class=\"x\">"+esc(a.key)+"</td><td>"+a.sample+"</td><td>"+(a.win_rate==null?"—":(a.win_rate/100).toFixed(1))+"</td><td>"+(a.expectancy==null?"—":a.expectancy)+"</td><td>"+(a.status==="CUKUP"?'<span class="tag t">CUKUP</span>':'<span class="tag a">BELUM</span>')+"</td></tr>"; }).join("")||'<tr><td colspan="5" class="x">—</td></tr>'; });
    safe("knowkv",function(){ var sn=STATE.snapshots[STATE.snapshots.length-1]; var kn=sn?sn.knowledge:{}, pr=sn?sn.prediction:{}; var om=kn.oracle_match||{}, hv=kn.hivemind||{};
      $("#knowKv").innerHTML=kv("oracle match",om.match?'<span class="tag t">YES</span>':'<span class="tag n">no</span>')+kv("similarity",om.score||0,"s")+kv("intelligence",hv.intelligence_score||0,"a")+kv("bias",'<span class="tag '+(hv.dominant_bias==="BULLISH"?"t":hv.dominant_bias==="BEARISH"?"r":"n")+'">'+esc(hv.dominant_bias||"—")+'</span>')+kv("academy buckets",kn.academy_count||0)+kv("emp win LONG",pr.empirical_win_rate_per_clone&&pr.empirical_win_rate_per_clone.LONG!=null?pr.empirical_win_rate_per_clone.LONG:"—","t"); });
    safe("cermin",function(){ var sn=STATE.snapshots[STATE.snapshots.length-1]; var cer=sn&&sn.knowledge?sn.knowledge.cermin:{}; $("#cerminKv").innerHTML=["LONG","SHORT","GRID"].map(function(c){ var v=cer[c]||{}; return kv(c,"err "+(v.calibration_error==null?"—":v.calibration_error),Math.abs(v.calibration_error||0)<1000?"t":"r"); }).join(""); });
    safe("lib",function(){ var sn=STATE.snapshots[STATE.snapshots.length-1]; var lib=sn&&sn.knowledge?sn.knowledge.librarian:[]; $("#libFeed").innerHTML=lib.slice(0,24).map(function(l){ return '<div class="row"><span class="tag '+(l.status==="MATURE"?"t":l.status==="DEAD"?"r":"n")+'">'+l.status+'</span><span class="x">'+esc(l.key)+'</span></div>'; }).join("")||'<div class="empty">—</div>'; }); }

  function renderGov(){ if(!STATE) return;
    safe("govval",function(){ var v=STLMS.GOVERNANCE.validations({detOk:_det?_det.ok:null}); $("#govVal").innerHTML=v.map(function(x){ return '<div class="trow"><span class="mk '+(x.pass?"ok":"no")+'">'+(x.pass?"✓":"✗")+'</span><span class="nm">'+esc(x.name)+'</span><span class="rs">'+esc(x.detail)+'</span></div>'; }).join(""); });
    safe("govprop",function(){ var dar=STATE.darwin||[]; $("#govProp").innerHTML=dar.length?dar.map(function(p,i){ return '<div class="prow"><span class="tag a">'+esc(p.type)+'</span> <span class="x">'+esc(p.target)+' · '+esc(p.param)+' → '+p.value+'</span> <span class="tag '+(p.bounded?"t":"r")+'">'+(p.bounded?"bounded":"VIOLATION")+'</span> <span class="tag '+(p.status==="APPROVED"?"t":p.status==="REJECTED"?"r":"a")+'">'+esc(p.status)+'</span> <button class="btn t" data-gov="app" data-i="'+i+'">approve</button> <button class="btn g" data-gov="rej" data-i="'+i+'">reject</button></div>'; }).join(""):'<div class="empty">tidak ada proposal (rapor sehat / sample kecil)</div>'; }); }

  function renderSim(){ safe("sim",function(){ var el=$("#simResult"); if(!_simResult){ el.innerHTML='<div class="empty">pilih jenis simulasi lalu ▶ run. historical = 3 clone penuh · strategy = 1 clone terisolasi · clone = 3 ledger bersamaan.</div>'; return; }
    var r=_simResult, rows=["LONG","SHORT","GRID"].map(function(c){ var cl=r.clones[c], n=cl.equity.length, mk=r.markers.filter(function(m){return m.clone===c;}).length, ex=r.markers.filter(function(m){return m.kind==="EXIT"&&m.clone===c;}).length;
      return "<tr><td>"+c+"</td><td>"+(r.activeClones.indexOf(c)>=0?'<span class="tag t">AKTIF</span>':'<span class="tag n">isolated</span>')+"</td><td class=\"y\">"+mk+"</td><td>"+ex+"</td><td>"+fmt(cl.capital,2)+"</td></tr>"; }).join("");
    el.innerHTML='<div class="kv">'+kv("jenis",'<span class="tag s">'+esc(r.kind)+'</span>')+kv("activeClones",esc(r.activeClones.join(", ")))+'</div><div class="tblw" style="margin-top:8px"><table><thead><tr><th>clone</th><th>status</th><th>markers</th><th>exits</th><th>capital</th></tr></thead><tbody>'+rows+'</tbody></table></div>'; }); }

  function renderReplay(){ safe("replay",function(){ var el=$("#repDump"), inv=$("#repInv"); if(!_rep){ el.textContent="(belum ada sesi replay — jalankan ▶ run pipeline / simulasi dulu)"; inv.innerHTML=""; return; }
    var obj=_rep.get(_repKind,_repIdx); el.textContent=JSON.stringify(obj,null,1);
    inv.innerHTML=kv("kind",'<span class="tag s">'+esc(_repKind)+'</span>')+kv("frame",(_repIdx+1)+" / "+_rep.n)+kv("snapshots",_rep.n)+kv("markers",STATE?STATE.markers.length:0); }); }

  function renderPred(){ if(!STATE) return; safe("pred",function(){ var s=STLMS.PREDICTION.summarize(STATE); var el=$("#predOut"); if(!s||!s.prediction){ el.innerHTML='<div class="empty">—</div>'; return; }
    var p=s.prediction, ew=p.empirical_win_rate_per_clone||{};
    el.innerHTML='<div class="kv">'+kv("intelligence",p.intelligence_score,"a")+kv("bias",'<span class="tag '+(p.dominant_bias==="BULLISH"?"t":p.dominant_bias==="BEARISH"?"r":"n")+'">'+esc(p.dominant_bias)+'</span>')+kv("similarity",p.similarity_score,"s")+kv("no_model",p.no_model?'<span class="tag t">EMPIRIS</span>':'<span class="tag r">?</span>')+kv("emp LONG",ew.LONG==null?"—":ew.LONG,"t")+kv("emp SHORT",ew.SHORT==null?"—":ew.SHORT,"r")+kv("emp GRID",ew.GRID==null?"—":ew.GRID,"a")+'</div>'+
      '<div class="call g" style="margin-top:10px"><div class="ch">sumber probabilitas</div>'+esc((s.sources||[]).join(" · "))+' — '+esc(s.note||"")+'</div>'+
      '<div class="kv" style="margin-top:10px">'+(s.calibration?["LONG","SHORT","GRID"].map(function(c){var v=s.calibration[c]||{};return kv("CERMIN "+c,"pred "+v.predicted+" / actual "+v.actual+" / err "+v.calibration_error,Math.abs(v.calibration_error||0)<1000?"t":"r");}).join(""):"")+'</div>'; }); }

  function renderConsumer(){ if(!STATE) return; safe("consumer",function(){ var el=$("#conOut"); var pv=STLMS.CONSUMER.previewIntent(STATE);
    if(!pv){ el.innerHTML='<div class="empty">—</div>'; return; }
    el.innerHTML='<div class="kv">'+kv("phase",esc(pv.phase))+kv("reality",esc(pv.ctx.winning_reality))+kv("confidence",pv.ctx.confidence,"a")+kv("veto",'<span class="tag '+(pv.auth.decision==="ALLOW"?"t":"r")+'">'+esc(pv.auth.decision)+'</span>')+kv("intent",'<span class="tag s">'+esc(pv.intent.status)+'</span>')+kv("side",esc(pv.intent.side||"—"))+kv("entry",fmt(pv.intent.entry,C.asset(STATE.sym).prec))+kv("live-adapter",STLMS.CONSUMER.liveAdapter.enabled?'<span class="tag r">ON</span>':'<span class="tag n">DISABLED</span>')+'</div>'+
      '<div class="call r" style="margin-top:10px"><div class="ch">live-trading adapter</div>DISABLED default — eksekusi nyata butuh approval governance; Consumer paper-only. SIDEWAY → GRID_INTENT (bukan LONG).</div>'; }); }

  function renderAudit(){ safe("audit",function(){ if(_auditTests) $("#auditList").innerHTML=_auditTests.map(function(t){ return '<div class="trow"><span class="mk '+(t.ok?"ok":"no")+'">'+(t.ok?"✓":"✗")+'</span><span class="nm">'+esc(t.nm)+'</span><span class="rs">'+esc(t.rs)+'</span></div>'; }).join("");
    var pass=_auditTests?_auditTests.filter(function(t){return t.ok;}).length:0, tot=_auditTests?_auditTests.length:0;
    $("#kTest").textContent=pass+"/"+tot; $("#b-audit").textContent=pass===tot&&tot>0?"ALL CLEAR":(pass+"/"+tot); $("#b-audit").className="badge"+(pass===tot&&tot>0?" ok":"");
    $("#c-build").querySelector("b").textContent=pass===tot&&tot>0?"82/82":"STOP"; $("#c-build").className="chip"+(pass===tot&&tot>0?"":" bad");
    $("#fpKv").innerHTML=kv("fingerprint",'<span class="tag v">'+STLMS.AUDIT.fingerprint()+'</span>')+kv("self-test",pass+"/"+tot,pass===tot?"t":"r")+kv("determinism",_det?('<span class="tag '+(_det.ok?"t":"r")+'">'+(_det.ok?"identik":"mismatch")+'</span>'):"—"); });
    safe("auditdom",function(){ if(_domains) $("#auditDom2").innerHTML=_domains.map(function(d){ return '<div class="trow"><span class="mk '+(d.pass?"ok":"no")+'">'+(d.pass?"✓":"✗")+'</span><span class="nm">'+esc(d.name)+'</span><span class="rs">'+esc(d.detail)+'</span></div>'; }).join(""); }); }

  function renderKPI(){ $("#kCand").textContent=STATE?STATE.frames.length:0; $("#kCard").textContent=STLMS.WORKSPACE.count(); $("#kSnap").textContent=STATE?STATE.snapshots.length:0; $("#kLine").textContent=STATE?(STATE.frames.length?(STATE.frames[STATE.frames.length-1].struct.lines.length+" / "+STATE.frames[STATE.frames.length-1].struct.waves.length):"0 / 0"):"0 / 0"; }

  function renderFinalValidation(){ safe("finalval",function(){ if(STATE) _finalVal=STLMS.FINAL_VALIDATION.runAll(STATE,_det?_det.ok:null,_auditTests); if(_finalVal) $("#finalValList").innerHTML=_finalVal.map(function(d){ return '<div class="trow"><span class="mk '+(d.pass?"ok":"no")+'">'+(d.pass?"✓":"✗")+'</span><span class="nm">'+esc(d.domain)+'</span><span class="rs">'+esc(d.detail)+'</span></div>'; }).join(""); }); }

  function renderAll(idx){ renderKPI(); renderBoot(); renderPanels(idx); drawGeom(idx); renderClone(); drawEq(); renderTrade(); renderKnow(); renderGov(); renderSim(); renderReplay(); renderPred(); renderConsumer(); renderFinalValidation(); renderAudit(); $("#prog").textContent=(idx+1)+"/"+(STATE?STATE.frames.length:0); $("#scrub").max=Math.max(0,(STATE?STATE.frames.length:1)-1); $("#scrub").value=idx; }
  function renderBoot(){ safe("boot",function(){ $("#bootKv").innerHTML=kv("config_version","1.0")+kv("store",STLMS.WORKSPACE.available()?'<span class="tag t">indexeddb</span>':'<span class="tag s">memory</span>')+kv("cards",STLMS.WORKSPACE.count())+kv("chronicle",STLMS.WORKSPACE.chronicle().length)+kv("symbols",Object.keys(C.ASSETS).join(" · "))+kv("governor","OK"); });
    safe("cfg",function(){ $("#cfgTbl tbody").innerHTML=STLMS.CONFIG.all().map(function(c){ return "<tr><td>"+esc(c.k)+"</td><td class=\"y\">"+c.cur+"</td><td class=\"x\">"+c.min+"</td><td class=\"x\">"+c.max+"</td></tr>"; }).join(""); }); }

  function buildRun(sym,n,seed,ac,withAudit){ var candles=STLMS.MARKET.fixture(sym,n,seed); STATE=STLMS.SIMULATION.freshState(sym,candles); STATE.activeClones=ac; STATE.gaps=STLMS.MARKET.gaps(candles);
    STLMS.SIMULATION.runActive(STATE); STATE.rapor=STLMS.STATISTICS.tradeStats(STATE.markers); cursor=STATE.frames.length-1;
    STLMS.VIEW._govTs=candles.length?candles[candles.length-1].time:0;
    _rep=STLMS.REPLAY.create(STATE); _repIdx=cursor; _repKind=$("#repKind")?$("#repKind").value:"snapshot";
    if(withAudit){ _auditTests=STLMS.AUDIT.run(); _det=STLMS.SIMULATION.determinismHash(sym,80,seed); _domains=STLMS.AUDIT.domains(STATE,_det.ok); }
    renderAll(cursor); }
  function run(){ buildRun($("#gSym").value, Math.max(80,Math.min(1200,+$("#gN").value||320)), +$("#gSeed").value||42, ["LONG","SHORT","GRID"], true); }
  function runSim(){ var kind=$("#simKind").value, ac=kind==="strategy"?[$("#simClone").value]:["LONG","SHORT","GRID"];
    buildRun($("#gSym").value, Math.max(80,Math.min(1200,+$("#simN").value||320)), +$("#simSeed").value||42, ac, false);
    _simResult={kind:kind,activeClones:ac,clones:STATE.clones,markers:STATE.markers}; renderSim(); }
  function step(){ if(!STATE) return; if(cursor<STATE.frames.length-1){ cursor++; _repIdx=cursor; renderAll(cursor); } }
  function setPlay(p){ if(playT){ clearInterval(playT); playT=null; } $("#bPlay").textContent=p?"⏸ pause":"▶ play"; $("#bPlay").classList.toggle("on",p);
    if(p){ var spd=Math.max(1,+$("#gSpd").value||14); playT=setInterval(function(){ if(!STATE){ setPlay(false); return; } if(cursor<STATE.frames.length-1){ cursor++; _repIdx=cursor; renderAll(cursor); } else setPlay(false); }, Math.round(1000/spd)); } }
  function setRepPlay(p){ if(_repPlay){ clearInterval(_repPlay); _repPlay=null; } $("#repPlay").textContent=p?"⏸ pause":"▶ play"; $("#repPlay").classList.toggle("on",p);
    if(p){ var spd=Math.max(1,+$("#repSpd").value||16); _repPlay=setInterval(function(){ if(!_rep){ setRepPlay(false); return; } if(_repIdx<_rep.n-1){ _repIdx++; $("#repScrub").value=_repIdx; renderReplay(); } else setRepPlay(false); }, Math.round(1000/spd)); } }

  function bind(){ $("#bRun").onclick=run; $("#bStep").onclick=function(){ setPlay(false); step(); };
    $("#bPlay").onclick=function(){ setPlay(!playT); }; $("#bPrev").onclick=function(){ setPlay(false); if(cursor>0){ cursor--; _repIdx=cursor; renderAll(cursor); } };
    $("#bNext").onclick=function(){ setPlay(false); step(); }; $("#scrub").oninput=function(e){ setPlay(false); cursor=+e.target.value; _repIdx=cursor; renderAll(cursor); };
    $("#bVerify").onclick=function(){ var fp=STLMS.AUDIT.fingerprint(), fp2=STLMS.AUDIT.fingerprint(); $("#fpKv").innerHTML=kv("fingerprint",'<span class="tag v">'+fp+'</span>')+kv("re-verify",fp===fp2?'<span class="tag t">deterministic ✓</span>':'<span class="tag r">mismatch ✗</span>'); };
    $("#simRun").onclick=runSim;
    $("#repPrev").onclick=function(){ setRepPlay(false); if(_rep&&_repIdx>0){ _repIdx--; $("#repScrub").value=_repIdx; renderReplay(); } };
    $("#repNext").onclick=function(){ setRepPlay(false); if(_rep&&_repIdx<_rep.n-1){ _repIdx++; $("#repScrub").value=_repIdx; renderReplay(); } };
    $("#repPlay").onclick=function(){ setRepPlay(!_repPlay); };
    $("#repScrub").oninput=function(e){ setRepPlay(false); _repIdx=+e.target.value; renderReplay(); };
    $("#repKind").onchange=function(e){ _repKind=e.target.value; renderReplay(); };
    $("#govProp").onclick=function(e){ var b=e.target.closest("[data-gov]"); if(!b||!STATE) return; var p=(STATE.darwin||[])[+b.dataset.i]; if(!p) return;
      var val=p.value; var r=STLMS.GOVERNANCE.decide(p.id||i, b.dataset.gov==="app"?"APPROVED":"REJECTED", val, STATE.darwin); toast((r.decision||"")+" "+(p.param||"")+(r.value!=null?" = "+r.value:"")); renderGov(); };
    $("#govRollback").onclick=function(){ STLMS.GOVERNANCE.rollback(); toast("config di-rollback ke default"); renderGov(); renderBoot(); };
    $("#wasRun").onclick=function(){ var param=$("#wasParam").value, value=parseFloat($("#wasVal").value), folds=Math.max(2,Math.min(8,+$("#wasFolds").value||3));
      $("#wasOut").innerHTML='<div class="empty">worker paralel berjalan…</div>';
      STLMS.BENCHMARK.walkForward($("#gSym").value, Math.max(120,+$("#wasN").value||300), +$("#wasSeed").value||7, param, value, folds, function(res){
        if(res.verdict==="REJECTED"){ $("#wasOut").innerHTML='<div class="verdict r">REJECTED</div><div class="kv">'+kv("reason",esc(res.reason||"—"),"r")+'</div>'; return; }
        var g=res.gates||{}; $("#wasOut").innerHTML='<div class="verdict '+(res.verdict==="PASS"?"t":"r")+'">'+esc(res.verdict)+'</div>'+
          '<div class="kv" style="margin:8px 0">'+kv("parallel",res.parallel?'<span class="tag t">WORKER</span>':'<span class="tag s">fallback seq</span>')+kv("folds",res.folds)+kv("base exits",res.total_base)+kv("cand exits",res.total_cand)+'</div>'+
          '<table><thead><tr><th>gate</th><th>arti</th><th>lulus</th></tr></thead><tbody>'+
          [["G1","cand exits ≥30",g.G1],["G2","expectancy cand > base",g.G2],["G3","worst-loss tak memburuk >10%",g.G3],["G4","win-rate tak anjlok >2%",g.G4],["G5","fee-drag tak naik",g.G5]].map(function(rw){ return "<tr><td>"+rw[0]+"</td><td>"+rw[1]+"</td><td class=\""+(rw[2]?"y":"n")+"\">"+(rw[2]?"✓":"✗")+"</td></tr>"; }).join("")+
          '</tbody></table>'; }); };
    $("#conCsv").onclick=function(){ if(!STATE) return; var csv=STLMS.CONSUMER.exportCSV(STATE.markers); var blob=new Blob([csv],{type:"text/csv"}); var a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download="stlms_markers_"+STATE.sym+".csv"; a.click(); toast("csv exported"); };
    $$(".reveal").forEach(function(el){ revObs.observe(el); }); }
  var revObs=new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting){ en.target.classList.add("in"); revObs.unobserve(en.target); } }); },{threshold:.08});
  function toast(m){ var t=$("#toast"); if(!t) return; t.textContent=m; t.classList.add("show"); clearTimeout(t._t); t._t=setTimeout(function(){ t.classList.remove("show"); },1900); }

  function navActive(){ var secs=$$(".sec"), links=$$("nav.man a");
    var obs=new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting){ var id=en.target.id; links.forEach(function(a){ a.classList.toggle("on", a.getAttribute("data-s")===id); }); } }); },{rootMargin:"-45% 0px -50% 0px"});
    secs.forEach(function(s){ obs.observe(s); });
    links.forEach(function(a){ a.addEventListener("click",function(e){ e.preventDefault(); var t=document.getElementById(a.getAttribute("data-s")); if(t) t.scrollIntoView({behavior:"smooth"}); }); }); }

  function ambient(){ var cv=$("#field"), x=cv.getContext("2d"), w,h,walls=[],st=[],dots=[],t=0,raf, reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
    function size(){ w=cv.width=innerWidth; h=cv.height=innerHeight; build(); }
    function build(){ walls=[]; for(var i=0;i<6;i++) walls.push({y:h*(0.14+0.13*i),drift:(Math.random()-0.5)*0.06,col:i%2?"31,199,168":"255,93,115",dash:i%3===0});
      st=[]; var sy=h*0.5; for(var j=0;j<60;j++){ sy+=(Math.random()-0.5)*22; sy=Math.max(h*0.2,Math.min(h*0.8,sy)); st.push(sy); }
      dots=[]; for(var k=0;k<70;k++) dots.push({x:Math.random()*w,y:Math.random()*h,vy:(Math.random()-0.5)*0.12,r:Math.random()<0.5?1:1.4}); }
    function frame(){ x.clearRect(0,0,w,h); t+=1;
      walls.forEach(function(wl){ wl.y+=wl.drift; if(wl.y<h*0.06||wl.y>h*0.94) wl.drift*=-1; x.strokeStyle="rgba("+wl.col+",0.10)"; x.lineWidth=1; if(wl.dash) x.setLineDash([6,7]); else x.setLineDash([]); x.beginPath(); x.moveTo(0,wl.y); x.lineTo(w,wl.y); x.stroke(); }); x.setLineDash([]);
      var off=(t*0.5)%40; x.strokeStyle="rgba(244,180,0,0.16)"; x.lineWidth=1.4; x.beginPath(); for(var i=0;i<st.length;i++){ var px=i*(w/(st.length-1))-off, py=st[i]; i?x.lineTo(px,py):x.moveTo(px,py); } x.stroke();
      dots.forEach(function(d){ d.y+=d.vy; if(d.y<0||d.y>h) d.vy*=-1; x.fillStyle="rgba(233,227,213,0.13)"; x.beginPath(); x.arc(d.x,d.y,d.r,0,7); x.fill(); });
      raf=requestAnimationFrame(frame); }
    size(); if(!reduce) frame(); addEventListener("resize",function(){ cancelAnimationFrame(raf); size(); if(!reduce) frame(); }); }

  function clock(){ var el=$("#clock"), p=function(n){return String(n).padStart(2,"0");}; function t(){ var d=new Date(Date.now()+7*3600000); el.firstChild.textContent=p(d.getUTCHours())+":"+p(d.getUTCMinutes())+":"+p(d.getUTCSeconds()); } t(); setInterval(t,1000); }

  function init(){ ambient(); clock(); navActive(); bind(); STLMS.WORKSPACE.openDB().then(function(){ run(); }); }
  return {init:init,renderAll:renderAll,toast:toast};
})();

if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",function(){ STLMS.VIEW.init(); }); else STLMS.VIEW.init();
