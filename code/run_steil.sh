#!/usr/bin/env bash
set -e
mkdir -p outputs
for R in 30.279 30.404 31.057 31.916; do
  Rf=$(echo $R | tr . _)
  echo "=== RUNNING R=$R ==="
  sage maass_levelone_driver.sage $R 0.001 -1 > outputs/driver_${Rf}.txt 2>&1 || echo "FAILED R $R"
  echo "--- tail of output ---"
  tail -n 5 outputs/driver_${Rf}.txt || true
  echo
done
ls -l outputs
