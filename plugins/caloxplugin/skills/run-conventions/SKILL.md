---
name: run-conventions
description: CaloX run numbers, scan positions, data files and per-campaign conventions (tb2026 z-scan, FERS calibration and pedestal runs, Sep-2025 and Aug-2025 runs, git worktrees for 2025 analyses, DRS anchors and MCP-clean definitions). Use when choosing runs, reading positions, or working on 2025 vs 2026 data.
---

# Runs and conventions

## Files

- `data/datafiles.json` — run → ROOT file paths (pass with `--json-file`).
- `data/Runlist.json` — run metadata; scan position via `--position-key "Table position X"` (mm).
- `channels/channel_map.py` — channel maps per run: `get_mcp_channels(run)`, `get_mcp_reference(run)`, `get_pid_channels`, `get_service_drs_channels`. Channel maps change with run number, so always pass the run.

## tb2026

| Runs | What |
|---|---|
| 1897–1943 | along-fibre z-scan used for velocity, attenuation, rise time, pair timing (x ≈ −296 … +36 mm and beyond) |
| 1897 | single calibration run for the DRS PE chain |
| 1804, 1806, 1807 | FERS energy-calibration runs (80 GeV e+, swept, HV 28 V) |
| 1792–1796 | same-day FERS pedestal runs (HV 28 V) |

- MCPs: `MCP_DS_0/US_0/DS_1/US_1`; the timing reference is `MCP_DS_1` (via `get_mcp_reference`).
- Event selection used by the timing studies: `apply_mcp_selection(flag_only=True)` then `apply_beam_pid_selection(particle="mcp_clean")` unless `--no-mcp-clean`.
- Channel families: CerQuartz, CerPlastic, Sci; sizes 3 mm and 6 mm. Most timing studies use `--skip-sci`.

## 2025 data (separate worktrees)

2025 analyses are kept off the 2026 branch, in git worktrees next to the main checkout:

- `../CaloXDataAnalysis_target2025` (branch `target_runs_2025` off `main`): Aug-2025 interaction-target runs 1295–1306 (120 GeV π, baseline 1264/1265), DQM tower heatmaps and shower-blob study. Results in `results/2025_JETdata` (`DQM/`, `ShowerBlobs/`).
- `../CaloXDataAnalysis_pe2025` (branch `pe_studies_2025` off the timing branch): PE chain on the Sep-2025 90° along-fibre scan, runs 1499–1513 (40 GeV e+). Results in `results/PhotoElectrons2025`.

2025 DRS specifics:
- Pulses peak about −300 TS from the group Channel8 reference crossing → use `--anchor-offset -300`.
- The last ~20 cells (TS > 1000) contain an artifact; keep windows below that.
- Sep-2025 `mcp_clean` = `MCP_US_0 && MCP_DS_0` (~22% of events).

**Worktree trap:** the conda env imports `calox` from the main checkout (editable install). Jobs and interactive runs from a worktree must `export PYTHONPATH=<worktree>`.
