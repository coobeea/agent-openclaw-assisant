# OpenClaw 安装指南

## 安装方式选择

OpenClaw 支持多种安装方式，脚本会自动选择最佳方式。

### 方式 1: npm/yarn/pnpm（推荐）

```bash
# npm
npm install -g openclaw

# yarn
yarn global add openclaw

# pnpm
pnpm add -g openclaw
```

### 方式 2: 官方二进制包

从 GitHub Releases 下载对应平台的二进制包。

### 方式 3: 源码编译

在官方包不可用时使用。

---

## 使用安装脚本

### 自动安装

```bash
bash scripts/install_openclaw.sh
```

脚本会：
1. 检测系统环境（Node.js、包管理器）
2. 选择最佳安装方式
3. 安装 OpenClaw
4. 验证安装成功

### 指定版本

```bash
bash scripts/install_openclaw.sh 2026.3.8
```

### 检查安装

```bash
openclaw --version
openclaw --help
```

---

## 安装脚本工作流程

```
开始
  ↓
检测 npm/yarn/pnpm
  ↓
是否可用？
  ├─ 是 → 使用包管理器安装
  └─ 否 → 提示安装 Node.js
  ↓
验证安装
  ↓
输出版本信息
  ↓
完成
```

---

## 故障排查

### npm: command not found

安装 Node.js: https://nodejs.org/

### 权限错误

```bash
# 使用 sudo（不推荐）
sudo npm install -g openclaw

# 或配置 npm 全局目录（推荐）
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

### 版本冲突

```bash
# 卸载旧版本
npm uninstall -g openclaw

# 安装新版本
npm install -g openclaw@2026.3.8
```
