from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from src.question import Question
from src.utils import pct


@dataclass(frozen=True)
class AnswerRecord:
    question: Question
    selected_index: int | None  # None means skipped/quit
    is_correct: bool


@dataclass(frozen=True)
class ScoreReport:
    total_questions: int
    correct: int
    incorrect: int
    percentage: float
    topic_breakdown: Dict[str, Tuple[int, int, float]]  # topic -> (correct, total, pct)
    difficulty_breakdown: Dict[str, Tuple[int, int, float]]
    weak_topics: List[str]


class Scorer:
    @staticmethod
    def build_report(records: Iterable[AnswerRecord], weak_threshold_pct: float = 70.0) -> ScoreReport:
        records_list = list(records)
        total = len(records_list)
        correct = sum(1 for r in records_list if r.is_correct)
        incorrect = total - correct
        percentage = pct(correct, total)

        topic_counts: Dict[str, List[int]] = {}
        difficulty_counts: Dict[str, List[int]] = {}
        # Store as [correct, total]
        for r in records_list:
            t = r.question.topic
            d = r.question.difficulty
            topic_counts.setdefault(t, [0, 0])
            difficulty_counts.setdefault(d, [0, 0])
            topic_counts[t][1] += 1
            difficulty_counts[d][1] += 1
            if r.is_correct:
                topic_counts[t][0] += 1
                difficulty_counts[d][0] += 1

        topic_breakdown = {
            k: (v[0], v[1], pct(v[0], v[1])) for k, v in sorted(topic_counts.items(), key=lambda kv: kv[0].lower())
        }
        difficulty_breakdown = {
            k: (v[0], v[1], pct(v[0], v[1]))
            for k, v in sorted(difficulty_counts.items(), key=lambda kv: kv[0].lower())
        }

        weak_topics = [t for t, (c, tot, p) in topic_breakdown.items() if tot > 0 and p < weak_threshold_pct]

        return ScoreReport(
            total_questions=total,
            correct=correct,
            incorrect=incorrect,
            percentage=percentage,
            topic_breakdown=topic_breakdown,
            difficulty_breakdown=difficulty_breakdown,
            weak_topics=weak_topics,
        )

