from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer
import asyncio
from typing import AsyncGenerator, List, Dict, Any
from fastapi.responses import StreamingResponse
import json
import string

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


class TokenDetail(BaseModel):
    id: int
    string: str
    type: str  # 'word', 'punctuation', 'special', 'space'


class TokenCountResponse(BaseModel):
    text: str
    token_count: int
    tokens: List[int]  # 保持向后兼容
    token_details: List[TokenDetail]  # 新增：分词详细信息
    statistics: Dict[str, int]  # 新增：统计信息


def classify_token(token_string: str, tokenizer) -> str:
    """基于tokenizer信息分类token类型"""
    # 确保token_string是字符串
    if not isinstance(token_string, str):
        try:
            token_string = str(token_string)
        except:
            token_string = ""

    # 检查是否为特殊token
    if hasattr(tokenizer, 'special_tokens_map'):
        special_tokens = tokenizer.special_tokens_map.values()
        # 转换为字符串进行比较
        special_tokens_str = [str(t) for t in special_tokens]
        if str(token_string) in special_tokens_str:
            return "special"

    # 检查是否为空格或SentencePiece前缀
    if isinstance(token_string, str) and (token_string.isspace() or token_string.startswith('▁')):
        return "space"

    # 检查是否为标点
    if isinstance(token_string, str) and token_string in string.punctuation:
        return "punctuation"

    # 默认分类为单词
    return "word"


@app.get("/")
async def root():
    return {"message": "DeepSeek Tokenizer API"}


@app.post("/count_tokens")
async def count_tokens(request: TokenCountRequest):
    """计算文本的 token 数量并返回分词详情"""
    try:
        # 获取token IDs
        tokens = tokenizer.encode(request.text)
        
        
        readable_strings = tokenizer.decode(tokens)

        # 获取token字符串（原始token表示）
        token_strings = tokenizer.convert_ids_to_tokens(tokens)

        # # 转换为可读字符串（处理字节编码）
        # readable_strings = []
        # for token_str in token_strings:
        #     # 尝试解码字节token
        #     if token_str.startswith('▁'):
        #         # SentencePiece风格的空格标记
        #         readable_str = ' ' + token_str[1:] if len(token_str) > 1 else ' '
        #     else:
        #         readable_str = token_str

        #     # 处理可能的编码问题
        #     try:
        #         # 如果是字节表示，尝试解码
        #         if isinstance(readable_str, bytes):
        #             readable_str = readable_str.decode('utf-8', errors='replace')
        #         elif '\\x' in repr(readable_str):
        #             # 包含转义序列，尝试处理
        #             readable_str = bytes(readable_str, 'latin-1').decode('utf-8', errors='replace')
        #     except:
        #         print(f"Decoding error: {e}")
        #         pass

        #     readable_strings.append(readable_str)

        # 构建分词详情和统计信息
        token_details = []
        statistics = {
            "words": 0,
            "punctuation": 0,
            "special_tokens": 0,
            "spaces": 0
        }

        for token_id, token_str, readable_str in zip(tokens, token_strings, readable_strings):
            token_type = classify_token(token_str, tokenizer)

            # 更新统计信息
            if token_type == "word":
                statistics["words"] += 1
            elif token_type == "punctuation":
                statistics["punctuation"] += 1
            elif token_type == "special":
                statistics["special_tokens"] += 1
            elif token_type == "space":
                statistics["spaces"] += 1

            token_details.append(TokenDetail(
                id=token_id,
                string=readable_str,
                type=token_type
            ))

        return {
            "text": request.text,
            "token_count": len(tokens),
            "tokens": tokens,  # 保持向后兼容
            "token_details": token_details,
            "statistics": statistics
        }
    except Exception as e:
        print(e)
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
                
                yield f"data: {json.dumps(data, ensure_ascii=True)}\n\n"
                
                # 等待指定时间
                if i < len(tokens) - 1:  # 最后一个 token 不需要等待
                    await asyncio.sleep(delay_per_token)
            
            # 发送完成信号
            yield f"data: {json.dumps({'done': True}, ensure_ascii=True)}\n\n"

        except Exception as e:
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data, ensure_ascii=True)}\n\n"
    
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
