"""Subset official Source Han Sans into disjoint, current-content font chunks.

Run with fontTools and Brotli available; accepts an asset directory argument.
The original font stays outside distributable output. Rebuild after content edits.
"""
from pathlib import Path
from html.parser import HTMLParser
import json
import sys
import shutil
from fontTools import subset
from fontTools.ttLib import TTFont

root=Path(__file__).parent
source=Path(sys.argv[1])
target=root/'assets/fonts'
target.mkdir(parents=True,exist_ok=True)
for name in ['Archivo-Variable.woff2','IBMPlexMono-Regular.woff2','IBMPlexMono-Medium.woff2','Archivo-OFL.txt','IBM-Plex-OFL.txt','Source-Han-Sans-OFL.txt']:
    shutil.copy2(source/name,target/name)

class Text(HTMLParser):
    def __init__(self):super().__init__();self.values=[]
    def handle_data(self,data):self.values.append(data)
    def handle_starttag(self,tag,attrs):
        self.values.extend(v for k,v in attrs if k in ['placeholder','title','aria-label'] and v)

parser=Text()
for file in (root/'dist').rglob('*.html'):parser.feed(file.read_text())
# Include transient UI labels and standard punctuation without shipping raw source data.
extra='已复制复制失败请手动选择代码清空搜索查看全部找到项内容篇文章减少动效没有匹配结果。：；，！？（）「」《》、—…·→×'
text=''.join(parser.values)+extra
font=TTFont(source/'SourceHanSansSC-VF.woff2')
cmap=font.getBestCmap()
needed=sorted(set(map(ord,text)) & set(cmap))
missing=sorted(set(map(ord,text))-set(cmap)-{9,10,13})
if missing:print('Font fallback for codepoints:',[hex(c) for c in missing])
chunks=[needed[i:i+360] for i in range(0,len(needed),360)]
css=["@font-face{font-family:Archivo;src:url('./Archivo-Variable.woff2') format('woff2');font-weight:100 900;font-stretch:62% 125%;font-style:normal;font-display:swap}","@font-face{font-family:'IBM Plex Mono';src:url('./IBMPlexMono-Regular.woff2') format('woff2');font-weight:400;font-display:swap}","@font-face{font-family:'IBM Plex Mono';src:url('./IBMPlexMono-Medium.woff2') format('woff2');font-weight:500;font-display:swap}"]
for i,points in enumerate(chunks):
    face=TTFont(source/'SourceHanSansSC-VF.woff2')
    opts=subset.Options();opts.name_IDs=['*'];opts.name_legacy=True;opts.name_languages=['*'];opts.layout_features=['*']
    engine=subset.Subsetter(options=opts);engine.populate(unicodes=points);engine.subset(face)
    for record in face['name'].names:
        if record.nameID in {0,13,14}:continue
        value=record.toUnicode()
        if 'SourceHanSansSC' in value:value=value.replace('SourceHanSansSC','OffsetHanSans')
        if 'Source Han Sans SC' in value:value=value.replace('Source Han Sans SC','Offset Han Sans')
        if 'Source Han Sans' in value:value=value.replace('Source Han Sans','Offset Han Sans')
        try:record.string=value.encode(record.getEncoding())
        except (UnicodeEncodeError,LookupError):record.string=value.encode('utf-16-be')
    face.flavor='woff2';name=f'OffsetHanSans-{i:02}.woff2';face.save(target/name)
    ranges=','.join(f'U+{p:X}' for p in points)
    css.append(f"@font-face{{font-family:'Offset Han Sans';src:url('./{name}') format('woff2');font-weight:250 900;font-style:normal;font-display:swap;unicode-range:{ranges}}}")
    verified=TTFont(target/name)
    assert set(points)<=set(verified.getBestCmap())
    for r in verified['name'].names:
        if r.nameID in {1,3,4,6,16,21,25}:assert 'Source' not in r.toUnicode(),r.toUnicode()
    print(name,(target/name).stat().st_size,'bytes',len(points),'codepoints',flush=True)
(target/'fonts.css').write_text('\n'.join(css)+'\n')
(target/'NOTICE.txt').write_text('Archivo and IBM Plex Mono are distributed with their accompanying SIL OFL licenses.\nOffset Han Sans is a renamed, current-content subset derivative of Source Han Sans SC by Adobe. It retains the original copyright and SIL OFL license. Rebuild subsets when content changes. System CJK fallbacks cover characters outside the subset.\n')
(root/'.sites-runtime/font-coverage.json').write_text(json.dumps({'codepoints':len(needed),'chunks':len(chunks),'missing':missing,'scope':'current allowlisted website content'}))
print('Font partitions cover current content; original full CJK font is excluded from distribution.')
