"""Copy local-only visual demos after build_site.py. Never publishes."""
from pathlib import Path
import shutil
root=Path(__file__).parent
assert (root/'dist/assets/fonts/fonts.css').exists(), 'Build the main site first'
shutil.copytree(root/'demos',root/'dist/demos',dirs_exist_ok=True)
page=(root/'dist/demos/index.html')
page.write_text(page.read_text().replace('<!-- STELLAR_PREVIEW -->',(root/'components/stellar.html').read_text()))
print('Three visual demos ready at /demos/; not published.')
