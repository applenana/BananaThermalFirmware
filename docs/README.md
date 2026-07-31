# Banana Thermal 文档中心

这里汇总设备使用、固件升级、Studio 上位机、开发协议与发布安全资料。第一次使用建议从[在线使用手册](user-guide/README.md)开始；知道具体功能名称时，可直接使用下表定位。

## 设备百科全书

| 章节 | 解决的问题 |
| --- | --- |
| [在线手册首页](user-guide/README.md) | 阅读路线、功能全景、版本边界 |
| [认识设备](user-guide/01-device-tour.md) | 硬件部件、状态栏、5 分钟上手、硬件差异 |
| [按键、触控与显示](user-guide/02-controls-and-display.md) | A/B/拨片/快捷键、手势、快捷菜单、16 项详细菜单 |
| [拍照与图库](user-guide/03-capture-and-gallery.md) | 设备相册、设备图库、软件图库、导出与缓存 |
| [BananaThermal Studio](user-guide/04-studio.md) | Windows/Android、连接、实时双路、趋势、拍照录像、更新 |
| [高级设置与维护](user-guide/05-advanced-and-service.md) | 双光对齐、测距视差、温度校准、UF2、串口命令与坏点 |
| [协议与数据格式](user-guide/06-data-formats.md) | 实时帧、设备照片、`.btpkg`、CSV/JSON/PNG/MP4 |
| [16 项设备菜单](menu/README.md) | 每个菜单的范围、默认值、使用方法与风险 |

## 安装、兼容与排障

| 文档 | 内容 |
| --- | --- |
| [安装与升级指南](INSTALLATION.md) | 备份、选择 UF2、进入 Bootloader、刷写与验证 |
| [固件变体说明](FIRMWARE_VARIANTS.md) | 8 MB 正常/稳定版与 2 MB 版如何选择 |
| [传感器与显示模式](SENSORS_AND_DISPLAY.md) | MLX、Heimann、全屏/方屏、可见光与测距差异 |
| [兼容性说明](COMPATIBILITY.md) | 固件、硬件与 Studio 的版本配合 |
| [故障排查](TROUBLESHOOTING.md) | 启动、连接、投屏、融合、测温、图库与导出异常 |

## 开发者资料

| 文档 | 内容 |
| --- | --- |
| [双光串口推流协议](STREAMING_PROTOCOL.md) | Thermal View JSON、热像帧、可见光帧、尺寸与兼容要求 |
| [协议与数据格式总览](user-guide/06-data-formats.md) | 照片下载格式、`.btpkg` 和导出格式的关系 |
| [传感器与显示模式](SENSORS_AND_DISPLAY.md) | 正确理解温度阵列尺寸和方屏参数 |

## 发布与安全

| 文档 | 内容 |
| --- | --- |
| [发布与版本策略](RELEASE_PROCESS.md) | 版本、构建、附件白名单与发布流程 |
| [发布完整性与签名](RELEASE_INTEGRITY.md) | SHA-256、Ed25519 与不可变发布验证 |
| [安全策略](../SECURITY.md) | 私下报告漏洞与敏感问题 |
| [贡献指南](../CONTRIBUTING.md) | 文档反馈和问题提交要求 |

## 版本说明

- [v1.7.0](releases/v1.7.0.md)：当前公开固件基线。

> 文档以公开固件 v1.7.0 与 BananaThermal Studio v0.4.2 的实现为基线。新版本行为与本文冲突时，以相应 Release Notes、当前源码和协议版本为准。
