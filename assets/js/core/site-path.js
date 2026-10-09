/* The deployment prefix is emitted by the builder, never inferred from a route. */
export function isSitePage(url, origin, basePath = '') {
  if (url.origin !== origin || !url.pathname.endsWith('/')) return false;
  if (basePath && !url.pathname.startsWith(`${basePath}/`)) return false;
  const route = url.pathname.slice(basePath.length);
  return !route.startsWith('/demos/');
}
