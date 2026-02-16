#!/usr/bin/env python3
"""
postprocess_scan_results.py
Scan driver log files (outputs/R_scan_32_36_parallel or outputs/R_scan_32_36)
for converged eigenvalues, extract coefficients and run the chi3 sign test.

Run inside the Sage container from the code directory:
  sage -python postprocess_scan_results.py --logs outputs/R_scan_32_36_parallel --tol 1e-8

Outputs go to: outputs/scan_postprocess/
"""
import re
import os
import math
import argparse

from maass_levelone_computations import maass_form_coeffs

FLOAT_RE = re.compile(r"([+-]?\d+\.\d+(?:[eE][+-]?\d+)?)")
COEFF_ERR_RE = re.compile(r"coeff|coeffs|coeff error|coeff_error", re.I)
COEFF_NUM_RE = re.compile(r"([0-9]+\.[0-9]+(?:[eE][+-]?\d+)?)")


def find_candidates(logdir, tol=1e-8):
    candidates = []
    for fn in sorted(os.listdir(logdir)):
        if not fn.startswith('driver_') or not fn.endswith('.txt'):
            continue
        path = os.path.join(logdir, fn)
        with open(path, 'r', errors='ignore') as f:
            txt = f.read()
        # Prefer explicit lines that state the refined eigenvalue, e.g.
        #   "32.018406433624925 is an eigenvalue."
        # or lines mentioning "is a near candidate" or "has passed check".
        cand = None
        for line in txt.splitlines():
            if re.search(r"is an eigenvalue", line, re.I) or re.search(r"is a near candidate", line, re.I) or re.search(r"has passed check", line, re.I):
                fr = FLOAT_RE.search(line)
                if fr:
                    try:
                        cand = float(fr.group(1))
                    except Exception:
                        pass
        # fallback: try to find a float that appears after the word 'eigen' anywhere
        if cand is None:
            eig_matches = []
            for m in re.finditer(r"eigen(?:value)?", txt, re.I):
                span = txt[m.end():m.end()+200]
                fr = FLOAT_RE.search(span)
                if fr:
                    eig_matches.append((m.start(), float(fr.group(1)), span))
            if eig_matches:
                cand = eig_matches[-1][1]
            else:
                # ultimate fallback: last float in file
                all_floats = FLOAT_RE.findall(txt)
                if all_floats:
                    try:
                        cand = float(all_floats[-1])
                    except Exception:
                        cand = None
        if cand is None:
            continue
        # find a coefficient error near the occurrence
        coeff_err = float('inf')
        # search for 'coeff' then a nearby float
        for m in re.finditer(r"coeff", txt, re.I):
            span = txt[m.end():m.end()+200]
            fr = COEFF_NUM_RE.search(span)
            if fr:
                try:
                    coeff_err = float(fr.group(1))
                    break
                except Exception:
                    pass
        # as fallback look for patterns like 'coeff error' with +/- e
        if coeff_err == float('inf'):
            m2 = re.search(r"coeff.*?([0-9]+\.[0-9]+e[+-]?\d+)", txt, re.I)
            if m2:
                coeff_err = float(m2.group(1))
        if coeff_err <= tol:
            candidates.append((path, cand, coeff_err))
    return candidates


def chi3(n):
    r = n % 3
    return 0 if r == 0 else (1 if r == 1 else -1)


def sieve(n):
    if n < 2:
        return []
    s = [True] * (n+1)
    s[0] = s[1] = False
    for p in range(2, int(n**0.5) + 1):
        if s[p]:
            for k in range(p*p, n+1, p):
                s[k] = False
    return [i for i in range(n+1) if s[i]]


def sign_test_for_R(R, outdir, Ys=(0.02,0.01)):
    os.makedirs(outdir, exist_ok=True)
    results = []
    for Y in Ys:
        coeffs = maass_form_coeffs(Y, R, symmetry=-1)
        a = [1.0] + [float(c) for c in coeffs]
        M = len(a)
        ps = sieve(M)
        # Hecke checks: a4 and a2
        a2 = a[1] if len(a) > 1 else float('nan')
        a4 = a[3] if len(a) > 3 else float('nan')
        hecke_err = abs(a4 - (a2**2 - 1)) if (not math.isnan(a2) and not math.isnan(a4)) else float('nan')
        Svals = {}
        for X in (500, 1000, 2000, 5000):
            S = sum(a[p-1]*chi3(p)*math.exp(-p/X) for p in ps if chi3(p) != 0 and p <= M)
            Svals[X] = S
        # save coefficients
        coeffile = os.path.join(outdir, f'coeffs_R_{R:.12f}_Y_{Y:.3f}.txt')
        with open(coeffile, 'w') as f:
            for i, ai in enumerate(a, start=1):
                f.write(f"{i} {ai:.16e}\n")
        results.append((Y, M, hecke_err, coeffile, Svals))
    return results


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--logs', default='outputs/R_scan_32_36_parallel', help='logs directory')
    p.add_argument('--tol', type=float, default=1e-8, help='coeff error threshold for accepting a candidate')
    p.add_argument('--out', default='outputs/scan_postprocess', help='output directory')
    args = p.parse_args()

    cand = find_candidates(args.logs, tol=args.tol)
    os.makedirs(args.out, exist_ok=True)
    summary_lines = []
    if not cand:
        print('No candidates found with coeff_err <=', args.tol, 'in', args.logs)
        return
    print('Found', len(cand), 'candidates')
    for path, R, coeff_err in cand:
        print('Processing', os.path.basename(path), 'R=', R, 'coeff_err=', coeff_err)
        outdir = os.path.join(args.out, f'R_{R:.12f}')
        res = sign_test_for_R(R, outdir, Ys=(0.02,0.01))
        # write summary
        for Y, M, hecke_err, coeffile, Svals in res:
            line = f"R={R:.12f} Y={Y:.3f} M={M} hecke_err={hecke_err:.3e} coeff_err={coeff_err:.3e} coeffile={coeffile}"
            summary_lines.append(line)
            for X, S in Svals.items():
                summary_lines.append(f"  X={X}: S_f={S:+.6f}")
    summary_file = os.path.join(args.out, 'summary.txt')
    with open(summary_file, 'w') as f:
        f.write('\n'.join(summary_lines))
    print('Wrote summary to', summary_file)

if __name__ == '__main__':
    main()
