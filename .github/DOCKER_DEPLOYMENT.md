# Docker Hub 自动部署配置指南

本文档说明如何配置 GitHub Actions 自动构建和发布 Docker 镜像到 Docker Hub。

## 📋 前置要求

1. **Docker Hub 账号**
   - 如果没有账号，请访问 https://hub.docker.com/ 注册
   - 记住你的用户名（例如：`evil0ctal`）

2. **Docker Hub Access Token**
   - 登录 Docker Hub
   - 进入 **Account Settings → Security → Access Tokens**
   - 点击 **New Access Token**
   - 名称：`GitHub Actions`
   - 权限：`Read, Write, Delete`
   - 复制生成的 Token（只显示一次，请妥善保存）

## 🔐 配置 GitHub Secrets

### 步骤 1: 进入仓库设置

1. 打开你的 GitHub 仓库
2. 点击 **Settings** 标签
3. 在左侧菜单选择 **Secrets and variables → Actions**

### 步骤 2: 添加 Secrets

点击 **New repository secret** 按钮，添加以下两个 Secret：

#### Secret 1: DOCKERHUB_USERNAME

- **Name**: `DOCKERHUB_USERNAME`
- **Value**: 你的 Docker Hub 用户名（例如：`evil0ctal`）
- 点击 **Add secret**

#### Secret 2: DOCKERHUB_TOKEN

- **Name**: `DOCKERHUB_TOKEN`
- **Value**: 从 Docker Hub 复制的 Access Token
- 点击 **Add secret**

### 验证配置

完成后，你应该看到两个 Secrets：
```
✅ DOCKERHUB_USERNAME
✅ DOCKERHUB_TOKEN
```

## 🚀 工作流说明

### 触发条件

工作流会在以下情况自动运行：

1. **推送到主分支** (`main`)
   ```bash
   git push origin main
   ```

2. **推送到开发分支** (`develop`)
   ```bash
   git push origin develop
   ```

