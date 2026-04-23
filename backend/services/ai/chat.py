import json
from collections.abc import AsyncGenerator

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.assistant import Assistant
from models.message import Message
from repositories.assistant import AssistantRepository
from repositories.conversation import ConversationRepository
from repositories.llm_model import LLMModelRepository
from repositories.message import MessageRepository


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.msg_repo = MessageRepository(db)
        self.conv_repo = ConversationRepository(db)
        self.asst_repo = AssistantRepository(db)
        self.model_repo = LLMModelRepository(db)

    def _build_context(
        self, messages: list[Message], context_length: int
    ) -> list[dict]:
        context = []
        total_tokens = 0
        paired_messages = []
        i = len(messages) - 1
        while i >= 0:
            if (
                messages[i].role == "assistant"
                and i > 0
                and messages[i - 1].role == "user"
            ):
                pair_tokens = messages[i].token_count + messages[i - 1].token_count
                if total_tokens + pair_tokens <= context_length:
                    paired_messages.insert(0, messages[i])
                    paired_messages.insert(0, messages[i - 1])
                    total_tokens += pair_tokens
                    i -= 2
                else:
                    break
            else:
                i -= 1
        for msg in paired_messages:
            context.append({"role": msg.role, "content": msg.content})
        return context

    async def _prepare(self, conversation_id: str, user_message: str, user_id: str):
        """公共准备逻辑：验证、保存用户消息、构建上下文"""
        conversation = await self.conv_repo.find_by_id(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="对话窗口不存在")

        assistant = await self.asst_repo.find_by_id(conversation.assistant_id)
        if not assistant:
            raise HTTPException(status_code=404, detail="AI助手不存在")

        llm_model = await self.model_repo.find_by_id(assistant.llm_model_id)
        if not llm_model or not llm_model.is_active:
            raise HTTPException(status_code=400, detail="大模型不可用")

        token_count = len(user_message.encode("utf-8")) // 4
        await self.msg_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            token_count=token_count,
        )

        all_messages = await self.msg_repo.find_by_conversation(conversation_id)
        context = self._build_context(all_messages[:-1], assistant.context_length)

        messages_payload = [
            {"role": "system", "content": assistant.system_prompt},
            *context,
            {"role": "user", "content": user_message},
        ]

        return assistant, llm_model, messages_payload

    async def stream_chat(
        self, conversation_id: str, user_message: str, user_id: str
    ) -> AsyncGenerator[str, None]:
        """流式对话，逐 token 返回"""
        assistant, llm_model, messages_payload = await self._prepare(
            conversation_id, user_message, user_id
        )

        full_response = ""
        async for chunk in self._call_llm(
            llm_model, messages_payload, assistant, stream=True
        ):
            full_response += chunk
            yield chunk

        ai_token_count = len(full_response.encode("utf-8")) // 4
        await self.msg_repo.create(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            token_count=ai_token_count,
        )

    async def normal_chat(
        self, conversation_id: str, user_message: str, user_id: str
    ) -> dict:
        """非流式对话，等待完整响应后一次性返回"""
        assistant, llm_model, messages_payload = await self._prepare(
            conversation_id, user_message, user_id
        )

        full_response = ""
        async for chunk in self._call_llm(
            llm_model, messages_payload, assistant, stream=False
        ):
            full_response += chunk

        ai_token_count = len(full_response.encode("utf-8")) // 4
        await self.msg_repo.create(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            token_count=ai_token_count,
        )

        return {"role": "assistant", "content": full_response}

    async def _call_llm(
        self, llm_model, messages: list[dict], assistant: Assistant, stream: bool
    ) -> AsyncGenerator[str, None]:
        """统一入口，根据 provider 分发"""
        if llm_model.provider == "anthropic":
            async for chunk in self._call_anthropic(
                llm_model, messages, assistant, stream
            ):
                yield chunk
        else:
            async for chunk in self._call_openai_compatible(
                llm_model, messages, assistant, stream
            ):
                yield chunk

    async def _call_openai_compatible(
        self, llm_model, messages, assistant, stream: bool
    ) -> AsyncGenerator[str, None]:
        base_url = llm_model.api_base_url or "https://api.openai.com"
        url = f"{base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {llm_model.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": llm_model.model_name,
            "messages": messages,
            "temperature": assistant.temperature,
            "max_tokens": assistant.max_tokens,
            "stream": stream,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            if stream:
                # 流式：逐行读取
                async with client.stream(
                    "POST", url, headers=headers, json=payload
                ) as response:
                    if response.status_code != 200:
                        raise HTTPException(status_code=502, detail="大模型调用失败")
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk["choices"][0]["delta"].get("content", "")
                                if delta:
                                    yield delta
                            except Exception:
                                continue
            else:
                # 非流式：等待完整响应
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    raise HTTPException(status_code=502, detail="大模型调用失败")
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                yield content  # 一次性 yield 完整内容

    async def _call_anthropic(
        self, llm_model, messages, assistant, stream: bool
    ) -> AsyncGenerator[str, None]:
        url = "https://api.anthropic.com/v1/messages"

        system_prompt = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                filtered_messages.append(msg)

        headers = {
            "x-api-key": llm_model.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": llm_model.model_name,
            "max_tokens": assistant.max_tokens,
            "system": system_prompt,
            "messages": filtered_messages,
            "stream": stream,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            if stream:
                async with client.stream(
                    "POST", url, headers=headers, json=payload
                ) as response:
                    if response.status_code != 200:
                        raise HTTPException(status_code=502, detail="Claude 调用失败")
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            try:
                                event = json.loads(data)
                                if event.get("type") == "content_block_delta":
                                    delta = event.get("delta", {}).get("text", "")
                                    if delta:
                                        yield delta
                            except Exception:
                                continue
            else:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    raise HTTPException(status_code=502, detail="Claude 调用失败")
                data = response.json()
                content = data["content"][0]["text"]
                yield content
