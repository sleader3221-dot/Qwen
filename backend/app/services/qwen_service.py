import json
import logging
import time
from typing import Optional, AsyncGenerator, Any
from openai import OpenAI
import tiktoken

from app.config import settings

logger = logging.getLogger(__name__)


class QwenService:
    def __init__(self):
        client_kwargs = settings.qwen_client_kwargs
        if not client_kwargs.get("api_key") or client_kwargs["api_key"] == "sk-test-placeholder":
            client_kwargs["api_key"] = "sk-placeholder-for-init"
        self.client = OpenAI(**client_kwargs)
        self.model = settings.qwen_model
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.total_tokens_used = 0
        self.daily_token_budget = settings.token_budget_daily

    def _count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))

    def chat_completion(
        self,
        messages: list,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        stream: bool = False,
        enable_thinking: bool = None,
        enable_search: bool = None,
        tools: list = None,
        tool_choice: str = "auto",
        response_format: dict = None,
        top_p: float = 0.9,
    ) -> dict:
        if enable_thinking is None:
            enable_thinking = settings.enable_thinking_mode
        if enable_search is None:
            enable_search = settings.enable_web_search

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        kwargs = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
        }

        extra_body = {}
        if enable_thinking:
            extra_body["enable_thinking"] = True
            kwargs["temperature"] = 0.6
            kwargs["top_p"] = 0.95
        if enable_search:
            extra_body["enable_search"] = True
            extra_body["search_options"] = {"search_strategy": "agent", "enable_source": True}
        if response_format:
            extra_body["response_format"] = response_format

        if extra_body:
            kwargs["extra_body"] = extra_body
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        try:
            if stream:
                return self._stream_completion(kwargs)
            response = self.client.chat.completions.create(**kwargs)
            self._track_usage(response)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Qwen API error: {str(e)}")
            raise

    def _stream_completion(self, kwargs: dict):
        stream = self.client.chat.completions.create(**kwargs)
        full_content = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                yield content

    def function_call(
        self,
        messages: list,
        tools: list,
        system_prompt: Optional[str] = None,
        max_iterations: int = 5,
    ) -> dict:
        current_messages = list(messages)
        if system_prompt:
            current_messages.insert(0, {"role": "system", "content": system_prompt})

        tool_results = []
        iteration = 0

        while iteration < max_iterations:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.1,
            )
            self._track_usage(response)

            msg = response.choices[0].message

            if not msg.tool_calls:
                return {
                    "final_response": msg.content or "",
                    "tool_results": tool_results,
                    "iterations": iteration,
                }

            current_messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]})

            for tc in msg.tool_calls:
                result = self._execute_tool_sync(tc.function.name, tc.function.arguments)
                tool_results.append({"tool": tc.function.name, "result": result})
                current_messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result) if isinstance(result, dict) else str(result),
                })

            iteration += 1

        return {
            "final_response": "Max iterations reached",
            "tool_results": tool_results,
            "iterations": iteration,
        }

    def _execute_tool_sync(self, tool_name: str, arguments: str) -> Any:
        from app.core.tool_registry import ToolRegistry
        import asyncio
        try:
            args = json.loads(arguments)
            tool = ToolRegistry.get_tool(tool_name)
            if tool:
                if asyncio.iscoroutinefunction(tool.execute):
                    import asyncio
                    loop = asyncio.new_event_loop()
                    try:
                        return loop.run_until_complete(tool.execute(**args))
                    finally:
                        loop.close()
                return tool.execute(**args)
            return {"error": f"Tool {tool_name} not found"}
        except json.JSONDecodeError:
            return {"error": "Invalid arguments JSON"}
        except Exception as e:
            logger.error(f"Tool execution error: {tool_name} - {str(e)}")
            return {"error": str(e)}

    def _track_usage(self, response):
        if hasattr(response, "usage") and response.usage:
            self.total_tokens_used += response.usage.total_tokens

    def _parse_response(self, response) -> dict:
        choice = response.choices[0]
        msg = choice.message
        result = {
            "content": msg.content or "",
            "finish_reason": choice.finish_reason,
            "role": msg.role,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, "usage") and response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, "usage") and response.usage else 0,
                "total_tokens": response.usage.total_tokens if hasattr(response, "usage") and response.usage else 0,
            },
        }
        if msg.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ]
        return result

    def check_token_budget(self) -> dict:
        return {
            "total_used": self.total_tokens_used,
            "daily_budget": self.daily_token_budget,
            "remaining": self.daily_token_budget - self.total_tokens_used,
            "percentage_used": round((self.total_tokens_used / self.daily_token_budget) * 100, 2) if self.daily_token_budget > 0 else 0,
        }

    def structured_output(self, messages: list, system_prompt: Optional[str] = None) -> dict:
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            extra_body={"response_format": {"type": "json_object"}},
        )
        self._track_usage(response)
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"raw": response.choices[0].message.content}


qwen_service = QwenService()
