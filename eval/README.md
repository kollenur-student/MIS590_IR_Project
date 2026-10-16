# Evaluation files

| File | Format | Status |
|---|---|---|
| `smoke_test_queries.tsv`, `smoke_test_qrels.txt` | see below | **Mock data for a smoke test only. Never report results from these.** |
| `queries.tsv` | tab-separated, header `qid	query	snapshot_date	query_type	split` | [TEAM] write ~50 queries |
| `qrels.txt` | TREC qrels: `qid 0 spot_id grade` (space-separated) | [TEAM] relevance judgments (grades 0-3) |
| `qrels_judge2.txt` | same format, second judge on the overlap sample | [TEAM] for Cohen's kappa |

- `snapshot_date` is `YYYY-MM-DD` (a folder in `data/snapshots/`). `latest` is allowed only for smoke tests.
- `query_type` is free text, e.g. `location`, `skill`, `time`, `attribute`, `vague`, `mixed`; results are broken down by it.
- `split` is `dev` (used to tune alpha) or `test` (used for the reported results).
- Optional columns: `skill` (overrides the skill found in the query), `ref_time` (`YYYY-MM-DD HH:MM`, overrides the snapshot's fetch time as "now").
- Lines starting with `#` are ignored in both files.
- Spots retrieved but not judged count as non-relevant (standard TREC practice). `05_evaluation` reports *judged@5* so you can see whether the pool was deep enough, and it exports the judging pool to `results/judging_pool.csv`.
