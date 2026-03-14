# Quiz JSON Format

The quiz file must be a JSON array of question objects.

## Required Keys
- `id` (int): unique identifier
- `topic` (string): category label used for topic-wise analytics
- `question` (string): the question text
- `options` (list of strings): answer options (2+)
- `correct_answer` (int): 0-based index into `options`
- `difficulty` (string): e.g. `Easy`, `Medium`, `Hard`

## Example
```json
[
  {
    "id": 1,
    "topic": "Python Basics",
    "question": "What is the output of print(2 ** 3)?",
    "options": ["6", "8", "9", "12"],
    "correct_answer": 1,
    "difficulty": "Easy"
  }
]
```

