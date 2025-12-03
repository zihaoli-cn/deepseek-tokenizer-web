"""
DeepSeek Tokenizer API 后端主文件
提供分词统计和流式输出功能
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer
import asyncio
from typing import AsyncGenerator, List, Dict, Any
from fastapi.responses import StreamingResponse
import json
import string
import unicodedata

# 创建 FastAPI 应用实例
app = FastAPI(title="DeepSeek Tokenizer API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载 DeepSeek tokenizer 模型
# 从本地 ./tokenizer 目录加载，需要信任远程代码
tokenizer = AutoTokenizer.from_pretrained(
    "./tokenizer",
    trust_remote_code=True
)


class TokenCountRequest(BaseModel):
    """计算 token 数量的请求模型"""
    text: str


class StreamRequest(BaseModel):
    """流式输出请求模型"""
    text: str
    tokens_per_second: float


class TokenDetail(BaseModel):
    """分词详情模型"""
    index: int  # token在列表中的序号（从0开始）
    id: int
    string: str
    type: str  # 'word', 'punctuation', 'special', 'space'


class TokenCountResponse(BaseModel):
    """计算 token 数量的响应模型"""
    text: str
    token_count: int
    tokens: List[int]  # 保持向后兼容
    token_details: List[TokenDetail]  # 新增：分词详细信息
    statistics: Dict[str, int]  # 新增：统计信息


def classify_token(token_string: str, tokenizer) -> str:
    """
    基于 tokenizer 信息分类 token 类型

    Args:
        token_string: token 字符串
        tokenizer: tokenizer 实例

    Returns:
        str: token 类型，可能的值：'word', 'punctuation', 'special', 'space'
    """
    # 确保 token_string 是字符串
    if not isinstance(token_string, str):
        try:
            token_string = str(token_string)
        except:
            token_string = ""

    # 检查是否为特殊 token（如 [CLS], [SEP], [PAD] 等）
    # 使用多种方式检测特殊 token，提高兼容性
    special_tokens_str = []

    # 方法1: 检查 special_tokens_map
    if hasattr(tokenizer, 'special_tokens_map'):
        special_tokens = tokenizer.special_tokens_map.values()
        special_tokens_str.extend([str(t) for t in special_tokens])

    # 方法2: 检查 all_special_tokens
    if hasattr(tokenizer, 'all_special_tokens'):
        special_tokens_str.extend([str(t) for t in tokenizer.all_special_tokens])

    # 方法3: 检查 added_tokens_decoder（对于添加的特殊 token）
    if hasattr(tokenizer, 'added_tokens_decoder'):
        added_tokens = tokenizer.added_tokens_decoder.values()
        special_tokens_str.extend([str(t) for t in added_tokens])

    # 去重并检查
    special_tokens_str = list(set(special_tokens_str))
    if str(token_string) in special_tokens_str:
        return "special"

    # 检查是否为空格或 SentencePiece 前缀（▁ 表示空格）
    if isinstance(token_string, str) and (token_string.isspace() or token_string.startswith('▁')):
        return "space"

    # 检查是否为标点符号（包括中文标点）
    if isinstance(token_string, str):
        # 检查是否所有字符都是标点符号
        if token_string and all(unicodedata.category(char).startswith('P') for char in token_string):
            return "punctuation"
        # 同时检查ASCII标点符号（保持向后兼容）
        if token_string in string.punctuation:
            return "punctuation"

    # 默认分类为单词
    return "word"


@app.get("/")
async def root():
    """根路径，返回 API 基本信息"""
    return {"message": "DeepSeek Tokenizer API"}


@app.post("/count_tokens")
async def count_tokens(request: TokenCountRequest):
    """
    计算文本的 token 数量并返回分词详情

    Args:
        request: TokenCountRequest 对象，包含待分析的文本

    Returns:
        TokenCountResponse: 包含 token 数量、分词详情和统计信息的响应
    """
    try:
        # 获取 token IDs
        tokens = tokenizer.encode(request.text)

        # 获取可读的 token 字符串（解码后的文本）
        readable_strings = tokenizer.decode(tokens)

        # 获取 token 字符串（原始 token 表示）
        token_strings = tokenizer.convert_ids_to_tokens(tokens)

        # 构建分词详情和统计信息
        token_details = []
        statistics = {
            "words": 0,          # 单词数量
            "punctuation": 0,    # 标点符号数量
            "special_tokens": 0, # 特殊 token 数量
            "spaces": 0          # 空格数量
        }

        # 遍历所有 token，进行分类和统计
        for i, (token_id, token_str, readable_str) in enumerate(zip(tokens, token_strings, readable_strings)):
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

            # 添加到分词详情列表
            token_details.append(TokenDetail(
                index=i,  # token序号（从0开始）
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
        print(f"计算 token 数量时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stream_text")
async def stream_text(request: StreamRequest):
    """
    按指定速度流式输出文本

    Args:
        request: StreamRequest 对象，包含文本和输出速度

    Returns:
        StreamingResponse: Server-Sent Events (SSE) 流式响应
    """

    async def generate() -> AsyncGenerator[str, None]:
        """
        生成 SSE 事件的异步生成器

        Yields:
            str: SSE 格式的事件数据
        """
        try:
            text = request.text
            tokens_per_second = request.tokens_per_second

            # 验证输出速度参数
            if tokens_per_second <= 0:
                raise ValueError("tokens_per_second must be positive")

            # 对文本进行 tokenize
            tokens = tokenizer.encode(text)

            # 计算每个 token 的延迟时间（秒）
            delay_per_token = 1.0 / tokens_per_second

            # 逐个 token 解码并输出
            for i in range(len(tokens)):
                # 解码当前 token（从开始到当前 token）
                current_tokens = tokens[:i+1]
                decoded_text = tokenizer.decode(current_tokens)

                # 发送当前进度数据
                data = {
                    "text": decoded_text,
                    "current_token": i + 1,
                    "total_tokens": len(tokens),
                    "progress": (i + 1) / len(tokens) * 100
                }

                # 生成 SSE 事件
                yield f"data: {json.dumps(data, ensure_ascii=True)}\n\n"

                # 等待指定时间（模拟流式输出速度）
                if i < len(tokens) - 1:  # 最后一个 token 不需要等待
                    # 添加中断检查点：每10个token或每秒检查一次
                    check_interval = max(1.0, 10 * delay_per_token)  # 至少1秒检查一次
                    if delay_per_token < check_interval:
                        # 如果延迟时间小于检查间隔，使用延迟时间
                        await asyncio.sleep(delay_per_token)
                    else:
                        # 如果延迟时间较长，分多次等待以便及时响应取消
                        remaining_wait = delay_per_token
                        while remaining_wait > 0:
                            wait_time = min(remaining_wait, check_interval)
                            await asyncio.sleep(wait_time)
                            remaining_wait -= wait_time

            # 发送完成信号
            yield f"data: {json.dumps({'done': True}, ensure_ascii=True)}\n\n"

        except asyncio.CancelledError:
            # 客户端取消请求，正常退出
            print(f"Stream cancelled by client for text length: {len(text) if 'text' in locals() else 'unknown'}")
            # 可以在这里添加清理逻辑
            raise
        except Exception as e:
            # 发送错误信息
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data, ensure_ascii=True)}\n\n"

    # 返回流式响应
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",  # SSE 媒体类型
        headers={
            "Cache-Control": "no-cache",  # 禁用缓存
            "Connection": "keep-alive",   # 保持连接
        }
    )


if __name__ == "__main__":
    """主程序入口，启动 FastAPI 服务器"""
    import uvicorn
    # 启动 Uvicorn 服务器，监听所有网络接口，端口 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
