# 🚀 快速部署指南

本指南将帮助您在 5 分钟内将 DeepSeek Tokenizer Web Tool 部署到云端。

## 📋 部署前准备

您需要：
- 一个 GitHub 账号
- 5 分钟时间

## 🎯 推荐方案：Railway（最简单）

### 步骤 1：Fork 仓库（可选）

如果您想自定义代码，可以先 Fork 这个仓库到您的 GitHub 账号。

### 步骤 2：访问 Railway

打开 https://railway.app/

### 步骤 3：登录

点击 "Sign in"，使用 GitHub 账号登录。

### 步骤 4：创建新项目

1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 授权 Railway 访问您的 GitHub
4. 选择 `deepseek-tokenizer-web` 仓库

### 步骤 5：配置部署

Railway 会自动检测项目配置，您只需：

1. 等待构建完成（约 2-3 分钟）
2. 点击生成的服务
3. 进入 "Settings" 标签
4. 找到 "Domains" 部分
5. 点击 "Generate Domain" 生成公开访问地址

### 步骤 6：访问应用

复制生成的域名（例如：`deepseek-tokenizer.railway.app`），在浏览器中打开即可使用！

## 🎨 方案 2：Render（完全免费）

### 步骤 1：访问 Render

打开 https://render.com/

### 步骤 2：登录

使用 GitHub 账号登录。

### 步骤 3：创建 Blueprint

1. 点击 "New" → "Blueprint"
2. 连接 GitHub 仓库
3. 选择 `deepseek-tokenizer-web`
4. Render 会自动读取 `render.yaml` 配置
5. 点击 "Apply"

### 步骤 4：等待部署

- 后端服务部署时间：约 3-5 分钟
- 前端服务部署时间：约 2-3 分钟

### 步骤 5：访问应用

部署完成后，Render 会提供一个 `.onrender.com` 域名，点击即可访问。

**注意**：Render 免费版会在 15 分钟不活动后休眠，首次访问需要等待约 30 秒唤醒。

## 🔧 方案 3：使用 Railway CLI（适合开发者）

### 步骤 1：安装 Railway CLI

```bash
npm install -g @railway/cli
```

或使用 Homebrew（macOS）：

```bash
brew install railway
```

### 步骤 2：登录

```bash
railway login
```

这会打开浏览器进行 GitHub 授权。

### 步骤 3：初始化项目

```bash
cd deepseek-tokenizer-web
railway init
```

选择 "Create a new project"，输入项目名称。

### 步骤 4：部署

```bash
railway up
```

### 步骤 5：生成域名

```bash
railway domain
```

选择自动生成的域名或绑定自定义域名。

### 步骤 6：查看日志

```bash
railway logs
```

## 🐳 方案 4：Docker 自托管

如果您有自己的服务器（VPS），可以使用 Docker 部署。

### 步骤 1：克隆仓库

```bash
git clone https://github.com/zihaoli-cn/deepseek-tokenizer-web.git
cd deepseek-tokenizer-web
```

### 步骤 2：构建前端

```bash
cd frontend
npm install -g pnpm
pnpm install
pnpm run build
cd ..
```

### 步骤 3：启动服务

```bash
docker-compose up -d
```

### 步骤 4：访问应用

打开 `http://your-server-ip`

## 📊 部署方案对比

| 方案 | 免费额度 | 部署难度 | 启动速度 | 推荐度 |
|------|---------|---------|---------|--------|
| Railway | $5/月 | ⭐ | 快 | ⭐⭐⭐⭐⭐ |
| Render | 750小时/月 | ⭐⭐ | 慢（冷启动） | ⭐⭐⭐⭐ |
| Railway CLI | $5/月 | ⭐⭐⭐ | 快 | ⭐⭐⭐ |
| Docker 自托管 | 取决于服务器 | ⭐⭐⭐⭐ | 快 | ⭐⭐⭐⭐ |

## ❓ 常见问题

### Q: 部署后无法访问？

A: 检查以下几点：
1. 确认部署已完成（查看日志）
2. 确认域名已生成
3. 等待 DNS 传播（可能需要几分钟）
4. 检查防火墙设置

### Q: Railway 免费额度够用吗？

A: Railway 提供 $5/月的免费额度，对于小型应用完全够用。通常一个月可以运行约 500 小时。

### Q: Render 为什么这么慢？

A: Render 免费版会在不活动后休眠，首次访问需要唤醒服务（约 30 秒）。付费版本没有这个问题。

### Q: 可以绑定自定义域名吗？

A: 可以！Railway 和 Render 都支持绑定自定义域名，在项目设置中配置即可。

### Q: 如何更新部署的应用？

A: 
- Railway/Render：推送代码到 GitHub，会自动重新部署
- Docker：拉取最新代码后重新运行 `docker-compose up -d --build`

### Q: 部署失败怎么办？

A: 
1. 查看部署日志找到错误信息
2. 检查 Python 版本是否为 3.11+
3. 确认所有依赖都在 requirements.txt 中
4. 在 GitHub Issues 中提问：https://github.com/zihaoli-cn/deepseek-tokenizer-web/issues

## 🎉 部署成功！

恭喜！您的 DeepSeek Tokenizer Web Tool 已经成功部署到云端。

现在您可以：
- 分享链接给朋友使用
- 在项目中集成 API
- 自定义界面和功能
- 绑定自定义域名

## 📞 需要帮助？

- 查看详细文档：[DEPLOYMENT.md](./DEPLOYMENT.md)
- 提交 Issue：https://github.com/zihaoli-cn/deepseek-tokenizer-web/issues
- 查看 Railway 文档：https://docs.railway.app/
- 查看 Render 文档：https://render.com/docs
