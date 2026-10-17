# Surf Spot Search Taiwan (MIS590 IR project)

An English-language search and recommendation system for Taiwan's surf spots. Users type natural-language queries such as *"beginner-friendly beach break near Kaohsiung this weekend"* and get a ranked list of spots. Each result says whether and when the spot is surfable, e.g. *"Fair for beginners. Best around Sat 06:00: 0.5 m swell, light wind, low tide."* The system combines spot profiles with wave and wind forecasts (Open-Meteo) and buoy observations (CWA).

> **Status.** The pipeline runs end to end on real data: 35 sourced spot profiles, sourced thresholds (some marked DESIGN CHOICE), a sourced synonym list, gazetteer and regions, and daily snapshots with live CWA buoy data (first snapshot: 2026-10-16). All seven notebooks were tested with Python 3.11 and 3.13. **Still missing:** the real test collection (queries and relevance judgments). Until then, notebook 05 runs on a mock smoke test whose numbers must not be reported.

Repository: <https://github.com/kollenur-student/MIS590_IR_Project>. A short overview for the team is in `PROJECT_OVERVIEW.ipynb`.

---

## 1. Baseline vs. improved system

| | **Baseline (BM25)** | **Improved (condition-aware)** |
|---|---|---|
| Ranking | Keyword search (BM25, Lucene IDF) over the spot profiles | BM25 **plus** the additions below |
| Query understanding: place, skill level, time | – | ✓ (gazetteer with spelling variants, region phrases, skill lexicon, time rules) |
| Surf-slang expansion (*newbie* → beginner) | – | ✓ |
| Condition-fit score from the forecast for the user's level and time window | – | ✓ |
| Safety: spots unsafe for the user's level go to the bottom with a warning | – | ✓ |
| Explanation per result | – | ✓ (template, built only from computed numbers) |

The baseline only matches words. It does not know where the user is, when they want to surf, or what the waves are doing. Example: for *"uncrowded reef break on the east coast tomorrow morning"* the baseline ranks a southern spot first, while the improved system returns only east-coast reef breaks.

Final score of the improved system: `α · text score + (1 − α) · condition fit`, after a location filter. α = 0.5 by default, or 0.85 for queries without condition intent; it can be tuned on dev queries in notebook 05. Ablation variants (`improved_no_cf`, `improved_no_qu`, `improved_no_syn`) switch off one component each, and `improved_oracle` uses buoy observations instead of the forecast as an upper bound.

## 2. Where the information comes from

**Live conditions** (fetched daily and saved as a snapshot in `data/snapshots/YYYY-MM-DD/`):

| Source | What it provides | Notes |
|---|---|---|
| Open-Meteo Marine API | 7-day hourly wave, swell and wind-wave height/period/direction; sea level including tides | Free, no key; attribution to Open-Meteo and DWD required |
| Open-Meteo Weather API | Wind speed and direction at each beach | Used for offshore vs. onshore wind |
| CWA Open Data (O-B0075-001) | Buoy and tide-station measurements of the last 48 h | Free API key; checks the forecast and measures forecast error |
| CWA station list (O-B0076-001) | Official English station names and coordinates | Refreshed automatically into `cwa_stations_en.csv` on every run |

**Static data** (every row lists its source in the file):

| File | Content | Sources |
|---|---|---|
| `data/spots/spots.csv` | 35 spot profiles | Mainly Swelleye; plus BreakFinder, NSYSU, Taiwan Outdoors, WSL, Nick Kembel and others; OpenStreetMap for county/town |
| `data/resources/surfability_thresholds.csv` | Rule thresholds per skill level | Surf-education sites (Climeradar, Rapture Camps, Sharp Eye…), Met Office Beaufort scale, Open-Meteo sunrise/sunset; rows without a source are marked DESIGN CHOICE with a reason |
| `data/resources/surf_synonyms.csv` | 38 surf-slang expansions | Wiktionary, Wikipedia Glossary of surfing, Independent Surfer glossary |
| `data/resources/gazetteer.csv` | 38 places with spelling variants (Kaohsiung = Gaoxiong = Takao) | Wikidata |
| `data/resources/regions.csv` | Region phrases ("east coast", "down south") | Wikipedia "Regions of Taiwan" (official NDC definition) |

Spot IDs are readable names, e.g. `WAIAO_BEACH`, `JINZUN_HARBOR`, `JIALESHUEI`, `CIJIN_BEACH`, `NSYSU_BEACH`, `FULONG`, `DONGHE`.

## 3. Setup in VS Code (Windows)

