from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class Question:
    qid: int
    topic: str
    prompt: str
    options: tuple[str, ...]
    correct_index: int
    difficulty: str

    @staticmethod
    def from_dict(raw: dict[str, Any]) -> "Question":
        required = ["id", "topic", "question", "options", "correct_answer", "difficulty"]
        missing = [k for k in required if k not in raw]
        if missing:
            raise ValueError(f"Question missing keys: {', '.join(missing)}")

        qid = raw["id"]
        topic = str(raw["topic"]).strip()
        prompt = str(raw["question"]).strip()
        options = raw["options"]
        correct = raw["correct_answer"]
        difficulty = str(raw["difficulty"]).strip()

        if not isinstance(qid, int):
            raise ValueError("Question id must be an int")
        if not topic:
            raise ValueError("Question topic must be non-empty")
        if not prompt:
            raise ValueError("Question text must be non-empty")
        if not isinstance(options, Sequence) or isinstance(options, (str, bytes)):
            raise ValueError("Question options must be a list of strings")
        if len(options) < 2:
            raise ValueError("Question options must have at least 2 items")
        normalized_options = tuple(str(o) for o in options)
        if not all(opt.strip() for opt in normalized_options):
            raise ValueError("Question options must be non-empty strings")
        if not isinstance(correct, int):
            raise ValueError("correct_answer must be an int index (0-based)")
        if correct < 0 or correct >= len(normalized_options):
            raise ValueError("correct_answer out of range for options")
        if not difficulty:
            raise ValueError("Question difficulty must be non-empty")

        return Question(
            qid=qid,
            topic=topic,
            prompt=prompt,
            options=normalized_options,
            correct_index=correct,
            difficulty=difficulty,
        )

    def correct_option_text(self) -> str:
        return self.options[self.correct_index]

