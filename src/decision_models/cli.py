"""JSON CLI; live calls always require an explicit mode."""
import argparse
import json
from pathlib import Path
import sys
from .contracts import DecisionError
from .runtime import SKILLS, PROVIDERS, execute


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DecisionError("invalid_request", "cannot read valid JSON input") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(prog="decision-models")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run one workflow with JSON input")
    run.add_argument("skill", choices=SKILLS)
    run.add_argument("--provider", choices=PROVIDERS, required=True)
    run.add_argument("--input", required=True)
    run.add_argument("--mode", choices=("demo", "live"), default="demo")
    run.add_argument("--demo-answers")
    run.add_argument("--model")
    run.add_argument("--retries", type=int, choices=(0,1,2), default=0)
    recipe = sub.add_parser("recipe", help="run a portable community decision recipe")
    recipe.add_argument("--recipe", required=True)
    recipe.add_argument("--provider", choices=PROVIDERS, required=True)
    recipe.add_argument("--input", required=True)
    recipe.add_argument("--mode", choices=("demo", "live"), default="demo")
    recipe.add_argument("--demo-answers")
    recipe.add_argument("--model")
    recipes_eval = sub.add_parser("evaluate-recipes", help="evaluate frozen community recipes")
    recipes_eval.add_argument("--repo", required=True)
    recipes_eval.add_argument("--providers", nargs="+", choices=PROVIDERS, default=list(PROVIDERS))
    recipes_eval.add_argument("--mode", choices=("demo", "live"), default="demo")
    recipes_eval.add_argument("--repetitions", type=int, default=3)
    recipes_eval.add_argument("--budget", type=float, default=1)
    recipes_eval.add_argument("--output", required=True)
    recipes_eval.add_argument("--rates")
    evaluate = sub.add_parser("evaluate", help="run frozen acceptance fixtures")
    evaluate.add_argument("--repo", required=True)
    evaluate.add_argument("--providers", nargs="+", choices=PROVIDERS, default=list(PROVIDERS))
    evaluate.add_argument("--mode", choices=("demo", "live"), default="demo")
    evaluate.add_argument("--repetitions", type=int, default=3)
    evaluate.add_argument("--budget", type=float, default=5)
    evaluate.add_argument("--output", required=True)
    evaluate.add_argument("--rates", help="reviewed per-million-token rates JSON; required for live mode")
    evaluate.add_argument("--skills", nargs="+", choices=SKILLS, default=list(SKILLS))
    smoke = sub.add_parser("smoke", help="live check of the three primitive mappings")
    smoke.add_argument("--provider", choices=PROVIDERS, required=True)
    report = sub.add_parser("report", help="generate Markdown from evaluation receipts")
    report.add_argument("--input", required=True)
    report.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "evaluate-recipes":
            from .recipe_evaluation import evaluate_recipes, write_recipe_report
            result = evaluate_recipes(Path(args.repo), args.providers, args.mode, args.repetitions,
                                      args.budget, Path(args.output), read_json(args.rates) if args.rates else None)
            write_recipe_report(result, Path(args.output).with_suffix(".md"))
            print(json.dumps({"summary": result["summary"], "budget": result["budget"]}, indent=2))
            return 0 if args.mode == "demo" or all(s["status"] == "Working" for s in result["summary"].values()) else 1
        if args.command == "recipe":
            from .recipes import execute_recipe, load_recipe
            demo = read_json(args.demo_answers) if args.demo_answers else None
            if demo is not None and "answers" in demo:
                demo = demo["answers"]
            result = execute_recipe(load_recipe(args.recipe), args.provider, read_json(args.input),
                                    mode=args.mode, demo_answers=demo, model=args.model)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "run":
            data = read_json(args.input)
            demo = read_json(args.demo_answers) if args.demo_answers else None
            if demo is not None and "answers" in demo:
                demo = demo["answers"]
            result = execute(args.skill, args.provider, data, mode=args.mode, demo_answers=demo,
                             model=args.model, retries=args.retries)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 2 if result["result"]["action"] in ("error", "judge_error") else 0
        from .evaluation import evaluate_fixtures, smoke_provider, write_report
        if args.command == "smoke":
            print(json.dumps(smoke_provider(args.provider), indent=2))
            return 0
        if args.command == "report":
            write_report(read_json(args.input), Path(args.output))
            return 0
        result = evaluate_fixtures(Path(args.repo), args.providers, args.mode, args.repetitions,
                                   args.budget, Path(args.output), read_json(args.rates) if args.rates else None,
                                   args.skills)
        print(json.dumps(result["summary"], indent=2))
        return 0 if all(v["status"] == "Working" for v in result["summary"].values()) else 1
    except DecisionError as exc:
        print(json.dumps({"result": {"action": "error", "reasons": [exc.code]}, "error": exc.as_dict()}))
        return 2
    except (KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"result": {"action": "error", "reasons": ["invalid_request"]},
                          "error": {"code": "invalid_request", "message": "input does not match workflow schema"}}))
        return 2
