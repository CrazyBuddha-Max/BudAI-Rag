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
from services.ai.rag import RAGService


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
        return [{"role": msg.role, "content": msg.content} for msg in paired_messages]

    async def _prepare(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str,
        knowledge_base_id: str = None,
    ):
        conversation = await self.conv_repo.find_by_id(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="对话窗口不存在")

        assistant = await self.asst_repo.find_by_id(conversation.assistant_id)
        if not assistant:
            raise HTTPException(status_code=404, detail="AI助手不存在")

        llm_model = await self.model_repo.find_by_id(assistant.llm_model_id)
        if not llm_model or not llm_model.is_active:
            raise HTTPException(status_code=400, detail="大模型不可用")
        # embedding 模型： 优先用助手单独配置的，没有就用对话模型的配置
        if assistant.embedding_model_id:
            embedding_model = await self.model_repo.find_by_id(
                assistant.embedding_model_id
            )
            if not embedding_model or not embedding_model.is_active:
                raise HTTPException(status_code=400, detail="嵌入模型不可用")
        else:
            embedding_model = llm_model  # 降级用对话模型配置
        token_count = len(user_message.encode("utf-8")) // 4
        await self.msg_repo.create(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            token_count=token_count,
        )

        all_messages = await self.msg_repo.find_by_conversation(conversation_id)
        context = self._build_context(all_messages[:-1], assistant.context_length)

        rag_context = ""
        if knowledge_base_id:
            rag_service = RAGService()
            try:
                chunks = await rag_service.search(
                    query=user_message,
                    knowledge_base_id=knowledge_base_id,
                    llm_model=embedding_model,
                    top_n=assistant.top_n,
                )
                if chunks:
                    rag_context = (
                        "\n\n以下是相关的参考资料，请基于这些资料回答用户的问题：\n"
                    )
                    rag_context += "\n---\n".join(chunks)
            finally:
                await rag_service.close()

        full_system_prompt = assistant.system_prompt
        if rag_context:
            full_system_prompt += rag_context

        messages_payload = [
            {"role": "system", "content": full_system_prompt},
            *context,
            {"role": "user", "content": user_message},
        ]

        return assistant, llm_model, messages_payload

    async def stream_chat(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str,
        knowledge_base_id: str = None,
    ) -> AsyncGenerator[str, None]:
        assistant, llm_model, messages_payload = await self._prepare(
            conversation_id, user_message, user_id, knowledge_base_id
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
        self,
        conversation_id: str,
        user_message: str,
        user_id: str,
        knowledge_base_id: str = None,
    ) -> dict:
        assistant, llm_model, messages_payload = await self._prepare(
            conversation_id, user_message, user_id, knowledge_base_id
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
        print(f"调用大模型 url：{url}")
        print(f"模型名称：{llm_model.model_name}")
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
                async with client.stream(
                    "POST", url, headers=headers, json=payload
                ) as response:
                    if response.status_code != 200:
                        # 加这两行
                        error_body = await response.aread()
                        print(
                            f"大模型报错：{response.status_code} - {error_body.decode()}"
                        )
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
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    # 加这两行
                    print(f"大模型报错：{response.status_code} - {response.text}")
                    raise HTTPException(status_code=502, detail="大模型调用失败")
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                yield content

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
