#!/bin/bash
#SBATCH --job-name=calox_vel_allevents_rev
#SBATCH --output=/lustre/research/hep/akshriva/CaloXDataAnalysis/jobs/log/velocityfits_allevents_revised_%j.out
#SBATCH --error=/lustre/research/hep/akshriva/CaloXDataAnalysis/jobs/log/velocityfits_allevents_revised_%j.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=32G
#SBATCH --partition=nocona

set -eo pipefail
set +u

workdir=/lustre/research/hep/akshriva/CaloXDataAnalysis
outdir="${workdir}/results/timing_velocity_allevents_revised"
tmpbase="${SLURM_TMPDIR:-/tmp}/calox_vel_allevents_rev_${SLURM_JOB_ID}"

mkdir -p "${outdir}" "${tmpbase}"
cd "${workdir}"
export PYTHONPATH="${workdir}${PYTHONPATH:+:${PYTHONPATH}}"

export CONDA_BACKUP_ROOTSYS=""
source /lustre/work/akshriva/miniconda3/etc/profile.d/conda.sh
conda activate /lustre/work/akshriva/aienv

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export PCM_CACHE_DIR="${tmpbase}/pcm"
export TMPDIR="${tmpbase}"
mkdir -p "${PCM_CACHE_DIR}"

mapfile -t runs < <(seq 1897 1943)

echo "Starting full-statistics velocity-fit run on ${HOSTNAME}"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Runs: ${runs[*]}"
echo "Events per run: all (no --last-event cap)"
echo "Output: ${outdir}"
echo "Python: $(which python)"

python scripts/plot_velocityfits.py \
    --runs "${runs[@]}" \
    --skip-sci \
    --reference-mpv-logic \
    --toa-bins 1500 \
    --toa-range 10 40 \
    --json-file data/datafiles.json \
    --runlist data/Runlist.json \
    --position-key "Table position X" \
    --position-label "Table position X" \
    --n-threads "${SLURM_CPUS_PER_TASK}" \
    --outdir "${outdir}"

echo "Velocity fits finished at $(date); running sim overlays"

# Sim overlays on the revised timing_summary.json (velocity only: attenuation
# inputs are unaffected and live in their own directory).
for xmin in "" -107 -195; do
    extra=()
    [[ -n "${xmin}" ]] && extra=(--velocity-x-min "${xmin}")
    python scripts/plot_sim_overlay_attenuation_velocity.py \
        --only velocity \
        --timing-dir "${outdir}" \
        "${extra[@]}"
done

echo "Finished at $(date)"
