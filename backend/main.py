from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer
import asyncio
from typing import AsyncGenerator
from fastapi.responses import StreamingResponse
import json

app = FastAPI(title="DeepSeek Tokenizer API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载 tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    "./tokenizer",
    trust_remote_code=True
)


class TokenCountRequest(BaseModel):
    text: str


class StreamRequest(BaseModel):
    text: str
    tokens_per_second: float


@app.get("/")
async def root():
    return {"message": "DeepSeek Tokenizer API"}


@app.post("/count_tokens")
async def count_tokens(request: TokenCountRequest):
    """计算文本的 token 数量"""
    try:
        tokens = tokenizer.encode(request.text)
        return {
            "text": request.text,
            "token_count": len(tokens),
            "tokens": tokens
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream_text")
async def stream_text(request: StreamRequest):
    """按指定速度流式输出文本"""
    
    async def generate() -> AsyncGenerator[str, None]:
        try:
            text = request.text
            tokens_per_second = request.tokens_per_second
            
            if tokens_per_second <= 0:
                raise ValueError("tokens_per_second must be positive")
            
            # 对文本进行 tokenize
            tokens = tokenizer.encode(text)
            
            # 计算每个 token 的延迟时间（秒）
            delay_per_token = 1.0 / tokens_per_second
            
            # 逐个 token 解码并输出
            for i in range(len(tokens)):
                # 解码当前 token
                current_tokens = tokens[:i+1]
                decoded_text = tokenizer.decode(current_tokens)
                
                # 发送当前进度
                data = {
                    "text": decoded_text,
                    "current_token": i + 1,
                    "total_tokens": len(tokens),
                    "progress": (i + 1) / len(tokens) * 100
                }
                
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
                # 等待指定时间
                if i < len(tokens) - 1:  # 最后一个 token 不需要等待
                    await asyncio.sleep(delay_per_token)
            
            # 发送完成信号
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
