# E3 ablation ladder: toy CPU PILOT (training-free memory rules)

**Status: PILOT at toy scale. This is not the preregistered E3.** No trained encoder, no language modelling,
no Transformer baseline, synthetic task, 3 held-out seeds. The results characterise *memory-rule regimes* in
one synthetic setting. They do not support claims about CDLR or BDH at scale. They are not yet cited in the
TMLR draft.

Run: `python e3_ablation.py --mode smoke` (<1 s) and `--mode sweep` (808 s wall, 8 CPU threads, torch 2.x CPU).
Outputs: `results_{smoke,sweep}.json` (meta + summary), `results_*_summary.csv`, `results_*_raw.csv` (every
λ × seed, per-task accuracies), `dual_vs_bytecontrol_paired.csv`, and the logs.

## Task
Continual associative recall with **shared inputs across tasks**, so tasks interfere as in A→B→A:
- K inputs x_i ∈ R^64 are shared by T = 8 tasks. Task t maps x_i to class perm_t(i), with K classes (chance 1/K).
  The class codes are Rademacher vectors in R^32.
- Token = [x_i ; α·c_t + 0.1·noise]. c_t is a per-task context vector, an input feature and not a label.
  **α is a trade-off, not just "task separability".** Large α separates tasks in key space but makes the items
  *within* a task share a strong common component (within-task crosstalk). Small α does the reverse.
- Stream: tasks 1..8 in order, each written r = 2 passes over its K pairs. Test after the full stream on every
  (task, input), using fresh context noise.
- Metrics: **plasticity** = accuracy on the last task, **retention** = mean accuracy on tasks 1..7,
  **overall** = mean over all 8 tasks.
- The encoder is a fixed random projection W (same seed, same width → same W), followed by the rung's feature
  map.

## Ladder rungs (each changes one thing)
| rung | keys | write | memory | bytes (fp32) |
|---|---|---|---|---|
| a_linattn | dense elu(We)+1 in R^n | raw outer product, decay λ | one S | 4·n·(d_v+1) |
| a_linattn_delta | same | normalised delta | one S | same |
| b_hebb_raw | positive k-WTA (1/16) in R^n | raw Hebbian | one S | same |
| b_hebb_delta | same | normalised delta | one S | same |
| **c_dual** | same | delta fast S, then consolidated into M = 4 slow slots at each task boundary (merge to nearest slot by mean-key cosine if sim ≥ 0.5 or bank full), then S is reset. Read: route the query to the store (S or a slot) with the most similar mean key | S + C | 4·(1+M)·n·(d_v+1) |
| **d_bytes_raw / d_bytes_delta** | same, width **n' = (1+M)·n** | raw / delta | one larger S: the **byte-transfer control** | same as c_dual |

λ ∈ {1, 0.999, 0.995, 0.98, 0.95} (per-token decay) is tuned for **every** rung on validation seed 0, using
overall accuracy. All numbers below are held-out seeds 1–3 at the selected λ. The full grid is in `results_sweep_raw.csv`.

## Results (`results_sweep_summary.csv`; overall acc, mean of 3 held-out seeds; chance 0.016 / 0.008)

| n | K | α | a_linattn | a_la_delta | b_raw | b_delta | **c_dual** | d_bytes_raw | **d_bytes_delta** |
|---|---|---|---|---|---|---|---|---|---|
| 256 | 64 | 0.5 | .018 | .020 | .086 | .217 | **.404** | .103 | .316 |
| 256 | 64 | 2.0 | .018 | .023 | .027 | .168 | .322 | .025 | **.557** |
| 256 | 128 | 0.5 | .008 | .011 | .053 | .150 | .267 | .058 | .263 |
| 256 | 128 | 2.0 | .008 | .012 | .009 | .065 | .131 | .016 | **.333** |
| 1024 | 64 | 0.5 | .019 | .017 | .099 | .298 | **.598** | .104 | .304 |
| 1024 | 64 | 2.0 | .018 | .022 | .021 | .482 | .635 | .026 | **.757** |
| 1024 | 128 | 0.5 | .009 | .011 | .058 | .256 | **.485** | .058 | .300 |
| 1024 | 128 | 2.0 | .009 | .010 | .016 | .273 | .403 | .019 | **.589** |
| 4096 | 64 | 0.5 | .019 | .016 | .100 | .311 | **.612** | .106 | .316 |
| 4096 | 64 | 2.0 | .019 | .021 | .023 | .756 | .809 | .023 | .799 |
| 4096 | 128 | 0.5 | .009 | .012 | .059 | .300 | **.593** | .060 | .315 |
| 4096 | 128 | 2.0 | .008 | .010 | .019 | .563 | .640 | .019 | .670 |