1. Install **Python 3.11 or newer** (tested with 3.11 and 3.13) and VS Code with the **Python** and **Jupyter** extensions.
2. Clone the repository and open the folder in VS Code (*File → Open Folder…*):
   ```powershell
   git clone https://github.com/kollenur-student/MIS590_IR_Project.git
   ```
3. Open a terminal (*Terminal → New Terminal*) and create the virtual environment:
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
   On macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
4. In each notebook click **Select Kernel** (top right) → *Python Environments* → `.venv`.
5. **CWA API key:** register (free) at <https://opendata.cwa.gov.tw>, request the API authorization key in your member area, copy `.env.example` to `.env` and paste it: `CWA_API_KEY=CWA-...`. **Never commit `.env`** (it is git-ignored). Without a key everything still runs; CWA observations are skipped.
6. Run `01_spot_corpus.ipynb` and `02_indexing.ipynb` once. Their outputs (`data/processed/`, `indexes/`) are not stored in Git.
7. Optional dense retrieval (installs PyTorch, ~1 GB): `pip install -r requirements-dense.txt`, then set `USE_DENSE = True` in `02_indexing`.

Keep VS Code's default notebook working folder. The notebooks find the project root themselves.

## 4. Using the tool (demo)

1. Open `notebooks/06_demo.ipynb`, select the `.venv` kernel and click **Run All**. You do **not** need to run notebooks 00–05 first (see section 5).
2. The interface appears inline. For presentations, open the printed link (e.g. `http://127.0.0.1:7860/`) in a browser and press F11.
3. Type a query in English and press **Search** or Enter. Baseline results are on the left, improved results on the right.

| Control | Meaning |
|---|---|
| **Query** | English question, e.g. *"i am an intermediate surfer, where do you recommend me to go tomorrow?"* |
| **Skill level / Day** | Optional overrides. *From query* (default) reads skill and day from the text; any other choice overrides the text |
| **Data** | *Saved snapshot* (instant, works offline; best for presentations) or *Live data* (current forecast) |
| **Snapshot** | Which saved day to use (only with *Saved snapshot*) |
| **Results** | Number of spots shown (1–10) |

**What you see:** what the system understood (*Location · Skill · Time*; "(default)" means it was not in the query), jargon expansions, the data timestamp, result cards with a verdict (Good / Fair / Poor), explanation, safety warnings and highlighted matching terms, a 7-day outlook for the top spots, and the data attribution.

**Defaults:** no place means all of Taiwan; no time means the next 48 hours; no skill means intermediate. "near X" means within 40 km.

**Waiting times:** with *Saved snapshot* a search takes under a second. With *Live data*, the first search takes about 30 seconds (forecasts for all 35 spots plus CWA data are downloaded). After that, searches are instant for 30 minutes (`LIVE_CACHE_MINUTES`). If an API or the internet fails, the demo falls back to the latest snapshot and says so. Tip: run one live search a minute before presenting.

**Example queries:** *"glassy waves for a newbie near Yilan on Saturday"*, *"point break with board rental near Kenting"*, *"uncrowded reef break on the east coast tomorrow morning"*, *"Sizihwan waves this weekend"*.

**User study:** set `SHOW_SYSTEM_NAMES = False` in the first cell; the columns are then labelled "System A" / "System B". To stop the server, set `STOP_DEMO = True` in the last cell and run it, or restart the kernel.

**Searching from code:** in `04_search.ipynb` (after Run All):
```python
search("beginner beach break near Kaohsiung this weekend", system="improved", k=5)   # or system="baseline"
info = search_verbose("glassy waves in Yilan on Saturday", snapshot_date="2026-10-16")
describe_parsed(info["parsed"]), info["results"][0]["explanation"]
```

## 5. The notebooks and when to run them

| # | Notebook | What it does | Output |
|---|---|---|---|
| 0 | `00_data_collection` | Downloads forecasts and CWA observations, refreshes the English station list | `data/snapshots/YYYY-MM-DD/` |
| 1 | `01_spot_corpus` | Validates `spots.csv`, statistics, map | `data/processed/spots_clean.json`, `results/figures/spot_map.html` |
| 2 | `02_indexing` | BM25 index (Lucene IDF), compiled synonym list, optional dense index | `indexes/`, `results/indexing_stats.json` |
| 3 | `03_surfability` | Condition-fit rules, surfable call, explanations, 7-day heatmap | `results/surfability_table.csv`, figure |
| 4 | `04_search` | Query understanding, `search()` for all system variants, side-by-side examples | – |
| 5 | `05_evaluation` | Metrics, significance tests, buoy comparison, latency, judging pool | `results/` |
| 6 | `06_demo` | Gradio interface | local web app |

