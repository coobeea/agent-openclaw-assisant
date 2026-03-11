# 凭证管理

## 加密机制

使用 Fernet 对称加密算法。

### 密钥存储

密钥文件: `workspace/.keyfile`
- 自动生成
- 权限: 600（仅所有者可读写）
- 不提交到 Git

## 加密流程

```
明文凭证
  ↓
Fernet 加密
  ↓
Base64 编码
  ↓
存储到配置
```

## 使用加密工具

### 加密

```bash
python scripts/credential_encrypt.py encrypt "my-secret"
```

### 解密

```bash
python scripts/credential_encrypt.py decrypt "<encrypted-text>"
```

## 安全最佳实践

1. 定期轮换凭证
2. 使用独立的测试凭证
3. 备份密钥文件
4. 限制密钥文件访问权限
