/* Select-only combobox. Native select remains the value/change contract and fallback. */
export function enhanceSelects(root, scope) {
  root.querySelectorAll('select').forEach(select => {
    const label = root.querySelector(`label[for="${select.id}"]`);
    if (!label) return;
    label.id ||= `${select.id}-label`;
    const wrapper = document.createElement('div');
    wrapper.className = 'select-control';
    select.before(wrapper);
    wrapper.append(select);
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.id = `${select.id}-trigger`;
    trigger.className = 'select-trigger';
    trigger.setAttribute('role', 'combobox');
    trigger.setAttribute('aria-haspopup', 'listbox');
    trigger.setAttribute('aria-expanded', 'false');
    trigger.setAttribute('aria-controls', `${select.id}-listbox`);
    trigger.setAttribute('aria-labelledby', `${label.id} ${select.id}-value`);
    const value = document.createElement('span');
    value.id = `${select.id}-value`;
    const chevron = document.createElement('i');
    chevron.setAttribute('aria-hidden', 'true');
    trigger.append(value, chevron);
    const list = document.createElement('div');
    list.id = `${select.id}-listbox`;
    list.className = 'select-options';
    list.setAttribute('role', 'listbox');
    list.setAttribute('aria-labelledby', label.id);
    list.hidden = true;
    const options = [...select.options].map((option, i) => {
      const node = document.createElement('div');
      node.id = `${select.id}-option-${i}`;
      node.className = 'select-option';
      node.setAttribute('role', 'option');
      node.textContent = option.textContent;
      list.append(node);
      scope.on(node, 'pointerdown', e => e.preventDefault());
      scope.on(node, 'click', () => { active = i; commit(); trigger.focus(); });
      return node;
    });
    wrapper.append(trigger, list);
    select.hidden = true;
    label.htmlFor = trigger.id;
    let active = select.selectedIndex, opened = false, typed = '', lastTyped = 0;
    const sync = () => {
      value.textContent = select.selectedOptions[0]?.textContent || '';
      wrapper.dataset.selected = String(select.value !== 'all');
      options.forEach((node, i) => node.setAttribute('aria-selected', String(i === select.selectedIndex)));
    };
    const highlight = index => {
      active = Math.max(0, Math.min(options.length - 1, index));
      options.forEach((node, i) => node.classList.toggle('is-active', i === active));
      trigger.setAttribute('aria-activedescendant', options[active].id);
      const node = options[active];
      if (node.offsetTop < list.scrollTop) list.scrollTop = node.offsetTop;
      if (node.offsetTop + node.offsetHeight > list.scrollTop + list.clientHeight) list.scrollTop = node.offsetTop + node.offsetHeight - list.clientHeight;
    };
    const close = () => {
      opened = false;
      list.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
      trigger.removeAttribute('aria-activedescendant');
      wrapper.classList.remove('is-open');
    };
    const open = () => {
      root.dispatchEvent(new CustomEvent('select:open', {detail: trigger}));
      opened = true;
      list.hidden = false;
      wrapper.classList.add('is-open');
      const below = innerHeight - trigger.getBoundingClientRect().bottom;
      wrapper.classList.toggle('opens-up', below < Math.min(280, list.scrollHeight) && trigger.getBoundingClientRect().top > below);
      trigger.setAttribute('aria-expanded', 'true');
      highlight(select.selectedIndex);
    };
    const commit = () => {
      select.selectedIndex = active;
      close(); sync();
      select.dispatchEvent(new Event('change', {bubbles: true}));
    };
    scope.on(trigger, 'click', () => opened ? close() : open());
    scope.on(trigger, 'keydown', e => {
      const wasOpen = opened;
      if (['ArrowDown', 'ArrowUp', 'Home', 'End', 'Enter', ' '].includes(e.key)) {
        e.preventDefault();
        if (!opened) open();
        if (e.key === 'Home') highlight(0);
        else if (e.key === 'End') highlight(options.length - 1);
        else if (wasOpen && e.key.startsWith('Arrow')) highlight(active + (e.key === 'ArrowDown' ? 1 : -1));
        else if (wasOpen && ['Enter', ' '].includes(e.key)) commit();
      } else if (e.key === 'Escape' && opened) {
        e.preventDefault(); close();
      } else if (e.key === 'Tab' && opened) commit();
      else if (e.key.length === 1 && !e.metaKey && !e.ctrlKey && !e.altKey) {
        if (!opened) open();
        const now = performance.now();
        typed = now - lastTyped > 700 ? e.key : typed + e.key;
        lastTyped = now;
        const found = options.findIndex(node => node.textContent.toLocaleLowerCase().startsWith(typed.toLocaleLowerCase()));
        if (found >= 0) highlight(found);
      }
    });
    scope.on(document, 'pointerdown', e => { if (!wrapper.contains(e.target)) close(); });
    scope.on(root, 'select:open', e => { if (e.detail !== trigger) close(); });
    scope.on(trigger, 'blur', close);
    scope.on(select, 'change', sync);
    scope.on(root, 'filters:restore', () => { close(); sync(); });
    sync();
  });
}
