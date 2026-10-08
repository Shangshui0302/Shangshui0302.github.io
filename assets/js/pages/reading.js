/* Local reading affordances; no network, analytics, or persistent reading history. */
export function initReading(root, scope) {
  const progress=root.querySelector('.reading-progress');
  const body=root.querySelector('.reading-body');
  const topbar=document.querySelector('.topbar');
  const links=[...root.querySelectorAll('.local-toc nav a,.article-toc nav a')];
  const targets=links.map(link=>({link,target:document.getElementById(decodeURIComponent(link.hash.slice(1)))})).filter(item=>item.target);
  let pending=false,previous=-1;
  function update(){
    pending=false;
    const header=topbar?.getBoundingClientRect().height||76;
    document.documentElement.style.setProperty('--topbar-height',`${header}px`);
    if(body&&progress){
      const rect=body.getBoundingClientRect(),distance=Math.max(1,rect.height-innerHeight+header+30);
      const value=Math.round(Math.max(0,Math.min(1,(header+30-rect.top)/distance))*100);
      if(value!==previous){previous=value;progress.style.setProperty('--read-progress',`${value}%`);progress.setAttribute('aria-valuenow',String(value));root.querySelectorAll('.reading-status span').forEach(el=>el.textContent=`${value}%`);}
    }
    let current=targets[0];
    for(const item of targets)if(item.target.getBoundingClientRect().top<header+85)current=item;
    for(const item of targets){if(item===current)item.link.setAttribute('aria-current','location');else item.link.removeAttribute('aria-current');}
  }
  const schedule=()=>{if(!pending){pending=true;scope.frame(update);}};
  scope.on(window,'scroll',schedule,{passive:true});scope.on(window,'resize',schedule);scope.on(window,'pageshow',schedule);
  document.fonts?.ready.then(() => { if (!scope.disposed) schedule(); });
  root.querySelectorAll('.scenario-controls input').forEach(input=>scope.on(input,'change',()=>{
    if(!input.checked)return;
    root.querySelectorAll('.scenario-panel').forEach(panel=>panel.hidden=panel.dataset.scenario!==input.value);schedule();
  }));
  update();
}
