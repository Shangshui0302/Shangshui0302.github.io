import {createStellarResponse} from './stellar-response.js';

/* Original perspective geometry. All simulation is local and illustrative. */
export function initStellar(root, scope) {
  const reducedQuery=matchMedia('(prefers-reduced-motion: reduce)');
  const fine=matchMedia('(hover: hover) and (pointer: fine)');
  const TAU=Math.PI*2;
  root.querySelectorAll('.galaxy-experience').forEach(hero=>{
    const field=hero.querySelector('.galaxy-field'), canvas=hero.querySelector('canvas');
    const ctx=canvas.getContext('2d',{alpha:false});
    const pause=hero.querySelector('.stellar-pause'), pulseButton=hero.querySelector('.galaxy-pulse');
    const reset=hero.querySelector('.galaxy-reset'), status=hero.querySelector('.galaxy-state');
    const journey=hero.querySelector('.galaxy-journey'), depth=hero.querySelector('.journey-depth');
    const chargeLabel=hero.querySelector('.charge-label'), chargeValue=hero.querySelector('.charge-value');
    const styleValues = new Map();
    const setStyle = (name, value) => {
      if (styleValues.get(name) !== value) { styleValues.set(name, value); hero.style.setProperty(name, value); }
    };
    const setText = (node, value) => { if (node && node.textContent !== value) node.textContent = value; };
    const setCharge = value => { if (hero.dataset.charge !== value) hero.dataset.charge = value; };
    let journeyTop=0,journeyHeight=1,journeyTarget=0,journeyProgress=0;
    let charging=false,charge=0,chargeStart=0,chargePointer=null,orbitalTime=0,burst=0,ignoreClickUntil=0;
    const response=createStellarResponse();
    let heldPointer=null,keyboardHeld=false;
    if(!ctx){[pause,pulseButton,reset].forEach(b=>b.hidden=true);return;}
    let W=1,H=1,dpr=1,mobile=false,frame=0,last=0,drawTime=0,t=0,visible=false,manual=false,reduced=false,paused=false;
    let scroll=0,scrollTarget=0,dragging=false,dragTravel=0,downX=0,downY=0,yawDrag=0,pitchDrag=0,inertia=0;
    let pointer={x:0,y:0,tx:0,ty:0,px:-9999,py:-9999,inside:false,gain:0},flares=[],mesh=[];
    let seed=481;const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
    const stars=Array.from({length:170},()=>({x:rnd(),y:rnd(),s:.3+rnd()*1.2,z:rnd(),phase:rnd()*TAU}));
    const dust=Array.from({length:1050},(_,i)=>{const r=.8+Math.pow(rnd(),.62)*4.5,a=(i%3)*TAU/3+Math.log(r)*2.2+(rnd()-.5)*.65;return {r,a,z:(rnd()-.5)*.22,s:.4+rnd()*1.3,light:rnd()};});
    const rings=[{r:2.35,tilt:1.08,turn:-.28,speed:.11,phase:1.9,red:false},{r:3.5,tilt:.72,turn:.55,speed:-.065,phase:4.0,red:true},{r:2.85,tilt:1.28,turn:-.88,speed:.085,phase:5.7,red:false},{r:4.4,tilt:1.12,turn:.16,speed:-.04,phase:.5,red:false}];
    let centerX=0,centerY=0,R=1,camera=1,rotY=0,rotX=0,rotZ=0,cy=1,sy=0,cx=1,sx=0,cz=1,sz=0,energy=0;
    const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
    function geometry(){
      mesh=[];const meridians=mobile?18:32,latitudes=mobile?17:25,steps=mobile?48:80;
      for(let i=0;i<meridians;i++){
        const a=i*TAU/meridians,curve=[];
        for(let j=0;j<=steps;j++){const b=-Math.PI/2+j*Math.PI/steps;curve.push([Math.cos(b)*Math.cos(a),Math.sin(b),Math.cos(b)*Math.sin(a)]);}
        mesh.push(curve);
      }
      for(let i=1;i<latitudes;i++){
        const b=-Math.PI/2+i*Math.PI/latitudes,curve=[];
        for(let j=0;j<=steps;j++){const a=j*TAU/steps;curve.push([Math.cos(b)*Math.cos(a),Math.sin(b),Math.cos(b)*Math.sin(a)]);}
        mesh.push(curve);
      }
    }
    function rotate(x,y,z){
      const a=x*cy+z*sy,b=-x*sy+z*cy,c=y*cx-b*sx,d=y*sx+b*cx;
      return {x:a*cz-c*sz,y:a*sz+c*cz,z:d};
    }
    function project(p){const k=camera/(camera-p.z);return {x:centerX+p.x*k,y:centerY+p.y*k,z:p.z,k};}
    function ringPoint(ring,a){
      const x=Math.cos(a)*R*ring.r,y=Math.sin(a)*R*ring.r,z=y*Math.sin(ring.tilt),yp=y*Math.cos(ring.tilt),c=Math.cos(ring.turn),s=Math.sin(ring.turn);
      return rotate(x*c-yp*s,x*s+yp*c,z);
    }
    function orbitalPath(ring,front){
      ctx.beginPath();let pen=false;
      for(let i=0;i<=160;i++){
        const p=ringPoint(ring,i*TAU/160),v=project(p),isFront=p.z>=0;
        if(isFront===front){if(pen)ctx.lineTo(v.x,v.y);else ctx.moveTo(v.x,v.y);pen=true;}else pen=false;
      }
      ctx.strokeStyle=ring.red?`rgba(255,77,46,${front?.62:.22})`:`rgba(204,197,181,${front?.35:.12})`;
      ctx.lineWidth=ring.red?1:.7;ctx.stroke();
    }
    function particles(){
      const count=mobile?440:dust.length;
      const paths=Array.from({length:8},()=>new Path2D());
      for(let i=0;i<count;i++){
        const p=dust[i],a=p.a+t*.025,r=p.r*R;
        const x=Math.cos(a)*r,y=Math.sin(a)*r*.26,z=Math.sin(a)*r*.95+p.z*R;
        const v=project(rotate(x,y,z));
        if(v.x<-10||v.x>W+10||v.y<-10||v.y>H+10)continue;
        const dx=pointer.px-v.x,dy=pointer.py-v.y,dist=dx*dx+dy*dy;
        const pull=pointer.gain>.005?Math.exp(-dist/30000)*.13*pointer.gain:0;
        let px=v.x+dx*pull,py=v.y+dy*pull;
        for(const f of flares){const age=t-f.time,len=Math.hypot(px-f.x,py-f.y)||1,wave=Math.exp(-Math.pow((len-age*(390+f.power*230))/90,2))*(1-age/2.7)*(28+f.power*55);px+=(px-f.x)/len*wave;py+=(py-f.y)/len*wave;}
        const bucket=p.light>.87?7:Math.min(6,Math.floor(p.light/.87*7));
        const size=p.s*clamp(v.k,.4,1.8);paths[bucket].rect(px,py,size,size);
      }
      paths.forEach((path,i)=>{ctx.fillStyle=i===7?'rgba(241,239,233,.65)':`rgba(255,92,58,${.20+(i+.5)/7*.87*.37})`;ctx.fill(path);});
    }
    function spiralArms(){
      // Fine luminous curves carry the stellar disc across the entire viewport.
      for(let arm=0;arm<3;arm++){
        for(let strand=0;strand<3;strand++){
          ctx.beginPath();
          for(let i=0;i<=130;i++){
            const r=(1.2+i/130*4.3)*R;
            const a=arm*TAU/3+Math.log(r/R)*2.2+t*.025+(strand-1)*.035;
            const q=project(rotate(Math.cos(a)*r,Math.sin(a)*r*.26,Math.sin(a)*r*.95));
            if(i)ctx.lineTo(q.x,q.y);else ctx.moveTo(q.x,q.y);
          }
          ctx.strokeStyle=strand===1?'rgba(255,77,46,.23)':'rgba(255,77,46,.065)';ctx.lineWidth=strand===1?.7:1.4;ctx.stroke();
        }
      }
    }
    function sphere(){
      const glow=ctx.createRadialGradient(centerX,centerY,R*.65,centerX,centerY,R*1.55);
      glow.addColorStop(0,`rgba(255,55,20,${.09+energy*.09})`);glow.addColorStop(1,'rgba(255,55,20,0)');
      ctx.fillStyle=glow;ctx.fillRect(centerX-R*1.6,centerY-R*1.6,R*3.2,R*3.2);
      ctx.beginPath();ctx.arc(centerX,centerY,R*1.023,0,TAU);ctx.fillStyle='#111214';ctx.fill();
      const paths=[new Path2D(),new Path2D(),new Path2D(),new Path2D()];
      const heat=clamp(response.heat+burst*.5,0,1),green=Math.round(77+162*heat),blue=Math.round(46+187*heat);
      const colors=[.15,.48,.76,1].map(alpha=>`rgba(255,${green},${blue},${alpha})`);
      const mx=(pointer.px-centerX)/R,my=(pointer.py-centerY)/R;
      const interacting=pointer.gain>.005, ripple=energy*.012+response.heat*.018;
      for(const line of mesh){let previous=null,previousBucket=-1;
        for(const point of line){
          const rotated=rotate(point[0]*R,point[1]*R,point[2]*R);
          const near=interacting&&rotated.z>0?Math.exp(-((rotated.x/R-mx)**2+(rotated.y/R-my)**2)*9)*pointer.gain:0;
          const warp=1+near*.07+(ripple>.0001?ripple*Math.sin(point[1]*16-t*3):0);
          rotated.x*=warp;rotated.y*=warp;rotated.z*=warp;
          const q=project(rotated);
          if(previous){const z=(q.z+previous.z)/2/R,bucket=z<0?0:z<.35?1:z<.75?2:3;const path=paths[bucket];if(bucket!==previousBucket)path.moveTo(previous.x,previous.y);path.lineTo(q.x,q.y);previousBucket=bucket;}
          previous=q;
        }
      }
      paths.forEach((path,i)=>{ctx.strokeStyle=colors[i];ctx.lineWidth=i===3?1:.75;ctx.stroke(path);});
      ctx.beginPath();ctx.arc(centerX,centerY,R*1.025,0,TAU);ctx.strokeStyle='rgba(255,77,46,.55)';ctx.lineWidth=.6;ctx.stroke();
      // A hot equatorial cut rotates in the same three-dimensional coordinate space.
      ctx.beginPath();let pen=false;
      for(let i=0;i<=150;i++){const a=i*TAU/150,v=rotate(Math.cos(a)*R*1.007,0,Math.sin(a)*R*1.007),q=project(v);if(v.z>=0){if(pen)ctx.lineTo(q.x,q.y);else ctx.moveTo(q.x,q.y);pen=true;}else pen=false;}
      ctx.strokeStyle='#ff6742';ctx.lineWidth=1.8;ctx.shadowColor='#ff4d2e';ctx.shadowBlur=8;ctx.stroke();ctx.shadowBlur=0;
    }
    function planets(){
      rings.forEach((ring,i)=>{
        const p=ringPoint(ring,orbitalTime*ring.speed+ring.phase),q=project(p);
        if(p.z<0&&Math.hypot(q.x-centerX,q.y-centerY)<R*1.03)return;
        const size=(i===0?10:i===1?6:3.5)*clamp(q.k,.7,1.6)*(mobile?.7:1);
        ctx.beginPath();ctx.arc(q.x,q.y,size+4,0,TAU);ctx.fillStyle='#111214';ctx.fill();
        ctx.beginPath();ctx.arc(q.x,q.y,size,0,TAU);ctx.strokeStyle=ring.red?'#ff6742':'#c8c5bd';ctx.lineWidth=.8;ctx.stroke();
        ctx.beginPath();ctx.ellipse(q.x,q.y,size*.38,size,0,0,TAU);ctx.stroke();
        ctx.beginPath();ctx.ellipse(q.x,q.y,size,size*.28,-.3,0,TAU);ctx.stroke();
        ctx.fillStyle=ring.red?'#ff6742':'#f1efe9';ctx.beginPath();ctx.arc(q.x-size*.38,q.y-size*.38,1.3,0,TAU);ctx.fill();
      });
    }
    function draw(){
      ctx.fillStyle='#111214';ctx.fillRect(0,0,W,H);
      const baseR=mobile?Math.min(W*.31,H*.19):Math.min(W*.185,H*.285);
      energy=flares.reduce((sum,f)=>sum+Math.max(0,1-(t-f.time)/2.7)*(1+f.power),0);
      burst=flares.reduce((sum,f)=>sum+f.power*Math.max(0,1-(t-f.time)/1.25),0);
      const passage=reduced?0:Math.sin(journeyProgress*Math.PI)**2;
      const arrival=clamp((journeyProgress-.70)/.30,0,1);
      R=baseR*(1+passage*4.6)*(1-arrival*.58)*(1+response.displacement+(dragging?.028:0));
      centerX=W*((mobile?.66:.725)-passage*.5-arrival*.14)+pointer.x*(mobile?8:27);
      centerY=H*((mobile?.35:.47)+passage*.32-arrival*.02)+pointer.y*18;
      camera=R*7;
      rotY=orbitalTime*.085+pointer.x*.24+yawDrag+journeyProgress*1.8;rotX=-.24+pointer.y*.20+pitchDrag;rotZ=-.27+pointer.x*.055;
      cy=Math.cos(rotY);sy=Math.sin(rotY);cx=Math.cos(rotX);sx=Math.sin(rotX);cz=Math.cos(rotZ);sz=Math.sin(rotZ);
      for(const s of stars){const x=s.x*W-pointer.x*s.z*18,y=s.y*H-pointer.y*s.z*12;ctx.fillStyle=`rgba(216,207,185,${.14+s.z*.35})`;ctx.fillRect(x,y,s.s,s.s);}
      spiralArms();particles();rings.forEach(r=>orbitalPath(r,false));sphere();rings.forEach(r=>orbitalPath(r,true));planets();
      for(const f of flares){
        const age=t-f.time;if(age<0)continue;
        const speed=390+f.power*230,fade=Math.max(0,1-age/2.7);
        ctx.beginPath();ctx.arc(f.x,f.y,age*speed,0,TAU);ctx.strokeStyle=`rgba(255,77,46,${fade*.7})`;ctx.lineWidth=.8+f.power;ctx.stroke();
        ctx.beginPath();ctx.arc(f.x,f.y,age*speed*.76,0,TAU);ctx.strokeStyle=`rgba(241,239,233,${fade*(.18+f.power*.18)})`;ctx.lineWidth=.8;ctx.stroke();
        if(f.power>.25&&age<1.4){
          ctx.beginPath();
          for(let i=0;i<72;i++){const a=i*TAU/72+f.time,r=age*speed*(.72+(i%5)*.08),len=(12+f.power*34)*(1-age/1.4);ctx.moveTo(f.x+Math.cos(a)*r,f.y+Math.sin(a)*r);ctx.lineTo(f.x+Math.cos(a)*(r+len),f.y+Math.sin(a)*(r+len));}
          ctx.strokeStyle=`rgba(255,143,101,${(1-age/1.4)*.65})`;ctx.stroke();
        }
      }
      if(charging){
        ctx.beginPath();ctx.arc(centerX,centerY,R*1.18,-Math.PI/2,-Math.PI/2+TAU*charge);ctx.strokeStyle='#f1efe9';ctx.lineWidth=1.4;ctx.stroke();
        for(let i=0;i<28;i++){const a=i*TAU/28+t*.22,rr=R*(1.35+((i*.17+t*1.2)%1)*1.35);ctx.beginPath();ctx.moveTo(centerX+Math.cos(a)*rr,centerY+Math.sin(a)*rr);ctx.lineTo(centerX+Math.cos(a)*(rr+18*charge),centerY+Math.sin(a)*(rr+18*charge));ctx.strokeStyle=`rgba(255,106,69,${charge*.65})`;ctx.lineWidth=.7;ctx.stroke();}
      }
      if(pointer.gain>.02&&!mobile){ctx.globalAlpha=pointer.gain*.5;ctx.strokeStyle='#ff6742';ctx.lineWidth=.7;ctx.beginPath();ctx.arc(pointer.px,pointer.py,dragging?19:9,0,TAU);ctx.moveTo(pointer.px-16,pointer.py);ctx.lineTo(pointer.px-11,pointer.py);ctx.moveTo(pointer.px+11,pointer.py);ctx.lineTo(pointer.px+16,pointer.py);ctx.stroke();ctx.globalAlpha=1;}
    }
    function tick(now){
      frame=scope.frame(tick);
      if(now-drawTime<(mobile?32:18))return;
      const dt=last?Math.min((now-last)/1000,.06):.016;last=now;drawTime=now;t+=dt;
      if(charging)charge=clamp((t-chargeStart)/1.65,0,1);
      response.step(charge,dt);
      orbitalTime+=dt*(1+response.heat*5);
      const smooth=1-Math.exp(-dt*5);pointer.x+=(pointer.tx-pointer.x)*smooth;pointer.y+=(pointer.ty-pointer.y)*smooth;
      pointer.gain+=((pointer.inside?1:0)-pointer.gain)*smooth;scroll+=(scrollTarget-scroll)*smooth;
      journeyProgress+=(journeyTarget-journeyProgress)*smooth;
      setStyle('--journey',journeyProgress.toFixed(3));
      setStyle('--journey-shift',`${(-journeyProgress*70).toFixed(1)}px`);
      setText(depth,String(Math.round(journeyProgress*100)).padStart(3,'0')+'%');
      setStyle('--charge',charge.toFixed(3));
      setCharge(String(Math.round(charge*100)));
      if(charging)setText(chargeValue,charge>=1?'RELEASE TO IGNITE':String(Math.round(charge*100)).padStart(3,'0')+'%');
      setStyle('--type-kick',`${(-response.displacement/.27*8).toFixed(1)}px`);
      if(!dragging){yawDrag+=inertia;inertia*=Math.pow(.91,dt*60);}
      const hadFlares=flares.length;flares=flares.filter(f=>t-f.time<2.7);
      if(hadFlares&&!flares.length&&!dragging&&!charging)status.textContent='自由运行';
      draw();
    }
    function endDrag(){
      const captured=heldPointer;
      heldPointer=null;dragging=false;hero.classList.remove('is-dragging');
      pointer.inside=false;pointer.tx=pointer.ty=0;
      if(captured!==null&&hero.hasPointerCapture(captured))hero.releasePointerCapture(captured);
    }
    function cancelInteraction(){endDrag();cancelCharge();inertia=0;}
    function sync(){
      if (scope.disposed) return;
      reduced=reducedQuery.matches||document.documentElement.dataset.reducedMotion==='true';paused=manual||reduced;
      hero.dataset.paused=String(paused);pause.disabled=reduced;pulseButton.disabled=paused;reset.disabled=reduced;
      pause.setAttribute('aria-pressed',String(paused));pause.innerHTML=reduced?'静态星系 <span aria-hidden="true">○</span>':manual?'继续运行 <span aria-hidden="true">▷</span>':'暂停星系 <span aria-hidden="true">Ⅱ</span>';
      status.textContent=paused?'静态轨道':'自由运行';
      if(frame)cancelAnimationFrame(frame);frame=0;last=0;
      if(paused||document.hidden||!visible)cancelInteraction();
      if(paused){response.reset();setStyle('--type-kick','0px');}
      if(reduced){pointer.x=pointer.y=pointer.gain=0;flares=[];setStyle('--type-kick','0px');}
      measureJourney();
      if(visible&&!document.hidden&&!paused)frame=scope.frame(tick);
      else if(visible)draw();
    }
    function resize(){
      if (scope.disposed) return;
      // Bound background raster cost independently of text and layout resolution.
      const nextMobile=innerWidth<701,nextDpr=Math.min(devicePixelRatio||1,1.15,Math.sqrt(1_000_000/(innerWidth*innerHeight)));
      if(W===innerWidth&&H===innerHeight&&dpr===nextDpr)return;
      W=innerWidth;H=innerHeight;const previous=mobile;mobile=nextMobile;dpr=nextDpr;
      canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);
      if(!mesh.length||previous!==mobile)geometry();measureJourney();if(!frame)draw();field.classList.add('ready');
    }
    function measureJourney(){
      if(journey){journeyTop=journey.getBoundingClientRect().top+scrollY;journeyHeight=journey.offsetHeight;}
      updateScroll();
    }
    function updateScroll(){
      scrollTarget=clamp(scrollY/H,0,1.5);
      journeyTarget=journey?clamp((scrollY-journeyTop+H*.70)/(journeyHeight+H*.12),0,1):0;
    }
    function ignite(x=centerX,y=centerY,power=0){
      if(paused)return;
      if(!power)response.velocity+=.42;
      flares.push({x,y,time:t,power});if(flares.length>3)flares.shift();status.textContent=power>.3?'恒星爆发':'脉冲扩散';
    }
    function beginCharge(){
      if(paused||charging)return;
      charging=true;charge=0;chargeStart=t;hero.classList.add('is-charging');chargeLabel.textContent='松开释放';status.textContent='恒星蓄能';
    }
    function cancelCharge(){
      charging=false;charge=0;keyboardHeld=false;
      const captured=chargePointer;chargePointer=null;
      if(captured!==null&&pulseButton.hasPointerCapture(captured))pulseButton.releasePointerCapture(captured);
      hero.classList.remove('is-charging');setStyle('--charge','0');setCharge('0');
      chargeLabel.textContent='长按蓄能';chargeValue.textContent='HOLD TO IGNITE';
      status.textContent=paused?'静态轨道':'自由运行';
    }
    function releaseCharge(){
      if(!charging)return;
      const power=charge*2;cancelCharge();ignoreClickUntil=performance.now()+450;ignite(centerX,centerY,power);
    }
    const interactive=e=>e.target.closest('a,button,input,select,summary');
    scope.on(hero,'pointermove',e=>{
      if(paused||e.pointerType==='touch')return;
      pointer.px=e.clientX;pointer.py=e.clientY;pointer.tx=(e.clientX/W-.5)*2;pointer.ty=(e.clientY/H-.5)*2;pointer.inside=!interactive(e);
      if(dragging){const dx=e.clientX-downX,dy=e.clientY-downY;yawDrag+=dx*.006;pitchDrag=clamp(pitchDrag+dy*.004,-.95,.95);inertia=dx*.003;dragTravel+=Math.abs(dx)+Math.abs(dy);downX=e.clientX;downY=e.clientY;}
    });
    scope.on(hero,'pointerleave',()=>{if(!dragging){pointer.inside=false;pointer.tx=pointer.ty=0;}});
    scope.on(hero,'pointerdown',e=>{
      if(paused||interactive(e)||e.button!==0)return;
      downX=e.clientX;downY=e.clientY;dragTravel=0;heldPointer=e.pointerId;
      if(e.pointerType!=='touch'&&fine.matches){dragging=true;hero.classList.add('is-dragging');hero.setPointerCapture(e.pointerId);status.textContent='轨道牵引';}
    });
    scope.on(hero,'pointerup',e=>{
      if(e.pointerId!==heldPointer)return;
      const wasDragging=dragging;
      endDrag();
      if(paused||interactive(e))return;
      if(wasDragging){if(dragTravel<7)ignite(e.clientX,e.clientY);else status.textContent='自由运行';}
      else if(e.pointerType==='touch'&&Math.hypot(e.clientX-downX,e.clientY-downY)<10)ignite(e.clientX,e.clientY);
    });
    scope.on(hero,'pointercancel',e=>{if(e.pointerId===heldPointer)cancelInteraction();});
    scope.on(hero,'lostpointercapture',e=>{if(e.pointerId===heldPointer)cancelInteraction();});
    scope.on(pause,'click',()=>{manual=!manual;sync();});
    scope.on(pulseButton,'pointerdown',e=>{
      if(e.button!==0||paused||charging)return;e.stopPropagation();beginCharge();chargePointer=e.pointerId;pulseButton.setPointerCapture(e.pointerId);
    });
    scope.on(pulseButton,'pointerup',e=>{if(e.pointerId!==chargePointer)return;e.stopPropagation();releaseCharge();});
    scope.on(pulseButton,'pointercancel',e=>{if(e.pointerId===chargePointer)cancelCharge();});
    scope.on(pulseButton,'lostpointercapture',e=>{if(e.pointerId===chargePointer&&charging)cancelCharge();});
    scope.on(pulseButton,'contextmenu',e=>e.preventDefault());
    scope.on(pulseButton,'keydown',e=>{
      if(e.code!=='Space'||paused)return;e.preventDefault();if(!e.repeat&&!charging){keyboardHeld=true;beginCharge();}
    });
    scope.on(pulseButton,'keyup',e=>{if(e.code==='Space'&&keyboardHeld){e.preventDefault();releaseCharge();}});
    scope.on(pulseButton,'blur',()=>{if(charging)cancelCharge();});
    scope.on(pulseButton,'click',()=>{if(performance.now()>ignoreClickUntil&&!charging)ignite();});
    scope.on(reset,'click',()=>{cancelInteraction();response.reset();setStyle('--type-kick','0px');yawDrag=pitchDrag=inertia=0;pointer.tx=pointer.ty=0;flares=[];status.textContent=paused?'静态轨道':'自由运行';draw();});
    scope.on(window,'pageshow',sync);
    scope.on(window,'scroll',updateScroll,{passive:true});
    const resizeObserver = new ResizeObserver(resize);
    const intersectionObserver = new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();},{threshold:.01});
    const motionObserver = new MutationObserver(sync);
    resizeObserver.observe(field);
    intersectionObserver.observe(hero);
    const atlas = hero.querySelector('.galaxy-atlas');
    const atlasObserver = new IntersectionObserver(entries => { hero.dataset.atlasVisible = String(entries[0].isIntersecting); });
    if(atlas)atlasObserver.observe(atlas);
    motionObserver.observe(document.documentElement,{attributes:true,attributeFilter:['data-reduced-motion']});
    scope.on(document,'visibilitychange',sync);
    scope.on(reducedQuery,'change',sync);
    scope.on(window,'blur',cancelInteraction);
    scope.on(hero,'stellar:replay',()=>{cancelInteraction();response.reset();setStyle('--type-kick','0px');t=orbitalTime=0;manual=false;yawDrag=pitchDrag=inertia=0;flares=[];sync();});
    scope.own(() => {
      resizeObserver.disconnect(); intersectionObserver.disconnect(); motionObserver.disconnect(); atlasObserver.disconnect();
      cancelAnimationFrame(frame); cancelInteraction();
    });
    resize();sync();
  });
}
