<div align="center">

# Banana Thermal Firmware

**双光与多款单光热成像：固件发布、使用手册与开发资料**

[设备分类](docs/devices/README.md) · [单光使用手册](docs/user-guide/single-light.md) · [双光使用手册](docs/user-guide/dual-light.md) · [DOCX / PDF 说明书](artifacts/README.md) · [下载最新固件](../../releases/latest)

![Firmware docs](https://img.shields.io/badge/firmware_docs-v1.8-0B3B60?style=flat-square)
![Studio docs](https://img.shields.io/badge/Studio_docs-0.5.5-E67E22?style=flat-square)
![Hardware](https://img.shields.io/badge/thermal-MLX%20%7C%20Heimann-2E8B57?style=flat-square)

</div>

> 这是设备用户、售后人员和上位机开发者共用的资料入口，覆盖 3.2 寸双光，以及 2.4 / 2.8 / 3.2 寸单光。先认板型与 Flash，再选择 UF2；三款单光共用 standard 固件，实体操作按各自说明书执行。文档基线不代表安装包已发布，下载以正式 Releases 为准。

## 先找到你的设备

| 设备 | 固件板型 | 在线说明书 | 离线文档 |
| --- | --- | --- | --- |
| 2.4 / 2.8 / 3.2 寸单光 | `standard` | [单光手册与三机型差异](docs/user-guide/single-light.md) | [Word](artifacts/BananaThermal_单光热成像使用说明书_v1.8.docx) / [PDF](artifacts/BananaThermal_单光热成像使用说明书_v1.8.pdf) |
| 3.2 寸双光融合 | `dual` | [双光手册](docs/user-guide/dual-light.md) | [Word](artifacts/BananaThermal_3.2寸双光热成像使用说明书_v1.8.docx) / [PDF](artifacts/BananaThermal_3.2寸双光热成像使用说明书_v1.8.pdf) |

**旧单光首次迁移会清空设备照片、配置和校准。** 先备份；仅在旧分区能挂载且激活信息有效时尝试保留激活。旧单光 v2.2 与统一 v1.8.x 属于不同版本线，不能只比较数字。

## 从这里开始

| 你的目标 | 最短入口 |
| --- | --- |
| 第一次拿到设备 | [设备分类与功能对照](docs/devices/README.md) → 对应机型手册 |
| 查询 A / B / 拨片 / 快捷键 | [按键与界面行为](docs/user-guide/02-controls-and-display.md) |
| 查某一个设备菜单 | [设备菜单完整索引](docs/menu/README.md)，含温度报警 |
| 在 Windows / Android 投屏 | [Studio 安装、连接与实时画面](docs/user-guide/04-studio.md) |
| 下载、回放或导出照片/录像 | [拍照与图库](docs/user-guide/03-capture-and-gallery.md) |
| 对齐双光或校准温度 | [高级设置与维护](docs/user-guide/05-advanced-and-service.md) |
| 升级固件 | [安装与升级指南](docs/INSTALLATION.md) |
| 排查启动、投屏、融合或测温异常 | [故障排查](docs/TROUBLESHOOTING.md) |
| 开发上位机或解析文件 | [协议与数据格式](docs/user-guide/06-data-formats.md) |
| 浏览全部资料 | [文档中心](docs/README.md) |

## 随设备装订的说明书

印刷稿按单台设备的使用任务编排，包含硬件识别、日常操作、参数解释、维护与资料支持。与上方电子版分别维护，按用途选择：

| 设备与用途 | 文件入口 | 成册规格 |
| --- | --- | --- |
| 3.2 寸双光，A4 直接拼版印刷 | [A5 / A6 / A7 视差图解版](artifacts/print-booklets/dual/README.md) | 当前各 36 面；保留 32 面详解版与 28 面初版 |
| 三款单光，交给印厂合版 | [A6 / A7 单页顺序 Word 原稿](artifacts/print-booklets/reading-order/README.md) | A6 32 面、A7 28 面，每款独立成册 |
| 三款单光，A7 四套预拼版 | [仅封面装订虚线版](artifacts/print-booklets/a7/README.md) | 每本 28 面，每组 7 张双面 A4 制作四本 |
| 三款单光，其他尺寸与历史拼版 | [A5](artifacts/print-booklets/README.md) / [A6](artifacts/print-booklets/a6/README.md) | 每本 32 面，按各目录说明打印 |

“面”指折订后的一面成品页，含封面、内封与封底。预拼版文件使用 A4、实际大小 100%、普通每张一页输出；单页原稿由印厂或小册子工具安排页序。各目录提供纸张方向、双面翻转与裁切位置，先以最终纸张制作校样。

## 选择正确的固件

从 v1.8.0 开始，正式 Release 提供 dual 与 standard 两套板型、每套三个 UF2。不能根据 UF2 文件大小猜测板型或 Flash 容量。

| UF2 文件后缀 | 目标硬件 | 适用场景 |
| --- | --- | --- |
| `dual_sketch3m_fs5m*.uf2` | 双光，8 MB | 300 MHz 性能版或 220 MHz 稳定版 |
| `dual_sketch1m_fs1m.uf2` | 双光，2 MB | 小容量 Flash |
| `standard_sketch3m_fs5m*.uf2` | 普通热成像，8 MB | 300 MHz 性能版或 220 MHz 稳定版 |
| `standard_sketch1m_fs1m.uf2` | 普通热成像，2 MB | 小容量 Flash |

完整选择规则见[固件变体说明](docs/FIRMWARE_VARIANTS.md)。

## 安全升级，7 步完成

1. 下载设备照片，记录发射率、温度校准、触摸校准；双光设备另记录对齐和视差锚点。
2. 从正式 [Releases](../../releases/latest) 下载与 `dual` / `standard` 板型及 Flash 容量匹配的 UF2。
3. 使用 `SHA256SUMS` 和 Ed25519 签名确认文件完整、来源可信。
4. 按机型进入 Bootloader；有 A/BOOTSEL 与复位的设备保持 USB 数据连接，按住 A、短按并松开复位，磁盘出现后松开 A。其他外壳见对应机型手册。
5. 把 UF2 复制到 RP2040 磁盘，等待磁盘自动断开和设备重启。
6. 检查传感器、全屏/方屏、热像与拍照；双光另查可见光、融合和可选测距。
7. 用最新版 [NextBananaThermalStudio](https://github.com/applenana/NextBananaThermalStudio/releases) 检查连接、投屏和校准参数。

刷入错误的 Flash 分区可能导致无法启动、LittleFS 不匹配或旧数据不可读。请在操作前阅读[完整升级指南](docs/INSTALLATION.md)。

## 这套设备包含什么

| 层级 | 能力 |
| --- | --- |
| 共用固件功能 | 热像显示、测温光标、实体键、可选触摸、拍照与相册、滤波、分段校准和温度报警 |
| 双光专用功能 | 可见光摄像头、双光融合、独立快捷菜单键、可选测距与视差 |
| 可选硬件 | MLX90640 / MLX90641 / Heimann HTPA32x32、OV2640 / OV3660、VL53L0X 测距 |
| BananaThermal Studio | Windows / Android 实时双路投屏、测温趋势、设备图库、`.btpkg` 图库、视频导出、校准与更新 |
| 开发接口 | Thermal View JSON v2、热像/可见光串口帧、设备照片下载、校准协议与公开文件格式 |

距离与视差菜单仅在测距初始化成功后显示；单光本机摄像头和融合栏目可能保留不可用提示，Studio 则按身份隐藏双光操作。方屏和全屏使用独立配置。MLX90641 原生 16×12，在固件中上采样到 32×24；LCD 分辨率、传输尺寸与原生测温点数不能混为一谈。详见[传感器与显示模式](docs/SENSORS_AND_DISPLAY.md)。

## 发布为什么可信

正式 Release 由自动化流程构建，只允许以下附件进入发布：

- v1.8.0 起六个允许发布的 UF2（历史 Release 保持三个）；
- `manifest.json`；
- `SHA256SUMS` 与 `SHA256SUMS.sig`；
- `firmware-release-allowed-signers`。

正式版本启用不可变发布保护，附件发布后不可替换。验证方法见[发布完整性与签名](docs/RELEASE_INTEGRITY.md)。

## 文档地图

| 读者 | 推荐路径 |
| --- | --- |
| 设备用户 | [在线使用手册](docs/user-guide/README.md) → [菜单索引](docs/menu/README.md) → [故障排查](docs/TROUBLESHOOTING.md) |
| 售后 / 维护 | [安装与首次迁移](docs/INSTALLATION.md) → [兼容性](docs/COMPATIBILITY.md) → [v1.8.0 说明](docs/releases/v1.8.0.md) |
| 上位机开发者 | [协议与数据格式](docs/user-guide/06-data-formats.md) → [串口推流协议](docs/STREAMING_PROTOCOL.md) → [传感器与显示模式](docs/SENSORS_AND_DISPLAY.md) |
| 发布维护者 | [发布与版本策略](docs/RELEASE_PROCESS.md) → [发布完整性](docs/RELEASE_INTEGRITY.md) → [贡献指南](CONTRIBUTING.md) |

## 获取帮助

更多使用资料与交流可加入 QQ 群 **1002979587**，也可使用[群二维码](docs/assets/manual-design/qq-group-1002979587.jpg)。项目入口：[NextBananaThermalStudio 上位机](https://github.com/applenana/NextBananaThermalStudio)、[Python 上位机](https://github.com/applenana/BananaThermal-Studio)、[在线文档与固件](https://github.com/applenana/BananaThermalFirmware)。

提交 Issue 前请准备设备型号、Flash 容量、固件完整版本、UF2 变体、传感器/摄像头型号、全屏或方屏模式、Studio 版本、操作系统和最短复现步骤。日志和截图必须移除序列号、激活码、密钥等敏感信息。

普通使用问题可提交 Issue。涉及密钥、激活机制、未公开实现或可利用漏洞时，请按 [SECURITY.md](SECURITY.md) 私下报告。

## 许可说明

公开下载不等同于开源授权。本仓库中的固件二进制、文档、名称和发布材料保留其各自权利；除非对应文件明确附带许可，否则不得推定获得源码、再发布或商业使用授权。
