# 自动发布安全概览

面向用户的固件真实性、附件白名单、哈希与签名验证说明已经迁移到：

[发布完整性与签名](RELEASE_INTEGRITY.md)

安全问题请不要在公开 Issue 中披露，报告方式见：

[安全策略](../SECURITY.md)

构建器不会把私有编译器输出写入公开日志。仅当构建失败时，诊断日志才会使用专用 RSA 证书与 AES-256 内容加密封装成 CMS 密文，并作为保留 1 天的 Artifact 保存。解密私钥只以 Windows DPAPI 加密形式保存在维护者本机，不存放于仓库、GitHub Secret、Runner 或 Artifact 中。
