"""E3 toy ablation ladder (CPU, training-free memory rules, fixed random encoder).

Task: interleaved-episode associative recall with *shared inputs across tasks*.
  - K inputs x_i (shared by all T tasks). Task t maps x_i -> class perm_t(i) (random permutation of K classes).
  - A token is e = [x_i ; alpha * c_t + sigma * noise]; c_t is a per-task context vector (an input feature,
    not a label). alpha controls how separable tasks are in key space (small alpha -> highly correlated keys
    across tasks for the same input = strong interference).
  - Stream: tasks 1..T, each an episode of r passes over its K pairs (shuffled). A task-boundary signal is
    available (used only by the dual model's consolidation step).
  - Test after the whole stream: for every task t and input i, query with a fresh token of (x_i, c_t) and decode
    argmax over the K class codes (Rademacher, d_v dims). Chance = 1/K.
  - Metrics: plasticity = acc on the last task; retention = mean acc on tasks 1..T-1; overall = mean over all T.

Ladder rungs (each changes ONE thing; encoder W is the same random matrix for the same seed/width):
  a_linattn     : dense keys phi = elu(W e)+1 in R^n, outer-product write, decay lambda         (bytes ~ n*d_v)
  a_linattn_delta: same dense keys, normalised delta-rule write (DeltaNet-style fairness rung)
  b_hebb_raw    : positive k-WTA sparse keys (frac 1/16) in R^n, raw Hebbian outer product, decay
  b_hebb_delta  : same keys, normalised delta-rule write, decay
  c_dual        : fast S (delta, decay) + slow bank of M slots C_j; at each task boundary S is consolidated
                  into the nearest slot (by mean-key cosine; new slot if sim<tau and a slot is free) then reset.
                  Read: pick the store (S or a slot) whose mean key is most similar to phi(q), read it only.
                  Bytes = (1+M)*n*(d_v+1).
  d_bytes_raw   : BYTE-TRANSFER CONTROL: one state of width n' = (1+M)*n (same bytes as c_dual), raw Hebbian
  d_bytes_delta : BYTE-TRANSFER CONTROL: same width n', delta rule
Lambda (per-token decay) is a tuned hyperparameter for every rung, picked on a validation seed (seed 0) by
overall accuracy and reported on held-out seeds (1..S). The full lambda grid is also written out.
"""
from __future__ import annotations
import argparse, csv, json, math, time, platform, itertools
import numpy as np
import torch

torch.set_num_threads(8)
D_IN, D_C, D_V, FRAC, SIGMA, TAU = 64, 64, 32, 1 / 16, 0.1, 0.5


def kwta(pre, frac):
    k = max(1, int(round(frac * pre.shape[-1])))
    pre = torch.relu(pre)
    thr = pre.topk(k, dim=-1).values[..., -1:]
    return torch.where(pre >= thr, pre, torch.zeros_like(pre))


class Encoder:
    def __init__(self, n, dense, gen):
        self.W = torch.randn(n, D_IN + D_C, generator=gen) / math.sqrt(D_IN + D_C)
        self.dense = dense

    def __call__(self, e):
        pre = e @ self.W.T
        if self.dense:
            return torch.nn.functional.elu(pre) + 1.0
        return kwta(pre, FRAC)


class Store:
    """Single linear associative state with decay; raw or delta write."""

    def __init__(self, n, rule, lam):
        self.S = torch.zeros(n, D_V); self.k = torch.zeros(n); self.rule, self.lam = rule, lam

    def write(self, phi, v):
        self.S.mul_(self.lam); self.k.mul_(self.lam); self.k.add_(phi)
        if self.rule == "raw":
            self.S.add_(torch.outer(phi, v))
        else:  # normalised delta rule, eta = 1
            err = v - phi @ self.S
            self.S.add_(torch.outer(phi, err) / (phi @ phi + 1e-8))

    def read(self, q):
        return q @ self.S


def make_task(K, T, alpha, gen):
    X = torch.randn(K, D_IN, generator=gen)
    Cx = torch.randn(T, D_C, generator=gen)
    perms = [torch.randperm(K, generator=gen) for _ in range(T)]
    codes = torch.randint(0, 2, (K, D_V), generator=gen).float() * 2 - 1
    def tok(i, t):
        return torch.cat([X[i], alpha * Cx[t] + SIGMA * torch.randn(D_C, generator=gen)])
    return X, Cx, perms, codes, tok


def run(rung, n, K, T, M, r, alpha, lam, seed):
    gen = torch.Generator().manual_seed(1000 + seed)
    X, Cx, perms, codes, tok = make_task(K, T, alpha, gen)
    egen = torch.Generator().manual_seed(77 + seed)
    width = (1 + M) * n if rung.startswith("d_") else n
    enc = Encoder(width, dense=rung.startswith("a_linattn"), gen=egen)
    rule = "delta" if rung in ("a_linattn_delta", "b_hebb_delta", "c_dual", "d_bytes_delta") else "raw"
    S = Store(width, rule, lam)
    bank = []  # list of (C, key)
    ogen = torch.Generator().manual_seed(5000 + seed)
    for t in range(T):
        for _ in range(r):
            for i in torch.randperm(K, generator=ogen).tolist():
                S.write(enc(tok(i, t)), codes[perms[t][i]])
        if rung == "c_dual" and t < T - 1:  # consolidate at boundary (not after the last task)
            ks = S.k / (S.k.norm() + 1e-8)
            sims = [float(ks @ (kj / (kj.norm() + 1e-8))) for _, kj in bank]
            if bank and (max(sims) >= TAU or len(bank) >= M):
                j = int(np.argmax(sims)); C, kj = bank[j]; bank[j] = (C + S.S, kj + S.k)
            else:
                bank.append((S.S.clone(), S.k.clone()))
            S = Store(width, rule, lam)
    # test
    acc = []
    for t in range(T):
        Q = torch.stack([enc(tok(i, t)) for i in range(K)])
        if rung == "c_dual":
            stores = [(S.S, S.k)] + bank
            keys = torch.stack([k / (k.norm() + 1e-8) for _, k in stores])
            sel = (Q / (Q.norm(dim=1, keepdim=True) + 1e-8) @ keys.T).argmax(1)
            Y = torch.stack([Q[i] @ stores[int(sel[i])][0] for i in range(K)])
        else:
            Y = Q @ S.S
        pred = (Y @ codes.T).argmax(1)
        acc.append(float((pred == perms[t]).float().mean()))
    bytes_ = 4 * width * (D_V + 1) * (1 + (M if rung == "c_dual" else 0))
    return dict(rung=rung, n=n, K=K, T=T, M=M, r=r, alpha=alpha, lam=lam, seed=seed, width=width,
                state_bytes=bytes_, slots_used=len(bank) if rung == "c_dual" else 0,
                plasticity=acc[-1], retention=float(np.mean(acc[:-1])), overall=float(np.mean(acc)),
                acc_per_task=acc)


