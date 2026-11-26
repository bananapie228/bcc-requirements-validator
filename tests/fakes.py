from typing import Dict, Type

from pydantic import BaseModel


class FakeLLM:
    """Тестовый адаптер шва LLM: на каждую схему ответа — заранее заданный ответ."""

    model = "fake"

    def __init__(self, responses: Dict[Type[BaseModel], BaseModel] = None):
        self.responses = responses or {}
        self.prompts = []

    def ask(self, prompt, schema, system=""):
        self.prompts.append(prompt)
        return self.responses[schema]
