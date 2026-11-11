---
name: upstream-sync
description: Bring upstream CaloXDataAnalysis changes (yongbinfeng/CaloXDataAnalysis origin/main) into the user's fork branch safely, find what the merge breaks, and decide which results must be regenerated. Use when the user asks to pull, update, sync or merge with upstream, or when results may be stale relative to upstream fixes.
---

# Syncing with upstream

## Remotes

- `origin` = yongbinfeng/CaloXDataAnalysis (upstream, `main`).
- `fork` = the user's fork. The 2026 branch `Akshats_timingstudies_26` tracks `fork/Akshats_timingstudies_26`, so a plain `git pull` does **not** bring in upstream. Use `git fetch origin` then `git merge origin/main`.

## Procedure

1. `git fetch origin`, then `git log --oneline HEAD..origin/main` — read the commit list and `git show --stat` the ones touching the code you use.
2. Dry run: `git merge-tree --write-tree HEAD origin/main` (conflicts are listed; exit code non-zero on conflict).
3. Check the working tree: `git status --short`; for each modified file make sure upstream does not touch it (`git diff --stat HEAD...origin/main -- <file>`), and that upstream does not add a file with the same path as an untracked one.
4. Ask before merging if anything conflicts. If clean: `git merge --no-edit origin/main`.
5. **Find breakage**: grep the branch's own scripts for names upstream removed or renamed (`git diff HEAD~1 -- <module>` on the merge commit for removed definitions), then smoke-test every script you use with `python scripts/<s>.py --help` under `PYTHONPATH=<checkout>`.
6. **Decide what to rerun**: list the upstream changes that alter physics output (references, ranges, selections, kernels) and every results directory produced by code paths they touch. Rerun into `<study>_revised` directories.

## Known upstream changes (merged Nov 2026)

- 39fd229: `variables.drs.MCP_REF` removed → use `channels.channel_map.get_mcp_reference(run)` (`MCP_DS_1` for tb2026). Before this, `Time_cfd_mcp` had **no** MCP shift for any tb2026 run. All three of `scripts/plot_velocityfits.py`, `scripts/compare/plot_velfitsperchannel.py`, `scripts/compare_timing_runs.py` were ported; their JSON now has `mcp_reference_name_by_run`.
- 3bb8600: `configs/plot_config.get_drs_time_ns_finebins_range` (6.5, 16.5) → (15, 35); broad range (0, 40). With the MCP shift the in-time peaks are ~22–29 ns.
- a8aa034: TS fine-bins range widened to (400, 600) — documents the silent-clipping MPV bug.
- `compute_cfd_integral` gained rise/fall/FWHM, `energy_short` and saturation outputs; the reference LED time is sub-sample interpolated; optional in-time search via `prepare(drs_intime=True)` (not default).

Any job that passes its own `--toa-range` (not the config default) must be updated by hand — see the `timing-calibration` skill.
