# 发布完整性与签名

## 为什么同时需要哈希和签名

SHA-256 可以发现文件损坏，但来源不明的人也可以为被替换的文件重新生成 SHA-256。Ed25519 签名进一步证明 `SHA256SUMS` 来自官方发布密钥。

每个 Release 应包含：

| 文件 | 用途 |
| --- | --- |
| `*.uf2` | 可刷写固件 |
| `manifest.json` | 版本、构建环境、大小和哈希 |
| `SHA256SUMS` | 附件 SHA-256 |
| `SHA256SUMS.sig` | 对 `SHA256SUMS` 的 Ed25519 SSH 签名 |
| `firmware-release-allowed-signers` | OpenSSH 允许签名身份 |

## Linux / macOS 校验

```bash
sha256sum -c SHA256SUMS
ssh-keygen -Y verify \
  -f firmware-release-allowed-signers \
  -I banana-thermal-firmware \
  -n file \
  -s SHA256SUMS.sig < SHA256SUMS
```

任意 UF2 哈希失败或签名失败都应停止刷写。

## Windows PowerShell 校验

```powershell
Get-FileHash -Algorithm SHA256 .\*.uf2
Get-Content .\SHA256SUMS -Raw | ssh-keygen -Y verify `
  -f .\firmware-release-allowed-signers `
  -I banana-thermal-firmware `
  -n file `
  -s .\SHA256SUMS.sig
```

`Get-FileHash` 的结果应与 `SHA256SUMS` 对应行一致。

## 固定公开签名身份

仓库内的验证文件位于 [`keys/firmware-release-allowed-signers`](../keys/firmware-release-allowed-signers)。

首次可信获取后，可以把它保存到独立位置。后续版本同时对比本地副本和 Release 附件，可以降低仓库账号被入侵后公钥一起被替换的风险。

## 构建隔离

- 构建以版本 Tag 为输入，不从任意分支发布；
- 三个变体必须全部成功；
- 发布目录只接受 UF2、JSON、哈希、签名和公开验证身份；
- `.elf`、`.map`、`.bin`、缓存、源码和完整构建目录不会进入 Release；
- 正式发布后附件不可修改。

这些措施证明发布来源和文件完整性，但不能阻止固件二进制被逆向分析，也不能替代设备端安全启动。
