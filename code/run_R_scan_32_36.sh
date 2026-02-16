#!/usr/bin/env bash
set -euo pipefail

# run_R_scan_32_36.sh
# Sequential scan of R in [32,36] (step 0.1) using maass_levelone_driver.sage
# Writes driver logs to outputs/R_scan_32_36/driver_R_XX.XX.txt

OUTDIR=outputs/R_scan_32_36
mkdir -p "$OUTDIR"
START=32.0
END=36.0
STEP=0.1
Y=0.02
SYMM=-1

echo "Scan start: R in [$START,$END] step $STEP, Y=$Y, symmetry=$SYMM"

# Use seq to generate floats; falls back to python if seq doesn't support floats
if seq --help 2>&1 | grep -q "floating"; then
  RS=$(seq $START $STEP $END)
else
  RS=$(python3 -c "import numpy as _; print(' '.join([f'{x:.2f}' for x in _frange := list(_:=__import__('numpy').arange($START,$END+$STEP/2,$STEP))]))")
fi

for R in $RS; do
  FILE="$OUTDIR/driver_R_$(printf "%05.2f" $R).txt"
  echo "Running R=$R -> $FILE"
  # Run sequentially to avoid overwhelming resources; remove 'time' if not desired
  sage maass_levelone_driver.sage $R $Y $SYMM > "$FILE" 2>&1
  echo "Finished R=$R"
done

echo "Scan complete. Logs in $OUTDIR"
