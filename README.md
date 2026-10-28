# Synaptic State or KV-Cache?
### A Unified Account of Softmax Attention, Hebbian Synaptic State, and Recurrent Latent Reasoning — with Compact Dual-Timescale Latent Reasoning (CDLR) and a Matched-Compute Evaluation Protocol

**Author:** Jalendar Reddy Maligireddy, Ph.D. Candidate, Information Technology, University of the Cumberlands (Edison, NJ), jalendarreddy97@gmail.com
**Status:** preprint draft (framework + analysis + protocol; large-scale experiments are future work)

## In one paragraph
Transformers (Vaswani et al., 2017) keep context in a growing KV-cache. BDH (Kosowski et al., 2025, arXiv:2509.26507) keeps it in a fixed-size Hebbian synaptic state. BDH-CQ (Engdahl et al., 2026, arXiv:2608.09888) writes demonstrations into a recurrent memory and reasons in latent space. This paper puts all three in one associative-memory operator. It shows that single-timescale states couple retention and interference, and it proposes **CDLR**: fast episodic state S + slow gated consolidated bank C + halting latent workspace + local adapter + audit. It audits BDH/BDH-CQ claims with (P) paper-stated vs. (I) inferred gaps and fixes a preregistrable matched-params/tokens/FLOPs protocol reporting accuracy × memory × latency. See [ABSTRACT.md](ABSTRACT.md) and [CONTRIBUTIONS.md](CONTRIBUTIONS.md).

## Files
| File | What |
|---|---|
| `main.tex` | Full paper (article class, compiles without venue style files) |
| `references.bib` | BibTeX (core four papers + linear attention/SSM, latent reasoning, continual learning/CLS, evaluation) |
| `main.pdf` | Compiled PDF (17 pp: ~11 pp main text, references, Appendices A–C) |
| `ABSTRACT.md`, `CONTRIBUTIONS.md` | Repo landing one-pagers |
| `Makefile` | `make` builds the PDF; `make clean` |

## Build
```bash
cd paper
make            # = latexmk -pdf main.tex  (pdflatex + bibtex)
# or manually:
pdflatex main && bibtex main && pdflatex main && pdflatex main
```
Requires TeX Live with `natbib`, `tikz`, `booktabs`, `tabularx`, `cleveref`, `enumitem`, `microtype`.
To submit, move the body into the venue template (`iclr20XX_conference.sty`, `neurips_20XX.sty`, or `IEEEtran.cls`) and re-check page limits.

## Venue strategy (honest)
- **Now (framework + critique + protocol, no large-scale runs):** a **workshop track** at ICLR / NeurIPS / ICML (workshops on efficient sequence models, memory, or continual/lifelong learning), or **TMLR**, which reviews correctness rather than novelty-at-scale.
- **After running E1–E4 of the protocol** (≈0.55–1.1k A100-hours): a full study in **IEEE Transactions on Neural Networks and Learning Systems (TNNLS)**, or a main-track submission to **ICLR / NeurIPS / ICML**. A main-track submission only makes sense once matched-compute empirics exist. Without them it would likely be desk-rejected as a framework paper.
- **Secondary:** IEEE Access (survey/critique version), IJCNN.
- Not a fit: security venues (ACSAC, CCS).
Verify each venue's current call, page limits, and anonymity rules before submitting (double-blind: remove the author block and the repo link).

## Preregistration

Frozen protocol (before large-scale runs): [`prereg/e1_e5_protocol_v0.json`](prereg/e1_e5_protocol_v0.json). Experiment order: **E2 → E3 → E4 → E1 → E5**.

## Honesty rules this draft follows
- Every number from prior work cites its section/table.
- (P) paper-stated limitation vs. (I) our inference are always marked.
- Toy CPU probes from `../alrs`, `../arena`, `../continual`, `../tiny_full` appear **only** in Appendix A, with caveats, and include negative results.
- No claim of ARC parity, 600B scaling, or closing BDH §7.2.

## Remote
GitHub: `https://github.com/Jalendar10/synaptic-state-vs-kv-cache` (public repo; see `prereg/` for frozen protocol).
```bash
git remote add origin https://github.com/Jalendar10/synaptic-state-vs-kv-cache.git
```
