"""Conversation history that stays inside a token budget."""

from dataclasses import dataclass, field

from app.tokens import count_message_tokens


@dataclass
class ChatHistory:
    system_prompt: str
    max_turns: int = 4  # PRD §6.2: last 4 turns
    token_budget: int = 1_500  # PRD §6.2: history budget
    turns: list[tuple[dict, dict]] = field(default_factory=list)

    def add_turn(self, user: str, assistant: str) -> None:
        self.turns.append(
            ({"role": "user", "content": user}, {"role": "assistant", "content": assistant})
        )

    def messages(self, new_question: str) -> list[dict]:
        """System prompt + as many recent turns as fit + the new question.

        Oldest turns are dropped first; the system prompt and new question are always kept.
        """
        system = {"role": "system", "content": self.system_prompt}
        question = {"role": "user", "content": new_question}
        kept: list[dict] = []
        for user, assistant in reversed(self.turns[-self.max_turns :]):
            candidate = [user, assistant, *kept]
            if count_message_tokens([system, *candidate, question]) > self.token_budget:
                break
            kept = candidate
        return [system, *kept, question]

    def dropped_turns(self, new_question: str) -> int:
        kept = (len(self.messages(new_question)) - 2) // 2
        return len(self.turns) - kept
