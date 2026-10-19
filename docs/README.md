# Banana Thermal 文档中心

这里汇总单光与双光设备使用、固件升级、Studio、协议与发布资料。先查看[设备分类](devices/README.md)，再阅读对应手册。三款单光共用 standard 板型，双光使用 dual，不能按屏幕尺寸判断固件。

## 按设备阅读

| 设备或用途 | 入口 |
| --- | --- |
| 2.4 / 2.8 / 3.2 寸单光 | [完整单光使用说明书](user-guide/single-light.md) |
| 3.2 寸双光融合 | [完整双光使用说明书](user-guide/dual-light.md) |
| Word 与 PDF | [离线手册及历史版本](../artifacts/README.md) |
| 板型与功能差异 | [设备对照](devices/README.md) |
| 文档来源与重建 | [维护说明](DOCUMENTATION_MAINTENANCE.md) |

## 设备百科全书

| 章节 | 解决的问题 |
| --- | --- |
| [在线手册首页](user-guide/README.md) | 阅读路线、功能全景、版本边界 |
| [认识设备](user-guide/01-device-tour.md) | 硬件部件、状态栏、5 分钟上手、硬件差异 |
| [按键、触控与显示](user-guide/02-controls-and-display.md) | A/B、组合键、拨片、双光快捷键、手势、详细菜单 |
| [拍照与图库](user-guide/03-capture-and-gallery.md) | 设备相册、设备图库、软件图库、导出与缓存 |
| [BananaThermal Studio](user-guide/04-studio.md) | Windows/Android、连接、实时双路、趋势、拍照录像、更新 |
| [高级设置与维护](user-guide/05-advanced-and-service.md) | 双光对齐、测距视差、温度校准、UF2、串口命令与坏点 |
| [协议与数据格式](user-guide/06-data-formats.md) | 实时帧、设备照片、`.btpkg`、CSV/JSON/PNG/MP4 |
| [设备菜单](menu/README.md) | 基础 15 项，含温度报警；双光测距成功后最多 17 项 |

## 安装、兼容与排障

| 文档 | 内容 |
| --- | --- |
| [安装与升级指南](INSTALLATION.md) | 备份、选择 UF2、进入 Bootloader、刷写与验证 |
| [固件变体说明](FIRMWARE_VARIANTS.md) | 两板型共六个 UF2、Flash 与迁移规则 |
| [传感器与显示模式](SENSORS_AND_DISPLAY.md) | MLX、Heimann、全屏/方屏、可见光与测距差异 |
| [兼容性说明](COMPATIBILITY.md) | 固件、硬件与 Studio 的版本配合 |
| [故障排查](TROUBLESHOOTING.md) | 启动、连接、投屏、融合、测温、图库与导出异常 |

## 开发者资料

| 文档 | 内容 |
| --- | --- |
| [串口推流协议](STREAMING_PROTOCOL.md) | 单光热帧、双光可见光帧、能力识别与兼容要求 |
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

- [v1.8.0](releases/v1.8.0.md)：统一单光与双光、六固件矩阵及首次迁移。
- [v1.7.0](releases/v1.7.0.md)：历史双光基线。

> 当前文档按统一固件 v1.8.0 对应源码和 Studio 0.5.5 源码核对；不表示该版本附件已经发布。下载以正式 Releases 为准。历史 v1.7 离线手册保留原内容，不能用于单光首次迁移。
