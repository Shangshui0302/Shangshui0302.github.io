/* Inlined before CSS by the page template to avoid a wrong-theme first frame.
   With no preference (or unavailable storage), CSS follows the system directly. */
(() => {
  try {
    const preference = localStorage.getItem('offset-theme');
    if (preference === 'light' || preference === 'dark') {
      document.documentElement.dataset.theme = preference;
    }
  } catch { /* CSS remains the system-aware fallback. */ }
})();
