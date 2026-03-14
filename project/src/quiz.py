from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence

from src.question import Question
from src.scorer import AnswerRecord, Scorer
from src.utils import ensure_dir, load_json_file, pct, safe_slug, utc_timestamp_compact


_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _label_for_index(i: int) -> str:
    if i < 0 or i >= len(_ALPHABET):
        return str(i + 1)
    return _ALPHABET[i]


def _parse_choice(user_input: str, option_count: int) -> Optional[int]:
    text = user_input.strip().upper()
    if not text:
        return None
    if text in {"Q", "QUIT", "EXIT"}:
        return -1
    if text.isdigit():
        idx = int(text) - 1
        return idx if 0 <= idx < option_count else None
    if len(text) == 1 and text in _ALPHABET:
        idx = _ALPHABET.index(text)
        return idx if 0 <= idx < option_count else None
    return None


@dataclass
class AttemptMeta:
    quiz_path: str
    started_at_epoch: float
    finished_at_epoch: float
    duration_seconds: float


class Quiz:
    def __init__(self, questions: Sequence[Question], quiz_path: str) -> None:
        if not questions:
            raise ValueError("No questions available to run")
        self.questions = list(questions)
        self.quiz_path = quiz_path

    @staticmethod
    def from_json_file(
        path: str,
        *,
        limit: int | None = None,
        topic: str | None = None,
        difficulty: str | None = None,
        shuffle: bool = False,
        shuffle_options: bool = False,
    ) -> "Quiz":
        raw = load_json_file(path)
        if not isinstance(raw, list):
            raise ValueError("Quiz JSON must be a list of question objects")

        questions: List[Question] = []
        for idx, item in enumerate(raw):
            if not isinstance(item, dict):
                raise ValueError(f"Question at index {idx} must be an object")
            questions.append(Question.from_dict(item))

        if topic is not None:
            t = topic.strip().lower()
            questions = [q for q in questions if q.topic.strip().lower() == t]
        if difficulty is not None:
            d = difficulty.strip().lower()
            questions = [q for q in questions if q.difficulty.strip().lower() == d]

        if not questions:
            raise ValueError("No questions matched the requested filters")

        if shuffle:
            random.shuffle(questions)

        if limit is not None:
            if limit <= 0:
                raise ValueError("--num must be > 0")
            questions = questions[:limit]

        if shuffle_options:
            questions = [Quiz._with_shuffled_options(q) for q in questions]

        return Quiz(questions, quiz_path=path)

    @staticmethod
    def _with_shuffled_options(q: Question) -> Question:
        pairs = list(enumerate(q.options))
        random.shuffle(pairs)
        new_options = tuple(text for _, text in pairs)
        new_correct = next(i for i, (old_idx, _) in enumerate(pairs) if old_idx == q.correct_index)
        return Question(
            qid=q.qid,
            topic=q.topic,
            prompt=q.prompt,
            options=new_options,
            correct_index=new_correct,
            difficulty=q.difficulty,
        )

    def run_interactive(self, *, save_results: bool = True) -> None:
        print("Quiz start")
        print(f"Questions: {len(self.questions)}")
        print("Answer with A/B/C/... or 1/2/3/...  (type 'q' to quit)\n")

        started = time.time()
        records: List[AnswerRecord] = []

        for idx, q in enumerate(self.questions, start=1):
            print(f"[{idx}/{len(self.questions)}] ({q.topic} | {q.difficulty})")
            print(q.prompt)
            for oi, opt in enumerate(q.options):
                print(f"  {_label_for_index(oi)}. {opt}")

            while True:
                raw = input("Your answer: ")
                choice = _parse_choice(raw, len(q.options))
                if choice == -1:
                    print("\nQuitting early.\n")
                    meta = self._finalize(records, started, save_results=save_results)
                    self._print_report(records, meta)
                    return
                if choice is None:
                    print("Invalid choice. Enter A/B/C/... or 1/2/3/... or 'q'.")
                    continue
                is_correct = choice == q.correct_index
                records.append(AnswerRecord(question=q, selected_index=choice, is_correct=is_correct))
                print("Correct!\n" if is_correct else f"Incorrect. Correct: {_label_for_index(q.correct_index)}\n")
                break

        meta = self._finalize(records, started, save_results=save_results)
        self._print_report(records, meta)

    def _finalize(self, records: Sequence[AnswerRecord], started_epoch: float, *, save_results: bool) -> AttemptMeta:
        finished = time.time()
        meta = AttemptMeta(
            quiz_path=self.quiz_path,
            started_at_epoch=started_epoch,
            finished_at_epoch=finished,
            duration_seconds=max(0.0, finished - started_epoch),
        )
        if save_results:
            self._save_results(records, meta)
        return meta

    def _save_results(self, records: Sequence[AnswerRecord], meta: AttemptMeta) -> None:
        ensure_dir("output")
        stamp = utc_timestamp_compact()
        base = f"{safe_slug(self.quiz_path)}_{stamp}"

        report = Scorer.build_report(records)

        # Human-readable text report
        txt_path = f"output/quiz_result_{base}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(self._render_text_report(records, meta, report))

        # Machine-readable JSON attempt
        json_path = f"output/quiz_attempt_{base}.json"
        payload: Dict[str, Any] = {
            "meta": asdict(meta),
            "summary": {
                "total_questions": report.total_questions,
                "correct": report.correct,
                "incorrect": report.incorrect,
                "percentage": report.percentage,
                "topic_breakdown": report.topic_breakdown,
                "difficulty_breakdown": report.difficulty_breakdown,
                "weak_topics": report.weak_topics,
            },
            "answers": [
                {
                    "id": r.question.qid,
                    "topic": r.question.topic,
                    "difficulty": r.question.difficulty,
                    "question": r.question.prompt,
                    "options": list(r.question.options),
                    "selected_index": r.selected_index,
                    "selected_label": None if r.selected_index is None else _label_for_index(r.selected_index),
                    "selected_text": None
                    if r.selected_index is None
                    else r.question.options[r.selected_index],
                    "correct_index": r.question.correct_index,
                    "correct_label": _label_for_index(r.question.correct_index),
                    "correct_text": r.question.correct_option_text(),
                    "is_correct": r.is_correct,
                }
                for r in records
            ],
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=True)

    def _print_report(self, records: Sequence[AnswerRecord], meta: AttemptMeta) -> None:
        report = Scorer.build_report(records)
        print(self._render_text_report(records, meta, report))

    def _render_text_report(self, records: Sequence[AnswerRecord], meta: AttemptMeta, report: Any) -> str:
        lines: List[str] = []
        lines.append("Quiz Results")
        lines.append("=" * 40)
        lines.append(f"Quiz file: {meta.quiz_path}")
        lines.append(f"Total Questions: {report.total_questions}")
        lines.append(f"Correct: {report.correct}")
        lines.append(f"Incorrect: {report.incorrect}")
        lines.append(f"Score: {report.percentage:.1f}%")
        lines.append(f"Duration: {meta.duration_seconds:.1f}s")
        lines.append("")
        lines.append("Topic-wise Performance:")
        for topic, (c, tot, p) in report.topic_breakdown.items():
            lines.append(f"- {topic}: {c}/{tot} ({p:.1f}%)")
        lines.append("")
        lines.append("Difficulty-wise Performance:")
        for diff, (c, tot, p) in report.difficulty_breakdown.items():
            lines.append(f"- {diff}: {c}/{tot} ({p:.1f}%)")
        lines.append("")
        if report.weak_topics:
            lines.append("Weak Areas (suggested focus):")
            for t in report.weak_topics:
                lines.append(f"- {t}")
            lines.append("")

        lines.append("Question Details:")
        for i, r in enumerate(records, start=1):
            q = r.question
            selected_label = None if r.selected_index is None else _label_for_index(r.selected_index)
            correct_label = _label_for_index(q.correct_index)
            status = "OK" if r.is_correct else "WRONG"
            lines.append(f"{i}. [{status}] ({q.topic} | {q.difficulty}) {q.prompt}")
            lines.append(f"   Your answer: {selected_label} - {None if r.selected_index is None else q.options[r.selected_index]}")
            lines.append(f"   Correct: {correct_label} - {q.correct_option_text()}")

        # High-level additional analytics
        lines.append("")
        lines.append("Performance Analytics:")
        lines.append(f"- Accuracy: {pct(report.correct, report.total_questions):.1f}%")
        lines.append(f"- Completed: {len(records)}/{len(self.questions)}")
        return "\n".join(lines) + "\n"
