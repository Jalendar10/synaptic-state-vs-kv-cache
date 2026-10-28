# E2 capacity probes (toy, CPU) — associative recall vs. stored facts N and width n

**Status: toy-scale preliminary probe, not the preregistered E2 run.** Widths n = 64…4096
(BDH-GPU 25M uses n = 32,768 with d = 256); value width d = 32; no trained encoder; synthetic keys.
These results bear on the *memory-rule* part of BDH Claim 7, not on a trained BDH model.

## Setup (`e2_capacity.py`)
- State: fixed n×d matrix, same write/read as `alrs/alrs/hebbian_memory.py` with λ=1, η=1:
  `S = Σ φ(k_i) v_iᵀ`, read `qᵀS / qᵀz` (the normaliser is a positive scalar and does not change argmax).
- Rules: `hebbian` (raw outer product), `hebbian_centered` (subtract the batch mean key before
  write/read — a cheap whitening), `delta` (sequential normalised delta rule; n ≤ 2048, N ≤ 16n).
- Keys: positive, k-WTA sparse (active fraction 1/16 of n), BDH-like.
  `random` = i.i.d. Gaussian pre-activation; `corr_ρ` = √ρ·shared + √(1−ρ)·private pre-activation
  (ρ ∈ {0.2, 0.5, 0.8}); `clustered` = 8 centres + 0.5·noise.
- Values: i.i.d. Rademacher in R^d. Recall = argmax correlation over the N stored values (chance 1/N).
- N swept on a quarter-octave grid (4…65,536) until accuracy < 0.3 twice; N50 by log-linear
  interpolation; 3 seeds; slope = least-squares fit of log N50 on log n.

Run: `python e2_capacity.py --mode smoke` (<1 s) and `--mode sweep` (41 s wall on 8 CPU threads).

## Results (`results_sweep.json`, `results_sweep_n50.csv`, raw: `results_sweep_raw.csv`, plot: `n50_plot.dat`)
N50 (mean ± sd over 3 seeds):

| rule | keys | n=64 | 256 | 1024 | 2048 | 4096 | slope (±se) |
|---|---|---|---|---|---|---|---|
| hebbian | random | 160 | 351 | 564 | 596 | 532±101 | 0.29 ± 0.07 (saturates) |
| hebbian | corr 0.5 | 27 | 27 | 36 | 34 | 43 | 0.14 ± 0.04 |
| hebbian_centered | random | 196 | 682 | 2208 | 3958 | 7172 | **0.86 ± 0.01** |
| hebbian_centered | corr 0.2 | 109 | 420 | 1267 | 2317 | 4148 | 0.86 ± 0.02 |
| hebbian_centered | corr 0.5 | 60 | 233 | 775 | 1412 | 2514 | 0.88 ± 0.02 |
| hebbian_centered | corr 0.8 | 42 | 159 | 511 | 905 | 1626 | 0.88 ± 0.01 |
| hebbian_centered | clustered | 66 | 83 | 84 | 78 | 86 | 0.04 ± 0.02 |
| delta | random | 103 | 398 | 1430 | 2688 | — | **0.94 ± 0.01** |
| delta | corr 0.5 | 25 | 112 | 472 | 846 | — | 1.01 ± 0.03 |
| delta | corr 0.8 | 5 | 5 | 6 | 4 | — | −0.02 ± 0.06 |
| delta | clustered | 36 | 43 | 37 | 35 | — | 0.05 ± 0.08 |

## Reading against Claim 7
Claim 7 (BDH §6.1, App. C.2): Õ(n) separable facts for non-adversarial keys, Ω̃(√n) worst case.
- **Supports the Õ(n) part only conditionally.** With random keys, centred Hebbian and delta states
  give N50 ≈ 1.3–1.75 n with fitted exponents 0.86 and 0.94 — consistent with n / log n.
- **Raw positive Hebbian state does not scale linearly.** With fixed active fraction, positive keys
  share a common-mode component, whose crosstalk does not shrink with n. N50 plateaus at ≈ 550 from
  n ≈ 512 on (exponent 0.29 overall, ≈ 0 above n = 512). Linear capacity needs centring/whitening
  (or a delta rule), which BDH's positive-only state does not do as written.
- **Correlated keys:** a single shared direction (corr ρ) is removed by centring or by the delta rule.
  The exponent stays ≈ 0.9–1.0, with a constant-factor loss of 2–4.5×. Clustered keys (several shared
  directions) and the raw state with ρ ≥ 0.5 have **flat N50 (exponent ≈ 0)**, *below* the Ω̃(√n)
  worst-case bound. Our clustered/ρ=0.8 construction is a family whose correlation is fixed as n grows.
  Claim 7's adversarial model may restrict key overlap differently, so this is a mismatch of
  assumptions and not a refutation.
- We measured **no exponent ≈ ½ regime**: the curves are either ≈1 or ≈0, depending on whether
  the correlation structure is removable by the rule.
- **Verdict:** Claim 7 is *not confirmed*. The toy data support linear capacity only for
  decorrelated keys with a centring or error-correcting write. Preregistered E2 (n = 2^12…2^16, trained
  encoders, MQAR) is still required.
