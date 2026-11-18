# 星像 StarThermal 发布

星像固件与原单光／双光固件共用分发仓库，使用独立版本线、构建工作流及签名身份。

- 私有源码正式 Tag：`vMAJOR.MINOR.PATCH`。
- 公开 Release：`StarThermal-vMAJOR.MINOR.PATCH`，不设置为仓库 Latest。
- 每小时第 37 分钟检查一次；手动运行默认 `check_only`，只检查 Tag 和 Release 状态。
- 每次处理一个尚未发布的版本；仅草稿可恢复上传，已公开版本不能覆盖。

## 配置

`starthermal-build` Environment 只允许 main 分支。Secrets 为 `STARTHERMAL_SOURCE_REPOSITORY` 和 `STARTHERMAL_READ_KEY`，后者对应上游只读 Deploy Key。源码地址不放在公开变量、代码或日志中。沿用公开 SSH 主机身份变量 `UPSTREAM_SSH_KNOWN_HOSTS`。

`starthermal-release` Environment 只允许 main 分支，Secret 为 `STARTHERMAL_SIGNING_KEY`。可通过仓库变量 `STARTHERMAL_MINIMUM_TAG` 调整最低版本，默认 `v0.1.0`。

私有源码必须包含 `tools/build_release.py`，读取 `STARTHERMAL_VERSION` 并生成可互相核对的 BIN/UF2。版本和产品身份必须写入镜像；缺少发布适配的历史 Tag 将失败，不会静默发布默认版本。

## 发布包

每个 Release 只包含 `StarThermal-vX.Y.Z.bin`、`StarThermal-vX.Y.Z.uf2`、`manifest.json`、`SHA256SUMS`、`SHA256SUMS.sig` 和 `starthermal-allowed-signers`。

schema v3 固定 `product_id=starthermal`、`device_model=StarThermal`；OTA BIN 使用 `serial-ota-v1`，恢复 UF2 使用 `rp2040-uf2`。设备硬件标识为 `starthermal-rp2040-8m`。旧单光／双光继续使用原 schema v1/v2，不能把星像作为原矩阵的额外变体。

公开名称及说明使用“星像 StarThermal”。不发布私有源码地址、环境名称、编译日志、源码、ELF、MAP 或完整构建目录。源码提交只公开哈希的摘要。

## 诊断与恢复

失败日志使用 `keys/starthermal-diagnostics-cert.pem` 加密，仅上传 CMS 密文并保留一天。诊断解密私钥保存在私有源码仓库的非版本标签 `starthermal-diagnostics-key`，随附跨电脑恢复说明。有私有仓库读取权限的账号可按此标签检出密钥。该标签不触发固件发布；密钥不在固件 main 或版本标签中，也不保存到公开仓库或构建 Runner。

传输源码使用 SSH 加密；固件以可直接使用的 BIN/UF2 分发，并使用独立 Ed25519 发布密钥签名。诊断密钥和发布签名密钥用途不同。

## 客户端兼容

已检查的原 Studio 版本解析器会忽略 `StarThermal-` 前缀。新版 Studio 必须先按产品过滤，再按数字版本排序，支持分页，并在写入前验证固定公钥签名及硬件身份。不能把仓库 Latest 作为星像的最新版。
