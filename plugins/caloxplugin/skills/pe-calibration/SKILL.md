---
name: pe-calibration
description: ADC→photoelectron calibration for CaloX — the DRS step chain (Step1 integrals → Step2 multi-peak fits → Step3 ADC→PE lookup → Step4/5 TOA and rise time vs PE → Step6 attenuation corrections, pair timing resolution vs PE) and FERS high-gain PE gain from calibration/pedestal runs. Use when running or debugging compute_pe_integrals.py, fit_pe_peaks.py, convert_adc_to_pe.py, plot_pe_vs_event_quantity.py, plot_pair_timing_resolution_vs_pe.py or any FERS gain study.
---

# Photoelectron calibration

## DRS chain (tb2026, calibration run 1897 by default)

Results live under `results/PhotoElectrons/`. Each step reads the previous step's directory.

| Step | Script | Job | Output dir |
|---|---|---|---|
| 1 ADC integrals | `scripts/compute_pe_integrals.py --runs 1897` | `jobs/pe_step1_integral_calculation.slurm` | `Step1_IntegralCalculation` |
| 2 PE peak fits | `scripts/fit_pe_peaks.py --step1-dir … --run 1897 --npe-max 8` | `jobs/pe_step2_pe_fits.slurm` | `Step2_PEFits` |
| 3 ADC→PE lookup | `scripts/convert_adc_to_pe.py --step1-dir … --step2-dir …` | `jobs/pe_step3_adc_to_pe_conversion.slurm` | `Step3_ADCtoPEConversion` (`pe_bin_boundaries.json`) |
| 4 TOA vs PE | `scripts/plot_pe_vs_event_quantity.py --quantity toa --step3-dir …` | `jobs/pe_step4_time_vs_pe.slurm` | `Step4TimevsPE` |
| 5 rise time vs PE | `… --quantity risetime` | `jobs/pe_step5_pe_vs_risetime.slurm` | `Step5PEvsRiseTime` |
| 6a–d attenuation corrections | steps 1–3 over the scan runs + `scripts/plot_pe_vs_position.py` | `jobs/pe_step6{a,b,c,d}_*.slurm` | `Step6_AttenuationCorrections/…` |
| pair timing vs PE | `scripts/plot_pair_timing_resolution_vs_pe.py --step3-dir … --pe-definition …` then `…_plots.py --indir` | `jobs/pair_timing_resolution_vs_pe.slurm` | `PairTimingResolutionvsPE/<pe_def>` |

Key definitions:
- **Integral**: exactly one definition, `{ch}_energy_adaptive` = CFD-to-baseline-crossing integral (`variables.drs.add_cfd_to_baseline_energy`). It keeps the 0-PE pedestal peak (no amplitude threshold) and follows the pulse on both 3 mm and 6 mm fibres. Steps 4/5 and pair-timing recompute it the same way — do not swap in a different integral in one step only.
- **Fit**: `utils.fitter.fit_pe_spectrum`, multi-peak RooCrystalBall; peak positions are fitted, not bin maxima.
- **Lookup**: PE bin edges at the crossing points of consecutive fitted peaks.

Checks: gain (1 PE − pedestal) roughly constant across channels of one size; peaks equally spaced; chi2/ndf reasonable; the Step-3 plot crossings sit in the valleys. Step 4 uses `Time_cfd_mcp`, so the timing-calibration rules (MCP reference, range clipping) apply there too.

## FERS high-gain PE gain (tb2026)

Calibration runs 1804, 1806, 1807 (80 GeV e+, beam swept, HV 28 V); same-day pedestal runs 1792–1796 (HV 28 V) in `data/datafiles.json`. Read `FERS_Board{b}_energyHG` with uproot (fast); full calibration files are 5–9 GB, so run full passes as slurm jobs.

- **6 mm boards (2–5, 8–15)**: low-ADC spectrum in calibration runs ≈ pedestal run 1793 → it is SiPM dark-count/crosstalk structure. 1 PE sits ~55–60 ADC above a ~130–145 pedestal and is only a shoulder. **Use pedestal runs for 6 mm gain.**
- **3 mm boards 6/7**: clean separated peaks, gain ~80–85 ADC.
- Boards 0/1 are read out but not in the tb2026 FERS map.
- **Do not use `fit_pe_spectrum` on FERS** — it is tuned for DRS integrals, locks onto about half the true spacing (chi2/ndf ~300). Use a dedicated model: μ_n = ped + n·G, σ_n² = s0² + n·s1², gain seeded from the spectrum's FFT/autocorrelation.
- `FERS_pedestals_tb2026.json` uses plain means; the dark-count tail biases it upward relative to the true 0-PE peak.

## 2025 data

The Sep-2025 90° along-fibre scan (runs 1499–1513, 40 GeV e+) PE chain lives in the `../CaloXDataAnalysis_pe2025` worktree (branch `pe_studies_2025`), results in `results/PhotoElectrons2025`. See the `run-conventions` skill for the 2025 DRS anchor and PYTHONPATH rules.
