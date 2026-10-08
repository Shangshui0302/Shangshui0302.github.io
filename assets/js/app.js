import {createScope} from './core/scope.js';
import {initTheme} from './core/theme.js';
import {initMotion} from './core/motion.js';
import {createRouter} from './core/router.js';
import {enhanceSelects} from './components/select.js';
import {initCopyCode} from './components/copy-code.js';
import {initReveals} from './components/reveal.js';
import {initLibrary} from './pages/library.js';
import {initSearch} from './pages/search.js';
import {initReading} from './pages/reading.js';

function mountPage(root, navigation) {
  const scope = createScope();
  const restoreLibrary = initLibrary(root, scope, navigation);
  const restoreSearch = initSearch(root, scope, navigation);
  enhanceSelects(root, scope);
  initCopyCode(root, scope);
  initReveals(root, scope);
  initReading(root, scope);
  if (root.querySelector('.galaxy-experience')) {
    import('./scenes/stellar.js').then(({initStellar}) => {
      if (!scope.disposed) initStellar(root, scope);
    }).catch(() => { /* The illustrated no-script background remains available. */ });
  }
  return {dispose: () => scope.dispose(), restore: () => { restoreLibrary(); restoreSearch(); }};
}
initTheme();
initMotion();
createRouter(mountPage);
