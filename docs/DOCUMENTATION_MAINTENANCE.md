# 文档来源与维护

文档导航与装订版维护记录更新于 2026-10-22；电子手册的行为核对基线日期仍为 2026-10-19。当前手册的固件行为基线为统一 v1.8.0 对应源码，Studio 行为按 0.5.5+109 源码核对；这不是安装包已正式发布的声明。历史 v1.7 手册保留原版，用于历史查询。

当前双光装订稿为 36 面视差图解版；单光印厂交接推荐单页顺序原稿，自行四套拼版另有 A7 28 面仅封面装订虚线版。下文按版本记录构建流程，历史版本的页数、辅助线和审阅方式属于对应版本。最新下载入口以 `artifacts/README.md` 及各子目录交接页为准。

## 文件与维护入口

| 用途 | 维护位置 |
| --- | --- |
| 单光完整说明书 | `docs/user-guide/single-light.md` |
| 双光完整说明书 | `docs/user-guide/dual-light.md` |
| 设备与功能对照 | `docs/devices/README.md` |
| 逐项菜单 | `docs/menu/`，基础 15 项，含可选距离栏目最多 17 项 |
| 新版 DOCX 构建 | `scripts/build_manuals.py`，版式为 `scripts/manual_layout.py` |
| 印刷版逐页编排 | `scripts/manual_content.py`，单光与双光各 20 页 |
| 可重建的技术示意图 | `scripts/manual_artwork.mjs` 与 `docs/assets/manual-design/` |
| 新版 PDF 与逐页图 | `scripts/render_manuals.py` 与 `scripts/export_manual_pdf.ps1` |
| 发布给读者的离线文件 | `artifacts/`，入口为 `artifacts/README.md` |
| 历史 v1.7 构建器 | `scripts/build_user_manual.py`，不用于生成当前手册 |

Markdown 是在线事实基线；印刷版按阅读任务在 `manual_content.py` 中重新编辑，并非逐行导出 Markdown。DOCX 使用原生标题、步骤、段落、表格、链接与页码，正文仍可编辑。技术变更需同时核对在线稿和印刷稿，在同一次更新中重建 DOCX 与 PDF，不能只改其中一种。图像、页图和临时导出分开存放，`.work/manuals/` 已被 Git 忽略。

## 三份原始单光说明书

三份均为两页，已逐页读取文本并检查渲染。第一页面向外壳与按键，第二页为相同的旧版常见问题。保留其外壳图及实体差异，新固件操作以代码为依据。

| 原文件名 | 资料修订日期 | 核实的实体差异 |
| --- | --- | --- |
| 2.4寸热成像使用说明书.pdf | 2025-09-17 | A/B、右开左关、图中有快速重启按钮 |
| 2.8寸热成像文档新.pdf | 2025-10-15 | A/B、右开左关、挂绳孔、未明确复位入口 |
| 3.2寸热成像使用说明书.pdf | 2025-09-17 | A/B、三向拨片、左开右关、快速重启按钮 |

原文件 SHA-256：

```text
2.4寸热成像使用说明书.pdf
8b631f5925c68b912d94d3d9d6bf58fdc2bbacc08b4187960f62a4c66a418bdb
2.8寸热成像文档新.pdf
5136e75c424e704a0778b5e66e2f962d179eca780d7c64589548d4ba1dce83b4
3.2寸热成像使用说明书.pdf
19776d72c8f7a2d4d1c017b6b5752750c09cc71e882586dd46a9d2ffb97516d8
```

`docs/assets/devices/` 保存三款硬件图。2.4/2.8 直接提取 PDF 内嵌图；3.2 的标签是独立 PDF 文本，保留标签后裁切渲染，移除单独的资料群二维码及其文字。未修改原始 PDF，也未把旧的测温公式和其他波段发射率表放入新手册。

## 三个仓库的行为依据

