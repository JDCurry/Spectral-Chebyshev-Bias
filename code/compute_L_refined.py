#!/usr/bin/env python3
"""
Compute L(1/2) and finite-difference L'(1/2) for specific refined-R subdirectories.
Writes outputs/scan_postprocess/L_derivatives_refined.csv
"""
import os
import argparse
import compute_L_derivative as cld


def process_dirs(dirs, outcsv, delta=0.01, smooth=2000.0):
    rows = []
    for d in dirs:
        if not os.path.isdir(d):
            print('dir not found:', d)
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.startswith('coeffs_') or not fn.endswith('.txt'):
                continue
            path = os.path.join(d, fn)
            a = cld.read_coeff_file(path)
            if not a:
                continue
            # extract R and Y from filename
            parts = fn.split('_')
            try:
                R = float(parts[2])
                Y = float(parts[4].split('.txt')[0])
            except Exception:
                R = float('nan')
                Y = float('nan')
            s0 = 0.5
            Lp = cld.L_of_s(a, s0+delta, smooth)
            Lm = cld.L_of_s(a, s0-delta, smooth)
            L0 = cld.L_of_s(a, s0, smooth)
            deriv = (Lp - Lm) / (2.0*delta)
            rows.append((R, Y, len(a), L0, deriv, path))
    # write CSV-like output
    with open(outcsv, 'w') as f:
        f.write('# R, Y, M, L(1/2), L\' (1/2) (delta=%g smooth=%g)\n' % (delta, smooth))
        for R, Y, M, L0, deriv, path in sorted(rows):
            f.write('%.12f,%.3f,%d,%.12e,%.12e,%s\n' % (R, Y, M, L0, deriv, path))
    print('Wrote', outcsv)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dirs', nargs='+', required=True)
    p.add_argument('--out', default='outputs/scan_postprocess/L_derivatives_refined.csv')
    p.add_argument('--delta', type=float, default=0.01)
    p.add_argument('--smooth', type=float, default=2000.0)
    args = p.parse_args()
    process_dirs(args.dirs, args.out, delta=args.delta, smooth=args.smooth)

if __name__ == '__main__':
    main()
