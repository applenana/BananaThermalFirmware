# 固件变体说明

同一个版本提供三个固件变体，它们使用相同功能代码，但 Flash 分区和运行频率不同。

## 8 MB 正常版

```text
banana-thermal-VERSION-sketch3m_fs5m.uf2
```

- 最大 Flash：8 MB；
- 程序区域：约 3 MB；
- LittleFS：约 5 MB；
- CPU：300 MHz；
- 摄像头时序偏向性能。

这是 8 MB 设备的默认选择。

## 8 MB 稳定版

```text
banana-thermal-VERSION-sketch3m_fs5m_stable.uf2
```

- 最大 Flash：8 MB；
- 程序区域：约 3 MB；
- LittleFS：约 5 MB；
- CPU：220 MHz；
- 摄像头时序偏向稳定。

当正常版出现随机重启、可见光竖纹、长时间融合不稳定或个体硬件无法稳定高频运行时，优先测试稳定版。

## 2 MB 兼容版

```text
banana-thermal-VERSION-sketch1m_fs1m.uf2
```

- Flash：2 MB；
- LittleFS：约 1 MB；
- 面向旧款或小容量硬件。

空间较小会限制可保存照片、配置和后续功能增长。

## 不要这样选择

- 不要因为某个 UF2 文件更小就认为它适合 2 MB 设备；
- 不要把 8 MB 分区固件刷入无法确认容量的旧设备；
- 不要在没有备份时切换 8 MB 与 2 MB 分区方案；
- 不要用设备能否短暂启动作为文件系统兼容的唯一依据。
