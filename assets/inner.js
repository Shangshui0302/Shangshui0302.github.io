/* Local reading affordances; no network, analytics, or persistent reading history. */
(() => {
  const progress=document.querySelector('.reading-progress');
  const body=document.querySelector('.reading-body');
  const topbar=document.querySelector('.topbar');
  const links=[...document.querySelectorAll('.local-toc nav a,.article-toc nav a')];
  const targets=links.map(link=>({link,target:document.getElementById(link.hash.slice(1))})).filter(item=>item.target);
  let pending=false,previous=-1;
  function update(){
    pending=false;
    const header=topbar?.getBoundingClientRect().height||76;
    document.documentElement.style.setProperty('--topbar-height',`${header}px`);
    if(body&&progress){
      const rect=body.getBoundingClientRect(),distance=Math.max(1,rect.height-innerHeight+header+30);
      const value=Math.round(Math.max(0,Math.min(1,(header+30-rect.top)/distance))*100);
      if(value!==previous){previous=value;progress.style.setProperty('--read-progress',`${value}%`);progress.setAttribute('aria-valuenow',String(value));document.querySelectorAll('.reading-status span').forEach(el=>el.textContent=`${value}%`);}
    }
    let current=targets[0];
    for(const item of targets)if(item.target.getBoundingClientRect().top<header+85)current=item;
    for(const item of targets){if(item===current)item.link.setAttribute('aria-current','location');else item.link.removeAttribute('aria-current');}
  }
  const schedule=()=>{if(!pending){pending=true;requestAnimationFrame(update);}};
  addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule);addEventListener('pageshow',schedule);
  document.fonts?.ready.then(schedule);
  document.querySelectorAll('.scenario-controls input').forEach(input=>input.addEventListener('change',()=>{
    if(!input.checked)return;
    document.querySelectorAll('.scenario-panel').forEach(panel=>panel.hidden=panel.dataset.scenario!==input.value);schedule();
  }));
  update();
})();