Paired dual − byte-control (delta) difference in overall accuracy, mean [min, max] over the 3 held-out seeds
(`dual_vs_bytecontrol_paired.csv`):
- **α = 0.5** (keys strongly correlated across tasks): +0.088 [+0.055, +0.141] at n=256/K=64, +0.005 [−0.04, +0.08]
  at n=256/K=128, +0.29 (n=1024/K=64), +0.19 (n=1024/K=128), +0.30 (n=4096/K=64), +0.28 (n=4096/K=128). For n ≥ 1024,
  all seeds are positive. The gain is almost entirely in **retention** (for example n=4096/K=64: 0.557 vs 0.219),
  with plasticity equal (1.00 vs 1.00).
- **α = 2.0** (tasks separable, within-task crosstalk): the **byte-transfer control wins or ties**. It is ahead by
  −0.12 to −0.24 for n ≤ 1024 (all seeds), and ties at n = 4096 (+0.010 [−0.03, +0.05]; −0.029 [−0.06, −0.001]).

## Honest reading
1. **The dual-timescale advantage is regime-dependent here, and the byte-transfer control matters.** When tasks
   overlap strongly in key space, a single larger state, even at the same bytes, cannot keep them apart. Routing
   to separate slots then raises retention 2–2.5×. When tasks are already separable in key space, spending the
   same bytes on one wider state is as good or better. This is the confound the control was designed to expose.
   "More memory" explains all of the α = 2 gain over b_delta, and none of the α = 0.5 gain.
2. **The dual model gets a task-boundary signal** (when to consolidate and reset S). The single-state rungs do not
   use one. Part of the α = 0.5 gain may come from this signal and not from the second timescale itself.
   Preregistered E3/E4 must run every rung with and without boundary signals (as the protocol says). We did not
   do that here.
3. **Decay did not matter.** The selected λ was 1.0 (no decay) for almost every delta rung, and 0.995 for most raw
   rungs. So these toy results do not exercise Proposition 1's retention–interference trade-off, which is about
   decaying states. They show slot routing vs. a wider single state.
4. **Raw positive Hebbian states fail at every width** (overall ≤ 0.11; retention ≈ chance), consistent with the E2
   PILOT plateau. Widening the state 5× (d_bytes_raw) does not help. The write rule (b_raw → b_delta) is the
   largest single rung gain at α = 0.5.
5. **The linear-attention rungs (a) are at chance**, and this is a property of this toy: dense elu+1 features of a
   random, untrained projection have a large common mode (key cosine ≈ 0.8), so neither the raw nor the delta
   write separates items in 2 passes. This is **not** evidence against trained linear attention, whose encoder
   learns to decorrelate keys. A fair rung (a) needs a trained encoder (mid-scale design below).
6. M = 4 slots < 7 earlier tasks, so the bank must merge tasks. Slot routing is unsupervised, using mean-key
   cosine. It is not a labelled support set, unlike P2 in the paper's appendix.

## Mid-scale design (not run; too heavy for a ~20 min CPU budget)
- **Backbone:** the public `bdh.py` (as in `tiny_full/`), with trained encoders. Each rung changes one component,
  following the paper's Fig. 4 (a)→(i): (a) linear attention elu+1 at d_s = d → (b) positive ReLU keys →
  (c) n ≫ d → (d) k-WTA → (e) decay/damping → (f) delta write → (g) + slow bank C, κ → (h) + workspace R>1 →
  (i) + local adapter.
- **Controls:** byte-transfer at (g) (bank bytes → wider S, as here), a backbone control (Transformer++ with a
  positive head), and a with/without task-boundary signal toggle on every rung.
- **Budget:** about 10–30M non-embedding parameters, matched within ±5% on parameters *and* separately on
  training FLOPs (P1). Equal LR/WD sweep points per rung (P2). 3 seeds, Wilson intervals, paired bootstrap, and
  Holm correction (P5).
- **Tasks:** MQAR with controlled key correlation (E2 families) for capacity; interleaved A→B→A permutation and
  multi-domain streams for retention (E4 metrics: forgetting gap, relearning speed); and bytes plus p50 latency
  at T ∈ {512, 2k, 8k}.
- **Compute:** about 1–2 GPU-days for the 9 rungs, 2 controls, and 3 seeds at 10M. CPU is not feasible beyond
  about 1M parameters.
- **Pre-stated outcome rules:** H2 is refuted if c_dual ≤ the byte-transfer control on retention at matched
  bytes in the low-separability regime *with boundary signals removed from both*.
