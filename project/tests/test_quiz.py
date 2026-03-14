import unittest

from src.quiz import Quiz


class TestQuiz(unittest.TestCase):
    def test_from_json_file_missing(self) -> None:
        with self.assertRaises(FileNotFoundError):
            Quiz.from_json_file("data/does_not_exist.json")

