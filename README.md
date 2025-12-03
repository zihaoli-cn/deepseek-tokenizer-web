# DeepSeek Tokenizer Web Tool

一个基于 FastAPI 和 Vue.js 3 的 Web 应用，用于分析和模拟 DeepSeek tokenizer 的行为。

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
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── locales/        # 国际化语言文件
│   │   ├── App.vue         # 主组件
│   │   └── main.js         # 入口文件
│   ├── index.html          # HTML 模板
│   ├── vite.config.js      # Vite 配置
│   └── package.json        # 前端依赖
└── README.md               # 项目说明
```

## 快速开始

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
```
POST /count_tokens
Content-Type: application/json

{
  "text": "要分析的文本"
}
```

### 模拟流式输出
```
POST /stream_text
Content-Type: application/json

{
  "text": "要输出的文本",
  "tokens_per_second": 50
}
```

## 使用说明

1. **计算 Token**：在左侧输入框输入文本，点击"计算 Token 数量"按钮
2. **模拟输出**：设置输出速度（tokens/秒），点击"模拟输出"按钮
3. **查看结果**：右侧输出区域会实时显示输出文本和进度
4. **停止输出**：在输出过程中可点击"停止输出"按钮中断
5. **切换语言**：点击右上角的语言选择器切换中英文界面

## 开发说明

### 后端开发
- 使用 FastAPI 提供 RESTful API
- 使用 Transformers 库加载 DeepSeek tokenizer
- 支持 Server-Sent Events (SSE) 实现流式输出

### 前端开发
- 使用 Vue 3 Composition API
- 使用 Element Plus 组件库
- 使用 Vue I18n 实现国际化
- 使用 Axios 进行 HTTP 请求

## 许可证

MIT License

## 作者

Created with ❤️ by Manus
