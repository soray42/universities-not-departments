#!/usr/bin/env bash
# Reproduce every number, table and figure of the paper.
#
#   ./reproduce.sh [all|data|analysis|paper] [--from-local RAW_DIR] [--orcid-local ORCID_DIR]
#                  [--only STEP,STEP,...] [--from STEP]
#
#   data       download the public inputs listed in data/sources.csv (scripts/download_data.py)
#   analysis   run the analysis scripts in dependency order (steps listed in STEPS below)
#   paper      build paper/nhb/si.pdf and paper/nhb/main.pdf with latexmk
#   all        data, analysis and paper (the default)
#
#   --from-local RAW_DIR    instead of downloading, symlink every file of data/sources.csv from an existing
#                           data/raw directory; the ORCID files are taken from RAW_DIR/../orcid unless
#                           --orcid-local is given
#   --only / --from         run a subset of the analysis steps
#
# Environment: PYTHON (default python3), WORKERS (worker processes per script, default 1), THREADS (BLAS threads,
# default 4), MEM_CAP (address-space limit per Python process in bytes, default 3000000000).
set -euo pipefail
cd "$(dirname "$0")"

PYTHON=${PYTHON:-python3}
WORKERS=${WORKERS:-1}
THREADS=${THREADS:-4}
MEM_CAP=${MEM_CAP:-3000000000}
LOGS=logs

TARGET=all
FROM_LOCAL=""
ORCID_LOCAL=""
ONLY=""
FROM=""
while [ $# -gt 0 ]; do
    case "$1" in
        all|data|analysis|paper) TARGET=$1 ;;
        --from-local) FROM_LOCAL=$2; shift ;;
        --orcid-local) ORCID_LOCAL=$2; shift ;;
        --only) ONLY=$2; shift ;;
        --from) FROM=$2; shift ;;
        -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
    shift
done

# analysis steps in dependency order (see the comment of each step below)
STEPS="wapman 24 28 56 55 57 58 52 59 73 65 67 68 40 62 72 76 66 75 78 79 80 81 82 84 85 checks 83 86"

# one Python process per call, capped address space, single-process unless WORKERS is set
py() {
    env PYTHONDONTWRITEBYTECODE=1 MALLOC_ARENA_MAX=2 ARROW_DEFAULT_MEMORY_POOL=system \
        OMP_NUM_THREADS="$THREADS" OPENBLAS_NUM_THREADS="$THREADS" MKL_NUM_THREADS="$THREADS" \
        ICC57_NPROC="$WORKERS" ER73_NPROC="$WORKERS" GST_WORKERS="$WORKERS" ERA68_WORKERS="$WORKERS" \
        GAP78_WORKERS="$WORKERS" GAP84_WORKERS="$WORKERS" GAP_NAMEJOIN=repaired \
        prlimit --as="$MEM_CAP" -- "$PYTHON" "$@"
}

script() { ls scripts/"$1"_*.py; }

run_step() {
    local s=$1
    case "$s" in
        # data/raw/wapman2022/: the 2026 upstream files in the formats the scripts read
        wapman) py -m src.wapman_release ;;
        # the field map of scripts/24 is read by later scripts as outputs/expanded66_gap_map.csv
        24) py "$(script 24)" && cp data/interim/expanded_gap_map.csv outputs/expanded66_gap_map.csv ;;
        28) py "$(script 28)" && cp data/interim/field_vs_generic.csv outputs/field_vs_generic.csv ;;
        # scripts/76 checks its pre-specification block against the copy frozen on 2026-09-27
        76) cp scripts/prespec/uk_triad_prespec_frozen.txt data/interim/ &&
            touch -d "2026-09-27 18:14:07.317515589 UTC" data/interim/uk_triad_prespec_frozen.txt &&
            py "$(script 76)" ;;
        72) py "$(script 72)" --workers "$WORKERS" ;;
        79) py "$(script 79)" --workers "$WORKERS" ;;
        75) py "$(script 75)" --only T0,T1,T3,T5,T6,T7,T8 --cache data/interim/theory_tests_cache --workers "$WORKERS" &&
            py "$(script 75)" --report --cache data/interim/theory_tests_cache ;;
        # checks computed for the paper from the main-design cells (Supplementary Information, section S1)
        checks)
            py scripts/paper_checks/c_headline.py repaired > "$LOGS/c_headline.log" &&
            py scripts/paper_checks/c_headline.py v1 > "$LOGS/c_headline_v1.log" &&
            py scripts/paper_checks/us_between.py > "$LOGS/us_between.log" &&
            py scripts/paper_checks/sample_flow.py > "$LOGS/sample_flow.log" &&
            py scripts/paper_checks/d_sens.py > "$LOGS/d_sens.log" &&
            py scripts/paper_checks/b2_opeid.py > "$LOGS/b2_opeid.log" &&
            py scripts/paper_checks/s3_fields.py > "$LOGS/s3_fields.log" &&
            py scripts/paper_checks/s3_check.py > "$LOGS/s3_check.log" ;;
        *) py "$(script "$s")" ;;
    esac
}

do_data() {
    if [ -n "$FROM_LOCAL" ]; then
        local orcid=${ORCID_LOCAL:-$(dirname "$(readlink -f "$FROM_LOCAL")")/orcid}
        "$PYTHON" scripts/download_data.py --from-local "$FROM_LOCAL" --orcid-local "$orcid"
    else
        "$PYTHON" scripts/download_data.py
    fi
}

do_analysis() {
    mkdir -p "$LOGS" data/interim outputs/figures/wapman2026
    local started=0
    [ -z "$FROM" ] && started=1
    for s in $STEPS; do
        [ "$s" = "$FROM" ] && started=1
        [ $started -eq 1 ] || continue
        if [ -n "$ONLY" ] && ! printf ',%s,' "$ONLY" | grep -q ",$s,"; then continue; fi
        echo "[$(date +%T)] step $s"
        local t0=$SECONDS
        if ! run_step "$s" > "$LOGS/step_$s.log" 2>&1; then
            echo "step $s failed; last lines of $LOGS/step_$s.log:" >&2
            tail -n 30 "$LOGS/step_$s.log" >&2
            exit 1
        fi
        echo "[$(date +%T)] step $s done ($((SECONDS - t0)) s)"
    done
}

do_paper() {
    # the main text resolves its Supplementary Information references through si.aux: build si first
    mkdir -p "$LOGS"
    if ! (cd paper/nhb && latexmk -pdf -interaction=nonstopmode -halt-on-error si.tex &&
          latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex) > "$LOGS/paper.log" 2>&1; then
        tail -n 30 "$LOGS/paper.log" >&2
        exit 1
    fi
    echo "built paper/nhb/si.pdf and paper/nhb/main.pdf (log: $LOGS/paper.log)"
}

case "$TARGET" in
    data) do_data ;;
    analysis) do_analysis ;;
    paper) do_paper ;;
    all) do_data; do_analysis; do_paper ;;
esac