| 仓库与核对点 | 依据 |
| --- | --- |
| 3inch2-Heimann-dual-thermal HEAD `b5f13c8` | 最高温追踪显示默认温度 |
| 固件 `5b85822` | standard/dual 引脚、六环境、缺失硬件禁用与迁移存储重建 |
| 固件 `6369564` | 去掉按屏幕大小判定按键的逻辑 |
| 固件 `ef6c05b` | standard 热传感器 Wire 与触摸 Wire1 的总线映射 |
| 固件 `812083f`、`bc0900d` | 屏幕反色与按传感器类别一次性应用默认值 |
| 固件 `src/device/button.h`、`src/menu.h` | A/B、A+B、拨片、相册和 15/17 栏目行为 |
| 固件 `src/temperature_alarm.h`、`src/temperature_calibration.h` | 报警状态机、默认值、分段校准与兼容接口 |
| 固件 `src/probe/mlx_driver.hpp` | MLX90641 原生 16×12 到 32×24 上采样 |
| NextBananaThermalStudio HEAD `840cce2` | 迁移时开放同板型容量变体选择 |
| Studio `763116b`、`196e440` | 板型锁定、schema v2、单光能力识别与双光控件隐藏 |
| Studio `lib/app_state.dart`、`lib/firmware/` | 连接身份、热像/可见光能力、升级与校准协商 |
| BananaThermalFirmware 起点 `c443fe9` | 六固件矩阵与 manifest schema v2 发布约定 |

外壳位置由原说明书决定，升级后的按键语义由新代码决定；无法从代码确定的实体入口不作猜测。单光摄像头与融合栏目目前保留不可用占位，不能写成所有不适用栏目都会隐藏。

