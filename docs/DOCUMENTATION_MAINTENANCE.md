# 文档来源与维护

本次资料更新日期为 2026-10-19。当前手册的固件行为基线为统一 v1.8.0 对应源码，Studio 行为按 0.5.5+109 源码核对；这不是安装包已正式发布的声明。历史 v1.7 手册保留原版，用于历史查询。

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
