"""E2 toy capacity probe: associative recall in a fixed-size n x d synaptic state.

Memory (same update/read as ALRS `HebbianMemory`, lambda=1, eta=1, i.e. no decay):
    S = sum_i phi(k_i) v_i^T  (n x d)       read(q) = q^T S / (q^T z)
Delta-rule variant (sequential, normalised):  S += phi(k) (v - S^T phi(k))^T / ||phi(k)||^2
Recall: query with the stored key, decode by argmax correlation against the N stored
values (closed-set, chance = 1/N). N50 = number of stored facts at which accuracy = 0.5
(log-linear interpolation on a geometric N grid).

Key families (all positive, k-WTA sparse in R^n, BDH-like, active fraction f):
  random      : ReLU(G x) top-k of an i.i.d. Gaussian pre-activation
  corr_rho    : pre-activation = sqrt(rho) * shared + sqrt(1-rho) * private
  clustered   : C=8 cluster centres, keys = centre + sigma*noise (pre-activation corr ~0.8)
Values: i.i.d. Rademacher in R^d.
"""
from __future__ import annotations
import argparse, csv, json, math, time, platform
import numpy as np
import torch

torch.set_num_threads(8)


def make_keys(N, n, family, frac, gen):
    k = max(1, int(round(frac * n)))
    if family == "random":
        pre = torch.randn(N, n, generator=gen)
    elif family.startswith("corr"):
        rho = float(family.split("_")[1])
        shared = torch.randn(1, n, generator=gen)
        pre = math.sqrt(rho) * shared + math.sqrt(1 - rho) * torch.randn(N, n, generator=gen)
    elif family == "clustered":
        C = 8
        cent = torch.randn(C, n, generator=gen)
        idx = torch.randint(0, C, (N,), generator=gen)
        pre = cent[idx] + 0.5 * torch.randn(N, n, generator=gen)
    else:
        raise ValueError(family)
    if frac >= 1.0:
        return pre  # dense signed reference (not BDH-like)
    top = pre.topk(k, dim=1)
    out = torch.zeros_like(pre)
    out.scatter_(1, top.indices, torch.relu(top.values))
    return out


def recall_acc(keys, vals, rule, chunk=1024):
    N, n = keys.shape
    if rule == "hebbian":
        S = keys.T @ vals
    elif rule == "hebbian_centered":
        # cheap whitening: remove the common-mode key component before write/read
        keys = keys - keys.mean(0, keepdim=True)
        S = keys.T @ vals
    elif rule == "delta":
        S = torch.zeros(n, vals.shape[1])
        kn = keys / (keys.pow(2).sum(1, keepdim=True) + 1e-8)
        for i in range(N):
            S += torch.outer(kn[i], vals[i] - keys[i] @ S)
    else:
        raise ValueError(rule)
    correct = 0
    for s in range(0, N, chunk):
        r = keys[s:s + chunk] @ S                      # (c, d); normaliser q^T z is a positive scalar -> argmax-invariant
        scores = r @ vals.T                            # (c, N)
        pred = scores.argmax(1)
        correct += (pred == torch.arange(s, s + r.shape[0])).sum().item()
    return correct / N


def n50(Ns, accs):
    for i in range(1, len(Ns)):
        if accs[i - 1] >= 0.5 > accs[i]:
            a0, a1 = accs[i - 1], accs[i]
            x0, x1 = math.log(Ns[i - 1]), math.log(Ns[i])
            return math.exp(x0 + (a0 - 0.5) / (a0 - a1) * (x1 - x0))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "sweep"], default="smoke")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.mode == "smoke":
        widths, seeds, d = [64, 128, 256], [0], 32
        families, rules = ["random", "corr_0.5"], ["hebbian", "hebbian_centered", "delta"]
    else:
        widths, seeds, d = [64, 128, 256, 512, 1024, 2048, 4096], [0, 1, 2], 32
        families = ["random", "corr_0.2", "corr_0.5", "corr_0.8", "clustered"]
        rules = ["hebbian", "hebbian_centered", "delta"]
    frac = 1 / 16
    Ngrid_all = sorted({int(round(2 ** (e / 4))) for e in range(8, 4 * 16 + 1)})  # 4 .. 65536, quarter-octaves
    rows, t0 = [], time.time()
    for rule in rules:
        for fam in families:
            for n in widths:
                for seed in seeds:
                    Ns, accs = [], []
                    below = 0
                    for N in Ngrid_all:
                        if rule == "delta" and (N > 16 * n or n > 2048):  # delta is O(N n d) sequential; cap
                            break
                        gen = torch.Generator().manual_seed(1000 * seed + 7 * n + N)
                        keys = make_keys(N, n, fam, frac, gen)
                        vals = torch.randint(0, 2, (N, d), generator=gen).float() * 2 - 1
                        acc = recall_acc(keys, vals, rule)
                        Ns.append(N); accs.append(acc)
                        rows.append(dict(rule=rule, family=fam, n=n, d=d, seed=seed, N=N, acc=acc,
                                         state_bytes_fp32=4 * (n * d + n)))
                        below = below + 1 if acc < 0.3 else 0
                        if below >= 2:
                            break
                    rows[-1]["_n50"] = n50(Ns, accs)
                    print(f"[{time.time()-t0:6.1f}s] {rule:7s} {fam:9s} n={n:5d} s={seed} N50={rows[-1]['_n50']}", flush=True)
    # aggregate
    n50s = {}
    for r in rows:
        if "_n50" in r:
            n50s.setdefault((r["rule"], r["family"], r["n"]), []).append(r.pop("_n50"))
    summary = []
    for (rule, fam, n), v in sorted(n50s.items()):
        vv = [x for x in v if x is not None]
        summary.append(dict(rule=rule, family=fam, n=n, d=d, n50_mean=float(np.mean(vv)) if vv else None,
                            n50_std=float(np.std(vv)) if vv else None, n_seeds=len(v), n_seeds_reached=len(vv)))
    fits = []
    for rule in rules:
        for fam in families:
            pts = [(s["n"], s["n50_mean"]) for s in summary if s["rule"] == rule and s["family"] == fam and s["n50_mean"]]
            if len(pts) >= 3:
                x = np.log([p[0] for p in pts]); y = np.log([p[1] for p in pts])
                A = np.vstack([x, np.ones_like(x)]).T
                coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
                # bootstrap-free CI: slope std err
                yhat = A @ coef; dof = max(1, len(x) - 2)
                se = math.sqrt(((y - yhat) ** 2).sum() / dof / ((x - x.mean()) ** 2).sum()) if len(x) > 2 else float("nan")
                fits.append(dict(rule=rule, family=fam, slope=float(coef[0]), slope_se=float(se),
                                 intercept=float(coef[1]), n_points=len(pts),
                                 n50_over_n_at_max=float(pts[-1][1] / pts[-1][0])))
    out = a.out or f"results_{a.mode}"
    with open(out + "_raw.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(out + "_n50.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys())); w.writeheader(); w.writerows(summary)
    meta = dict(mode=a.mode, widths=widths, seeds=seeds, d=d, active_fraction=frac, families=families, rules=rules,
                torch=torch.__version__, host=platform.platform(), wall_s=time.time() - t0,
                decode="closed-set argmax over the N stored values (chance 1/N)")
    json.dump(dict(meta=meta, n50=summary, fits=fits), open(out + ".json", "w"), indent=2)
    print(json.dumps(fits, indent=1))
    print(f"total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
