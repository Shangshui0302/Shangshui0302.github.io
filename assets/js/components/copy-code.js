import {t} from '../core/language.js';
export function initCopyCode(root, scope) {
  root.querySelectorAll('.copy-code').forEach(button => scope.on(button, 'click', async () => {
    let message;
    try { await navigator.clipboard.writeText(button.parentElement.querySelector('code').textContent); message = t('已复制', 'Copied'); }
    catch { message = t('复制失败，请手动选择', 'Could not copy. Select the code manually.'); }
    if (scope.disposed) return;
    button.textContent = message;
    button.setAttribute('aria-live', 'polite');
    scope.timeout(() => { button.textContent = t('复制代码', 'Copy code'); }, 2200);
  }));
}
