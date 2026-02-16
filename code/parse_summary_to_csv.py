#!/usr/bin/env python3
"""
Parse outputs/scan_postprocess/summary.txt into a CSV of sign-test results.
"""
import re, csv, os
p = re.compile(r"R=([0-9\.]+) Y=([0-9\.]+) M=([0-9]+) hecke_err=([0-9\.eE+-]+) coeff_err=([0-9\.eE+-]+) coeffile=(\S+)")
Sre = re.compile(r"\s*X=([0-9]+): S_f=([+-]?[0-9\.eE+-]+)")
summary = 'outputs/scan_postprocess/summary.txt'
outcsv = 'outputs/scan_postprocess/sign_tests_scan_forms.csv'
rows = []
if not os.path.exists(summary):
    raise SystemExit('summary.txt not found')
with open(summary) as f:
    lines = f.readlines()
    i = 0
    while i < len(lines):
        m = p.match(lines[i].strip())
        if m:
            R=float(m.group(1)); Y=float(m.group(2)); M=int(m.group(3)); hecke_err=float(m.group(4)); coeff_err=float(m.group(5)); coefffile=m.group(6)
            S = {}
            j = i+1
            while j < i+5 and j < len(lines):
                mm = Sre.match(lines[j])
                if mm:
                    X=int(mm.group(1)); Sf=float(mm.group(2))
                    S[X]=Sf
                j += 1
            rows.append({'R':R,'Y':Y,'M':M,'hecke_err':hecke_err,'coeff_err':coeff_err,'coefffile':coefffile,'S500':S.get(500,''),'S1000':S.get(1000,''),'S2000':S.get(2000,''),'S5000':S.get(5000,'')})
            i = j
        else:
            i += 1
with open(outcsv,'w',newline='') as f:
    w = csv.DictWriter(f, fieldnames=['R','Y','M','hecke_err','coeff_err','coefffile','S500','S1000','S2000','S5000'])
    w.writeheader()
    for r in rows:
        w.writerow(r)
print('Wrote', outcsv)
