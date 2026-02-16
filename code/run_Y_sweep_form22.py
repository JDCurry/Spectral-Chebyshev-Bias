# run_Y_sweep_form22.py
import math
from maass_levelone_computations import maass_form_coeffs

# Parameters
R = 30.27904849913951
Y_values = [0.05, 0.04, 0.03, 0.025, 0.02]
TRUNC_M = 219  # use same number of coefficients for each Y

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

primes_to_check = [2,3,5,7,11,13,17,19,23]
composite_checks = {
    'a4_check': (4, lambda a: a[3] - (a[1]**2 - 1)),     # a4 - (a2^2 - 1)
    'a6_check': (6, lambda a: a[5] - (a[1]*a[2])),       # a6 - (a2*a3)
    'a9_check': (9, lambda a: a[8] - (a[2]**2 - 1)),     # a9 - (a3^2 - 1)
    'a10_check': (10, lambda a: a[9] - (a[1]*a[4])),     # a10 - (a2*a5)
    'a15_check': (15, lambda a: a[14] - (a[2]*a[4])),    # a15 - (a3*a5)
    'a25_check': (25, lambda a: a[24] - (a[4]**2 - 1)),   # a25 - (a5^2 - 1)
}

X_values = [500, 1000, 2000, 5000]

out_lines = []
for Y in Y_values:
    coeffs = maass_form_coeffs(Y, R, symmetry=-1)
    a_full = [1.0] + [float(c) for c in coeffs]
    # Truncate/pad to TRUNC_M
    if len(a_full) >= TRUNC_M:
        a = a_full[:TRUNC_M]
    else:
        a = a_full + [0.0] * (TRUNC_M - len(a_full))
    M = len(a)
    ps = sieve(M)

    out_lines.append(f"Y={Y}: M={M}")
    # Hecke composite checks
    for name, (idx, func) in composite_checks.items():
        # idx is the n whose a_n will be compared; ensure index exists
        if idx-1 < len(a):
            val = func(a)
            out_lines.append(f"  {name}: {val:+.3e}")
        else:
            out_lines.append(f"  {name}: n/a (M too small)")

    # Report small primes and Ramanujan bound
    for p in primes_to_check:
        if p-1 < len(a):
            out_lines.append(f"  a_{p} = {a[p-1]:+.6f} |a_p|<=2: {abs(a[p-1])<=2}")
        else:
            out_lines.append(f"  a_{p} = n/a")

    # Compute S_f(X) with truncation to primes <= M
    for X in X_values:
        S = sum(a[p-1]*chi3(p)*math.exp(-p/X) for p in ps if chi3(p) != 0 and p <= M)
        out_lines.append(f"  X={X:5d}: S_f={S:+.6f} {'NEG' if S<0 else 'POS'}")

    out_lines.append("")

# Write outputs
outpath = 'outputs/Y_sweep_form22.txt'
with open(outpath, 'w') as f:
    f.write('\n'.join(out_lines))

print('Wrote', outpath)
print('\n'.join(out_lines))
