(() => {
  document.documentElement.classList.remove('no-js');
  const names=['section','archive','fold'];
  const links=[...document.querySelectorAll('[data-select]')];
  let active='section';
  function choose(name, update=true) {
    if (!names.includes(name)) return;
    active=name;
    document.querySelector('.ribbon-stage').classList.remove('expanded');
    document.querySelector('.project-ribbon').setAttribute('aria-expanded','false');
    document.querySelectorAll('.direction').forEach(panel=>{
      panel.hidden=panel.id!==name;
      panel.classList.remove('enter');
    });
    links.forEach(a=>a.dataset.select===name?a.setAttribute('aria-current','page'):a.removeAttribute('aria-current'));
    const panel=document.getElementById(name);
    void panel.offsetWidth;
    panel.classList.add('enter');
    if(name==='section')panel.querySelector('.stellar-hero')?.dispatchEvent(new Event('stellar:replay'));
    document.title=links.find(a=>a.dataset.select===name).textContent.trim()+' · OFFSET 视觉 Demo';
    if(update)history.replaceState(null,'','#'+name);
    window.scrollTo({top:0,behavior:'instant'});
  }
  links.forEach(a=>a.addEventListener('click',e=>{e.preventDefault();choose(a.dataset.select);}));
  document.querySelector('#replay').addEventListener('click',()=>choose(active,false));
  document.querySelectorAll('.small-brand').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();choose(active);}));
  document.querySelectorAll('.site-nav a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{
    const target=document.querySelector(a.getAttribute('href'));
    if(target){e.preventDefault();target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
  }));
  const fold=document.querySelector('.project-ribbon');
  fold.addEventListener('click',()=>{
    const stage=document.querySelector('.ribbon-stage');
    const panel=document.querySelector('.fold');
    panel.classList.remove('enter');
    const expanded=stage.classList.toggle('expanded');
    fold.setAttribute('aria-expanded',String(expanded));
  });
  choose(names.includes(location.hash.slice(1))?location.hash.slice(1):'section',false);
  window.addEventListener('hashchange',()=>{if(names.includes(location.hash.slice(1)))choose(location.hash.slice(1),false);});
})();
