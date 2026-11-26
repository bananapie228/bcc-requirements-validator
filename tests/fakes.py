from typing import Dict, Type

from pydantic import BaseModel


class FakeLLM:
    """Test adapter for the LLM seam: returns a canned response per response schema."""

    model = "fake"

    def __init__(self, responses: Dict[Type[BaseModel], BaseModel] = None):
        self.responses = responses or {}
        self.prompts = []

    def ask(self, prompt, schema, system=""):
        self.prompts.append(prompt)
        # fresh copy per call, like the real adapter: callers may mutate the result
        return self.responses[schema].model_copy(deep=True)