Every notebook runs with **Run All** on a fresh kernel. Settings are in the first code cell of each notebook. Notebooks 04, 05 and 06 load earlier notebooks with `%run` (functions only), so no code is copied.

**What to re-run after a change:**

| You changed … | Run |
|---|---|
| Nothing; just searching or presenting | only `06_demo` (or `04_search`) |
| `spots.csv`, synonyms, gazetteer or regions | `01` → `02`, then restart the demo |
| `surfability_thresholds.csv` | restart the demo (or `03` / `04`) |
| Want a new day of data without the scheduler | `00` |
| Need evaluation results for the report | `05` |
| Fresh clone of the repository | `01` → `02` once |

A spot that is missing from an older snapshot (e.g. added later) shows "No data" instead of failing.

## 6. Daily snapshots (run every day)

Relevance depends on conditions, so the evaluation needs snapshots from several different days. A missed day cannot be back-filled. `collect_snapshot.py` executes the code cells of notebook 00, so the scheduled job and the notebook are always identical. Test it once:

```powershell
.venv\Scripts\python.exe collect_snapshot.py
```

**Windows Task Scheduler** (adjust the path; the computer must be on at that time):

```powershell
schtasks /Create /TN "SurfIR daily snapshot" /SC DAILY /ST 07:00 /TR "\"C:\path\to\MIS590_IR_Project\.venv\Scripts\python.exe\" \"C:\path\to\MIS590_IR_Project\collect_snapshot.py\""
```

Then open *Task Scheduler → SurfIR daily snapshot → Properties → Settings* and tick **"Run task as soon as possible after a scheduled start is missed"**. On the *Conditions* tab, untick "Start the task only if the computer is on AC power".

**macOS / Linux (cron):** `crontab -e`, then add
```
0 7 * * * cd /path/to/MIS590_IR_Project && mkdir -p logs && .venv/bin/python collect_snapshot.py >> logs/cron.log 2>&1
```

Notes:
- The scheduler uses the computer's local time; the snapshot folder is named by the **Taiwan** date.
- Check `data/snapshots/<date>/manifest.json` (`"status": "complete"`) and `collection.log`.
- If today's snapshot exists, the run is skipped (`OVERWRITE = False` in notebook 00).
- A full run takes about 30 seconds for 35 spots.
- Decide as a team whether `data/snapshots/` is shared through Git or a shared drive (see the note in `.gitignore`).

## 7. Evaluation

The evaluation compares all system variants on the same queries and snapshots (notebook 05).

**Smoke test (current default).** Notebook 05 runs out of the box on `eval/smoke_test_queries.tsv` and `eval/smoke_test_qrels.txt`: 5 made-up queries with **mock** grades. It only proves that the code runs. **Never report these numbers**, including the files currently in `results/`.

**Building the real test collection.** The team writes the queries and judgments itself; nothing generates them. Templates are in `eval/`:

| File | Purpose |
|---|---|
| `eval/RELEVANCE_GUIDELINES.md` | Relevance guidelines template: writing queries, what judges may see, the 0–3 scale, double judging, examples, change log. Complete the [TEAM] sections before judging |
| `eval/queries.tsv` | Your ~50 queries (tab-separated: `qid  query  snapshot_date  query_type  split`) |
| `eval/qrels.txt` | Relevance judgments in TREC format: `qid 0 spot_id grade` |
| `eval/judging_template.csv` | Judging sheet (grade plus reasons: topical match, conditions, safety, notes) |
| `eval/qrels_judge2.txt` | Optional: second judge on ~20% of the queries, for Cohen's kappa |
| `eval/README.md` | Format details |

**Relevance scale:** 3 = matches all constraints and good conditions for the level; 2 = matches, surfable but mediocre; 1 = related but poor conditions, outside the window or one constraint missed; 0 = wrong place or type, or unsafe for the level. Judges see the raw forecast/buoy numbers, never the system's scores or explanations.

**Workflow:**
1. Complete `RELEVANCE_GUIDELINES.md` as a team.
2. Review the 50 queries in `eval/queries.tsv`. Each is paraphrased from a real Forumosa forum question (source, date and verbatim wording in `eval/query_sources.csv`); 7–10 per type (location, skill, time, attribute, vague, mixed); 15 `dev`, 35 `test`. Once more snapshots exist, spread the snapshot dates over 3–4 days with different conditions. Finalise the queries **before** looking at system output.
3. In the first cell of notebook 05 set `QUERIES_FILE = EVAL_DIR / "queries.tsv"` and `QRELS_FILE = EVAL_DIR / "qrels.txt"`, then run it. Without judgments it only runs all systems and exports `results/judging_pool.csv`, the (query, spot) pairs to judge (top 10 of every system; about 730 pairs for the 50 queries). The metric sections are skipped until judgments exist.
4. Judge the pool using `judging_template.csv`; copy the grades into `eval/qrels.txt`. A second judge fills `qrels_judge2.txt` for ~10 queries.
5. Set `EVAL_SPLIT = "test"` and `TUNE_ALPHA = True`, then run notebook 05 again for the full evaluation.

