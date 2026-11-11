---
name: slurm-jobs
description: Write, submit and follow CaloX analysis jobs on the TTU HPCC slurm cluster (nocona partition, conda env aienv, jobs/ and jobs/log/ layout). Use whenever a CaloX study needs a full-statistics pass, a rerun into a new results directory, or waiting on a running job.
---

# CaloX slurm jobs

## Template

Copy an existing job in `jobs/` that runs the same script, and keep its flags. The house layout:

```bash
#!/bin/bash
#SBATCH --job-name=calox_<study>
#SBATCH --output=/lustre/research/hep/akshriva/CaloXDataAnalysis/jobs/log/<study>_%j.out
#SBATCH --error=/lustre/research/hep/akshriva/CaloXDataAnalysis/jobs/log/<study>_%j.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1            # required on this cluster
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=32G
#SBATCH --partition=nocona

set -eo pipefail
set +u

workdir=/lustre/research/hep/akshriva/CaloXDataAnalysis
outdir="${workdir}/results/<study>"
tmpbase="${SLURM_TMPDIR:-/tmp}/calox_<study>_${SLURM_JOB_ID}"
mkdir -p "${outdir}" "${tmpbase}"
cd "${workdir}"
export PYTHONPATH="${workdir}${PYTHONPATH:+:${PYTHONPATH}}"

export CONDA_BACKUP_ROOTSYS=""
source /lustre/work/akshriva/miniconda3/etc/profile.d/conda.sh
conda activate /lustre/work/akshriva/aienv

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export PCM_CACHE_DIR="${tmpbase}/pcm"   # ROOT module cache per job
export TMPDIR="${tmpbase}"
mkdir -p "${PCM_CACHE_DIR}"

mapfile -t runs < <(seq 1897 1943)
python scripts/<script>.py --runs "${runs[@]}" --n-threads "${SLURM_CPUS_PER_TASK}" --outdir "${outdir}" ...
```

## Rules

- **PYTHONPATH**: the env has `calox` pip-installed in editable mode from the main checkout. Always export `PYTHONPATH=<checkout>`, and point `workdir` at the worktree when running from one — otherwise the job silently imports code from the wrong checkout.
- **Revisions**: put a revised study in a new job file (`<study>_revised_….slurm`) and a new `results/<study>_revised` directory. Keep the old job and results as the baseline.
- **Downstream steps** that only read the main output (sim overlays, report regeneration) go at the end of the same job, so they can never run on stale input.
- Before submitting, smoke-test the changed scripts: `python scripts/<script>.py --help` (catches import errors after merges), or one run with `--last-event 1000`.

## Submit and wait

```bash
sbatch jobs/<file>.slurm                       # prints the job ID
squeue -j <id> -o "%.10i %.8T %.10M %R"
sacct -j <id> -X -o JobID,State,ExitCode,Elapsed -n
```

To wait without polling, run in the background: `until ! squeue -h -j <id> | grep -q .; do sleep 60; done; sacct -j <id> -X -o JobID,State,ExitCode,Elapsed -n`.

When it ends: check `State`/`ExitCode`, `grep -iE "error|traceback|\[WARN\]"` in the `.err` and `.out`, and list the files written. The full 47-run velocity job takes about 40 minutes.
