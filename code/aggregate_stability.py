#!/usr/bin/env python3
"""
Aggregate stability sweep results and produce robust per-file and per-R summaries.
Writes:
 - outputs/scan_postprocess/stability_summary_by_file.csv
 - outputs/scan_postprocess/stability_summary_by_R.csv
 - outputs/scan_postprocess/plots/stability_hist.png
 - outputs/scan_postprocess/plots/stability_vs_R.png

Usage:
  python3 aggregate_stability.py --posts outputs/scan_postprocess --boot 2000
"""
import os
import glob
import csv
import argparse
import math
from statistics import median

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except Exception:
    np = None
    plt = None


def ensure_dir(d):
    os.makedirs(d, exist_ok=True)


def read_stab_file(path):
    rows = []
    with open(path, 'r') as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            try:
                delta = float(r['delta'])
                smooth = float(r['smooth'])
                R = float(r['R'])
                Y = float(r['Y'])
                M = int(float(r['M']))
                L0 = float(r['L0'])
                Lp = float(r['Lprime'])
                rows.append({'delta':delta,'smooth':smooth,'R':R,'Y':Y,'M':M,'L0':L0,'Lprime':Lp})
            except Exception:
                continue
    return rows


def bootstrap_median(samples, reps=2000):
    if np is None:
        # simple non-numpy bootstrap
        import random
        n = len(samples)
        if n == 0:
            return (None,None,None)
        meds = []
        for _ in range(reps):
            s = [random.choice(samples) for _ in range(n)]
            meds.append(median(s))
        meds.sort()
        lo = meds[int(0.025*reps)]
        hi = meds[int(0.975*reps)]
        return (median(samples), lo, hi)
    else:
        arr = np.array(samples)
        if arr.size == 0:
            return (None,None,None)
        n = arr.size
        idx = np.random.randint(0, n, size=(reps, n))
        # compute median across axis=1 for each bootstrap sample
        res = np.median(arr[idx], axis=1)
        lo = np.percentile(res, 2.5)
        hi = np.percentile(res, 97.5)
        return (float(np.median(arr)), float(lo), float(hi))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--posts', default='outputs/scan_postprocess')
    p.add_argument('--boot', type=int, default=2000)
    args = p.parse_args()

    posts = args.posts
    stab_dir = os.path.join(posts, 'stability')
    if not os.path.isdir(stab_dir):
        raise SystemExit('stability dir not found: '+stab_dir)

    files = sorted(glob.glob(os.path.join(stab_dir, '*.stab.csv')))
    if not files:
        raise SystemExit('no stability files found in '+stab_dir)

    per_file_rows = []
    by_R = {}

    for fp in files:
        rows = read_stab_file(fp)
        if not rows:
            continue
        lps = [r['Lprime'] for r in rows]
        med, lo, hi = bootstrap_median(lps, reps=args.boot)
        frac_pos = sum(1 for v in lps if v > 0)/len(lps)
        n = len(lps)
        # take R and Y from first row (all rows same file)
        R = rows[0]['R']
        Y = rows[0]['Y']
        per_file_rows.append({'file':os.path.basename(fp),'R':R,'Y':Y,'n':n,'median':med,'lo':lo,'hi':hi,'frac_pos':frac_pos})
        by_R.setdefault(R,[]).extend(lps)

    # write per-file summary
    ensure_dir(os.path.join(posts,'plots'))
    file_out = os.path.join(posts,'stability_summary_by_file.csv')
    with open(file_out,'w',newline='') as f:
        w = csv.DictWriter(f, fieldnames=['file','R','Y','n','median','lo','hi','frac_pos'])
        w.writeheader()
        for r in per_file_rows:
            w.writerow(r)

    # aggregate by R
    rows_R = []
    for R, samples in sorted(by_R.items()):
        med, lo, hi = bootstrap_median(samples, reps=args.boot)
        frac_pos = sum(1 for v in samples if v > 0)/len(samples)
        rows_R.append({'R':R,'n':len(samples),'median':med,'lo':lo,'hi':hi,'frac_pos':frac_pos})

    R_out = os.path.join(posts,'stability_summary_by_R.csv')
    with open(R_out,'w',newline='') as f:
        w = csv.DictWriter(f, fieldnames=['R','n','median','lo','hi','frac_pos'])
        w.writeheader()
        for r in rows_R:
            w.writerow(r)

    # plots
    try:
        if plt is None:
            print('matplotlib not available; skipping plots')
            return
        # histogram of per-R medians
        meds = [r['median'] for r in rows_R if r['median'] is not None]
        plt.figure(figsize=(6,4))
        plt.hist(meds, bins=8)
        plt.xlabel("L'(1/2) median per-R")
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(posts,'plots','stability_hist.png'), dpi=200)
        plt.close()

        # scatter median vs R with errorbars
        Rs = [r['R'] for r in rows_R]
        meds = [r['median'] for r in rows_R]
        los = [r['median']-r['lo'] if r['lo'] is not None else 0 for r in rows_R]
        his = [r['hi']-r['median'] if r['hi'] is not None else 0 for r in rows_R]
        plt.figure(figsize=(6,4))
        plt.errorbar(Rs, meds, yerr=[los,his], fmt='o')
        plt.axhline(0, color='k', linewidth=0.5)
        plt.xlabel('R')
        plt.ylabel("L'(1/2) median")
        plt.tight_layout()
        plt.savefig(os.path.join(posts,'plots','stability_vs_R.png'), dpi=200)
        plt.close()
    except Exception as e:
        print('Plotting failed:', e)

    print('Wrote:', file_out)
    print('Wrote:', R_out)
    print('Plots (if created) in', os.path.join(posts,'plots'))

if __name__ == '__main__':
    main()
