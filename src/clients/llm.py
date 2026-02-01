from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel


class LLMClientProvider:
    def __init__(self, *, api_key: str, base_url: str):
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        self._vision_model = None
        self._language_model = None

    @property
    def vision_model(self) -> OpenAIChatCompletionsModel:
        if self._vision_model is None:
            self._vision_model = OpenAIChatCompletionsModel(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                openai_client=self._client,
            )
        return self._vision_model

    @property
    def language_model(self) -> OpenAIChatCompletionsModel:
        if self._language_model is None:
            self._language_model = OpenAIChatCompletionsModel(
                model="openai/gpt-oss-120b",
                openai_client=self._client,
            )
        return self._language_model
