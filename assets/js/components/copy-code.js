export function initCopyCode(root, scope) {
  root.querySelectorAll('.copy-code').forEach(button => scope.on(button, 'click', async () => {
    let message;
    try { await navigator.clipboard.writeText(button.parentElement.querySelector('code').textContent); message = '已复制'; }
    catch { message = '复制失败，请手动选择'; }
    if (scope.disposed) return;
    button.textContent = message;
    button.setAttribute('aria-live', 'polite');
    scope.timeout(() => { button.textContent = '复制代码'; }, 2200);
  }));
}
