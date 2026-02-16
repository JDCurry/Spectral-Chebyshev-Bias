# run_chebyshev_sign_tests.py
import math
from maass_levelone_computations import maass_form_coeffs

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

targets = [
    (30.27904849913951, 22),
    (30.404327054043744, 23),
    (31.056533962096182, 24),
    (31.916182470919598, 25),
]

for R, num in targets:
    for Y in (0.02, 0.01):
        coeffs = maass_form_coeffs(Y, R, symmetry=-1)
        a = [1.0] + [float(c) for c in coeffs]
        M = len(a)
        ps = sieve(M)
        a2 = a[1] if len(a) > 1 else float('nan')
        a4 = a[3] if len(a) > 3 else float('nan')
        print(f"#{num} R={R:.12f} Y={Y}: M={M}, Hecke |a4-(a2**2-1)|={abs(a4-(a2**2-1)):.2e}")
        for X in (500, 1000, 2000, 5000):
            S = sum(a[p-1]*chi3(p)*math.exp(-p/X) for p in ps if chi3(p) != 0 and p <= M)
            print(f"  X={X:5d}: S_f={S:+.6f} {'NEG' if S<0 else 'POS'}")
        print()