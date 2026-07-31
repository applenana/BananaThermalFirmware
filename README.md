# Banana Thermal Firmware

香蕉热成像设备的官方固件下载、升级指南、协议规范与技术支持中心。

本仓库面向设备用户、售后人员和上位机开发者，提供经过校验的 UF2 固件、版本说明、热成像传感器兼容信息，以及双光串口协议文档。

## 快速入口

| 我想要…… | 前往 |
| --- | --- |
| 下载最新固件 | [Releases](../../releases/latest) |
| 第一次升级设备 | [安装与升级指南](docs/INSTALLATION.md) |
| 了解设备每一项菜单 | [设备菜单完整指南](docs/menu/README.md) |
| 选择正确的 UF2 | [固件变体说明](docs/FIRMWARE_VARIANTS.md) |
| 了解 MLX / 海曼和方屏差异 | [传感器与显示模式](docs/SENSORS_AND_DISPLAY.md) |
| 开发或调试上位机 | [双光串口推流协议](docs/STREAMING_PROTOCOL.md) |
| 判断固件和上位机是否兼容 | [兼容性说明](docs/COMPATIBILITY.md) |
| 校验固件真实性 | [发布完整性与签名](docs/RELEASE_INTEGRITY.md) |
| 设备升级后异常 | [故障排查](docs/TROUBLESHOOTING.md) |
| 下载官方上位机 | [NextBananaThermalStudio](https://github.com/applenana/NextBananaThermalStudio/releases) |

## 下载哪一个固件

每个正式 Release 提供三个 UF2 变体：

| 文件后缀 | 设备配置 | 适用场景 |
| --- | --- | --- |
| `sketch3m_fs5m.uf2` | 8 MB Flash，300 MHz | 默认正常版；性能优先 |
| `sketch3m_fs5m_stable.uf2` | 8 MB Flash，220 MHz | 稳定版；摄像头竖纹或高频运行不稳定时使用 |
| `sketch1m_fs1m.uf2` | 2 MB Flash | 旧款或小容量 Flash 设备 |

无法确认 Flash 容量时不要凭文件大小猜测。请先查看设备资料、原固件说明或联系设备提供方。更详细的选择方法见[固件变体说明](docs/FIRMWARE_VARIANTS.md)。

## 安全升级摘要

1. 备份设备照片、标定参数和重要配置；
2. 下载与硬件匹配的 UF2；
3. 按 Release 中的 SHA-256 和 Ed25519 签名校验文件；
4. 进入 UF2 Bootloader 后复制固件；
5. 等待设备自动重启；
6. 验证版本、传感器识别、全屏/方屏、热像和可见光；
7. 使用最新版 NextBananaThermalStudio 做投屏兼容检查。

刷入错误变体可能导致设备无法启动、文件系统容量不匹配或原有数据不可用。完整步骤见[安装与升级指南](docs/INSTALLATION.md)。

## 发布可信度

正式 Release 由自动化构建产生，并包含：

- 三个允许发布的 UF2；
- `manifest.json`；
- `SHA256SUMS`；
- `SHA256SUMS.sig`；
- `firmware-release-allowed-signers`。

发布过程只允许上述文件进入 Release。正式版本启用不可变发布保护，发布后不能替换附件。校验方法见[发布完整性与签名](docs/RELEASE_INTEGRITY.md)。

## 文档目录

- [设备菜单完整指南](docs/menu/README.md)
- [安装与升级指南](docs/INSTALLATION.md)
- [固件变体说明](docs/FIRMWARE_VARIANTS.md)
- [传感器与显示模式](docs/SENSORS_AND_DISPLAY.md)
- [双光串口推流协议](docs/STREAMING_PROTOCOL.md)
- [兼容性说明](docs/COMPATIBILITY.md)
- [发布与版本策略](docs/RELEASE_PROCESS.md)
- [发布完整性与签名](docs/RELEASE_INTEGRITY.md)
- [故障排查](docs/TROUBLESHOOTING.md)
- [参与文档和问题反馈](CONTRIBUTING.md)
- [安全问题报告](SECURITY.md)

## 问题反馈

提交问题前请准备：

- 设备型号和 Flash 容量；
- 固件版本与所选变体；
- 传感器型号；
- 全屏还是方屏；
- 是否启用可见光或融合；
- 上位机名称、版本和操作系统；
- 可复现步骤及已经移除序列号等敏感信息的日志。

普通使用问题可以提交 Issue。涉及密钥、激活机制、未公开实现或可利用漏洞时，请按 [SECURITY.md](SECURITY.md) 私下报告。

## 许可说明

公开下载不等同于开源授权。本仓库中的固件二进制、文档、名称和发布材料保留其各自权利；除非对应文件明确附带许可，否则不得推定获得源码、再发布或商业使用授权。
