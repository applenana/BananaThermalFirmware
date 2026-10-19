# 兼容性说明

## 推荐组合

建议始终使用最新正式固件和最新版 [NextBananaThermalStudio](https://github.com/applenana/NextBananaThermalStudio/releases)。

新上位机负责兼容新旧固件；新固件面向最新版上位机设计，不保证旧上位机能够理解方屏 Heimann `32 × 32`、动态可见光尺寸或 Thermal View v2。

## 板型与设备能力

| 设备版本 | 行为 |
| --- | --- |
| 历史统一 v1.7.x | 三个历史 UF2，只用于原双光板型 |
| 旧单光 v2.2 | 独立历史版本线；新版 Studio 提供迁移提示 |
| 统一 v1.8.0 起 standard | 2.4 / 2.8 / 3.2 寸单光，共用同板型容量变体；首次迁移重建存储 |
| 统一 v1.8.0 起 dual | 双光板型，各容量独立；不可刷 standard |

通过 `GetSysInfo` 读取 `hardwareProfile`、`firmwareVariant` 与 `capabilities`，不要从屏幕尺寸、热传感器名称或 Thermal View 中的预期可见光尺寸推断是否有摄像头。standard 的 `capabilities.camera`、`capabilities.distance`、`capabilities.key2` 为 false；Studio 应隐藏双光操作并只开启热流。dual 的编译能力为 true 也不保证可选模块已安装或初始化成功，仍需结合运行状态。

本次文档按 Studio 0.5.5 源码核对，实际应安装支持 schema v2、单光能力识别及迁移流程的正式版本。温度报警和分段校准还需分别按对应协议能力判断，不能只因有 Thermal View v2 就认为全部支持。

## 协商策略

上位机开启热流前发送：

```text
thermal view\n
```

若收到合法 JSON，应按返回的传感器、屏幕模式、尺寸、缩放、偏移和旋转解析后续热帧。

若设备没有响应，按旧协议回退：

- 热流 `32 × 24`；
- 768 个 little-endian float32；
- 使用旧版默认显示参数；
- 不假定存在动态方屏复原信息。

## 兼容矩阵

| 固件能力 | 最新上位机行为 |
| --- | --- |
| 不响应 `thermal view` | 回退到旧版 `32 × 24 / 768` |
| Thermal View v1 | 读取基本尺寸与几何参数 |
| Thermal View v2 | 同时读取传感器、屏幕模式、可见光尺寸、旋转和热流尺寸 |
| 方屏 MLX | 接收 `32 × 24` 并在上位机复原逻辑 `32 × 32` |
| 方屏 Heimann | 接收真实 `32 × 32` |
| 动态 VBEG | 始终按帧头 `width / height / length` 解析 |

## 模式切换

投屏期间从全屏切换到方屏，或从方屏切回全屏时：

单光仅需更新热像上下文；下面等待可见光帧与 VBEG 的步骤适用于双光。

1. 设备等待新的可见光帧形状稳定；
2. Thermal View 上下文发生变化；
3. 设备先发送新的 JSON；
4. 再发送与新上下文匹配的热帧；
5. 可见光帧通过自身帧头声明新尺寸。

上位机不能继续沿用上一个模式的热流高度、缩放和偏移。
