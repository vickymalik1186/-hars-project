# Environment Notes

**No secrets, credentials, API keys, or tokens are stored in this file or anywhere in
this repository.** This file documents the technical environment only.

## Prototyping Environment
- **Platform:** Google Colab (cloud-hosted, browser-based)
- **Runtime:** Python 3.x (Colab default)
- **Purpose:** Initial design and validation of the HARS scoring logic
  (`HARS_prototype.ipynb`) before conversion into the deployed application.

## Local Development Environment
- **OS:** Windows
- **Python version:** 3.14
- **Package manager:** pip
- **Git version:** 2.55.0 (installed via `winget install --id Git.Git -e --source winget`)

## Application Environment
- **Language:** Python 3.14
- **Framework:** Streamlit 1.59.1
- **Libraries:** pandas 3.0.3 (see `/config/requirements.txt` for the full pinned list
  as resolved at deploy time)
- **No ML libraries used** — deliberate design decision consistent with HARS's
  "no ML dependency" principle (Part A, Table 6).

## Deployment Environment
- **Platform:** Streamlit Community Cloud (free tier)
- **Repository connection:** GitHub (`expertswriteup-create/hars-project`), branch `main`
- **Entry point:** `src/app.py`
- **Dependency resolution:** `uv pip install`, reading `src/requirements.txt`
- **Data handling:** All scoring computation happens within the deployed session; no
  external database, no cloud storage of user-entered device data, no API keys or
  external service calls required.

## Version Control
- **Host:** GitHub (private repository)
- **Structure:** `/src`, `/docs`, `/config`, `/tests`, `/env`
- **Branching model:** feature branches (e.g. `feature/comparative-analysis`) merged
  into `main` via Pull Request once stable.

## Known Environment Issues Encountered
- Direct Git installer download was inaccessible on the local network; resolved via
  Windows' built-in `winget` package manager instead.
- Initial `git clone` failed due to a local network/firewall connectivity issue;
  resolved by using GitHub's web-based file upload interface as an alternative to
  command-line cloning.
