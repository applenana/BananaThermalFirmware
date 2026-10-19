# Banana Thermal 单光与双光在线使用手册

本手册覆盖三款单光与 3.2 寸双光设备，按统一固件 v1.8.0 对应源码及 Studio 0.5.5 源码核对。实际下载以正式 Releases 为准。先确认板型和按键，再使用下面的专题章节。

| 设备 | 完整手册 |
| --- | --- |
| 2.4 / 2.8 / 3.2 寸单光 | [单光说明书与三种实体操作差异](single-light.md) |
| 3.2 寸双光融合 | [双光说明书](dual-light.md) |
| 不确定自己的设备 | [设备分类与功能对照](../devices/README.md) |

## 推荐阅读路线

| 你是谁 | 从这里开始 |
| --- | --- |
| 第一次使用 | [认识设备与 5 分钟上手](01-device-tour.md) → [按键、触控与显示](02-controls-and-display.md) |
| 日常巡检 | [按键与快捷菜单](02-controls-and-display.md#按键在不同界面中的行为) → [拍照与图库](03-capture-and-gallery.md) |
| Studio 用户 | [安装、连接与实时画面](04-studio.md) → [设备/软件图库](03-capture-and-gallery.md) |
| 售后维护 | [高级设置与维护](05-advanced-and-service.md) → [故障排查](../TROUBLESHOOTING.md) |
| 上位机开发 | [协议与数据格式](06-data-formats.md) → [串口推流协议](../STREAMING_PROTOCOL.md) |

## 全部章节

1. [认识设备](01-device-tour.md)：部件、状态栏、传感器差异、第一次开机。
2. [按键、触控与显示](02-controls-and-display.md)：A/B/组合键/拨片，双光快捷菜单，手势和详细菜单。
3. [拍照与图库](03-capture-and-gallery.md)：设备相册、设备图库、软件图库、缓存和导出。
4. [BananaThermal Studio](04-studio.md)：Windows/Android、USB、双路实时、趋势、拍照录像、更新。
5. [高级设置与维护](05-advanced-and-service.md)：双光对齐、测距视差、温度校准、UF2、控制台与坏点。
6. [协议与数据格式](06-data-formats.md)：实时帧、设备照片、`.btpkg` 与导出格式。

设备菜单另有[逐项参数手册](../menu/README.md)，基础 15 项，双光测距成功后最多 17 项；包含新增温度报警。升级与故障处理分别见[安装与升级](../INSTALLATION.md)和[故障排查](../TROUBLESHOOTING.md)。

需要离线保存或打印时，请到[离线说明书](../../artifacts/README.md)按单光或双光下载当前 Word / PDF。旧 v1.7 文件是历史双光资料。

## 功能覆盖检查

| 功能域 | 已覆盖内容 |
| --- | --- |
| 硬件与输入 | 三款单光外壳差异、电源、Type-C、复位、A/B、组合键、拨片；双光独立快捷键；可选触摸 |
| 本机显示 | 状态栏、全屏/方屏、7 套伪彩、图例、反色、亮度、滤波与测温光标 |
| 双光系统 | OV2640/OV3660、融合模式、缩放/X/Y、旋转镜像、VL53L0X、视差锚点 |
| 数据采集 | 本机拍照/相册、Studio 拍照/录像、动态热像/可见光槽位、趋势记录 |
| Studio | Windows/Android、连接与激活、11 色板、悬浮窗、图库、历史、校准、设置与更新 |
| 维护与发布 | 两板型六 UF2、单光首次迁移、分段校准、温度报警、坏点、校验签名与问题收集 |
| 开发数据 | Thermal View v2、热像/可见光帧、设备照片格式、`.btpkg` v2、CSV/JSON/PNG/MP4 |

> 安全边界：本手册不公开激活算法、私钥、签名材料、生产测试流程或寄存器级危险写入。这些不是终端用户可安全操作的功能。

[返回项目首页](../../README.md) · [文档中心](../README.md) · [故障排查](../TROUBLESHOOTING.md)
