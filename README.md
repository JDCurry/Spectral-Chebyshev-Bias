Heuristic Hejhal / Maass-form scan bundle

Contents:
- code/: core scripts used to run scans and postprocess (postprocess_scan_results.py, compute_L_derivative.py, run_stability_sweep.py, aggregate_stability.py, compute_L_refined.py, parse_summary_to_csv.py, etc.)
- sage/: Sage-specific helpers and notes (if present)
- outputs/scan_postprocess/: coefficient dumps for refined scan eigenforms and sign-test CSVs
- drafts/: draft text files used in manuscript

Usage notes:
- Many scripts require Sage for `maass_form_coeffs` and were developed to run inside a Sage container. See `requirements.txt` and use the provided `prepare_repo_bundle.sh` to build an archive.
- To reproduce scans or analyses, start a Sage container with the environment used previously (Sage 9.6 recommended).

Files of interest:
- `postprocess_scan_results.py` — extract refined eigenvalues, dump coefficients, run sign tests
- `compute_L_derivative.py` — compute L(1/2) and finite-difference L'(1/2) from coefficient dumps
- `run_stability_sweep.py`, `aggregate_stability.py` — stability sweep and aggregation tools
- `compute_L_refined.py` — helper to compute L' for refined-R directories
- `sign_tests_scan_forms.csv` — sign-test results for scan forms
- `L_derivatives_refined.csv` — refined L' results for scan forms

License: please add your preferred license before publishing.
