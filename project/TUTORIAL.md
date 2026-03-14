# Tutorial: Quiz App

## 1) Run the sample quiz
```bash
python main.py --quiz data/sample_quiz.json
```

## 2) Common options
- Shuffle question order:
```bash
python main.py --quiz data/sample_quiz.json --shuffle
```

- Shuffle answer options (preserves correctness):
```bash
python main.py --quiz data/sample_quiz.json --shuffle-options
```

- Limit number of questions:
```bash
python main.py --quiz data/sample_quiz.json --num 5
```

- Filter by difficulty:
```bash
python main.py --quiz data/sample_quiz.json --difficulty Easy
```

## 3) Result files
- Text report: `output/quiz_result_<timestamp>.txt`
- JSON attempt record: `output/quiz_attempt_<timestamp>.json`