RUNGS = ["a_linattn", "a_linattn_delta", "b_hebb_raw", "b_hebb_delta", "c_dual", "d_bytes_raw", "d_bytes_delta"]


def wilson(p, N, z=1.96):
    d = 1 + z * z / N; c = (p + z * z / (2 * N)) / d; h = z * math.sqrt(p * (1 - p) / N + z * z / (4 * N * N)) / d
    return c - h, c + h


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", default="smoke", choices=["smoke", "sweep"])
    a = ap.parse_args()
    if a.mode == "smoke":
        grid = dict(n=[128], K=[32], alpha=[1.0], lams=[1.0, 0.99], seeds=[0, 1], T=4, M=2, r=2)
    else:
        grid = dict(n=[256, 1024, 4096], K=[64, 128], alpha=[0.5, 2.0], lams=[1.0, 0.999, 0.995, 0.98, 0.95],
                    seeds=[0, 1, 2, 3], T=8, M=4, r=2)
    t0 = time.time(); raw = []
    for n, K, alpha, rung in itertools.product(grid["n"], grid["K"], grid["alpha"], RUNGS):
        for lam in grid["lams"]:
            for s in grid["seeds"]:
                raw.append(run(rung, n, K, grid["T"], grid["M"], grid["r"], alpha, lam, s))
        print(f"{time.time()-t0:7.1f}s n={n} K={K} alpha={alpha} {rung}", flush=True)
    # select lambda on seed 0 (validation), report held-out seeds
    summ = []
    for n, K, alpha, rung in itertools.product(grid["n"], grid["K"], grid["alpha"], RUNGS):
        rows = [x for x in raw if (x["n"], x["K"], x["alpha"], x["rung"]) == (n, K, alpha, rung)]
        val = {x["lam"]: x["overall"] for x in rows if x["seed"] == 0}
        lam = max(val, key=lambda l: (val[l], l))
        test = [x for x in rows if x["lam"] == lam and x["seed"] != 0]
        agg = {m: (float(np.mean([x[m] for x in test])), float(np.std([x[m] for x in test])))
               for m in ("plasticity", "retention", "overall")}
        Ntest = len(test) * K * grid["T"]
        lo, hi = wilson(agg["overall"][0], Ntest)
        summ.append(dict(rung=rung, n=n, K=K, alpha=alpha, T=grid["T"], M=grid["M"], lam_selected=lam,
                         state_bytes=test[0]["state_bytes"], width=test[0]["width"],
                         plasticity=agg["plasticity"][0], plasticity_sd=agg["plasticity"][1],
                         retention=agg["retention"][0], retention_sd=agg["retention"][1],
                         overall=agg["overall"][0], overall_sd=agg["overall"][1],
                         overall_wilson95=[lo, hi], n_test_seeds=len(test), chance=1 / K))
    meta = dict(mode=a.mode, grid=grid, wall_s=time.time() - t0, torch=torch.__version__,
                python=platform.python_version(), threads=torch.get_num_threads(),
                constants=dict(D_IN=D_IN, D_C=D_C, D_V=D_V, FRAC=FRAC, SIGMA=SIGMA, TAU=TAU),
                selection="lambda chosen on seed 0 by overall acc; metrics are held-out seeds",
                status="TOY PILOT: training-free memory rules, fixed random encoder, synthetic task")
    json.dump(dict(meta=meta, summary=summ), open(f"results_{a.mode}.json", "w"), indent=1)
    with open(f"results_{a.mode}_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in summ[0] if k != "overall_wilson95"] + ["wilson_lo", "wilson_hi"])
        w.writeheader()
        for s_ in summ:
            d = {k: v for k, v in s_.items() if k != "overall_wilson95"}; d["wilson_lo"], d["wilson_hi"] = s_["overall_wilson95"]
            w.writerow(d)
    with open(f"results_{a.mode}_raw.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(raw[0].keys())); w.writeheader()
        for x in raw:
            w.writerow({**x, "acc_per_task": " ".join(f"{v:.4f}" for v in x["acc_per_task"])})
    print(f"done {time.time()-t0:.1f}s")
    for s_ in summ:
        print(f"n={s_['n']:5d} K={s_['K']:4d} a={s_['alpha']:.1f} {s_['rung']:15s} lam={s_['lam_selected']:<6} "
              f"B={s_['state_bytes']:>9d} plast={s_['plasticity']:.3f} ret={s_['retention']:.3f} all={s_['overall']:.3f}")


if __name__ == "__main__":
    main()
