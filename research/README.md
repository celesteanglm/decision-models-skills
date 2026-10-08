# Community use-case research

Publication window: **8 September–8 October 2026**, inclusive, using UTC publication dates.

Reviewed 36 public posts; ranked 17 originals inspiring the 18 published recipes. Every published recipe qualified as Working on at least one backend. Multiple slices may credit the same original.

X Top search required login. This is a ranked discovered sample, not an exhaustive ranking of X. Discovery used public search, the independent [Jev AI Dev collection](https://jevai.dev/user-cases/), user-provided posts, and linked original Decisions API posts.

## Ranking method

Publication eligibility: at least one inspired recipe qualified as Working on a backend, non-game, in the date window, a concrete adaptable use case, and at least **100 likes or 10,000 views**. Rank combines usefulness (40%), reproducibility of a bounded slice (25%), specificity of source evidence (15%), and engagement (20%). Editorial criteria are explicit subjective 1–5 ratings. Engagement uses the capped logarithmic formula in [rank_sources.py](../scripts/rank_sources.py); [sources.json](sources.json) preserves ratings, exact snapshots, dates, and exclusions.

Metrics came from named FXTwitter fields. Other public mirrors showed inconsistent or unlabeled counts; they were not substituted. Counts are timestamped third-party snapshots, not audited X analytics. A popular post is not evidence that its technical claims are correct.

## Ranked original posts

| Rank | Use case / original author | Published | Likes | Reposts | Bookmarks | Views | Score / 100 |
|---|---|---|---|---|---|---|---|
| 1 | [Browser action selection — @gregpr07](https://x.com/gregpr07/status/2100411066966749359) | 2026-09-17 | 9,130 | 662 | 9,967 | 3,254,978 | 91.7 |
| 2 | [Template field matching — @yongfook](https://x.com/yongfook/status/2100801037192024478) | 2026-09-18 | 135 | 4 | 107 | 15,259 | 89.6 |
| 3 | [Email queue classification — @rileybrown](https://x.com/rileybrown/status/2100404532119269426) | 2026-09-17 | 3,877 | 98 | 1,707 | 297,899 | 88.5 |
| 4 | [Model tier routing — @ephraimduncan](https://x.com/ephraimduncan/status/2100454070536351824) | 2026-09-17 | 1,874 | 68 | 1,068 | 119,620 | 87.2 |
| 5 | [Invoice file classification — @marcelpociot](https://x.com/marcelpociot/status/2100906882365788167) | 2026-09-18 | 1,150 | 48 | 908 | 139,931 | 86.5 |
| 6 | [Suspicious email escalation — @nutlope](https://x.com/nutlope/status/2100614659690713543) | 2026-09-17 | 872 | 51 | 762 | 60,725 | 86.1 |
| 7 | [Six bounded workflow patterns — @akshay_pachaar](https://x.com/akshay_pachaar/status/2107469584773300545) | 2026-10-06 | 485 | 66 | 515 | 31,633 | 85.4 |
| 8 | [Page quality and change classification — @ethank_6](https://x.com/ethank_6/status/2107576429928169934) | 2026-10-06 | 290 | 12 | 282 | 42,757 | 83.6 |
| 9 | [Research, inbox, and content workflows — @aiedge_](https://x.com/aiedge_/status/2107835983735787568) | 2026-10-07 | 117 | 14 | 375 | 105,240 | 83.2 |
| 10 | [Agent workflow routing — @ericwilliamrea](https://x.com/ericwilliamrea/status/2107911336583946374) | 2026-10-07 | 82 | 4 | 22 | 13,902 | 83.2 |
| 11 | [Brand news matching — @SUOHA_AI](https://x.com/SUOHA_AI/status/2101000339948282090) | 2026-09-18 | 2,273 | 333 | 2,675 | 415,185 | 81.1 |
| 12 | [Draft quality screening — @robj3d3](https://x.com/robj3d3/status/2100722975645598191) | 2026-09-17 | 1,384 | 65 | 2,097 | 240,643 | 79.5 |
| 13 | [Semantic spreadsheet urgency — @dabit3](https://x.com/dabit3/status/2100780008193020049) | 2026-09-18 | 1,204 | 57 | 935 | 277,886 | 78.8 |
| 14 | [Secondhand listing fit — @AlanDaitch](https://x.com/AlanDaitch/status/2100757989212754085) | 2026-09-18 | 953 | 41 | 1,124 | 86,396 | 78.3 |
| 15 | [Ad funnel classification — @mightyking](https://x.com/mightyking/status/2100939189869002819) | 2026-09-18 | 227 | 186 | 209 | 173,815 | 77.0 |
| 16 | [Spoken-topic slide selection — @rinte0321](https://x.com/rinte0321/status/2100749640866165092) | 2026-09-18 | 420 | 39 | 322 | 80,611 | 76.8 |
| 17 | [Outfit option selection — @charlierguo](https://x.com/charlierguo/status/2107573880974127319) | 2026-10-06 | 688 | 37 | 572 | 64,450 | 72.5 |

## Runnable contributions

Each recipe implements a small recommendation on supplied text. It does not reproduce the source application, connect accounts, execute tools, or substantiate the author's performance claims. All code, instructions, and fixtures are independently authored; sources are credited as inspiration.

| Priority | Recipe | Source rank | Original source |
|---|---|---|---|
| 1 | [Select the next browser action](../recipes/browser-action-selection/SKILL.md) | 1 | [@gregpr07](https://x.com/gregpr07/status/2100411066966749359) |
| 2 | [Template Field Matching](../recipes/template-field-matching/SKILL.md) | 2 | [@yongfook](https://x.com/yongfook/status/2100801037192024478) |
| 3 | [Route an email to a review queue](../recipes/email-queue-routing/SKILL.md) | 3 | [@rileybrown](https://x.com/rileybrown/status/2100404532119269426) |
| 4 | [Route a request to an eligible model tier](../recipes/model-tier-routing/SKILL.md) | 4 | [@ephraimduncan](https://x.com/ephraimduncan/status/2100454070536351824) |
| 5 | [Classify a downloaded file for invoice handling](../recipes/invoice-file-triage/SKILL.md) | 5 | [@marcelpociot](https://x.com/marcelpociot/status/2100906882365788167) |
| 6 | [Suspicious Email Escalation](../recipes/suspicious-email-escalation/SKILL.md) | 6 | [@nutlope](https://x.com/nutlope/status/2100614659690713543) |
| 7 | [Screen instructions embedded in retrieved text](../recipes/retrieved-instruction-screening/SKILL.md) | 7 | [@akshay_pachaar](https://x.com/akshay_pachaar/status/2107469584773300545) |
| 8 | [Distinguish substantive page changes](../recipes/page-change-triage/SKILL.md) | 8 | [@ethank_6](https://x.com/ethank_6/status/2107576429928169934) |
| 9 | [Content Revision Gate](../recipes/content-revision-gate/SKILL.md) | 9 | [@aiedge_](https://x.com/aiedge_/status/2107835983735787568) |
| 10 | [Research Source Filter](../recipes/research-source-filter/SKILL.md) | 9 | [@aiedge_](https://x.com/aiedge_/status/2107835983735787568) |
| 11 | [Route a request to a workflow](../recipes/agent-workflow-routing/SKILL.md) | 10 | [@ericwilliamrea](https://x.com/ericwilliamrea/status/2107911336583946374) |
| 12 | [Match a news item to a brand response opportunity](../recipes/brand-news-matching/SKILL.md) | 11 | [@SUOHA_AI](https://x.com/SUOHA_AI/status/2101000339948282090) |
| 13 | [Decide whether a draft is ready for another revision](../recipes/draft-quality-triage/SKILL.md) | 12 | [@robj3d3](https://x.com/robj3d3/status/2100722975645598191) |
| 14 | [Rate spreadsheet rows for follow-up urgency](../recipes/spreadsheet-urgency/SKILL.md) | 13 | [@dabit3](https://x.com/dabit3/status/2100780008193020049) |
| 15 | [Secondhand Listing Fit](../recipes/secondhand-listing-fit/SKILL.md) | 14 | [@AlanDaitch](https://x.com/AlanDaitch/status/2100757989212754085) |
| 16 | [Ad Funnel Classification](../recipes/ad-funnel-classification/SKILL.md) | 15 | [@mightyking](https://x.com/mightyking/status/2100939189869002819) |
| 17 | [Spoken Slide Selection](../recipes/spoken-slide-selection/SKILL.md) | 16 | [@rinte0321](https://x.com/rinte0321/status/2100749640866165092) |
| 18 | [Choose among described outfit options](../recipes/outfit-option-selection/SKILL.md) | 17 | [@charlierguo](https://x.com/charlierguo/status/2107573880974127319) |

## Exclusions and limitations

Games in the discovery collection were skipped. Infrastructure tutorials about training or deploying alternative models are useful adapter roadmap references, but are not counted as use-case contributions. Announcement and amplification posts remain corroborating references. Posts below the engagement floor remain in the source record with an exclusion reason.

Working backend labels come from [the verified catalog](../reports/VERIFIED_CATALOG.md) and immutable live receipts, not social metrics. Synthetic fixture acceptance is narrower than production accuracy. Reported benchmark multipliers and AUPRC were not reproduced.

Regenerate this document and ranking JSON with `python scripts/rank_sources.py`. The source snapshot is intentionally frozen rather than silently refreshing metrics and changing historical ranks.
