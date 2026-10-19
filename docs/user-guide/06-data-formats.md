# 协议与数据格式

适用于单光和双光。standard 只传热像，dual 另可提供可见光；先用 GetSysInfo 识别板型与能力，再用 thermal view 获取当前视图。MLX90641 原生 16×12，由固件上采样到 32×24 传输，不能把协议温度数量当成物理像素数量。

[上一章：高级设置](05-advanced-and-service.md) · [在线手册首页](README.md) · [完整串口协议](../STREAMING_PROTOCOL.md)

这一章说明“设备如何传、Studio 如何存、导出后还能做什么”。实现上位机时，应先读取 `thermal view`，再依据字段和实际帧长度解析，不能按 LCD 分辨率猜温度点数。

## 实时数据流

| 数据 | 帧结构 | 尺寸与说明 |
| --- | --- | --- |
| 视图描述 | `thermal view` → JSON v2 | 包含 `screen_mode`、热阵列宽高/点数、scale、偏移等解析依据 |
| 热像帧 | `BEGIN` + Tmax/Tmin/Tavg + 温度数组 + `END` | 统计值与温度均为 little-endian float32；MLX 768 点，Heimann 方屏 1024 点 |
| 可见光帧 | `VBEG` + width/height/length + RGB565 + `VEND` | 三个头字段为 little-endian uint32；全屏常见 120×160，方屏常见 120×120 |
| 保活 | 约 500 ms 心跳，约 1 s 超时 | 超时后 Studio 判断流中断并进入提示/重连流程 |

### 热像尺寸

| 视图 | `thermal_width × thermal_height` | `thermal_count` |
| --- | --- | --- |
| 全屏，MLX / Heimann | 32×24 | 768 |
| 方屏，MLX | 32×24 | 768 |
| 方屏，Heimann | 32×32 | 1024 |

320×240 / 240×240 是 LCD 显示尺寸，不是温度数组尺寸。详细字段与状态机见[双光串口推流协议](../STREAMING_PROTOCOL.md)。

## 设备照片下载

Studio 使用 `check` 获取列表，使用 `download <filename>` 获取十六进制数据，并以 `END FILE DATA` 判断传输结束。

| 格式 | 识别与内容 | Studio 处理 |
| --- | --- | --- |
| v1 Simple | Tmax、Tmin + 768 个 float32，共 3080 字节 | 32×24 纯热照片 |
| v1 Full | Tmax、Tmin、`full_screen` + 768/1024 个 float32 | 依据长度和屏幕标志兼容 MLX/Heimann |
| HTPH v2/v3 | `HTPH` 魔数、版本/flags、热像和可选 RGB565 | 保留双路与视图元数据；缺失字段使用兼容默认值 |
| JPEG | 文件头 `FF D8 FF` | 原样保存为 JPEG/JPG；无温度矩阵时不能重新测温 |

设备照片和 `.btpkg` 是两套格式：前者由固件存入 LittleFS，后者由 Studio 在本地创建。

## `.btpkg` v2

`.btpkg` 以 `BTPK` 开头，版本为 2，类型为 photo 或 video；后跟定长填充 JSON 元数据。每帧包含 `slotMask`、`tsMs`、可选 thermal float32 数组与 visible PNG，文件以 `BTPK_END` 结束。

```text
BTPK + version/type + padded JSON metadata
  ├─ frame 0: slotMask + tsMs + [thermal] + [visible PNG]
  ├─ frame 1: slotMask + tsMs + [thermal] + [visible PNG]
  └─ ...
BTPK_END
```

- `slotMask` 按帧记录热像/可见光是否存在，所以录像允许纯热、纯可见、双路和空帧动态切换。
- 色板、融合、标签等可以在回放时重新应用，不改写原始温度矩阵。
- 当前 v2 不承诺与早期实验性 v1 直接兼容；迁移前保留原文件，并用对应 Studio 版本验证。

## 导出格式怎么选

| 格式 | 保留内容 | 适合用途 | 能否重新测温 |
| --- | --- | --- | --- |
| `.btpkg` | 原始帧、时间戳、可用槽位、元数据 | Studio 回放、重新渲染、视频 | 有热像槽位时可以 |
| 设备 HTPH / 旧热照片 | 温度矩阵及可选可见光/视图字段 | 原始归档、兼容下载 | 有温度矩阵时可以 |
| JPEG / JPG | 像素图像 | 分享、普通查看 | 通常不可以 |
| PNG | 当前渲染、融合、统计和标签 | 报告、截图 | 不可以，只能看已烘焙数值 |
| MP4 | 逐帧渲染后的视频 | 演示、分享 | 不可以 |
| CSV | 完整趋势原始记录 | Excel / Python 分析 | 可分析记录，不能恢复热矩阵 |
| JSON | 时间戳、设备信息、坐标和测温点 | 系统集成、历史导入 | 可恢复趋势会话，不等于热矩阵 |

## 兼容实现建议

1. 连接后先请求 `thermal view`，并保存协议版本与热阵列尺寸。
2. 用魔数、长度、结束标记和合理数值范围共同校验，不只依赖固定字节数。
3. 解析 RGB565 时按 little-endian 读取，并分别处理全屏 120×160 与方屏 120×120。
4. 保留未知 JSON 字段；新版本增加字段时不要直接判错。
5. 热像流、可见光流和照片下载共用串口时做互斥，避免命令与二进制帧交叉。
6. 对 768/1024 点、旧照片、HTPH、JPEG、缺槽位和空帧建立回归测试。

固件与 Studio 的版本组合见[兼容性说明](../COMPATIBILITY.md)，传感器尺寸背景见[传感器与显示模式](../SENSORS_AND_DISPLAY.md)。
