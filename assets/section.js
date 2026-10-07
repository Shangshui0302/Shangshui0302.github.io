(() => {
  const root = document.documentElement;
  root.classList.remove('no-js');
  const systemMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const motion = document.querySelector('.motion');
  let preference = null;
  try { preference = localStorage.getItem('offset-reduced-motion'); } catch {}
  let reduced = systemMotion.matches || preference === 'true';
  const applyMotion = () => {
    root.dataset.reducedMotion = String(reduced);
    motion?.setAttribute('aria-pressed', String(reduced));
    if (motion) {
      motion.disabled = systemMotion.matches;
      motion.title = systemMotion.matches ? '遵循系统的减少动效设置' : '';
    }
    root.classList.toggle('motion-ready', !reduced);
  };
  applyMotion();
  motion?.addEventListener('click', () => {
    preference = String(!reduced);
    reduced = systemMotion.matches || preference === 'true';
    applyMotion();
    try { localStorage.setItem('offset-reduced-motion', String(reduced)); } catch {}
  });
  systemMotion.addEventListener('change', e => { reduced = e.matches || preference === 'true'; applyMotion(); });
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.remove('pending'); entry.target.classList.add('visible'); observer.unobserve(entry.target); }
    }), {threshold:.12});
    document.querySelectorAll('.cut-reveal').forEach(el => { el.classList.add('pending'); observer.observe(el); });
  }
  const wordmark = document.querySelector('.wordmark');
  let queued = false;
  if (wordmark) addEventListener('scroll', () => {
    if (queued || reduced || innerWidth <= 760) return;
    queued = true;
    requestAnimationFrame(() => {
      wordmark.style.setProperty('--slice-shift', `${Math.min(8, Math.max(0, scrollY / 35))}px`);
      queued = false;
    });
  }, {passive:true});

  const topic = document.querySelector('#topic');
  const noteRows = [...document.querySelectorAll('#writing-list .writing-row')];
  const count = document.querySelector('.count');
  topic?.addEventListener('change', () => {
    let visible = 0;
    noteRows.forEach(row => {
      row.hidden = topic.value !== 'all' && row.dataset.category !== topic.value;
      if (!row.hidden) visible++;
    });
    if (count) count.textContent = `${visible} 篇文章`;
    document.querySelector('#writing-empty').hidden = visible > 0;
  });

  const form = document.querySelector('#search');
  const input = document.querySelector('#search-input');
  const kind = document.querySelector('#kind');
  const results = [...document.querySelectorAll('#search-results .result-row')];
  if (form && input && kind) {
    const params = new URLSearchParams(location.search);
    input.value = params.get('q') || '';
    if (['all','work','writing'].includes(params.get('kind'))) kind.value = params.get('kind');
    const filter = () => {
      const terms = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      results.forEach(row => {
        row.hidden = (kind.value !== 'all' && row.dataset.kind !== kind.value) || !terms.every(term => row.dataset.search.toLocaleLowerCase().includes(term));
        if (!row.hidden) visible++;
      });
      count.textContent = `${visible} 项内容`;
      document.querySelector('#search-empty').hidden = visible > 0;
      const next = new URL(location.href);
      input.value.trim() ? next.searchParams.set('q', input.value.trim()) : next.searchParams.delete('q');
      kind.value !== 'all' ? next.searchParams.set('kind',kind.value) : next.searchParams.delete('kind');
      history.replaceState(null,'',next);
    };
    input.addEventListener('input',filter);
    kind.addEventListener('change',filter);
    form.addEventListener('submit',e=>{e.preventDefault();filter();});
    document.querySelector('.reset-search').addEventListener('click',()=>{input.value='';kind.value='all';filter();input.focus();});
    filter();
  }

  document.querySelectorAll('.copy-code').forEach(button => {
    button.addEventListener('click', async () => {
      const code = button.parentElement.querySelector('code').textContent;
      try {
        await navigator.clipboard.writeText(code);
        button.textContent = '已复制';
      } catch {
        button.textContent = '复制失败，请手动选择';
      }
      button.setAttribute('aria-live','polite');
      setTimeout(()=>{button.textContent='复制代码';},2200);
    });
  });
})();
