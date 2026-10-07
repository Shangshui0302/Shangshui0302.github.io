# 偏移 / OFFSET

作品与文章组成的独立技术刊物。纸白、墨黑与朱红，横向切面动效。SECTION 是设计方向代号；网站名称可在 `site_config.json` 中调整。

当前只有本地预览，内容处于作者审阅阶段，尚未发布。

三个轻量视觉 Demo 位于 `demos/`。运行 `python3 build_demos.py` 后访问 `/demos/`，在切面、暗室档案、折叠场之间切换。它们仅用于比较视觉，正式站点构建不会自动包含 Demo；再次执行 `build_site.py` 会移除生成目录中的 Demo。暗室档案使用本机 Source Serif 4 / Noto Serif CJK SC 回退字体，不额外分发字体文件。

## 构建与预览

```sh
python3 build_site.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

打开 `http://127.0.0.1:4173/`。常规构建仅需 Python 标准库，无需安装依赖。静态页面支持直接打开项目、文章与段落链接；JavaScript 仅增强搜索、筛选、复制代码和动效偏好。

## 内容与结构

- `public-content/manifest.json`：明确允许进入预览的项目与文章清单。
- `public-content/work/`：4 个公开 GitHub 项目的说明、边界和固定 revision 证据。
- `public-content/writing/`：3 篇去除私人信息、重新整理的技术文章。
- `assets/section.css`、`assets/section.js`：共享排版与交互。
- `components/stellar.html`、`assets/stellar.*`：首页与切面 Demo 共用的整屏星系。Canvas 实时投影朱红立体网格、轨道与旋臂，支持鼠标牵引、拖动旋转、点击脉冲、长按蓄能爆发与滚动穿越；四个作品行星可直接进入项目，普通目录入口始终可用。蓄能按钮支持鼠标/触摸按住与空格键，回车触发普通脉冲；无脚本时显示原创 SVG 后备画面。仅作视觉表达，不作天文模拟。支持暂停、系统/站内减少动效，隐藏页面停止绘制。
- `stellar_template.py`：从现有公开项目清单生成共用的作品行星入口。
- `build_site.py`：只读取清单列出的内容，生成页面、搜索目录和 RSS。
- `dist/`：唯一静态发布目录。`/work/`、`/writing/`、`/index/` 可独立访问；旧 `/journal/` 预览链接保留。

原始笔记库不在项目中，构建不访问笔记库、GitHub API 或其他外部源。页面不显示个人姓名、联系方式和设备信息；源码链接仍能关联到公开 GitHub 账号。技术图示根据公开源码绘制，主题示意不是运行截图。

## 字体与隐私

字体、CSS 与脚本均由本站提供，无第三方分析、远程头像或字体请求。动效开关仅将偏好存入本站 localStorage，并尊重系统减少动效设置。外部链接不发送 referrer。

Archivo Variable、IBM Plex Mono 与思源黑体的许可证位于 `assets/fonts/`。中文字体为按当前内容裁剪并改名的 Offset Han Sans，保留原版权和 SIL OFL；缺失字符使用系统中文字体。来源记录见 `FONT-SOURCES.md`。

修改内容后，如需重新生成中文字体分片，先构建页面，再在已有 FontTools 与 Brotli 环境中执行 `python prepare_fonts.py <字体源目录>`，最后再次构建。源目录需包含脚本列出的官方字体及许可证；完整中文源字体不得复制到 `dist/`。

## 发布边界

Sites 项目已经注册，尚未部署。后续发布必须先取得作者对预览和内容的确认，复用 `.openai/hosting.json` 的现有项目。确认后填写 `site_config.json` 的正式 `site_url`，再构建，以确保 RSS 使用正式域名。当前 RSS 使用本机预览地址。

旧版快照、构建缓存、字体覆盖报告和本地验证记录保存在被 Git 忽略的 `.sites-runtime/` 中，不进入发布目录。
