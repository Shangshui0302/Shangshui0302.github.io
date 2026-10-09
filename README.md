# 偏移 / OFFSET

作品与文章组成的独立技术刊物。纸白、墨黑与朱红，横向切面动效。SECTION 是设计方向代号；网站名称可在 `site_config.json` 中调整。

线上地址：[偏移 / OFFSET](https://offset-digital-garden.shimmeringobsidian.chatgpt.site)。网站已开放访问，GitHub 源码仓库保持私有。本地预览继续保留。

三个轻量视觉 Demo 位于 `demos/`。运行 `python3 build_demos.py` 后访问 `/demos/`，在切面、暗室档案、折叠场之间切换。它们仅用于比较视觉，正式站点构建不会自动包含 Demo；再次执行 `build_site.py` 会移除生成目录中的 Demo。暗室档案使用本机 Source Serif 4 / Noto Serif CJK SC 回退字体，不额外分发字体文件。

## 构建与预览

```sh
python3 build_site.py
python3 check_site.py
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

打开 `http://127.0.0.1:4173/`。常规构建仅需 Python 标准库，无需安装依赖。静态页面支持直接打开项目、文章与段落链接；JavaScript 增强星系交互、搜索、筛选、情境切换、阅读进度、复制代码和动效偏好。

## 内容与结构

- `public-content/manifest.json`：明确允许进入预览的项目、文章与专题清单。
- `public-content/home.json`：按 slug 明确首页主推项目、精选作品与文章；与发布清单的顺序无关，重复或未知引用会阻止构建。项目 `case_study.steps` 将稳定 ID、控件标签、流程节点、说明及来源放在同一条记录中，模板不另存流程事实。
- `public-content/work/`：6 个公开项目（含壁纸收藏）的说明、边界和固定 revision 证据。
- `public-content/writing/`：去除私人信息、保留完整章节的技术文章；每篇有一个 `category_id` 和一组规范化 `tags`。内容数量以清单和构建报告为准。
- `public-content/taxonomy.json`：领域分类与技术标签的稳定 ID、名称和说明。
- `public-content/topics/`：专题的介绍、文章顺序与逐篇阅读引导；文章可被多个专题引用，正文只保存一份。
- `site_builder/content.py`：读取明确清单，验证首页引用与案例场景；不涉及页面或交互。
- `site_builder/search.py`：从同一份公开内容生成带内容哈希的全文索引，与目录 HTML 分离。
- `site_builder/templates/`：页面与服务端组件。`layout.py` 管理共享导航与页脚，`library.py` 管理文章/专题/标签视图，`search.py` 管理统一搜索，`components.py` 放复用条目；文章、作品、星系和技术图示各自独立。
- `assets/js/app.js`：装配页面组件。`core/` 管理路由、页面资源清理、动效与外观偏好；`pages/` 管理文章筛选、搜索、阅读进度；`components/` 放选择框、代码复制、进入视口动效；`scenes/` 放按需加载的星系。
- `assets/css/design/`：颜色、字体、间距和动效规则；`components/`：导航、控件；`pages/`：文章、作品、专题、首页星系。`site_builder/assets.py` 在构建时合并为一个 CSS 入口，避免浏览器逐层请求样式。
- `components/stellar.html`：首页与切面 Demo 共用的星系结构。Canvas 保留鼠标牵引、拖动旋转、点击脉冲、长按蓄能与滚动穿越；六个行星通过统一路由进入作品。只作视觉表达，不作天文模拟；无脚本时显示 SVG 后备画面。
- `build_site.py`：只读取清单列出的内容，生成页面、搜索目录和含分类标签的 RSS；未知分类、标签、文章引用及不完整阅读路线会阻止构建。
- `check_site.py`：构建后核对站内链接、锚点、分类标签归属、专题关系、RSS 与公开输出边界，支持文章数继续增长。
- `dist/`：唯一静态发布目录。`/work/`、`/writing/`、`/writing/topics/`、`/index/` 可独立访问；旧 `/topics/`、`/journal/` 预览链接保留。

原始笔记库不在项目中，构建不访问笔记库、GitHub API 或其他外部源。页面不显示个人姓名、联系方式和设备信息；源码链接仍能关联到公开 GitHub 账号。项目预览优先使用项目 README 中的真实图片及仓库官方预览，缺少图片时才使用依据公开源码绘制的结构示意。`public-content/work/` 的可选 `preview` 字段独立记录图片版本、来源与尺寸，首页和详情页共用同一个预览组件。图片保持原始文件与比例，自托管、延迟加载；来源及校验值见 `ASSET-SOURCES.md`。壁纸预览来自用户指定的公开收藏仓库，不声明为本站原创。

文章脱敏保留原笔记的实质章节、推导过程、命令与配置示例，不默认压缩为摘要或固定阅读时长。只清理私人信息、重复对话和无关内容；示例路径采用明确占位符，技术结论按可追溯资料校正，源码分析与实际运行验证分开表述。

新增阅读路线覆盖操作系统与桌面、Nix 语言及生态、SOPS、Git/GitHub，以及容器、虚拟机和兼容层。OneDrive 与 RemoteAccess 不在收录范围。空笔记和目录导航不作为文章；重复笔记合并引用，保留独有章节。剪藏材料保留原文归属和参考链接，历史版本经验标明适用范围。示例中的磁盘、密钥、主机和服务均为通用场景，不代表本站运行配置或已执行的操作。

分类描述领域，标签连接具体技术，专题提供有顺序的阅读路线。文章目录使用复用的选择控件，支持分类、标签与专题交集筛选，并把条件保存在 URL 中；静态分类页、标签页和专题页无需 JavaScript。专题及分类标签同样进入全站搜索。新增内容时先更新分类标签元数据和明确清单，再检查对应专题的文章顺序与阅读引导。

全文搜索在首次输入关键词时按需加载独立 JSON 索引，同一文档内跨页面切换复用同一版本与并发请求；索引文件名包含内容哈希，内容更新后自动使用新版本。小写文本只建立一次，输入时只做匹配和必要的可见性更新；加载中和失败时保留目录并显示状态，失败可以重试，卸载后的异步响应不修改页面。正文里的 HTML 字符实体先解码，代码符号也能直接检索。批量内容导入使用一次性编辑工具，日常构建仍只依赖 Python 标准库。

## 页面生命周期与交互

顶部包含首页、作品、文章和搜索四个入口。文章中心包含全部文章、专题、标签视图；搜索同时展示完整索引。

顶栏采用紧凑的单行导航，窄屏才换为两行；统一的无色薄玻璃只在圆角边缘做不超过 2 像素的连续折射，使用细亮边与指针反光。位移包络限制局部伸缩，避免背景文字折叠成亮带；滤镜各阶段共用留出采样余量的像素区域，不叠加第二份背景补洞。Chromium 使用 SVG 位移滤镜；其他浏览器保留背景模糊，不依赖未验证的 SVG 支持。折射图只在尺寸变化时生成，静止时没有动画循环。玻璃层不设置独立转场名称，避免 backdrop root 阻断真实背景采样；随页面一起叠化。正文主题保留，首页星系背后的顶栏文字自动提高对比。开启站内或系统“减少动效”后关闭玻璃与指针效果，恢复不透明纯色；禁用脚本或不支持模糊时也使用纯色。

站内 HTML 导航通过 `fetch` 读取页面，只替换 `main`，同步标题、描述、页面主题和导航状态；顶部导航、动效与外观偏好保持。页面数据就绪后，用原生 View Transition 对视口做 360 毫秒叠化，液态玻璃顶栏随视口原位叠化，纯色顶栏保持独立快照。旧快照保持不透明，只让新画面淡入，使用普通合成，避免双层加法混合与大画面位移的逐帧重采样。只捕获视口，不复制长页面 DOM，也不给整个 `main` 创建动画图层。网络读取在快照前完成，没有固定退场等待；不支持该 API 时，仅对可见标题和筛选控件做 360 毫秒入场。实现依据 [Chrome 同文档 View Transitions 文档](https://developer.chrome.com/docs/web-platform/view-transitions/same-document)。修饰键、新窗口、外链、RSS、下载和独立视觉 Demo 保留浏览器默认行为。没有 JavaScript 时，静态页面和阅读链接照常可用。

- 路由是唯一的 history 写入者。筛选 push、搜索 replace，前进/后退恢复查询和滚动位置；段落链接仍可分享。
- 每次挂载建立一个 `scope`。卸载时中止监听、断开 observer、取消 RAF 与定时器；异步字体/星系加载检查页面是否已卸载。
- 快速导航中止过期请求，并跳过上一次视觉过渡；过期回调不能提交页面，跳过快照也不重复挂载。减少动效或切到后台会立即结束正在运行的过渡。失败时保留当前页面，提供重试和直接打开，不自动循环刷新。
- 只缓存已经访问过的静态 HTML，不预取；最多 8 页、约 800 KB，60 秒过期。查询参数仍由页面恢复逻辑处理，缓存不保存增强后的 DOM 或筛选状态。
- 星系按明暗批量绘制网格和粒子，背景 Canvas 使用约百万像素预算；离开星系区域或切换到后台时停止绘制，作品行星只在所在区域可见时转动。DOM 状态仅在数值变化时写入，进度条使用 `transform`，避免逐帧触发布局。
- 阅读进度只在文章和案例页监听滚动，同一帧先读取几何信息，再更新变化的进度与目录状态。
- 选择框保留原生 `select` 作为值与 change 接口，增强为 combobox/listbox。箭头/Home/End/typeahead 浏览，Enter/空格/Tab 提交，Escape 取消，外点关闭；URL 恢复后同步显示。
- 外观默认跟随系统，顶部选择器可切换浅色、深色或恢复跟随。CSS 实时响应系统外观；手动偏好在首屏样式前恢复，避免闪白，跨标签页同步。文章、目录、控件共用语义颜色，星系、作品图片与深色代码展板保留独立配色；不增加框架或轮询。
- 系统和站内“减少动效”同时约束页面过渡、控件和星系；全局只关闭动画与过渡，图标旋转等静态几何保留，揭示组件自行解除动画裁切。拖拽在暂停、失焦、取消、失去指针捕获和卸载时统一清理。焦点随新页面/段落移动，阅读历史仅在当前浏览器 history 中。

组件键盘行为参考 [WAI select-only combobox](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/examples/combobox-select-only/)。保持无运行依赖，不为页面展示引入框架或组件包。

## 字体与隐私

字体、CSS 与脚本均由本站提供，无第三方分析、远程头像或字体请求。外观与动效开关仅将偏好存入本站 localStorage，并尊重系统减少动效设置。外部链接不发送 referrer。

Archivo Variable、IBM Plex Mono 与思源黑体的许可证位于 `assets/fonts/`。中文字体为按当前内容裁剪并改名的 Offset Han Sans，保留原版权和 SIL OFL；缺失字符使用系统中文字体。来源记录见 `FONT-SOURCES.md`。

修改内容后，如需重新生成中文字体分片，先构建页面，再在已有 FontTools 与 Brotli 环境中执行 `python prepare_fonts.py <字体源目录>`，最后再次构建。源目录需包含脚本列出的官方字体及许可证；完整中文源字体不得复制到 `dist/`。

## 发布边界

Sites 项目已部署，复用 `.openai/hosting.json` 的现有项目。后续发布保持现有访问权限，变更访问范围由作者指定。`site_config.json` 的 `site_url` 使用首次成功部署返回的正式地址，RSS 使用相同域名。正式发布应运行以下独立门禁（仅构建与检查，不会部署）：

```sh
python3 build_site.py --release
python3 check_site.py --release
```

发布构建拒绝缺失、预览或私网域名；发布检查额外拒绝 Demo、隐藏文件、符号链接及非发布目录，并校验 RSS 的频道地址、文章链接和 GUID 与配置完全一致。普通检查同时覆盖搜索索引条目及目录 HTML 的缓存预算。

结构回归检查使用 Python 与 Node 标准库，无需安装依赖：

```sh
python3 -m unittest discover -s tests
node --test tests/*.test.mjs
```

Node 检查需要先完成本地构建，验证实际搜索页面能进入缓存，以及索引跨挂载复用、失败后重试；同时检查玻璃采样映射在直边、圆角和尺寸变化下保持连续、无反转。

旧版快照、构建缓存、字体覆盖报告和本地验证记录保存在被 Git 忽略的 `.sites-runtime/` 中，不进入发布目录。


## GitHub Pages 构建

支持根域名与项目子路径；默认构建仍读取原有 `site_config.json`，不改动现有 Sites 项目或 `.openai/hosting.json`。两个脚本共享同一配置规则：`--site-url` 参数优先，其次是 `SITE_URL` 环境变量，最后是配置文件。构建与检查必须使用相同地址。

```sh
# 仅演示项目路径的本地构建与检查；此命令不会发布网站。
python3 build_site.py --release --site-url https://shangshui0302.github.io/offset
python3 check_site.py --release --site-url https://shangshui0302.github.io/offset
python3 -m unittest discover -s tests
node --test tests/*.test.mjs
```

上述 Pages 地址是部署配置示例，不表示已成功上线。生成文件仍直接位于 `dist/`，不是 `dist/offset/`；页面导航、图片、CSS 字体、搜索索引和 RSS 都包含一致的 `/offset` 前缀。路由只接管相同源且位于当前站点子路径内的 HTML 导航，其他仓库站点、下载和 Demo 交给浏览器。默认根路径预览请重新运行不带覆盖参数的构建命令。

`.github/workflows/pages.yml` 使用 GitHub 官方 Actions 并固定完整提交 SHA。流程先检查根路径及 `/offset`，再以 `configure-pages` 返回的 `base_url` 构建实际发布文件，最后只上传 `dist/`。构建任务仅有源码和 Pages 元数据读取权限；独立部署任务才有 Pages 写入和 OIDC 权限。流程不创建密钥、不保存检出凭据、不自动开启 Pages，也不改变仓库可见性。运行环境使用 GitHub 托管 Ubuntu 的 Python 3 与 Node.js，无额外运行依赖。

启用前先确认全部图片、字体与文章的公开分发权，以及仓库公开范围；再将仓库 Settings → Pages → Source 设为 GitHub Actions。推送 `main` 或在 `main` 手动运行流程会触发部署；其他分支的手动运行会跳过。建议将 `github-pages` 环境的部署分支限制为 `main`。发布状态应以 Actions 的实际部署结果和线上检查为准，不能以本地构建成功代替。

流程依据 [GitHub Pages 官方自定义工作流说明](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)；Actions 固定版本来自 [checkout](https://github.com/actions/checkout/releases/tag/v7.0.1)、[configure-pages](https://github.com/actions/configure-pages/releases/tag/v6.0.0)、[upload-pages-artifact](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0) 与 [deploy-pages](https://github.com/actions/deploy-pages/releases/tag/v5.0.1) 的官方发布。
