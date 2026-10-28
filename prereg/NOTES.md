# Prereg notes (the frozen protocol `e1_e5_protocol_v0.json` is unchanged)

- 2026-10-28: Toy-scale **E2 pilot** (CPU, n = 64–4096, d = 32, synthetic k-WTA keys, no trained encoder)
  is in `experiments/e2_capacity/` (`e2_capacity.py`, `results_sweep.json`, `results_sweep_n50.csv`,
  `README.md`). It is a pipeline/memory-rule check, **not** the preregistered E2 run
  (n = 2^12…2^16, MQAR, matched bytes). Claim 7 is not confirmed by it.
- Paper figures are TikZ/pgfplots sources in `figures/` (F2 crossover, F3 E2 pilot capacity from
  `experiments/e2_capacity/n50_plot.dat`, F4 E3 ladder, F5 empty Pareto template).