科学性修订还核对了 [Melexis MLX90641 产品资料](https://www.melexis.com/en/product/MLX90641/High-Operating-Temperature-FIR-Thermal-Sensor-Array)与 [FLIR 测温参数说明](https://docs.flir.com/T810605/en-US/latest/s10.html)：原生像素与上采样应区分；发射率补偿涉及辐射与反射，不能直接用摄氏温度相除。没有沿用旧资料对夜视或隐藏摄像头识别效果的保证。

## 重建说明书

安装 Python 依赖 `python-docx`、`Pillow`；仅重新提取原始图时另需 `pdfplumber`、`pypdf`、`reportlab` 与 Poppler。运行：

```powershell
python scripts/build_manuals.py
python scripts/build_manuals.py --profile standard
```

这些命令生成 DOCX；原始图已进入仓库，正常构建不依赖桌面资料目录。需要重新提取图时使用 `--extract-source-drawings <原始PDF目录>`，并确保 pdftoppm 在 PATH 中。

封面、按键、画面读数、迟滞与对齐示意保留 SVG 源文件和高分辨率 PNG。修改示意图时运行 `node scripts/manual_artwork.mjs --modules <依赖加载器返回的node_modules目录>`，需要 Sharp。示意热像不是实测数据，不用于宣称量程或精度。软件截图在 Word 内原生裁切，仅展示温度与趋势区域，不改变源图片。

在带 LibreOffice 的环境中，使用文档渲染器 `render_docx.py` 导出 PDF 和逐页 PNG。本次 Windows 运行环境没有随包 LibreOffice，使用仓库的 Word 转换适配器：

```powershell
python scripts/render_manuals.py --renderer <documents技能目录中的render_docx.py>
```

该适配器以独立隐藏的 Microsoft Word 实例读取新 DOCX、导出 PDF，再调用同一个 `render_docx.py` 的页图渲染流程；不附着用户正在编辑的文档。依赖已安装 Word 与 PATH 中的 Poppler。最终 PDF 复制到 artifacts，PNG 仅存于 `.work/manuals/` 供检查。

在 Codex 环境中使用依赖加载器返回的 Python/Node 与工具路径，不依赖系统 Python。每次更新后检查所有最终页图、链接、照片和表格、页码及输出文本；运行 `python scripts/verify_manuals.py` 与仓库现有测试。若内容增减改变分页，必须同时修改页面计划、目录和校验的预期页数，不能只让 Word 自动溢出。页码与总页数使用原生 PAGE/NUMPAGES 字段。保留来源版本和仍需实物确认的事项。

## 单光随附印刷分册

`artifacts/print-booklets/` 的三册另有离线内容计划与版式，不从 Markdown 直接导入。当前修订版正文 28 页，加封面、封底及两面内封留白，共 32 个逻辑页面；预拼成 16 个 A4 横向纸面、8 张纸。读者页码采用静态正文页码 1–28，不使用 Word 物理页面的 PAGE 字段。调整页数必须同时更新正文交叉引用、目录、拼版与校验脚本。

```powershell
python scripts/build_print_booklets.py
python scripts/render_print_booklets.py --renderer <documents技能目录中的render_docx.py>
python scripts/verify_print_booklets.py
```

也可用 `--model 24`、`--model 28` 或 `--model 32` 单独构建、渲染及校验。硬件页直接使用三份原说明书线稿，Word 原生裁切保留完整标注和立体机身朝向；裁切应目视检查每个标注，避免切字。现有插图完整保存在仓库中，日常改文案时不必重新生成图片。用户提供的背面 CAD 截图仅保存在被忽略的工作目录，背面插图是经核对的重绘版，来源与提示词见 `docs/assets/devices/PRINT_ARTWORK.md`。

标题、段落、表格和步骤均处在 Word 原生文本框中，按纸面定位，保持可编辑；不可把每半页转成图片替代。段落在各自文本框内自动换行，框高固定，因此须通过校样检查溢出，不能仅凭 Word 总页数验收。校验脚本逐半页对照 DOCX 原生文字与实际 PDF 文字的完整性、A4 尺寸、留白、安全区及骑马订映射；最终所有 48 个 A4 校样面还需逐页目视检查。

文案只说明本机具备的功能，以操作、结果和具体风险组织内容。删去缺失功能的比较、重复否定提醒与泛化售后指引。校验脚本同时检查相关退化句式，并验证已嵌入原说明书硬件图。

Word 导出的内部 PDF、PNG、页序与校验记录仅放在 `.work/print-booklets/`，不作为本次 DOCX 交付附件。印刷时保留文件第 2 页的整面留白，不做二次小册子拼版。具体设置、套帖对照和印前打样要求见 `artifacts/print-booklets/README.md`。印厂应以最终纸张验证双面方向、爬移和裁切，不以屏幕校样代替实物折订打样。

### A6 成册 A4 上下双套新版

新版输出在 `artifacts/print-booklets/a6/`，原 A5 DOCX 完整保留。内容仍由 `print_booklet_content.py` 提供，触屏选配说明保持一致；A6 版式通过 `build_a6_booklets.py` 单独构建。A4 竖向 210 × 297 mm，上下各一套相同的骑马订页对；横切坐标 y=148.5 mm，裁切后各半张的折线 x=105 mm。8 张双面 A4 纸产出两本各 32 面的小册，未修边尺寸 105 × 148.5 mm。

```powershell
python scripts/build_a6_booklets.py build
python scripts/build_a6_booklets.py render --renderer <documents技能目录中的render_docx.py>
python scripts/build_a6_booklets.py verify
# 全部 48 个最终 A4 页图目视通过后，才发布新 DOCX
python scripts/build_a6_booklets.py publish
```

构建、校样和校验报告先存于 `.work/a6-booklets/`；发布采用排他新建方式，遇到同名输出会停止，避免覆盖已有 DOCX。更新已发布版本时先选择新文件名。校验逐四象限检查文字完整性、留白、页码与安全区，并对照已确认的 A5 触屏选配说明版，确认内容完整复制两套。正文为 9.5 磅、13 磅行距，表格 9 磅，图表独立分配尺寸；文字和表格保持原生可编辑。

A6 版使用 A4 竖向、100% 实际大小、长边双面翻转建议设置，与 A5 横向版分开交接。具体裁切、套帖、修边和实物打样要求见 `artifacts/print-booklets/a6/README.md`。

### A7 成册 A4 四套新版

`artifacts/print-booklets/a7/` 保留三款独立 A7 DOCX，原 A5、A6 文件保持不变。每个原正文主题拆为两页，正文共 56 页，加封面、封底和两面内封留白为 60 面。目录及所有文内页码随之更新；保留原硬件标注线稿，独立安排按键及接口图页。正文 9 磅，表格 8.5 磅，小流程与报警示意使用原生文字表格。

```powershell
python scripts/build_a7_booklets.py build
python scripts/build_a7_booklets.py render --renderer <documents技能目录中的render_docx.py>
python scripts/build_a7_booklets.py verify
# 全部 90 个最终 A4 页图目视通过后，排他新建发布
python scripts/build_a7_booklets.py publish
```

构建和内部校样在 `.work/a7-booklets/`。A4 横向 297 × 210 mm，四个 148.5 × 105 mm 的小张分别构成四套相同骑马订页对；裁切 x=148.5 mm、y=105 mm，两处带灰色虚线。各小张沿自身 x=74.25 mm 对折，未修边 74.25 × 105 mm。每组 15 张双面 A4 形成四本完整小册，输出建议短边翻转、100% 原尺寸；第 2 页只有辅助线，仍须保留。校验逐八个页面区核对原生/渲染文字、留白、安全区和页序，并比对所有已有 DOCX 的哈希。实际纸张的套准、爬移及折订验证见 `artifacts/print-booklets/a7/README.md`。

### A6 A7 资料支持与双面辅助线修订

以上为基础版构建流程。A6 当前交付在基础版之后运行 `scripts/update_booklet_support.py --size a6`，以 `_资料支持与双面对齐版.docx` 后缀新建三份文件，旧版保持不变。A7 当前采用下述 28 面精简版流程，工作区临时 60 面资料支持版不发布。封三改为资料页，封二仍留白；A6 正文、页序及原封底操作速记不变。QQ 图片存于 `docs/assets/manual-design/qq-group-1002979587.jpg`，保留用户原始 JPEG，通过 Word 原生裁切显示码区与静区。群号及三个项目地址均以原生文字排印，可离线阅读。

每个纸面的裁切线改为按纸张绝对坐标定位的镜像对称短划；外层纸正反面同时增加折订虚线。验证读取 Word 导出 PDF 中的实际线段坐标，按双面翻转匹配，不以 XML 预设坐标代替实际输出。文件校样线段误差小于 0.03 mm，此为数字文件核验结果，不代表实体机器套准精度。印厂反馈的平行偏移须通过实物测量横纵偏移量并校准双面套准；不在未测量时给文件加入猜测性的背面偏移。建议原尺寸 PDF、A4、100% 双面输出，先做套准与 QQ 扫码实物校样。

```powershell
python scripts/update_booklet_support.py build --size a6
python scripts/update_booklet_support.py render --size a6 --renderer <documents技能目录中的render_docx.py>
python scripts/update_booklet_support.py verify --size a6
# 检查新增外层纸校样，以及与已审阅基准不同的正文栅格区域。
# 目检通过记录在 .work/booklet-support/<size>/<model>/visual-review.json。
python scripts/update_booklet_support.py publish --size a6
```

修订校样在 `.work/booklet-support/`。逐页检查原生文字完整、二维码存在、页数、翻转线段几何，并检查原正文框规范化 XML 完全一致；正文 PNG 与先前逐页目检通过的基准逐成品区比较，相同部分沿用原目检结果，差异区域重新目检。发布绑定验证时的 DOCX 哈希并排他新建输出。

### A7 28 面精简版 当前交付

`scripts/build_compact_a7.py` 从已确认内容连续排流，正文 24 页，加封面、封二留白、封三资料与封底共 28 面。每组仅 7 张双面 A4，形成四本 A7 小册，较 60 面版减少 8 张纸。正文 7.5 磅、9.2 磅行距，表格 7 磅、8.9 磅行距，主题标题 10 磅。段落、步骤与表格行完整保留，菜单流程和迟滞示例以紧凑文字表示。字体变小后应以最终印张确认阅读效果。

```powershell
python scripts/build_compact_a7.py flow
python scripts/build_compact_a7.py paginate
python scripts/build_compact_a7.py remap
python scripts/build_compact_a7.py paginate
# 若页码映射发生变化，重复 remap / paginate，直到稳定。
python scripts/build_compact_a7.py build
python scripts/build_compact_a7.py render --renderer <documents技能目录中的render_docx.py>
python scripts/build_compact_a7.py verify
# 全部 42 个 A4 校样面的首套原尺寸页面目检通过后，排他新建发布。
python scripts/build_compact_a7.py publish
```

Word 分页使用 `paginate_booklet.ps1` 的独立隐藏实例，读出每个段落及表格行的页码；它是文档分页的内部适配器。按这些页码拆分原生内容，续表复制表头；所有页码引用均依据新正文映射重算。内部文件位于 `.work/compact-a7/`，最终文件增加 `_精简28面_资料支持与双面对齐版` 后缀。验证全册每个页面区文字、行内容、内封、图片、页码、边界和双面辅助线。保留原 60 面 A7、A6 及 A5 文件。上述为历史预拼版交付流程；当前推荐单页原稿，见下一节。

### A6 / A7 单页顺序 Word 原稿 当前推荐

印刷交接以 `artifacts/print-booklets/reading-order/README.md` 为准。三款机型分别提供 A6 32 面和 A7 28 面原稿，按封面、封二留白、正文、封三资料、封底的正常顺序排列。每个 Word 页面只有一个成品面，不包含多套复制、辅助线或预设小册子选项。原生段落、表格及图片从已确认版本提取，保留媒体及样式；正文使用真实 Word 页眉和 PAGE 域。三节采用统一页边距，封面及资料页因此略向下调整；A7 资料页适当收紧段后间距以保持 28 面，二维码及字号不变。

```powershell
python scripts/build_reading_order_manuals.py build
python scripts/build_reading_order_manuals.py render --renderer <documents技能目录中的render_docx.py>
python scripts/build_reading_order_manuals.py wordcheck
python scripts/build_reading_order_manuals.py verify
# 逐页目检，将最终文件哈希及页数记录于各工作目录 visual-review.json。
python scripts/build_reading_order_manuals.py publish
```

内部文件位于 `.work/reading-order/`。验证检查源文件未改动、媒体及样式完整、正文文字与页码、封二留白、安全边界和页面尺寸，并在独立隐藏 Word 实例中只读测试“书籍折叠”，不保存、不打印。先设置母纸，再启用折叠，六份文档均保持原页数；母纸横向尺寸分别为 210 × 148.5 mm 和 148.5 × 105 mm，以保留前版精确裁后尺寸及分页。Word 的一次折叠不能直接代替 A4 上多套 A6 / A7 合版；该工序交由印厂。发布绑定校验与目检哈希，排他新建六份 DOCX，旧文件保持原样。

### 单光 A7 仅封面装订虚线修订

`scripts/build_a7_cover_guides.py` 从已发布的 28 面精简版新建三份 `_仅封面装订虚线版.docx`，移除纸面中心裁切线与背面折线，保留第一印刷面上封面与封底之间的装订线。正文、图像、页序和字号沿用源文件。流程为 `build` → `render --renderer <render_docx.py路径>` → `verify` → `publish`；验证核对原始文件哈希、包内资源、文字图像位置，以及辅助线仅出现在封面一侧。交接说明见 `artifacts/print-booklets/a7/README.md`。

### 3.2 寸双光 28 面 A5 A6 A7 装订版

以下为 28 面基础版构建记录，当前推荐的 36 面版本见后文“视差图解修订”。

内容在 `scripts/dual_booklet_content.py`，构建在 `scripts/build_dual_print_booklets.py`，交接入口为 `artifacts/print-booklets/dual/README.md`。三份为 A4 单套、双套、四套原生 Word 拼版，每本均 28 面，正文 24 页。沿用单光系列的任务结构，但按双光实际硬件与固件重新编写，并以肯定、直接的步骤说明操作。QQ 群和三个完整开源地址集中在封三。辅助线只保留封面与封底间的装订线。

双光硬件图来自 `device-controls.png` 原线稿。新增 `dual-32-controls-manual.png`、`dual-32-rear-manual.png` 仅裁切原像素，利用非矩形选区排除相邻视图；部件、引线与文字保持原样。接口图继续使用 Word 原生裁切。原图中的示例传感器参数表未用于新印刷图。

```powershell
python scripts/build_dual_print_booklets.py build
python scripts/build_dual_print_booklets.py render --renderer <documents技能目录中的render_docx.py>
python scripts/build_dual_print_booklets.py verify
# 本次按用户要求抽样目检，记录最终哈希与结论于各尺寸目录 sample-review.json。
python scripts/build_dual_print_booklets.py publish
```

内部校样在 `.work/dual-print-booklets/`。全页自动核对原生文字、每套页序、封二留白、二维码、纸边和正文框底边，另外检查旧 DOCX 哈希。抽样覆盖封面、资料页、机身图、校准报警、融合与表格页；发现的裁切与 A7 版心问题修正后重新渲染。A7 正文 7.5 磅、行距 9.5 磅，以精炼文案和段落间距保持 28 面。发布绑定校验和抽样记录哈希，排他新建文件。

### 双光 32 面视差详解与测距选配修订

在上述构建、渲染、验证及发布命令中加入 `--edition parallax`，生成三份独立的 32 面文件。内部校样改用 `.work/dual-parallax-booklets/`，28 面版的内容计划和发布文件保持原样。扩展计划为 `dual_booklet_content.parallax_book()`，正文 28 页，A4 印刷面 16 个，每组 8 张双面纸。封三资料及封面装订虚线沿用原设计。

产品负责人补充的量贩版预留测距接口、选购方式、中距离出厂校准和四项画面移动方向作为本修订的事实依据。偏移方向按出厂画面方向说明；摄像头 X 增大向下、Y 增大向右，热像 X 增大向左、Y 增大向上。约 ±200 的摄像头移动边界写成与当前缩放、摄像头相关的现场判断，而非固定软件限值。第 15–18 页分开讲解原理、快捷调节、方向表与行程补充；第 20–21 页讲解测距配置与自动校准。目录、文内页码及套帖页序同步更新。全部文件自动核对文字和版心，视觉阶段按用户要求抽样检查新增主题、方向表与封面资料页。

### 双光 36 面视差图解修订

使用 `--edition illustrated` 构建、渲染、验证与发布，内部校样位于 `.work/dual-illustrated-booklets/`。内容计划为 `dual_booklet_content.illustrated_book()`，在 32 面文字版基础上穿插四张图页：正文 16 页的原理图、18 页的摄像头方向图、20 页的热像方向图、22 页的逐步对齐图。同步更新目录和文内引用，保留原详细说明与全部选配信息。每册 36 面，正文 32 页；18 个 A4 印刷面，每组 9 张双面纸，复制套数及翻边方式沿用前版。

`scripts/parallax_artwork.mjs --modules <bundled-node_modules>` 仅生成 `docs/assets/manual-design/parallax-*` 四组 SVG/PNG。蓝色空心轮廓与橙色斜线热区分别表示两路画面，既用颜色也用纹理区分；箭头、参数名与增减方向对应产品负责人提供的实际操作。原理图为抽象观察中心示意，硬件图仍使用原线稿。图片以 2400 像素宽度内嵌，正文与表格继续保留原生 Word 内容。全页自动核对文字、安全区、版心、封面辅助线与旧文件哈希，抽样查看新增四张图页及封面资料页。A7 图页删去重复的菜单操作描述，以维持图幅和既有字号。发布使用独立文件名，并绑定最终校验和抽样记录。
