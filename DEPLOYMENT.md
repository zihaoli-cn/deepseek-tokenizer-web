# 部署指南

本项目支持多种部署方式，您可以根据需求选择合适的部署平台。

## 部署选项

### 选项 1: Railway（推荐 - 最简单）

Railway 提供免费额度，支持 Docker 部署，配置简单。

#### 步骤：

1. 访问 [Railway.app](https://railway.app/)
2. 使用 GitHub 账号登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择 `deepseek-tokenizer-web` 仓库
5. Railway 会自动检测并部署应用
6. 等待部署完成，获取访问地址

**优点**：
- 免费额度充足
- 自动 HTTPS
- 支持 Docker
- 部署简单

### 选项 2: Render

Render 提供免费的 Web 服务，适合小型应用。

#### 步骤：

1. 访问 [Render.com](https://render.com/)
2. 使用 GitHub 账号登录
3. 点击 "New" → "Blueprint"
4. 连接 `deepseek-tokenizer-web` 仓库
5. Render 会自动读取 `render.yaml` 配置
6. 点击 "Apply" 开始部署

**优点**：
- 完全免费
- 自动 HTTPS
- 支持多服务部署
- 配置灵活

**注意**：免费版服务会在 15 分钟不活动后休眠，首次访问需要等待唤醒（约 30 秒）。

### 选项 3: Vercel + Railway

前端部署到 Vercel，后端部署到 Railway。

#### 后端部署（Railway）：

1. 访问 [Railway.app](https://railway.app/)
2. 创建新项目，选择 `deepseek-tokenizer-web` 仓库
3. 设置根目录为 `backend`
4. 获取后端 URL（例如：`https://xxx.railway.app`）

#### 前端部署（Vercel）：

1. 访问 [Vercel.com](https://vercel.com/)
2. 导入 `deepseek-tokenizer-web` 仓库
3. 设置构建配置：
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `pnpm run build`
   - Output Directory: `dist`
4. 添加环境变量：
   - `VITE_API_URL`: 后端 Railway URL
5. 部署

**优点**：
- Vercel 前端性能极佳
- Railway 后端稳定
- 分离部署更灵活

### 选项 4: Docker 自托管

如果您有自己的服务器（VPS），可以使用 Docker Compose 部署。

#### 前置要求：
- Docker
- Docker Compose

#### 步骤：

1. 克隆仓库到服务器：
```bash
git clone https://github.com/zihaoli-cn/deepseek-tokenizer-web.git
cd deepseek-tokenizer-web
```

2. 构建前端：
```bash
cd frontend
pnpm install
pnpm run build
cd ..
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 访问：`http://your-server-ip`

**优点**：
- 完全控制
- 无限制
- 性能最佳

### 选项 5: Hugging Face Spaces

适合 AI/ML 项目展示。

#### 步骤：

1. 访问 [Hugging Face Spaces](https://huggingface.co/spaces)
2. 创建新 Space，选择 Docker 模板
3. 上传代码或连接 GitHub 仓库
4. 配置 Dockerfile
5. 部署

**优点**：
- AI 社区友好
- 免费额度
- 易于分享

## 推荐部署方案

### 快速测试：Railway
- 一键部署，无需配置
- 适合快速验证和演示

### 长期使用：Vercel + Railway
- 前端性能最优
- 后端稳定可靠
- 免费额度充足

### 生产环境：Docker 自托管
- 完全控制
- 性能最佳
- 适合企业使用

## 环境变量配置

### 后端环境变量
- `PORT`: 服务端口（默认 8000）

### 前端环境变量
- `VITE_API_URL`: 后端 API 地址（如果前后端分离部署）

## 域名配置

部署完成后，您可以：
1. 使用平台提供的默认域名
2. 绑定自定义域名（需要在平台设置中配置）

## 故障排查

### 后端无法启动
- 检查 Python 版本是否为 3.11+
- 检查依赖是否正确安装
- 查看日志文件

### 前端无法访问后端
- 检查 API 代理配置
- 检查 CORS 设置
- 确认后端服务正常运行

### 流式输出不工作
- 检查 Nginx 配置中的 `proxy_buffering off`
- 确认使用了支持 SSE 的部署平台

## 成本估算

### 免费方案
- Railway: 500 小时/月（约 $5 免费额度）
- Render: 750 小时/月
- Vercel: 100 GB 带宽/月

### 付费方案
- Railway: $5/月起
- Render: $7/月起
- VPS: $5-20/月

## 技术支持

如有问题，请在 GitHub 仓库提交 Issue：
https://github.com/zihaoli-cn/deepseek-tokenizer-web/issues
