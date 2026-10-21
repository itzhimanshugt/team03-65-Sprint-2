"""Ask the model for JSON and validate it against a Pydantic schema."""

import json
from typing import TypeVar

from pydantic import BaseModel, Field, ValidationError

from app.llm import complete


class Citation(BaseModel):
    n: int = Field(description="Source number as shown in the context, e.g. 1 for [1]")
    chunk_id: str
    source: str
    page: int


class Answer(BaseModel):
    answer: str
    citations: list[Citation] = []
    refused: bool = False


class StructuredOutputError(RuntimeError):
    pass


T = TypeVar("T", bound=BaseModel)


def schema_instruction(model: type[BaseModel]) -> str:
    return (
        "Reply with only a JSON object, no prose or code fences, matching this JSON schema:\n"
        + json.dumps(model.model_json_schema())
    )


def complete_json(messages: list[dict], model: type[T], **params) -> T:
    """Get a reply as `model`. One retry with the validation error if the JSON is invalid."""
    messages = [*messages, {"role": "user", "content": schema_instruction(model)}]
    for attempt in range(2):
        reply = complete(messages, response_format={"type": "json_object"}, **params)
        try:
            return model.model_validate_json(reply.text)
        except ValidationError as error:
            if attempt == 1:
                raise StructuredOutputError(f"Invalid JSON after retry: {error}") from error
            messages = [
                *messages,
                {"role": "assistant", "content": reply.text},
                {
                    "role": "user",
                    "content": f"That JSON was invalid: {error}. Send corrected JSON.",
                },
            ]