3. **推送版本标签** (例如 `v2.0.0`)
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   ```

4. **修改 API 服务代码** (`api-service/**`)
   - 任何对 `api-service` 目录下文件的修改

5. **手动触发**
   - 在 GitHub Actions 页面点击 "Run workflow"

### 生成的镜像标签

根据不同的触发条件，会生成不同的标签：

| 触发条件 | 生成的标签 | 示例 |
|---------|-----------|------|
| 推送到 `main` | `latest` | `evil0ctal/wechat-decrypt-api:latest` |
| 推送到 `main` | `main` | `evil0ctal/wechat-decrypt-api:main` |
| 推送到 `develop` | `develop` | `evil0ctal/wechat-decrypt-api:develop` |
| 版本标签 `v2.0.0` | `2.0.0`, `2.0`, `2`, `latest` | `evil0ctal/wechat-decrypt-api:2.0.0` |
| 提交 SHA | `main-abc1234` | `evil0ctal/wechat-decrypt-api:main-abc1234` |

### 支持的平台

工作流会构建多平台镜像：
- ✅ `linux/amd64` (x86_64 - Intel/AMD 处理器)
- ✅ `linux/arm64` (ARM64 - Apple Silicon, Raspberry Pi 4+)

## 📦 使用发布的镜像

### 拉取最新版本

```bash
docker pull evil0ctal/wechat-decrypt-api:latest
```

### 拉取特定版本

```bash
docker pull evil0ctal/wechat-decrypt-api:2.0.0
```

### 使用发布的镜像运行服务

```bash
# 直接运行
docker run -d \
  --name wechat-decrypt-api \
  -p 3000:3000 \
  evil0ctal/wechat-decrypt-api:latest

# 或使用 docker-compose.yml
```

更新 `api-service/docker-compose.yml`：

```yaml
version: '3.8'

services:
  wechat-decrypt-api:
    image: evil0ctal/wechat-decrypt-api:latest  # 使用 Docker Hub 镜像
    # image: wechat-decrypt-api:playwright      # 注释掉本地构建
    # build:
    #   context: .
    #   dockerfile: Dockerfile
    container_name: wechat-decrypt-api
    ports:
      - "3000:3000"
    # ... 其他配置保持不变
```

然后运行：

```bash
docker-compose pull  # 拉取最新镜像
docker-compose up -d # 启动服务
```

## 🔍 查看构建状态

### 方法 1: GitHub Actions 页面

1. 进入仓库的 **Actions** 标签
2. 选择 **Build and Push Docker Image** 工作流
3. 查看最近的运行记录

### 方法 2: README Badge

在 `README.md` 中添加状态徽章：

```markdown
[![Docker Image CI](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Evil0ctal/WeChat-Channels-Video-File-Decryption/actions/workflows/docker-image.yml)
```

### 方法 3: Docker Hub

访问 https://hub.docker.com/r/evil0ctal/wechat-decrypt-api 查看发布的镜像。

## 🐛 故障排除

### 问题 1: 认证失败

**错误信息**:
```
Error: failed to authorize: failed to fetch anonymous token
```

**解决方案**:
1. 检查 `DOCKERHUB_USERNAME` 是否正确
2. 检查 `DOCKERHUB_TOKEN` 是否有效
3. 确保 Token 权限包含 `Read, Write, Delete`
4. 重新生成 Token 并更新 Secret

### 问题 2: 推送失败 (权限问题)

**错误信息**:
```
Error: denied: requested access to the resource is denied
```

**解决方案**:
1. 确保仓库名称正确（`<username>/wechat-decrypt-api`）
2. 在 Docker Hub 创建仓库（如果不存在）
3. 检查 Token 权限

### 问题 3: 构建超时

**解决方案**:
- GitHub Actions 免费版有时间限制
- 考虑优化 Dockerfile（使用缓存、多阶段构建）
- 当前 Dockerfile 已优化，通常在 5-10 分钟内完成

### 问题 4: 多平台构建失败

**解决方案**:
- 某些平台可能构建失败（如 arm64）
- 可以临时移除有问题的平台：
  ```yaml
  platforms: linux/amd64  # 只构建 amd64
  ```

## 📝 工作流文件说明

工作流配置文件位于：`.github/workflows/docker-image.yml`

### 关键配置

1. **触发条件** (`on`)
   - 控制何时自动运行

2. **环境变量** (`env`)
   - `IMAGE_NAME`: Docker 镜像名称

3. **构建步骤** (`steps`)
   - Checkout 代码
   - 设置 QEMU（多平台支持）
   - 设置 Docker Buildx
   - 登录 Docker Hub
   - 提取元数据（标签）
   - 构建并推送镜像
   - 更新 Docker Hub 描述

4. **缓存** (`cache-from/cache-to`)
   - 使用 GitHub Actions 缓存加速构建

## 🎯 最佳实践

### 1. 版本标签

使用语义化版本标签：

```bash
# 主版本更新
git tag v3.0.0
git push origin v3.0.0

# 次版本更新
git tag v2.1.0
git push origin v2.1.0

# 修订版更新
git tag v2.0.1
git push origin v2.0.1
```

### 2. 开发流程

```bash
# 开发阶段：推送到 develop 分支
git checkout develop
git add .
git commit -m "feat: add new feature"
git push origin develop
# 生成镜像: wechat-decrypt-api:develop

# 准备发布：合并到 main 并打标签
git checkout main
git merge develop
git tag v2.1.0
git push origin main --tags
# 生成镜像: wechat-decrypt-api:latest, wechat-decrypt-api:2.1.0
```

### 3. 回滚到旧版本

```bash
# 拉取特定版本
docker pull evil0ctal/wechat-decrypt-api:2.0.0

# 更新 docker-compose.yml
# image: evil0ctal/wechat-decrypt-api:2.0.0

docker-compose up -d
```

## 🔒 安全建议

1. **永远不要** 在代码中硬编码 Token
2. **定期轮换** Docker Hub Access Token
3. **最小权限原则** - Token 只授予必要的权限
4. **审计日志** - 定期检查 Docker Hub 的访问日志
5. **私有镜像** - 如需私有，在 Docker Hub 设置仓库为 Private

## 📚 相关链接

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Hub 文档](https://docs.docker.com/docker-hub/)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [项目 README](../README.md)
- [API 服务文档](../api-service/README.md)

## ✅ 检查清单

部署前确保：

- [ ] Docker Hub 账号已创建
- [ ] Docker Hub Access Token 已生成
- [ ] GitHub Secrets 已配置（`DOCKERHUB_USERNAME` 和 `DOCKERHUB_TOKEN`）
- [ ] 工作流文件已提交到仓库
- [ ] 已测试触发工作流（推送代码或手动运行）
- [ ] 构建成功且镜像已发布到 Docker Hub
- [ ] 可以从 Docker Hub 拉取并运行镜像

---

**作者**: Evil0ctal
**更新时间**: 2025-10-17
**版本**: 1.0
