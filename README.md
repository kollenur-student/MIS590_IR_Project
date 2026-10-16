# Surf Spot Search Taiwan (MIS590 IR project)

An English-language search and recommendation system for Taiwan's surf spots. Users type natural-language queries ("beginner-friendly beach break near Kaohsiung this weekend") and get a ranked list of spots. Each result explains whether and when the spot is surfable, based on wave and wind forecasts (Open-Meteo) and buoy observations (CWA).

- **Baseline:** BM25 over team-written spot profiles.
- **Improved system:** query understanding (place, skill, time) + surf-jargon expansion + a condition-fit score from the forecast, the spot's ideal conditions and the user's skill level, with template explanations.

> **Prototype status.** The pipeline runs end to end on real data: 35 sourced spot profiles, sourced thresholds (some marked DESIGN CHOICE), a sourced synonym list, gazetteer and regions. Still missing: the real test collection (queries + judgments); the smoke-test judgments are mock data. See *What the team must fill in* below.

---

## 1. Setup in VS Code (Windows)

1. Install **Python 3.11** (tested; 3.12 should also work) from python.org, plus VS Code with the **Python** and **Jupyter** extensions.
2. In VS Code: *File → Open Folder…* and open this project folder (the one containing `requirements.txt`).
3. Open a terminal (*Terminal → New Terminal*) and create the virtual environment:
   ```powershell
   py -3.11 -m venv .venv
   .venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
   On macOS/Linux: `python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
4. Select the environment: `Ctrl+Shift+P` → *Python: Select Interpreter* → `.venv`. In each notebook, click **Select Kernel** (top right) → *Python Environments* → `.venv`.
5. Optional dense retrieval (installs PyTorch, ~1 GB): `pip install -r requirements-dense.txt`, then set `USE_DENSE = True` in `02_indexing`.

Keep VS Code's default notebook working folder (the notebook's own folder). The notebooks find the project root themselves, and the `%run` cells change into `notebooks/` before loading other notebooks.

## 2. CWA API key

1. Register (free) at <https://opendata.cwa.gov.tw> and log in.
2. In your member area, request the **API authorization key** (menu names may differ slightly; the site is also available in English).
3. Copy `.env.example` to `.env` and paste the key: `CWA_API_KEY=CWA-...`. `.env` is git-ignored; never commit it or paste the key into a notebook.

Without a key, everything still runs; CWA observations are simply skipped.

**[TEAM] Verify once you have the key:** run `00_data_collection`, open `data/snapshots/<date>/raw/cwa_obs_48h.json.gz`, and check the dataset ID (`CWA_DATASETS`), the field names (`CWA_FIELD_PATTERNS`) and the units (`CWA_UNIT_FACTORS`) in notebook 00. Then fill `data/resources/cwa_stations_en.csv` with English names, coordinates and `station_type` (`buoy` / `tide`). Stations not yet mapped are listed automatically in `data/resources/cwa_stations_unmapped.csv`.

## 3. Run order

| # | Notebook | What it does | Run when |
|---|---|---|---|
| 0 | `00_data_collection.ipynb` | Fetches forecasts + observations → `data/snapshots/YYYY-MM-DD/` | daily (or via the scheduler) |
| 1 | `01_spot_corpus.ipynb` | Validates `data/spots/spots.csv`, statistics, map → `data/processed/` | after editing spots |
| 2 | `02_indexing.ipynb` | BM25 index, synonym list, optional dense index → `indexes/` | after 01 |
| 3 | `03_surfability.ipynb` | Condition-fit rules and explanations; heatmap | after editing thresholds |
| 4 | `04_search.ipynb` | Query understanding, `search()`, side-by-side examples | any time after 0–2 |
| 5 | `05_evaluation.ipynb` | Metrics, significance, buoy checks, latency → `results/` | after judging |
| 6 | `06_demo.ipynb` | Gradio demo (inline + browser URL) | demo / user study |

Every notebook runs with **Run All** on a fresh kernel. Settings are in the first code cell of each notebook (paths, `SAMPLE_N`, seed, snapshot date, flags).

**How notebooks share code.** 04, 05 and 06 load earlier notebooks with `%run ./NN_name.ipynb` instead of copying code. While loading, the environment variable `SURF_IR_LIBRARY_MODE=1` makes the loaded notebook define its functions but skip its own builds and demos. Each notebook's settings are applied *after* its `%run` lines, so they take precedence.

## 4. Daily snapshots (start in week 1!)

`collect_snapshot.py` executes the code cells of `00_data_collection.ipynb`, so the scheduled job and the notebook are always identical. Test it once by hand:

```powershell
.venv\Scripts\python.exe collect_snapshot.py
```

**Windows Task Scheduler** (the computer must be on at that time). In a terminal, replace the path:

```powershell
schtasks /Create /TN "SurfIR daily snapshot" /SC DAILY /ST 07:00 /TR "\"C:\path\to\MIS590_IR_Project\.venv\Scripts\python.exe\" \"C:\path\to\MIS590_IR_Project\collect_snapshot.py\""
```

Then open *Task Scheduler → SurfIR daily snapshot → Properties → Settings* and tick **"Run task as soon as possible after a scheduled start is missed"** (laptops are often asleep). On the *Conditions* tab, untick "Start the task only if the computer is on AC power".

**macOS / Linux (cron):** `crontab -e`, then add

