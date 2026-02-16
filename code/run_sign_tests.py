#!/usr/bin/env python3
import mpmath
from maass_levelone_computations import find_single_ev_linearized
from pathlib import Path
Rs = [30.27904849913951,30.404327054043744,31.056533962096182,31.916182470919598]
outdir = Path('outputs')
outdir.mkdir(exist_ok=True)
for R in Rs:
    print('Computing coeffs for R=', R)
    val = find_single_ev_linearized(R, 0.001, -1, verbosity=0)
    if val is None:
        print('No eigenvalue returned for', R)
        continue
    coeffs = val[1]
    fname = outdir / f'coeffs_{str(R).replace('.', '_')}.txt'
    with open(fname, 'w') as f:
        for i in range(1, len(coeffs)+1):
            try:
                v = float(coeffs[i-1])
            except Exception:
                v = float(mpmath.nstr(coeffs[i-1], 20))
            f.write(f"{v}\n")
    print('Wrote', fname)

# run sign test
import subprocess
for R in Rs:
    fname = outdir / f'coeffs_{str(R).replace('.', '_')}.txt'
    if not fname.exists():
        print('Missing', fname)
        continue
    out = outdir / f'sign_test_{str(R).replace('.', '_')}.txt'
    print('Running sign test on', fname)
    subprocess.run(['python3', str(Path('/workspace/sign_test_new_forms.py')), str(fname), str(R)], stdout=open(out, 'w'), stderr=subprocess.STDOUT)
    print('Wrote', out)
print('Done')
