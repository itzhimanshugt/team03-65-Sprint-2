"""First completion call: python -m scripts.hello_llm "your question" """

import sys

from app.llm import complete

question = sys.argv[1] if len(sys.argv) > 1 else "In one sentence, what is a mutual fund exit load?"
result = complete([{"role": "user", "content": question}])

print(f"Model: {result.model}")
print(f"Answer: {result.text}")
print(f"Tokens: {result.prompt_tokens} in / {result.completion_tokens} out")
