#!/usr/bin/env python3
"""
compute_L_derivative.py
Compute a numeric approximation of L'(1/2, f x chi3) using coefficient dumps
produced by postprocess_scan_results.py. Uses a smoothed truncated Dirichlet series:

  L(s) ≈ sum_{n=1..M} a_n * chi3(n) * n^{-s} * exp(-n/SMOOTH)

and a central finite-difference for the derivative:

  L'(1/2) ≈ (L(1/2+delta) - L(1/2-delta)) / (2*delta)

Usage (inside Sage container, run from code/):
  sage -python compute_L_derivative.py --posts outputs/scan_postprocess --delta 0.01 --smooth 2000

Outputs a small table: R, Y, M, L(1/2), L'(1/2).
"""
import os
import math
import argparse


def chi3(n):
    r = n % 3
    return 0 if r == 0 else (1 if r == 1 else -1)


def read_coeff_file(path):
    # expect lines: index value
    a = {}
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    idx = int(parts[0])
                    val = float(parts[1])
                    a[idx] = val
                except Exception:
                    continue
    # return list a[1..M]
    if not a:
        return []
    M = max(a.keys())
    arr = [a.get(i, 0.0) for i in range(1, M+1)]
    return arr


def L_of_s(a, s, smooth):
    # a is list with a[0]=a1
    tot = 0.0
    for n, an in enumerate(a, start=1):
        c = chi3(n)
        if c == 0:
            continue
        tot += an * c * (n**(-s)) * math.exp(-n/float(smooth))
    return tot


def process_posts_dir(posts_dir, delta, smooth):
    results = []
    # expect folders R_*/ with coeff files coeffs_R_..._Y_...txt
    if not os.path.isdir(posts_dir):
        raise SystemExit('posts dir not found: '+posts_dir)
    for entry in sorted(os.listdir(posts_dir)):
        sub = os.path.join(posts_dir, entry)
        if not os.path.isdir(sub):
            continue
        # find coeff files
        for fn in sorted(os.listdir(sub)):
            if fn.startswith('coeffs_') and fn.endswith('.txt'):
                path = os.path.join(sub, fn)
                a = read_coeff_file(path)
                if not a:
                    continue
                # extract R and Y from filename
                # coeffs_R_{R:.12f}_Y_{Y:.3f}.txt
                parts = fn.split('_')
                try:
                    R = float(parts[2])
                    Y = float(parts[4].split('.txt')[0])
                except Exception:
                    R = float('nan')
                    Y = float('nan')
                s0 = 0.5
                Lp = L_of_s(a, s0+delta, smooth)
                Lm = L_of_s(a, s0-delta, smooth)
                L0 = L_of_s(a, s0, smooth)
                deriv = (Lp - Lm) / (2.0*delta)
                results.append((R, Y, len(a), L0, deriv, path))
    return results


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--posts', default='outputs/scan_postprocess', help='postprocess outputs dir')
    p.add_argument('--delta', type=float, default=0.01, help='finite-difference delta')
    p.add_argument('--smooth', type=float, default=2000.0, help='smoothing parameter (exponential)')
    args = p.parse_args()

    res = process_posts_dir(args.posts, args.delta, args.smooth)
    if not res:
        print('No coefficient files found in', args.posts)
        return
    print('# R, Y, M, L(1/2), L\'(1/2) (delta=%g smooth=%g)' % (args.delta, args.smooth))
    for R, Y, M, L0, deriv, path in sorted(res):
        print('R=%.12f Y=%.3f M=%d L(1/2)=%+.6e L\'(1/2)=%+.6e  file=%s' % (R, Y, M, L0, deriv, os.path.relpath(path)))

if __name__ == '__main__':
    main()
