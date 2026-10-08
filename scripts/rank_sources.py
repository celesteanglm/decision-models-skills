"""Rebuild the editorial ranking from attributed, dated public snapshots."""
import json
import math
from pathlib import Path


def main():
    repo = Path(__file__).resolve().parents[1]
    research = json.loads((repo / "research" / "sources.json").read_text())
    recipes = [json.loads(path.read_text()) for path in (repo / "recipes").glob("*/recipe.json")]
    selected_urls = {url for recipe in recipes for url in recipe["source_urls"]}
    posts = []
    for source in research["posts"]:
        metrics = source["metrics"]
        date = source["published_at"][:10]
        within = research["window"]["since"] <= date <= research["window"]["through"]
        decent = (metrics.get("likes") or 0) >= 100 or (metrics.get("views") or 0) >= 10000
        if source.get("exclusion") or not within or not decent or source["url"] not in selected_urls:
            continue
        engagement = sum(weight * min(1, math.log1p(metrics.get(field) or 0) / math.log1p(cap))
                         for field, cap, weight in (("likes", 10000, .4), ("bookmarks", 10000, .3),
                                                   ("retweets", 1000, .2), ("views", 1000000, .1)))
        scores = source["editorial_scores"]
        score = 40 * scores["usefulness"] / 5 + 25 * scores["reproducibility"] / 5 + 15 * scores["evidence"] / 5 + 20 * engagement
        posts.append(dict(source, engagement_score=round(engagement * 5, 3), score=round(score, 3)))
    posts.sort(key=lambda p: (-p["score"], p["id"]))
    for index, post in enumerate(posts, 1):
        post["rank"] = index
    methodology = {"engagement_floor": "at least 100 likes OR 10000 views",
                   "weights": {"editorial_usefulness": 40, "editorial_reproducibility": 25, "editorial_evidence": 15, "observed_engagement": 20},
                   "engagement": "Weighted log1p counts, capped: likes 40% at 10000, bookmarks 30% at 10000, reposts 20% at 1000, views 10% at 1000000.",
                   "editorial_ratings": "Manual 1-5 assessments in sources.json. Reproducibility means a bounded slice can be independently implemented, not that the author's benchmark was reproduced.",
                   "selection": "Include only source posts inspiring at least one currently published recipe with a Working backend. Exclude games, weak engagement, infrastructure-only tutorials, unsupported broad announcements, and duplicate amplification. Preserve all inspected source records and exclusion reasons."}
    result = {"window": research["window"], "methodology": methodology, "limitations": research["limitations"], "ranked_posts": posts}
    (repo / "research" / "ranking.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    lines = ["# Community use-case research", "", "Publication window: **8 September–8 October 2026**, inclusive, using UTC publication dates.",
             "", f"Reviewed {len(research['posts'])} public posts; ranked {len(posts)} originals inspiring the {len(recipes)} published recipes. Every published recipe qualified as Working on at least one backend. Multiple slices may credit the same original.",
             "", "X Top search required login. This is a ranked discovered sample, not an exhaustive ranking of X. Discovery used public search, the independent [Jev AI Dev collection](https://jevai.dev/user-cases/), user-provided posts, and linked original Decisions API posts.",
             "", "## Ranking method", "", "Publication eligibility: at least one inspired recipe qualified as Working on a backend, non-game, in the date window, a concrete adaptable use case, and at least **100 likes or 10,000 views**. Rank combines usefulness (40%), reproducibility of a bounded slice (25%), specificity of source evidence (15%), and engagement (20%). Editorial criteria are explicit subjective 1–5 ratings. Engagement uses the capped logarithmic formula in [rank_sources.py](../scripts/rank_sources.py); [sources.json](sources.json) preserves ratings, exact snapshots, dates, and exclusions.",
             "", "Metrics came from named FXTwitter fields. Other public mirrors showed inconsistent or unlabeled counts; they were not substituted. Counts are timestamped third-party snapshots, not audited X analytics. A popular post is not evidence that its technical claims are correct.",
             "", "## Ranked original posts", "", "| Rank | Use case / original author | Published | Likes | Reposts | Bookmarks | Views | Score / 100 |", "|---|---|---|---|---|---|---|---|"]
    for post in posts:
        m = post["metrics"]
        lines.append(f"| {post['rank']} | [{post['title']} — @{post['author']['handle']}]({post['url']}) | {post['published_at'][:10]} | {m['likes']:,} | {m['retweets']:,} | {m['bookmarks']:,} | {m['views']:,} | {post['score']:.1f} |")
    lines += ["", "## Runnable contributions", "", "Each recipe implements a small recommendation on supplied text. It does not reproduce the source application, connect accounts, execute tools, or substantiate the author's performance claims. All code, instructions, and fixtures are independently authored; sources are credited as inspiration.",
              "", "| Priority | Recipe | Source rank | Original source |", "|---|---|---|---|"]
    rank_by_url = {p["url"]: p for p in posts}
    recipes.sort(key=lambda r: (min((rank_by_url[u]["rank"] for u in r["source_urls"] if u in rank_by_url), default=999), r["id"]))
    for index, recipe in enumerate(recipes, 1):
        source = min((rank_by_url[u] for u in recipe["source_urls"] if u in rank_by_url), key=lambda p: p["rank"])
        lines.append(f"| {index} | [{recipe['title']}](../recipes/{recipe['id']}/SKILL.md) | {source['rank']} | [@{source['author']['handle']}]({source['url']}) |")
    lines += ["", "## Exclusions and limitations", "", "Games in the discovery collection were skipped. Infrastructure tutorials about training or deploying alternative models are useful adapter roadmap references, but are not counted as use-case contributions. Announcement and amplification posts remain corroborating references. Posts below the engagement floor remain in the source record with an exclusion reason.",
              "", "Working backend labels come from [the verified catalog](../reports/VERIFIED_CATALOG.md) and immutable live receipts, not social metrics. Synthetic fixture acceptance is narrower than production accuracy. Reported benchmark multipliers and AUPRC were not reproduced.",
              "", "Regenerate this document and ranking JSON with `python scripts/rank_sources.py`. The source snapshot is intentionally frozen rather than silently refreshing metrics and changing historical ranks."]
    (repo / "research" / "README.md").write_text("\n".join(lines) + "\n")
    print(f"Ranked {len(posts)} originals and {len(recipes)} runnable recipes")


if __name__ == "__main__":
    main()
