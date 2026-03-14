from __future__ import annotations

import argparse
import sys

from src.quiz import Quiz


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI quiz application with scoring and analytics.")
    parser.add_argument(
        "--quiz",
        default="data/sample_quiz.json",
        help="Path to quiz JSON file (default: data/sample_quiz.json).",
    )
    parser.add_argument("--num", type=int, default=None, help="Limit number of questions.")
    parser.add_argument("--difficulty", default=None, help="Filter by difficulty (case-insensitive).")
    parser.add_argument("--topic", default=None, help="Filter by topic (case-insensitive).")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle question order.")
    parser.add_argument("--shuffle-options", action="store_true", help="Shuffle options per question.")
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not write result files to output/.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        quiz = Quiz.from_json_file(
            args.quiz,
            limit=args.num,
            topic=args.topic,
            difficulty=args.difficulty,
            shuffle=args.shuffle,
            shuffle_options=args.shuffle_options,
        )
        quiz.run_interactive(save_results=not args.no_save)
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

