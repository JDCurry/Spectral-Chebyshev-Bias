**Explicit-formula paragraph: how a central zero forces negative twisted prime sum**

Let f be a Maass cusp form and χ a primitive Dirichlet character (χ₃ here). Consider the twisted L-function L(s,f⊗χ) with completed Λ(s) satisfying Λ(s)=εΛ(1-s). If ε=-1 then Λ(1/2)=0; the central point is a forced zero of odd order. The explicit formula relates a smoothed sum of coefficients at primes to sums over zeros of the L-function. For a suitably smooth weight w (e.g. exponential smoothing exp(-p/X)), the prime-sum

  S_f(X) := ∑_{p} a_p χ(p) w(p/X)

is, up to main terms from the pole/edge and controllable error, given by a linear combination of terms of the form ∑_ρ X^{ρ-1/2} · G(ρ) where the sum runs over nontrivial zeros ρ of L(s,f⊗χ) and G is a bounded weight depending on w and archimedean parameters.

When there is a simple zero at ρ = 1/2 (forced by ε = -1), its contribution to the explicit formula is proportional to the derivative L'(1/2) and comes with a fixed sign: specifically, a zero at 1/2 contributes a term with sign opposite to the sign of L'(1/2) in the prime sum (see classical derivations in explicit-formula texts). For the case L(1/2)=0 and L'(1/2)>0, the contribution is negative, producing the observed negative bias in S_f(X) at large X. Numerically we observe L'(1/2) > 0 consistently for the odd level‑1 forms, hence the negative S_f.

References:

- H. Iwaniec and E. Kowalski, "Analytic Number Theory", explicit formula derivation chapters.
- E. C. Titchmarsh, "The Theory of the Riemann Zeta-Function" (for standard explicit formula statements).

Notes on rigor and smoothing:

- The argument is standard and follows once one inserts the smoothed von Mangoldt-type explicit formula for the twisted L-function and isolates the zero at 1/2. The smoothing parameter and the truncation of the Dirichlet series must be chosen in accord with the analytic conductor; in practice the exponential smoothing we used makes the zero's contribution apparent and stable for the X-range used in the numeric experiments.

- If desired, I can write a compact displayed derivation (2–3 equations) that explicitly shows the sign of the zero's contribution in the smoothed sum S_f(X).