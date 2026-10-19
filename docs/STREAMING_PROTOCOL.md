# 单光与双光串口推流协议

协议运行在 USB CDC 字节流上。热成像帧、可见光帧和以换行结尾的 JSON 文本可以交织出现，上位机解析器必须按 magic 分帧。

standard 单光只提供热流，dual 另可提供可见光；不要向单光持续请求 vstream。先用 `GetSysInfo` 识别板型和能力，再用 `thermal view` 获取几何上下文。

## 设备身份与能力

新版 `GetSysInfo` 包含 `firmwareVersion`、`deviceModel`、`hardwareProfile`、`firmwareVariant`、`flashSizeBytes`、`cpuFrequencyHz` 与 `capabilities`。标准单光返回 `hardwareProfile=standard`、`deviceModel=HEIMAN-NSP-STANDARD`，其 `capabilities.camera`、`capabilities.distance` 和 `capabilities.key2` 均为 false。双光返回 dual，其编译能力不代表可选模块实际初始化成功。

只提取排障需要的字段，不把完整回显中的序列号和激活信息直接发布。旧单光可能没有这些新字段，应由新版 Studio 的历史身份识别和迁移流程处理。Thermal View 的 visible_width/height 是几何字段，不能据此推断存在摄像头。

全部整数和 float 均为 little-endian。float 使用 IEEE 754 float32。

## 命令与保活

| 命令 | 功能 |
| --- | --- |
| `thermal view\n` | 查询当前传感器、屏幕模式、尺寸和几何参数 |
| `stream\n` | 开启或续期热成像流 |
| `vstream\n` | 开启或续期可见光流 |
| `streaming stoped\n` | 停止热成像流 |
| `vstream stoped\n` | 停止可见光流 |

推流命令也是保活心跳。上位机建议每 500 ms 重发一次；超过约 1 秒未收到保活时设备会自动停止对应流。

## Thermal View v2

示例：

```json
{
  "type": "thermal_view",
  "version": 2,
  "sensor": "mlx90640",
  "screen_mode": "square",
  "visible_width": 120,
  "visible_height": 120,
  "thermal_width": 32,
  "thermal_height": 24,
  "thermal_count": 768,
  "display_width": 240,
  "display_height": 240,
  "x_offset": 0,
  "y_offset": 0,
  "scale": 1.3,
  "sensor_rotate180": true
}
```

| 字段 | 含义 |
| --- | --- |
| `sensor` | `mlx90640`、`mlx90641`、`heimann_htpa32x32` 或 `unknown` |
| `screen_mode` | `fullscreen` 或 `square` |
| `visible_width/height` | 当前可见光预期尺寸；实际仍以每个 VBEG 帧头为准 |
| `thermal_width/height/count` | 后续 BEGIN 热帧 payload 的真实形状 |
| `display_width/height` | 设备显示坐标空间 |
| `x_offset/y_offset/scale` | 当前屏幕模式的热像几何参数 |
| `sensor_rotate180` | 传感器方向 |

传感器、屏幕模式、缩放、偏移或旋转变化后，设备会在下一张热帧前重新发送 Thermal View JSON。

## 热成像帧

```text
"BEGIN"
+ max_temperature     : float32 LE
+ min_temperature     : float32 LE
+ average_temperature : float32 LE
+ temperature[thermal_count] : float32 LE
+ "END"
```

总长度：

```text
5 + 12 + thermal_count × 4 + 3
```

尺寸由最近一次合法 Thermal View 响应确定。旧设备没有响应时固定使用 `thermal_count = 768`。新上位机应从温度数组重算统计值；帧头三个统计字段用于维持旧协议结构。

## 可见光帧

本节只适用于支持摄像头的双光设备。单光的温度数组与热流外壳仍遵循前面的规则。

```text
"VBEG"
+ width  : uint32 LE
+ height : uint32 LE
+ length : uint32 LE
+ rgb565[length]
+ "VEND"
```

约束：

```text
length == width × height × 2
```

RGB565 为 little-endian、行优先：

```text
pixel_index = row × width + column
```

当前标准尺寸：

- 全屏：`120 × 160`；
- 方屏：`120 × 120`。

解析器必须读取每帧尺寸，不能写死长度。

## 流解析建议

1. 在缓冲区查找最早出现的 `BEGIN` 或 `VBEG`；
2. 把 magic 之前以换行结尾的内容交给文本/JSON解析器；
3. 按当前 Thermal View 计算热帧长度，或读取 VBEG 的三个 uint32；
4. 对尺寸和长度设置上限，防止损坏帧导致无限等待或超大分配；
5. 验证 `END` / `VEND`；
6. 帧不完整时保留可能构成 magic 前缀的末尾字节；
7. 帧尾错误时丢弃一个字节并重新同步，而不是清空全部缓冲。

## 建议的安全上限

- 热流只接受 `32 × 24` 或 `32 × 32`；
- `thermal_count` 只接受 768 或 1024；
- 可见光只接受协议约定的 `120 × 160` 或 `120 × 120`；
- `length` 必须等于 `width × height × 2`；
- 未协商状态下只接受传统 768 点热帧。

## 温度校准协议

兼容单直线接口为 `calibration get`、`calibration set <gain> <offset>` 与 `calibration reset`。gain 限制 0.5 至 1.5，offset 限制 -100 至 100 °C；以响应和回读确认是否持久化。

新固件还提供 `calibration2 get/begin/chunk/commit/abort/reset`，用事务、分块数据和 CRC 管理最多 128 段的连续曲线。客户端需先协商能力，旧 `calibration get` 不能替代完整曲线读取。推荐由新版 Studio 完成曲线传输，详细用户操作见[温度校准](menu/04-temperature-calibration.md)。

## 温度报警与其他记录

报警事件以 `!A,1,H,1,+0850` 加 LF 等 ASCII 行发送，与图像和图库记录交织。二进制帧内部按长度读取，不能在载荷中搜索文本魔数；记录边界处独立处理报警行。单光与双光使用相同事件规则。

配置入口为 `alarm get/set/ack/defaults`。状态判断、迟滞、确认与断连语义见[温度报警](menu/17-temperature-alarm.md)，精确配置字段和测试向量见 [Studio 报警协议](https://github.com/applenana/NextBananaThermalStudio/blob/main/docs/protocol_temperature_alarm.md)。
