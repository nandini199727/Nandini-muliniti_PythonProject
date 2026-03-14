import unittest

from src.question import Question


class TestQuestion(unittest.TestCase):
    def test_from_dict_valid(self) -> None:
        q = Question.from_dict(
            {
                "id": 1,
                "topic": "Python",
                "question": "2+2?",
                "options": ["3", "4"],
                "correct_answer": 1,
                "difficulty": "Easy",
            }
        )
        self.assertEqual(q.qid, 1)
        self.assertEqual(q.correct_index, 1)
        self.assertEqual(q.correct_option_text(), "4")

    def test_from_dict_invalid_correct_range(self) -> None:
        with self.assertRaises(ValueError):
            Question.from_dict(
                {
                    "id": 1,
                    "topic": "Python",
                    "question": "2+2?",
                    "options": ["3", "4"],
                    "correct_answer": 2,
                    "difficulty": "Easy",
                }
            )

