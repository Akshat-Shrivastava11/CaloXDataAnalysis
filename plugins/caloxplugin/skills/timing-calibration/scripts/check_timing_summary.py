#!/usr/bin/env python3
"""Sanity-check a timing_summary.json written by scripts/plot_velocityfits.py.

Reports, per (material, size): median per-channel TOA slope below and above a
split position, the spread of timing points, and how many points sit within
the MPV window of either edge of the booked TOA range (clipping). Also reports
how many runs had the MCP reference applied.

Usage: check_timing_summary.py SUMMARY.json [--split-x -106] [--edge-window 1.2]
Exit code 1 if any point is near an edge or any run lacks the MCP reference.
"""
import argparse
import json
import sys

import numpy as np


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("summary")
    p.add_argument("--split-x", type=float, default=-106.0)
    p.add_argument("--edge-window", type=float, default=1.2,
                   help="ns; the get_hist_mpv window (window_ts) used for the MPV")
    a = p.parse_args()

    d = json.load(open(a.summary))
    lo, hi = d["toa_range_ns"]
    pos = {int(r): x for r, x in d["run_positions_mm"].items()}
    applied = d.get("mcp_reference_applied_by_run", {})
    refs = d.get("mcp_reference_name_by_run") or {"all": d.get("mcp_reference_name")}
    n_applied = sum(bool(v) for v in applied.values())

    print(f"TOA range [{lo}, {hi}] ns; MCP reference applied in {n_applied}/{len(applied)} runs; "
          f"references: {sorted({str(v) for v in refs.values()})}")
    for fam, f in sorted(d.get("shared_slope_fits", {}).items()):
        print(f"  shared {fam}: v = {f['speed_cm_per_ns']:.2f} cm/ns ({f['n_channels']} channels)")

    groups, bad = {}, 0
    for ch, info in d["channels"].items():
        pts = [(pos[int(r)], q["mean_ns"]) for r, q in d["timing_fits"].get(ch, {}).items()
               if q.get("fit_ok") and q.get("mean_ns") is not None and int(r) in pos]
        if not pts:
            continue
        x, t = np.array(pts).T
        g = groups.setdefault((info.get("material"), info.get("size")),
                              {"below": [], "above": [], "t": [], "edge": 0})
        b, u = x < a.split_x, x > a.split_x
        if b.sum() > 2 and u.sum() > 2:
            g["below"].append(np.polyfit(x[b], t[b], 1)[0] * 1e3)
            g["above"].append(np.polyfit(x[u], t[u], 1)[0] * 1e3)
        g["t"] += list(t)
        g["edge"] += int(np.sum((t > hi - a.edge_window) | (t < lo + a.edge_window)))

    print(f"\n{'family':22s} {'slope<split':>12s} {'slope>split':>12s} {'t p5..p95 [ns]':>16s} {'near edge':>10s}")
    for (mat, size), g in sorted(groups.items(), key=lambda kv: str(kv[0])):
        sb = np.median(g["below"]) if g["below"] else float("nan")
        sa = np.median(g["above"]) if g["above"] else float("nan")
        p5, p95 = np.percentile(g["t"], [5, 95])
        flag = ""
        if sa and abs(sb - sa) > 0.2 * abs(sa):
            flag = "  <-- slope changes >20% across split"
        print(f"{str(mat)+' '+str(size):22s} {sb:9.2f} ps/mm {sa:9.2f} ps/mm {p5:7.2f}..{p95:<7.2f} "
              f"{g['edge']:4d}/{len(g['t']):<5d}{flag}")
        bad += g["edge"]

    ok = bad == 0 and n_applied == len(applied)
    print("\nRESULT:", "OK" if ok else "PROBLEM (edge-clipped points or missing MCP reference)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
