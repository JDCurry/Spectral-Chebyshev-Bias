#!/usr/bin/env python3
"""
Run a stability sweep over delta and smoothing values using
`compute_L_derivative.py` internals. Writes per-coefficient-file stability CSVs
into `outputs/scan_postprocess/stability/` as `*.stab.csv`.

Usage:
  python3 run_stability_sweep.py --posts outputs/scan_postprocess
"""
import os
import argparse
import compute_L_derivative as cld


def ensure_dir(d):
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)


def run_sweep(posts_dir, deltas, smooths):
    stability_dir = os.path.join(posts_dir, 'stability')
    ensure_dir(stability_dir)

    # We'll accumulate per-file rows then write
    perfile = {}

    for delta in deltas:
        for smooth in smooths:
            print('Running delta=%g smooth=%g' % (delta, smooth))
            rows = cld.process_posts_dir(posts_dir, delta, smooth)
            for R, Y, M, L0, deriv, path in rows:
                base = os.path.basename(path)
                outname = base.replace('.txt', '.stab.csv')
                outpath = os.path.join(stability_dir, outname)
                if outpath not in perfile:
                    perfile[outpath] = []
                perfile[outpath].append((delta, smooth, R, Y, M, L0, deriv))

    # write per-file CSVs
    for outpath, entries in perfile.items():
        with open(outpath, 'w') as f:
            f.write('delta,smooth,R,Y,M,L0,Lprime\n')
            for delta, smooth, R, Y, M, L0, deriv in entries:
                f.write('%g,%g,%.12f,%.3f,%d,%.12e,%.12e\n' % (delta, smooth, R, Y, M, L0, deriv))
        print('Wrote', outpath)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--posts', default='outputs/scan_postprocess', help='postprocess outputs dir')
    args = p.parse_args()

    # grid recommended in summary
    deltas = [0.005, 0.01, 0.02]
    smooths = [1000.0, 2000.0, 5000.0]

    posts_dir = args.posts
    if not os.path.isdir(posts_dir):
        raise SystemExit('posts dir not found: ' + posts_dir)

    run_sweep(posts_dir, deltas, smooths)


if __name__ == '__main__':
    main()
