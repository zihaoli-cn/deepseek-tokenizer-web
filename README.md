# DeepSeek Tokenizer Web Tool

一个基于 FastAPI 和 Vue.js 3 的 Web 应用，用于分析和模拟 DeepSeek tokenizer 的行为。

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deepseek-tokenizer)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🚀 一键部署

### 方案 1: Railway（推荐）

1. 点击上方 "Deploy on Railway" 按钮
2. 使用 GitHub 账号登录
3. 授权访问仓库
4. 等待自动部署完成
5. 获取访问地址

**优点**：
- 完全免费（$5 月度额度）
- 自动 HTTPS
- 部署速度快
- 支持 Docker

### 方案 2: Render

1. 点击上方 "Deploy to Render" 按钮
2. 使用 GitHub 账号登录
3. Render 会自动读取 `render.yaml` 配置
4. 点击 "Apply" 开始部署
5. 等待部署完成

**优点**：
- 完全免费
- 自动 HTTPS
- 配置简单

**注意**：免费版服务会在 15 分钟不活动后休眠。

### 方案 3: 手动部署到 Railway

```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
cd deepseek-tokenizer-web
railway init

# 部署
railway up
```

## 功能特性

- **Token 计数**：计算输入文本的 token 数量
- **模拟输出**：按指定速度（tokens/秒）流式输出文本，模拟大模型回答
- **中英文界面**：支持中英文界面切换
- **实时进度**：显示输出进度、当前 token 数和总 token 数
- **简洁美观**：左右分栏布局，界面简洁直观

## 技术栈

### 后端
- FastAPI - 现代化的 Python Web 框架
- Transformers - Hugging Face 的 tokenizer 库
- Uvicorn - ASGI 服务器

### 前端
- Vue.js 3 - 渐进式 JavaScript 框架
- Element Plus - Vue 3 组件库
- Vite - 下一代前端构建工具
- Vue I18n - 国际化支持

## 项目结构

```
deepseek-tokenizer-web/
├── backend/                 # 后端代码
│   ├── tokenizer/          # DeepSeek tokenizer 文件
│   ├── main.py             # FastAPI 主文件
│   ├── requirements.txt    # Python 依赖
│   └── Dockerfile          # Docker 配置
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── locales/        # 国际化语言文件
│   │   ├── App.vue         # 主组件
│   │   └── main.js         # 入口文件
│   ├── index.html          # HTML 模板
│   ├── vite.config.js      # Vite 配置
│   └── package.json        # 前端依赖
├── docker-compose.yml      # Docker Compose 配置
├── render.yaml             # Render 部署配置
├── nginx.conf              # Nginx 配置
├── DEPLOYMENT.md           # 详细部署指南
└── README.md               # 项目说明
```

## 本地开发

### 前置要求

- Python 3.11+
- Node.js 22+
- pnpm

### 安装依赖

#### 后端
```bash
cd backend
pip install -r requirements.txt
```

#### 前端
```bash
cd frontend
pnpm install
```

### 运行项目

#### 启动后端
```bash
cd backend
python main.py
```

后端将在 http://localhost:8000 运行

#### 启动前端
```bash
cd frontend
pnpm run dev
```

前端将在 http://localhost:5173 运行

### 访问应用

在浏览器中打开 http://localhost:5173

## API 接口

### 计算 Token 数量
```http
POST /count_tokens
Content-Type: application/json

{
  "text": "要分析的文本"
}
```

**响应示例**：
```json
{
  "text": "Hello, 你好世界!",
  "token_count": 6,
  "tokens": [19923, 14, 223, 30594, 3427, 3]
}
```

### 模拟流式输出
```http
POST /stream_text
Content-Type: application/json

{
  "text": "要输出的文本",
  "tokens_per_second": 50
}
```

**响应格式**：Server-Sent Events (SSE)

## 使用说明

1. **计算 Token**：在左侧输入框输入文本，点击"计算 Token 数量"按钮
2. **模拟输出**：设置输出速度（tokens/秒），点击"模拟输出"按钮
3. **查看结果**：右侧输出区域会实时显示输出文本和进度
4. **停止输出**：在输出过程中可点击"停止输出"按钮中断
5. **切换语言**：点击右上角的语言选择器切换中英文界面

## Docker 部署

### 使用 Docker Compose

```bash
# 构建前端
cd frontend
pnpm install
pnpm run build
cd ..

# 启动服务
docker-compose up -d
```

访问 http://localhost

### 单独构建后端

```bash
cd backend
docker build -t deepseek-tokenizer-backend .
docker run -p 8000:8000 deepseek-tokenizer-backend
```

## 环境变量

### 后端
- `PORT`: 服务端口（默认 8000）

### 前端
- `VITE_API_URL`: 后端 API 地址（如果前后端分离部署）

## 详细部署指南

查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 获取更多部署选项和详细说明。

## 故障排查

### 后端无法启动
- 检查 Python 版本是否为 3.11+
- 检查依赖是否正确安装：`pip list | grep -E "fastapi|transformers|uvicorn"`
- 查看日志文件

### 前端无法访问后端
- 检查 `vite.config.js` 中的代理配置
- 检查后端 CORS 设置
- 确认后端服务正常运行：`curl http://localhost:8000/`

### 流式输出不工作
- 检查浏览器是否支持 Server-Sent Events
- 检查网络代理设置
- 查看浏览器控制台错误信息

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

Created with ❤️ by Manus

---

**GitHub 仓库**：https://github.com/zihaoli-cn/deepseek-tokenizer-web
