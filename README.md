# HARS — Household Adaptive Risk-Scoring Framework

## Files
- `hars_core.py` — the framework logic (taxonomy, rubrics, scoring, aggregation, traceability). No ML, no dependencies beyond the standard library.
- `app.py` — Streamlit browser app UI, built on top of `hars_core.py`.
- `requirements.txt` — dependencies to install.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
This opens the app in your browser at http://localhost:8501

## Deploy free (so you can share a link)
1. Push these 3 files to a public GitHub repo.
2. Go to https://streamlit.io/cloud, sign in with GitHub, click "New app".
3. Point it at your repo and `app.py`. Deploy — free tier, no card required.

Alternative: Hugging Face Spaces (also free) — create a Space with SDK "Streamlit",
upload the same files.

## Design notes
- All scoring logic is local/offline — no cloud calls, consistent with HARS's
  own "no cloud dependency" design principle (Table 6/7, Part A).
- `hars_core.py` is deliberately separated from the UI so the same logic can
  later be ported to Kotlin for the Android version without rewriting the
  scoring rules from scratch — just re-implement the same functions.