**What notebook 05 reports:**

| Area | Measures |
|---|---|
| Ranking quality | nDCG@5 (primary), MRR, P@3, Recall@10, judged@5; per query, per query type, with 95% bootstrap confidence intervals |
| Significance | Paired randomisation test and paired t-test, Holm correction, mean difference with CI, Cohen's d_z, wins/ties/losses |
| Agreement | Cohen's kappa (quadratic-weighted and binary) if `qrels_judge2.txt` exists |
| Surfability vs. buoys | Forecast vs. observed surfable calls (accuracy, precision, recall, confusion matrix) by lead time; wave-height MAE, bias and RMSE; forecast error vs. ranking gain. Needs snapshots from several days |
| Efficiency | Indexing time and size, median and p95 query latency per system, snapshot load time, optional live API time |

**Outputs:** `results/summary.csv`, `per_query.csv`, `significance.csv`, `by_query_type.csv`, `judging_pool.csv`, `surfability_metrics.csv`, `forecast_error.csv`, `latency.csv`, `runs/*.run` (TREC run files), report-ready tables in `results/tables/*.md` and figures in `results/figures/*.png`.

## 8. Folder structure

```
MIS590_IR_Project/
├── PROJECT_OVERVIEW.ipynb    short overview for the team (Markdown only)
├── notebooks/                00_…06_ notebooks (all code)
├── collect_snapshot.py       scheduled runner for notebook 00
├── data/
│   ├── spots/spots.csv       35 sourced spot profiles
│   ├── resources/
│   │   ├── surfability_thresholds.csv   rule thresholds with sources / DESIGN CHOICE rationale
│   │   ├── surf_synonyms.csv            surf-slang expansions with sources
│   │   ├── gazetteer.csv                places + spelling variants (Wikidata)
│   │   ├── regions.csv                  region phrases (Wikipedia "Regions of Taiwan")
│   │   └── cwa_stations_en.csv          CWA stations with English names (auto-refreshed)
│   ├── snapshots/YYYY-MM-DD/  daily forecast/observation snapshots
│   └── processed/             validated corpus (generated, git-ignored)
├── indexes/                   BM25 / synonyms / dense index (generated, git-ignored)
├── eval/                      queries, qrels, guidelines and judging templates; smoke-test files are MOCK data
├── results/                   CSVs, report tables (tables/*.md), figures/*.png, runs/*.run
├── requirements.txt / requirements-dense.txt
└── .env.example               copy to .env with your CWA key
```

## 9. Open points

- Rewrite the spot descriptions in your own words (GenAI policy); they were drafted from the sources.
- Check Swelleye's terms of use (main source of the spot data) and add a second source for important spots.
- Verify values flagged as uncertain, e.g. the NSYSU Beach swell window, the Jialeshuei bottom type and the Jinzun coordinates.
- Have a surf school or instructor confirm the thresholds and judge a subset of queries.

## 10. Data attribution

- Forecasts: [Open-Meteo.com](https://open-meteo.com/), CC BY 4.0, including wave model data from the Deutscher Wetterdienst (DWD). Free for non-commercial use. Check the Open-Meteo marine documentation for which wave models your requests use and list every required attribution.
- Observations: Central Weather Administration (CWA) Open Data, Taiwan. Cite the CWA open-data licence terms in the report.
- The attribution is shown in the demo footer and stored in every snapshot's `manifest.json`.

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| `Project root not found` | Open the project folder itself in VS Code (*File → Open Folder*). |
| `No snapshots in data/snapshots/` | Run `00_data_collection` once (internet needed). |
| `... not found. Run 01_spot_corpus / 02_indexing first` | Run 01 and 02 (e.g. after a fresh clone). |
| `Index and corpus differ` | You edited `spots.csv`: re-run 01 and 02. |
| All wave values empty for a spot | The beach is in a land grid cell: set `forecast_lat`/`forecast_lon` a few km offshore. |
| A spot shows "No data" | The spot is not in the selected snapshot (added later); use a newer snapshot. |
| First *Live data* search is slow | Expected (~30 s download); later searches are cached for 30 minutes. |
| Gradio port in use | Re-run the launch cell (it closes the old server) or restart the kernel. |
| `TqdmWarning: IProgress not found` | Harmless. |
