# caloxplugin

Claude Code plugin for CaloX test-beam analysis in this repository.

## Install

In Claude Code:

```
/plugin marketplace add /lustre/research/hep/akshriva/CaloXDataAnalysis
/plugin install caloxplugin@calox-tools
```

If you work from your own checkout, pass its path to `/plugin marketplace add` instead. The marketplace file is `.claude-plugin/marketplace.json` at the repository root.

## Agents

| Agent | Model | Role |
|---|---|---|
| `caloxplugin:akcalo` | Sonnet | Analysis work: scripts, slurm jobs, reruns into `<study>_revised` directories, result summaries. |
| `caloxplugin:donkbin` | Opus | Read-only validator: logs, histogram-edge clipping, MCP reference, fit quality, slope consistency, data vs sim, stale inputs. Ends with PASS / WARN / FAIL. |

Example: "use akcalo to rerun the rise-time study, then have donkbin validate it".

## Skills

| Skill | Covers |
|---|---|
| `timing-calibration` | MCP-referenced time of arrival, velocity fits, sim overlays, TOA range and clipping; includes `scripts/check_timing_summary.py` |
| `pe-calibration` | DRS ADC→PE chain (steps 1–6, pair timing vs PE) and FERS high-gain gain |
| `slurm-jobs` | Job template for the TTU HPCC (nocona, aienv, PYTHONPATH), submitting and waiting |
| `upstream-sync` | Merging `origin/main` into the fork branch and finding what it breaks |
| `run-conventions` | Run lists and positions for tb2026 and 2025, worktrees, DRS anchors, `mcp_clean` |

Check a timing summary directly:

```bash
python plugins/caloxplugin/skills/timing-calibration/scripts/check_timing_summary.py \
    results/timing_velocity_allevents_revised/timing_summary.json
```
