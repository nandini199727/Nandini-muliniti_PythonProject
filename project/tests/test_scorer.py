import unittest

from src.question import Question
from src.scorer import AnswerRecord, Scorer


class TestScorer(unittest.TestCase):
    def test_build_report_counts(self) -> None:
        q1 = Question.from_dict(
            {
                "id": 1,
                "topic": "T1",
                "question": "Q1",
                "options": ["A", "B"],
                "correct_answer": 0,
                "difficulty": "Easy",
            }
        )
        q2 = Question.from_dict(
            {
                "id": 2,
                "topic": "T2",
                "question": "Q2",
                "options": ["A", "B"],
                "correct_answer": 1,
                "difficulty": "Hard",
            }
        )
        records = [
            AnswerRecord(question=q1, selected_index=0, is_correct=True),
            AnswerRecord(question=q2, selected_index=0, is_correct=False),
        ]
        report = Scorer.build_report(records, weak_threshold_pct=70.0)
        self.assertEqual(report.total_questions, 2)
        self.assertEqual(report.correct, 1)
        self.assertEqual(report.incorrect, 1)
        self.assertAlmostEqual(report.percentage, 50.0)
        self.assertIn("T2", report.weak_topics)

