<div align="center">

# Banana Thermal Firmware

**3.2 寸双光融合热成像：固件发布、完整使用手册与开发资料**

[在线使用手册](docs/user-guide/README.md) · [PDF 说明书](artifacts/BananaThermal_3.2寸双光热成像使用说明书_v1.7.pdf) · [Word 说明书](artifacts/BananaThermal_3.2寸双光热成像使用说明书_v1.7.docx) · [下载最新固件](../../releases/latest)

![Firmware](https://img.shields.io/badge/firmware-v1.7.0-0B3B60?style=flat-square)
![Studio](https://img.shields.io/badge/Studio-v0.4.2-E67E22?style=flat-square)
![Hardware](https://img.shields.io/badge/thermal-MLX%20%7C%20Heimann-2E8B57?style=flat-square)

</div>

> 这是设备用户、售后人员和上位机开发者共用的官方入口。你可以在这里选择并校验 UF2、学习设备的每个按键和菜单、使用 BananaThermal Studio，以及查阅双光协议和数据格式。

![设备按键、接口与传感器示意](docs/assets/user-guide/device-controls.png)

## 从这里开始

| 你的目标 | 最短入口 |
| --- | --- |
| 第一次拿到设备 | [5 分钟快速上手](docs/user-guide/01-device-tour.md#5-分钟快速上手) |
| 查询 A / B / 拨片 / 快捷键 | [按键与界面行为](docs/user-guide/02-controls-and-display.md) |
| 查某一个设备菜单 | [16 项菜单完整索引](docs/menu/README.md) |
| 在 Windows / Android 投屏 | [Studio 安装、连接与实时画面](docs/user-guide/04-studio.md) |
| 下载、回放或导出照片/录像 | [拍照与图库](docs/user-guide/03-capture-and-gallery.md) |
| 对齐双光或校准温度 | [高级设置与维护](docs/user-guide/05-advanced-and-service.md) |
| 升级固件 | [安装与升级指南](docs/INSTALLATION.md) |
| 排查启动、投屏、融合或测温异常 | [故障排查](docs/TROUBLESHOOTING.md) |
| 开发上位机或解析文件 | [协议与数据格式](docs/user-guide/06-data-formats.md) |
| 浏览全部资料 | [文档中心](docs/README.md) |

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
2. 从正式 [Releases](../../releases/latest) 下载与 Flash 容量匹配的 UF2。
3. 使用 `SHA256SUMS` 和 Ed25519 签名确认文件完整、来源可信。
4. 断开 USB；按住按钮 A，按一下复位，先松复位，出现 RP2040 磁盘后再松开 A。
5. 把 UF2 复制到 RP2040 磁盘，等待磁盘自动断开和设备重启。
6. 检查传感器、全屏/方屏、热像、可见光、融合与拍照。
7. 用最新版 [NextBananaThermalStudio](https://github.com/applenana/NextBananaThermalStudio/releases) 检查连接、投屏和校准参数。

刷入错误的 Flash 分区可能导致无法启动、LittleFS 不匹配或旧数据不可读。请在操作前阅读[完整升级指南](docs/INSTALLATION.md)。

## 这套设备包含什么

| 层级 | 能力 |
| --- | --- |
| 设备固件 | 32×24 / 32×32 热阵列、可见光摄像头、双光融合、测温光标、触屏/实体键、拍照与设备相册 |
| 可选硬件 | MLX90640 / MLX90641 / Heimann HTPA32x32、OV2640 / OV3660、VL53L0X 测距 |
| BananaThermal Studio | Windows / Android 实时双路投屏、测温趋势、设备图库、`.btpkg` 图库、视频导出、校准与更新 |
| 开发接口 | Thermal View JSON v2、热像/可见光串口帧、设备照片下载、校准协议与公开文件格式 |

不同硬件会自动隐藏不适用的菜单。方屏和全屏使用独立的对齐参数；LCD 的 320×240 / 240×240 显示分辨率不等于热阵列真实测温点数。详见[传感器与显示模式](docs/SENSORS_AND_DISPLAY.md)。

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
| 售后 / 维护 | [高级设置与维护](docs/user-guide/05-advanced-and-service.md) → [兼容性](docs/COMPATIBILITY.md) → [版本说明](docs/releases/v1.7.0.md) |
| 上位机开发者 | [协议与数据格式](docs/user-guide/06-data-formats.md) → [串口推流协议](docs/STREAMING_PROTOCOL.md) → [传感器与显示模式](docs/SENSORS_AND_DISPLAY.md) |
| 发布维护者 | [发布与版本策略](docs/RELEASE_PROCESS.md) → [发布完整性](docs/RELEASE_INTEGRITY.md) → [贡献指南](CONTRIBUTING.md) |

## 获取帮助

提交 Issue 前请准备设备型号、Flash 容量、固件完整版本、UF2 变体、传感器/摄像头型号、全屏或方屏模式、Studio 版本、操作系统和最短复现步骤。日志和截图必须移除序列号、激活码、密钥等敏感信息。

普通使用问题可提交 Issue。涉及密钥、激活机制、未公开实现或可利用漏洞时，请按 [SECURITY.md](SECURITY.md) 私下报告。

## 许可说明

公开下载不等同于开源授权。本仓库中的固件二进制、文档、名称和发布材料保留其各自权利；除非对应文件明确附带许可，否则不得推定获得源码、再发布或商业使用授权。
