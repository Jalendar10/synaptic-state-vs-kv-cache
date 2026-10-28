# TMLR re-validation, 2026-10-28 ~00:45 EDT (advise-only; nothing submitted/pushed/emailed)

Source: git clone https://github.com/Jalendar10/synaptic-state-vs-kv-cache -> /workspace/tmp/sskv
HEAD = b441199 (E3 pilot); TMLR fold = ff18884. Path in repo is `tmlr/` (not `paper/tmlr/`).
`git diff ff18884 b441199 -- tmlr` is empty -> b441199 touched only experiments/e3_ablation.
Local /workspace/bdh-research/paper/tmlr/{main.pdf,main.tex,VALIDATION.md,supplementary_anonymized.zip,references.bib}
are byte-identical (sha256) to the repo at ff18884.

Overall: CONDITIONAL (one required abstract fix; minor polish).

Anonymity: PASS. 0 hits in PDF text, PDF strings/metadata (Author/Title empty, 0 embedded files), bib, zip (96 files).
Author block only in main.tex source (hidden without [accepted]); tex is not uploaded to TMLR.
Minor: supp READMEs/JSON contain /workspace/bdh-research/... paths (not identifying; optional cleanup).

Required fix (abstract, last sentence): "correlated or clustered keys at fixed correlation give flat capacity"
is contradicted by Table 3 (centred corr 0.2/0.5/0.8 -> 0.86-0.88; delta corr 0.5 -> 1.01). Replace with:
"...centred Hebbian and delta-rule states with random keys give fitted exponents 0.86-0.94; and keys whose shared
structure the write rule cannot remove (fixed-correlation keys under the raw rule, strongly correlated keys under
the delta rule, or clustered keys) give flat capacity, a different regime from the sqrt(n) worst case."
Also fix VALIDATION S4 wording the same way.

Recommended polish:
- Delta rule n=2048: only 2/3 seeds reached N50 (results_sweep_n50.csv n_seeds_reached=2); Table 3 caption says mean over 3 seeds -> footnote.
- App. A P5 "Every curve has an exponent near 1 or near 0": raw/random is 0.29 -> "near 1, or <=0.3 (plateau/flat)".
- VALIDATION.md section 3 still says "Fig. 3: the E3 ablation ladder" -> now Fig. 4.
- Cosmetic: 1.5pt overfull hbox Table 1.
