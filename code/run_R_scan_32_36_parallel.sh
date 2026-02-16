#!/usr/bin/env bash
set -euo pipefail

# run_R_scan_32_36_parallel.sh
# Parallel scan of R in [32,36] (step 0.1) using maass_levelone_driver.sage
# Launches up to N_JOBS concurrent jobs (default 2). Writes logs to outputs/R_scan_32_36_parallel/

OUTDIR=outputs/R_scan_32_36_parallel
mkdir -p "$OUTDIR"
START=32.0
END=36.0
STEP=0.1
Y=0.02
SYMM=-1
N_JOBS=${N_JOBS:-2}

echo "Parallel scan start: R in [$START,$END] step $STEP, Y=$Y, symmetry=$SYMM, jobs=$N_JOBS"

# generate R list with Python for exact formatting
RS=$(python3 - <<PY
start = float("$START")
end = float("$END")
step = float("$STEP")
r = start
vals = []
while r <= end + 1e-12:
  vals.append(r)
  r = round(r + step, 12)
print(' '.join(["{:.2f}".format(v) for v in vals]))
PY
)

run_one() {
  R="$1"
  FILE="$OUTDIR/driver_R_$(printf "%05.2f" $R).txt"
  echo "[PID $$] Starting R=$R -> $FILE"
  # run the Sage driver; redirect stdout/stderr
  sage maass_levelone_driver.sage $R $Y $SYMM > "$FILE" 2>&1
  echo "[PID $$] Finished R=$R"
}

# control parallelism using a job counter and wait
pids=()
for R in $RS; do
  # start job in background
  run_one $R &
  pids+=("$!")

  # if number of background jobs reached limit, wait for any to finish
  while [ "$(jobs -rp | wc -l)" -ge "$N_JOBS" ]; do
    sleep 0.5
  done
done

# wait for remaining jobs
wait

echo "Parallel scan complete. Logs in $OUTDIR"
