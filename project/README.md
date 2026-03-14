# Quiz Application with Scoring System

Interactive CLI quiz platform with instant scoring and detailed performance reports.

# Project Description
A multiple-choice quiz application that loads questions from a JSON file, presents them in a CLI
interface, tracks user answers, calculates scores, and generates detailed result reports showing
correct/incorrect answers, percentage score, and performance analytics.
This is a simplified version of platforms like Quizlet, Kahoot, or corporate training systems.


## Features
- Load quizzes from JSON files
- Present questions one at a time with multiple choice options
- Accept answers as A/B/C/D or 1/2/3/4
- Validate input and track progress
- Calculate score, percentage, and analytics (topic/difficulty)
- Generate a detailed results report (question-wise + breakdowns)
- Save quiz attempts to `output/`

## Tech Stack
- Python 3.8+
- JSON for data storage
- No external dependencies

## Run
```bash
python main.py --quiz data/sample_quiz.json
```

Optional flags:
```bash 
python main.py --quiz data/sample_quiz.json --num 5 --shuffle --shuffle-options
```
Optional flags :
'''bash 
python main.py --quiz data/sample_quiz.json --difficulty Easy

'''

## Quiz JSON Format
Each question is an object:
```json
{
  "id": 1,
  "topic": "Python Basics",
  "question": "What is the output of print(2 ** 3)?",
  "options": ["6", "8", "9", "12"],
  "correct_answer": 1,
  "difficulty": "Easy"
}
```

Notes:
- `correct_answer` is a 0-based index into `options` (0..3 for 4 options).
- `options` must be a non-empty list; the app will label them A/B/C/... in the UI.

## Sample Output
Reports are saved under `output/` as both `.txt` and `.json` after each run.

## Output
project/output/Screenshot 2026-03-14 151610.pdf

## Tests
```bash
python -m unittest discover -s tests -v
```
## Author Information
- Name: Nandini Ramlingappa Muliniti
- Batch: ITC Infotech - Python Developer
- Submission Date: 14 March 2026
- Email: mulinitinandini@gmail.com



