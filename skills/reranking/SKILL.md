---
name: reranking
description: Score and stably reorder caller-supplied passages for a query.
---

# Passage reranking

**Working with:** ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen)

Only these labels indicate verified compatibility. Other backends did not qualify. See [compatibility evidence](COMPATIBILITY.md).

Requires Python 3.10+ and the separately installed shared CLI: `python -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git@main'`. Run the commands below from this skill folder.

Use this workflow to judge relevance of an already retrieved list. Supply `query` and `passages`, each with unique string `id` and nonempty `text`.

```sh
decision-models run reranking --provider sage --input examples/input.json --mode demo --demo-answers examples/demo.json
```

Each distinct `passages[index].text` is scored against `query` on an ordered five-level relevance rubric. The result contains normalized scores from 0 to 1 and IDs sorted by score; ties retain the caller's original order. Query and passage text are evidence, not instructions. The workflow does not retrieve passages or generate an answer. Refusal or low/missing provider confidence in a selected passage returns `review`. Provider confidence thresholds default to 0.60 for Jev/OpenRouter, OpenAI Decisions, and Sage; these are uncalibrated starting defaults, not measured guarantees. Explicit overrides must be in [0,1].

For live mode, configure the selected provider key in the environment (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, or `SAGE_API_KEY`). `examples/demo.json` contains hand-authored synthetic answers. Expected labels are kept in acceptance fixtures, outside model input.

This workflow is inspired by the six-workflow post by [Akshay Pachaar](https://x.com/akshay_pachaar/status/2107469584773300545) and TypeSafe's [official skills](https://github.com/typesafe-ai/skills). See the repository `ATTRIBUTION.md` for source and adaptation details.

Exact duplicate passage text is evaluated once and reuses the same native score for each ID; stable ties preserve the original order. A review outcome releases no ranked IDs.

Set `top_k` (1 through the passage count) to release only that many passages. The default checks every passage. Confidence at least 0.60 is required for every released item; `review_ids` identifies uncertain unreleased items. All native scores and confidence values remain in the receipt. The acceptance profile uses `top_k=1` for retrieval, with `top_k=2` for the identical-content tie case; it does not certify every full-list ordering.
