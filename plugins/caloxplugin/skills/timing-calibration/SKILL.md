---
name: timing-calibration
description: DRS timing calibration for CaloX tb2026 — MCP-referenced time of arrival (Time_cfd_mcp), per-channel and shared-slope velocity fits along the fibre (z-scan runs 1897–1943), TOA histogram ranges, core-MPV extraction, sim overlays, and how to check them for clipping. Use when running or debugging plot_velocityfits.py, compare_timing_runs.py, plot_risetime_vs_z.py, pair timing resolution, or the attenuation/velocity sim overlays.
---

# DRS timing and velocity calibration (tb2026)

## Pipeline

1. **Time of arrival per event** — `{ch}_Time_cfd_mcp` [ns], built in `variables/drs.py` (`process_drs_data`). CFD time from `compute_cfd_integral` (`utils/functions.cc`, searches the whole 1024-sample record, 5 ADC threshold), minus the group reference, minus the MCP reference.
2. **MCP reference** — always `channels.channel_map.get_mcp_reference(run)` (prefers `MCP_DS_1`, then `MCP_1`, else `None`). Never hard-code an MCP name. The old `variables.drs.MCP_REF` was removed upstream (39fd229) because it pointed at `MCP_1`, which tb2026 runs do not have, so the MCP shift was silently never applied.
3. **Per-run timing point** — `scripts/plot_velocityfits.py` books one TOA histogram per channel per run (`--toa-range`, `--toa-bins`). With `--reference-mpv-logic` the point is the core MPV from `utils.utils.get_hist_mpv(hist, window_ts=1.2)`: densest cluster, then weighted mean over ±1.2 ns.
4. **Velocity** — TOA vs table position (`--position-key "Table position X"` from `data/Runlist.json`), per channel and with a shared slope per material family. Output: `timing_overlays.{root,html}`, `timing_velocity_fits.html`, `timing_summary.json`.
5. **Sim overlay** — `scripts/plot_sim_overlay_attenuation_velocity.py --only velocity --timing-dir <outdir> [--velocity-x-min -107]` reads only `timing_summary.json` and writes `<outdir>/sim_overlay[_xmin<val>]/`. Rerun it every time the timing summary changes.

## Settings that work (after the Nov-2026 upstream merge)

| Setting | Value | Why |
|---|---|---|
| `--toa-range` | `10 40` | With the MCP shift applied, peaks sit at ~21–27 ns (3 mm) and ~18–24 ns (6 mm) |
| `--toa-bins` | `1500` | 0.02 ns bins |
| flags | `--skip-sci --reference-mpv-logic` | as in the reference job |
| job | `jobs/velocityfits_allevents_revised_1897_1943.slurm` | runs fits + all three sim overlays |

## The clipping trap (why `results/timing_velocity_allevents` was wrong)

The old job used `--toa-range 6.5 16.5`. Without the MCP shift the 3 mm peaks sat at 15–16.8 ns, so at x < −107 mm the peak ran past 16.5 ns into overflow, the ±1.2 ns MPV window was cut on the right, and the MPV pinned at ≈16.0 ns. Result: 3 mm plastic/quartz TOA looked flat for x < −107 (slope −2.4 instead of −5.5 ps/mm). The 6 mm channels (peaks 12–14 ns) were unaffected, which is the tell-tale sign.

**Rule:** any histogram-derived point must sit more than the MPV window (1.2 ns) inside both edges of the booked range. Change the range whenever the reference (MCP, anchor, group reference) changes.

## Reference numbers (revised run, runs 1897–1943, all events)

| Family | slope x<−106 | slope x>−106 | shared-fit v |
|---|---|---|---|
| 3 mm CerPlastic | −5.55 ps/mm | −5.62 ps/mm | 17.73 cm/ns (plastic, both sizes) |
| 3 mm CerQuartz | −5.31 | −5.36 | 18.52 cm/ns (quartz, both sizes) |
| 6 mm CerPlastic | −5.70 | −5.52 | |
| 6 mm CerQuartz | −5.41 | −5.51 | |

Sim (DREAMSim longscan): plastic ≈18.8, quartz ≈19.6 cm/ns — the data are about 1 cm/ns slower in both. The full-x fit and the x ≥ −107 refit should agree to about 0.05 cm/ns.

## Checks after every run

Run the bundled checker (in this skill's `scripts/` directory):

```bash
python <skill-dir>/scripts/check_timing_summary.py results/<dir>/timing_summary.json [--split-x -106] [--edge-window 1.2]
```

It prints, per material × size: median slope below and above the split, the range of timing points, and the number of points within the edge window of the TOA range, plus how many runs had the MCP reference applied. Expect: 0 edge points, MCP applied in every run, the two slopes within ~10% of each other.

Also check the job log for `[WARN] Run N: configured MCP reference ... is not live`.

## Other timing studies that use `Time_cfd_mcp`

Anything run before the merge was produced without the MCP shift and with ranges tuned to the unshifted times. Re-check ranges before rerunning: `scripts/plot_risetime_vs_z.py` (rise time itself is MCP-independent), `scripts/plot_pair_timing_resolution_vs_pe.py` (dt between adjacent channels — the MCP term cancels, but any absolute-time window does not), `scripts/plot_pe_vs_event_quantity.py --quantity toa`, `scripts/compare_timing_runs.py`.
