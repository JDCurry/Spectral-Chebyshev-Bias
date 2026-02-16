#!/usr/bin/env python3
"""
compute_L_stats.py
Postprocess coefficient dumps to compute L(1/2) and finite-difference L'(1/2) across forms,
produce a small CSV and plots (requires matplotlib + numpy).

Run inside the Sage container (it has matplotlib available):
  sage -python compute_L_stats.py --posts outputs/scan_postprocess --delta 0.01 --smooth 2000

Outputs:
  outputs/scan_postprocess/L_derivatives.csv
  outputs/scan_postprocess/plots/Lprime_hist.png
  outputs/scan_postprocess/plots/Lprime_vs_R.png
"""
import os
import math
import argparse
import csv

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
except Exception:
    plt = None
    np = None


def chi3(n):
    r = n % 3
    return 0 if r == 0 else (1 if r == 1 else -1)


def read_coeff_file(path):
    a = []
    with open(path,'r') as f:
        for line in f:
            if not line.strip():
                continue
            i, val = line.split()[:2]
            try:
                a.append(float(val))
            except:
                pass
    return a


def L_of_s(a, s, smooth):
    tot = 0.0
    for n, an in enumerate(a, start=1):
        c = chi3(n)
        if c == 0:
            continue
        tot += an * c * (n**(-s)) * math.exp(-n/float(smooth))
    return tot


def find_coeff_files(posts_dir):
    res = []
    for sub in sorted(os.listdir(posts_dir)):
        d = os.path.join(posts_dir, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.startswith('coeffs_') and fn.endswith('.txt'):
                res.append(os.path.join(d, fn))
    return res


def parse_filename(fn):
    # coeffs_R_{R:.12f}_Y_{Y:.3f}.txt
    base = os.path.basename(fn)
    parts = base.split('_')
    try:
        R = float(parts[2])
        Y = float(parts[4].split('.txt')[0])
    except Exception:
        R = float('nan'); Y = float('nan')
    return R, Y


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--posts', default='outputs/scan_postprocess', help='postprocess outputs dir')
    p.add_argument('--delta', type=float, default=0.01)
    p.add_argument('--smooth', type=float, default=2000.0)
    p.add_argument('--dpi', type=int, default=300, help='DPI for output plots')
    p.add_argument('--outfmt', choices=['png','pdf','both'], default='both', help='Output format for plots')
    args = p.parse_args()

    coeff_files = find_coeff_files(args.posts)
    if not coeff_files:
        print('No coeff files found in', args.posts)
        return
    rows = []
    for path in coeff_files:
        a = read_coeff_file(path)
        if not a:
            continue
        R, Y = parse_filename(path)
        Lp = L_of_s(a, 0.5+args.delta, args.smooth)
        Lm = L_of_s(a, 0.5-args.delta, args.smooth)
        L0 = L_of_s(a, 0.5, args.smooth)
        deriv = (Lp - Lm) / (2.0*args.delta)
        rows.append({'R':R,'Y':Y,'M':len(a),'L0':L0,'Lprime':deriv,'file':os.path.relpath(path)})

    outcsv = os.path.join(args.posts, 'L_derivatives.csv')
    with open(outcsv, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['R','Y','M','L0','Lprime','file'])
        w.writeheader()
        for r in sorted(rows, key=lambda x:(x['R'], x['Y'])):
            w.writerow(r)
    print('Wrote', outcsv)

    if plt is None:
        print('matplotlib not available: skipping plots')
        return

    os.makedirs(os.path.join(args.posts,'plots'), exist_ok=True)
    Lprimes = [r['Lprime'] for r in rows]
    Rs = [r['R'] for r in rows]
    Ys = [r['Y'] for r in rows]

    # histogram (high-res)
    plt.figure(figsize=(6,4))
    plt.hist(Lprimes, bins=14, color='C0', edgecolor='k', alpha=0.9)
    plt.axvline(0, color='k')
    plt.title("Histogram of L'(1/2) estimates")
    plt.xlabel("L'(1/2)")
    plt.ylabel('Count')
    plt.tight_layout()
    hist_png = os.path.join(args.posts,'plots','Lprime_hist.png')
    hist_pdf = os.path.join(args.posts,'plots','Lprime_hist.pdf')
    if args.outfmt in ('png','both'):
        plt.savefig(hist_png, dpi=args.dpi, bbox_inches='tight')
        print('Wrote', hist_png)
    if args.outfmt in ('pdf','both'):
        plt.savefig(hist_pdf, bbox_inches='tight')
        print('Wrote', hist_pdf)
    plt.close()

    # scatter vs R (color by Y)
    plt.figure(figsize=(7,4))
    sc = plt.scatter(Rs, Lprimes, c=Ys, cmap='viridis', s=50, edgecolor='k')
    cbar = plt.colorbar(sc)
    cbar.set_label('Y')
    plt.axhline(0,color='k', linestyle='--')
    plt.xlabel('R')
    plt.ylabel("L'(1/2)")
    plt.tight_layout()
    scatter_png = os.path.join(args.posts,'plots','Lprime_vs_R.png')
    scatter_pdf = os.path.join(args.posts,'plots','Lprime_vs_R.pdf')
    if args.outfmt in ('png','both'):
        plt.savefig(scatter_png, dpi=args.dpi, bbox_inches='tight')
        print('Wrote', scatter_png)
    if args.outfmt in ('pdf','both'):
        plt.savefig(scatter_pdf, bbox_inches='tight')
        print('Wrote', scatter_pdf)
    plt.close()

if __name__ == '__main__':
    main()
