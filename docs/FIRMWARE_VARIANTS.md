# 固件变体说明

从 v1.8.0 开始，一个版本提供六个 UF2。先按硬件板型选择 `dual`（双光热成像）或 `standard`（普通热成像），再选择 Flash 容量与运行配置；屏幕尺寸不决定固件变体。

“普通热成像”与“单光热成像”是同一板型。2.4 / 2.8 / 3.2 寸单光在 Flash 与运行配置相同时共用 standard 固件，不为每个屏幕单独发布。3.2 寸双光仍使用 dual。型号、输入与硬件能力见[设备对照](devices/README.md)。

| 环境名 | 板型 | Flash / LittleFS | CPU | 用途 |
| --- | --- | --- | --- | --- |
| `dual_sketch3m_fs5m` | dual | 8 MB / 5 MB | 300 MHz | 双光默认性能版 |
| `dual_sketch3m_fs5m_stable` | dual | 8 MB / 5 MB | 220 MHz | 双光 OV3660 稳定时序 |
| `dual_sketch1m_fs1m` | dual | 2 MB / 1 MB | 300 MHz | 双光小容量版 |
| `standard_sketch3m_fs5m` | standard | 8 MB / 5 MB | 300 MHz | 普通热成像默认版 |
| `standard_sketch3m_fs5m_stable` | standard | 8 MB / 5 MB | 220 MHz | 普通热成像降频稳定版 |
| `standard_sketch1m_fs1m` | standard | 2 MB / 1 MB | 300 MHz | 普通热成像小容量版 |

文件名为 `banana-thermal-VERSION-环境名.uf2`。v1.7.x 及更早 Release 继续保留三个历史文件名，并由 manifest schema v1 描述。

普通热成像首次迁移到统一固件时会格式化 LittleFS，清除旧配置、校准和照片；仅在旧分区可挂载且激活信息有效时尝试恢复激活。切换 2 MB / 8 MB 分区前必须备份，跨分区时可能需要重新激活。

不要跨 `dual` / `standard` 板型刷写，也不要根据 UF2 文件大小猜测板型或 Flash 容量。推荐使用支持 manifest schema v2 的最新版 NextBananaThermalStudio。

新版 Studio 根据设备身份锁定板型。旧单光迁移期间可在 standard 的容量变体间选择，这只是提供迁移路径，不代表设备 Flash 容量可以随意改变。旧 v2.2 是历史单光版本线，统一 v1.8.0 是其迁移目标之一，不能只按版本数字判断降级。
