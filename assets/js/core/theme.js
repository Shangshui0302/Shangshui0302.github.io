import {createScope} from './scope.js';
import {enhanceSelects} from '../components/select.js';

/* One persistent shell control. System changes are handled by CSS, without
   polling or a listener on each route. Only explicit overrides are stored. */
export function initTheme() {
  const root = document.documentElement;
  const picker = document.querySelector('.theme-picker');
  const select = picker?.querySelector('select');
  if (!select) return;
  const scope = createScope();
  const normalize = value => ['light', 'dark'].includes(value) ? value : 'system';
  const apply = preference => {
    root.dataset.theme = normalize(preference);
    select.value = root.dataset.theme;
    select.dispatchEvent(new Event('select:sync'));
  };
  apply(root.dataset.theme);
  enhanceSelects(picker, scope);
  picker.hidden = false;
  scope.on(select, 'change', () => {
    apply(select.value);
    try {
      if (select.value === 'system') localStorage.removeItem('offset-theme');
      else localStorage.setItem('offset-theme', select.value);
    } catch { /* The current page still switches when persistence is blocked. */ }
  });
  scope.on(window, 'storage', event => {
    if (event.key === 'offset-theme' || event.key === null) apply(event.newValue);
  });
}
