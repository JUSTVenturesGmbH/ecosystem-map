# Agents Guide

This document is meant for agents (human or automated) who want a quick orientation on how the repository is laid out, how data flows through the system, and which scripts keep the dataset valid.

## Repository Topography
- `data/` – YAML descriptors for ecosystem projects. Subfolders (e.g., `data/team`) contain specialty lists, but every file is validated against `data.schema.yml`.
- `data.schema.yml` – JSON Schema consumed by the validation tooling (`pajv`) to keep YAML structure consistent with the contribution rules described in `CONTRIBUTING.md`.
- `scripts/` – Operational utilities:
  - `render_map.py` regenerates `README.md` tables from YAML.
  - `metrics.py` refreshes the social/dev metrics that feed tables.
  - `validate.sh` iterates over `data/*.yaml` with `pajv` to enforce the schema.
  - `requirements.txt` captures Python deps (mainly `ruamel.yaml`) used by both Python scripts.
- `ecosystem-map/` – React app that powers https://justventuresgmbh.github.io/ecosystem-map/. Its build artifacts are fed by `dist/projects.json`, which in turn comes from combining all YAML files.
- `.github/workflows/` – Automation entry points:
  - `main.yml` runs on every push and during manual dispatch. It installs Node 20, runs the YAML validator, JS/TS lint, CSS lint, builds the site, copies shared assets, generates `dist/projects.json` via `src/utils/combineYAMLs.ts`, and uploads the static bundle when the `main` branch is updated.
  - `metrics_update.yml` runs monthly (or manually) to install Python deps, execute `metrics.py`, regenerate `README.md` through `render_map.py`, and open a PR with the changed YAML/markdown files.

The `.git/logs/refs/remotes/origin/feat/render-markdown-ecosystem-map` entry shows the upstream branch that first introduced the markdown rendering automation; expect future synchronization work to piggyback on that branch.

## Data Authoring Lifecycle
1. Start from `CONTRIBUTING.md` to copy the YAML template. Every entry must include at least `name`, `description`, `web.site`, and `layer`. Optional sections (`category`, `target_audience`, `treasury_funded`, etc.) must respect the enumerations defined in `data.schema.yml`.
2. Place the new or updated YAML file inside `data/` (or the relevant subfolder). Keep filenames kebab-cased and descriptive (e.g., `Acala-Karura.yaml`).
3. Capture metrics (follower counts, GitHub stars, etc.) in the `metrics` block when available. Each metric is a chronological list of `{date, value}` pairs (`date` must be ISO `YYYY-MM-DD` and inside the `2020-2039` window set by the schema).
4. Run the validation steps below before opening a PR.

## Validation & Build Checklist
The CI workflow (`main.yml`) will fail fast if anything here is skipped. Run the commands from the repository root unless noted otherwise.

1. **Install dependencies**
   ```bash
   cd ecosystem-map
   npm ci
   cd ..
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r scripts/requirements.txt
   ```
   (Reuse an existing virtualenv if you already have one.)
2. **Schema validation**
   ```bash
   cd ecosystem-map
   npm run lint:yaml   # wraps scripts/validate.sh -> pajv + data.schema.yml
   ```
   Fix any reported file path or enum issues directly inside `data/*.yaml`.
3. **Frontend lint/build sanity**
   ```bash
   npm run lint
   npm run stylelint
   npm run build
   ```
   These steps mirror `.github/workflows/main.yml`. The build stage also copies `img/*` into `dist/` and generates `dist/projects.json` by running `node --experimental-specifier-resolution=node --loader ts-node/esm src/utils/combineYAMLs.ts ../data/ > dist/projects.json`.
4. **README regeneration (optional but useful before landing dataset changes)**
   ```bash
   cd ..
   python scripts/render_map.py > README.md
   ```
   Commit the README refresh alongside any YAML modifications when tables change.
5. **Metrics refresh (only when actively updating social/dev stats)**
   ```bash
   cd scripts
   python metrics.py
   python render_map.py > ../README.md
   ```
   The monthly `metrics_update.yml` workflow automates this, but running it locally helps verify API access and formatting before triggering automation.

## Typical Troubleshooting Tips
- `pajv` errors referencing “additional properties” usually mean a typo in a field name; cross-check with `data.schema.yml`.
- Date validation requires zero-padded months/days (e.g., `2024-03-07`, not `2024-3-7`).
- When `scripts/render_map.py` hangs, confirm `ruamel.yaml` is installed in the Python environment referenced by the shebang-less script.
- The frontend build expects the `img/` directory to contain all assets referenced by YAML files (via `web.logo`). If a logo is missing, add it before running `npm run build`.

Following this checklist keeps local work aligned with the CI workflows and ensures new data points propagate to both the README tables and the published site without surprises.