```
0 7 * * * cd /path/to/MIS590_IR_Project && mkdir -p logs && .venv/bin/python collect_snapshot.py >> logs/cron.log 2>&1
```

Notes:
- The scheduler uses the computer's local time; the snapshot folder is named by the **Taiwan** date.
- Each run logs to `data/snapshots/<date>/collection.log` and `manifest.json` (status `complete` / `partial` / `failed`). Check them daily in week 1.
- If today's snapshot exists, the run is skipped (`OVERWRITE = False`).
- Snapshots cannot be back-filled later; a missed day is lost. Consider a second team member's computer as backup collector.

## 5. Folder structure

```
MIS590_IR_Project/
├── notebooks/                00_…06_ notebooks (all code)
├── collect_snapshot.py       scheduled runner for notebook 00
├── data/
│   ├── spots/spots.csv       spot profiles (35 sourced spots; [TEAM] rewrite descriptions in your own words)
│   ├── resources/
│   │   ├── surfability_thresholds.csv   rule thresholds with sources / DESIGN CHOICE rationale
│   │   ├── surf_synonyms.csv            [TEAM] jargon expansion (starter list)
│   │   ├── gazetteer.csv                [TEAM] towns + romanisation variants (verify coordinates)
│   │   ├── regions.csv                  [TEAM] region phrases ("east coast", "down south")
│   │   └── cwa_stations_en.csv          [TEAM] CWA station ID → English name, type, coordinates
│   ├── snapshots/YYYY-MM-DD/  daily forecast/observation snapshots (generated)
│   └── processed/             validated corpus (generated)
├── indexes/                   BM25 / synonyms / dense index (generated, git-ignored)
├── eval/                      queries + qrels (TREC format); smoke-test files are MOCK data
├── results/                   CSVs, report tables (tables/*.md), figures/*.png, runs/*.run
├── requirements.txt / requirements-dense.txt
└── .env.example               copy to .env with your CWA key
```

## 6. What the team must fill in

| File / setting | Task |
|---|---|
| `data/spots/spots.csv` | Rewrite the descriptions in your own words; add a second source for important spots; verify fields flagged in the chat notes |
| `surfability_thresholds.csv` | Have a surf school confirm the sourced values; tune the DESIGN CHOICE rows on dev queries |
| `surf_synonyms.csv` | Review, extend from real queries, cite a glossary |
| `gazetteer.csv`, `regions.csv` | Verify coordinates and agree on region boundaries |
| `cwa_stations_en.csv` + CWA settings in notebook 00 | See section 2 |
| `buoy_station_id` / `tide_station_id` in `spots.csv` | Map spots to stations (or rely on nearest buoy within `MAX_BUOY_DISTANCE_KM`) |
| `eval/queries.tsv`, `eval/qrels.txt` | Write the test collection and judge the pool exported by notebook 05 (`results/judging_pool.csv`) |
| Notebook 05 settings | Point `QUERIES_FILE`/`QRELS_FILE` at the real files; set `EVAL_SPLIT = "test"`; `TUNE_ALPHA = True` once dev queries exist |

## 7. Evaluation and demo

- **Smoke test:** notebook 05 runs out of the box on `eval/smoke_test_*` (5 made-up queries, mock grades). It only proves the code runs; never report its numbers.
- Outputs: `results/summary.csv`, `per_query.csv`, `significance.csv`, `by_query_type.csv`, `surfability_metrics.csv`, `forecast_error.csv`, `latency.csv`, `tables/*.md`, `figures/*.png`.
- **Demo:** run `06_demo.ipynb`; open the printed URL (e.g. `http://127.0.0.1:7860/`) in a browser and press F11. Rehearse on a saved snapshot. *Live data* falls back to the latest snapshot if an API fails. For the user study set `SHOW_SYSTEM_NAMES = False`.

## 8. Working together in Git

- One owner per notebook; others propose changes via pull requests.
- Strip outputs before committing so diffs stay readable and merges rarely conflict: `pip install nbstripout` then `nbstripout --install` (once per clone).
- For visual notebook diffs/merges: `pip install nbdime` then `nbdime config-git --enable`.
- Do not commit `.env`, `indexes/` or `.venv/` (already in `.gitignore`). **Decide as a team** whether `data/snapshots/` is shared through Git or a shared drive (see the note in `.gitignore`).

## 9. Data attribution

- Forecasts: [Open-Meteo.com](https://open-meteo.com/), CC BY 4.0, including wave model data from the Deutscher Wetterdienst (DWD). Free for non-commercial use. **[TEAM]** Check the Open-Meteo marine documentation for which wave models your requests use, and list every required attribution.
- Observations: Central Weather Administration (CWA) Open Data, Taiwan. **[TEAM]** Cite the CWA open-data licence terms in the report.
- The attribution is shown in the demo footer and stored in every snapshot's `manifest.json`.

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `Project root not found` | Open the project folder itself in VS Code (*File → Open Folder*). |
| `No snapshots in data/snapshots/` | Run `00_data_collection` once (internet needed). |
| `... not found. Run 01_spot_corpus / 02_indexing first` | Run the notebooks in order (section 3). |
| `Index and corpus differ` | You edited `spots.csv`: re-run 01 and 02. |
| All wave values empty for a spot | The beach is in a land grid cell: set `forecast_lat`/`forecast_lon` a few km offshore. |
| Gradio port in use | Re-run the launch cell (it closes the old server) or restart the kernel. |
| `TqdmWarning: IProgress not found` | Harmless. |
