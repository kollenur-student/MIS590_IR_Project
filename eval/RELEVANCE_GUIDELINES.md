# Relevance guidelines (template)

> **[TEAM]** This is a template. Complete every section marked [TEAM], agree on it as a team **before** judging, and keep it unchanged while judging. Record any later change (date, reason) in section 7. Put the final version in the report appendix.

## 1. Writing the queries (`eval/queries.tsv`)

- Write ~50 queries **before** looking at any system output.
- Base them on real information needs (paraphrased forum questions, surf-school FAQs, your own trips) and note the origin in section 8.
- Spread them across types: about 8 each of `location`, `skill`, `time`, `attribute`, `vague`, plus ~10 `mixed`.
- Assign each query a snapshot date. Use 3-4 dates with different conditions (flat, NE monsoon, typhoon swell, mixed).
- Mark ~15 queries `dev` (for tuning α) and ~35 `test` (for reported results), stratified by type.

## 2. What judges see

For each (query, spot) pair from `results/judging_pool.csv`:
- the query, its snapshot date and the snapshot reference time ("now" = when the snapshot was fetched),
- the spot profile (`data/spots/spots.csv`),
- the **raw** conditions for the requested time window: forecast wave height, period, direction, wind, tide (and buoy observations if available).

Judges must **not** see the system's ranking, condition-fit score, verdict or explanation. Otherwise the judgments copy the system.

## 3. Relevance scale

| Grade | Label | Definition |
|---|---|---|
| **3** | Highly relevant | Matches **all** constraints in the query (place, skill, type, facilities…) **and** conditions in the requested window are good for the stated (or default intermediate) level. |
| **2** | Relevant | Matches the constraints; conditions are surfable but mediocre for that level. |
| **1** | Marginally relevant | Topically related (right region or type) but conditions are poor or outside the window, **or** one constraint is missed. |
| **0** | Not relevant | Wrong place or type, **or unsafe** for the stated skill level (e.g. a reef break in big surf for a beginner). |

Rules:
- If the query names no time, judge the next 48 hours from the reference time; if it names no skill, judge for an intermediate surfer.
- Safety overrides everything: a spot that is unsafe for the stated level is **0**, even if it matches every other constraint.
- For pure attribute queries ("reef break with showers near Taitung"), judge mainly on the attributes; conditions decide only between 2 and 3.
- [TEAM] Define what counts as "good" vs "mediocre" conditions (e.g. refer to `surfability_thresholds.csv` or your surf-school source).
- [TEAM] Define how far "near X" may be (the system uses 40 km).

## 4. Filling in the judging sheet (`eval/judging_template.csv`)

One row per judged (query, spot) pair:

| Column | Content |
|---|---|
| `qid`, `query`, `snapshot_date`, `spot_id`, `spot_name` | copied from `results/judging_pool.csv` |
| `judge` | judge's initials |
| `grade` | 0-3 (section 3) |
| `topical_match` | yes / partly / no |
| `conditions_in_window` | good / mediocre / poor / no data |
| `safe_for_level` | yes / no |
| `notes` | short reason, especially for 0 and borderline cases |

When a query is finished, copy its grades into `eval/qrels.txt` (`qid 0 spot_id grade`).

## 5. Double judging and agreement

- A second judge independently grades ~20% of the queries (~10) and writes `eval/qrels_judge2.txt` in the same format.
- Notebook 05 reports Cohen's kappa (quadratic-weighted, and binary at grade ≥ 2). Target: κ > 0.6.
- Disagreements are discussed afterwards; the agreed grade goes into `eval/qrels.txt`. Record what changed in the guidelines (section 7).
- [TEAM] Ask an external surfer or surf-school instructor to judge a subset, so the team's own rules are not the only judgment (reduces circularity).

## 6. Worked examples

> [TEAM] Add 3-4 examples from your own snapshot data, one per grade, each with the raw conditions and the reasoning. Example structure:
>
> **Query:** … **Snapshot:** … **Spot:** …
> **Conditions in window:** wave … m, period … s, wind … km/h from …, tide …
> **Grade:** … **Reason:** …

## 7. Change log

| Date | Change | Reason |
|---|---|---|
| | | |

## 8. Query origins

| qid | Origin (paraphrased from …) |
|---|---|
| | |
