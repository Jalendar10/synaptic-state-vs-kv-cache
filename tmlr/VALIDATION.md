# VALIDATION — "Synaptic State or KV-Cache?" (CDLR) vs. venue terms

Prepared 2026-10-27 (America/New_York). Author: Jalendar Reddy Maligireddy (sole author).
Source: `../main.tex`, `../references.bib`, `../main.pdf` (18 pp, plain article class).
Output: this folder (`main.tex`, `references.bib`, `main.pdf`, `supplementary_anonymized.zip`).

## 1. Tier-1 venue status (why TMLR)

| Venue | Status on 2026-10-27 | Decision |
|---|---|---|
| ICLR 2027 | Abstract deadline Sep 18 2026, full paper Sep 25 2026, both passed (dates from the brief; not re-checked in this run) | Cannot submit |
| NeurIPS 2026 | Deadline passed (May 2026) | Cannot submit |
| NeurIPS 2027 | Call for papers not open yet | Not possible now |
| ICML 2027 | Not in scope of brief. Usually due late Jan; check the CFP when it opens | Optional later |
| **TMLR** | **Rolling submissions on OpenReview** | **Target** |

TMLR fits the paper. Its acceptance criteria ask whether claims are supported by evidence and whether the work interests part of the audience. Significance at scale is not required. Its listed scope includes "development of new analytical frameworks" and "formalization of ... methods for assessing performance". A framework, proposition, and protocol paper with no large-scale results is in scope, provided it claims nothing it has not shown. The J2C certification can later lead to a slot at NeurIPS, ICLR, or ICML.

## 2. TMLR requirements: pass/fail

Sources: https://jmlr.org/tmlr/author-guide.html, https://jmlr.org/tmlr/editorial-policies.html (read 2026-10-27),
style from https://github.com/JmlrOrg/tmlr-style-file (commit 7bf90ef, 2023-06-30).

| # | Requirement | Original draft | TMLR version (this folder) |
|---|---|---|---|
| 1 | Official TMLR LaTeX style + template | FAIL (plain `article`, 11pt, 1in) | PASS: `\usepackage{tmlr}`, `tmlr.bst`, official `fancyhdr.sty`. Header reads "Under review as submission to TMLR" |
| 2 | Double-blind, anonymized PDF | FAIL (name, affiliation, email, GitHub user in PDF) | PASS: "Anonymous authors / Paper under double-blind review". PDF text has no name, affiliation, email, ORCID, or `Jalendar10` (checked with `pdftotext \| grep`). PDF Author metadata is empty |
| 3 | No link to a de-anonymized version | FAIL (`github.com/Jalendar10/...`) | PASS: link removed. Code goes in the anonymized supplementary ZIP. Repo URL returns in camera-ready |
| 4 | `<repo-name>` placeholder | Already fixed in source (real URL) | Real URL kept out of the review PDF. Camera-ready gets `https://github.com/Jalendar10/synaptic-state-vs-kv-cache` |
| 5 | Supplementary material anonymized, PDF/ZIP, ≤100 MB | n/a | PASS: `supplementary_anonymized.zip` (0.61 MB). Contains prereg JSON (repo field anonymized), `tiny_full/`, `continual/`, `arena/`, and **`e2_capacity/` (added 2026-10-28; the internal module name was replaced with a generic one)**. Grep of all 96 members for name/email/ORCID/institution/`Jalendar10`: none found |
| 6 | Originality; no dual archival submission; arXiv OK | Not verifiable by me | **Author must confirm**: not under review or published at any archival venue. arXiv is fine, but the TMLR PDF must not link to it |
| 7 | Length justified by content | 18 pp, ~11 pp main | PASS: **15 pp total (after the E2 fold-in on 2026-10-28); main text pp. 1–10 (≤12 target)**, refs pp. 10–14, appendix pp. 14–15 |
| 8 | Abstract is one paragraph | PASS | PASS |
| 9 | Broader Impact Statement if there is significant risk of harm | Ethics paragraph inside Discussion | PASS: separate unnumbered "Broader Impact Statement" before refs, as the template asks |
| 10 | Claims supported by evidence (acceptance criterion) | Mostly PASS; probes sat near the main text | PASS: no large-scale results claimed. Smoke tests are only in App. A and labelled as supporting no main-text claim. Spot-checked against run files (52,531 params; 1.235 halting; BPTT 0.914 online acc; BDH val loss 1.87526). Figs. 1, 2, 4 are conceptual or closed-form. **Fig. 3 is the E2 PILOT, the only measured figure.** It plots `data/n50_plot.dat`, copied byte-for-byte from `../experiments/e2_capacity/n50_plot.dat`. Table 3 matches `results_sweep_n50.csv` and the E2 README |
| 11 | Venue-specific wording | "Main-track claims at ICLR/NeurIPS/ICML should wait..." | Removed. Compute envelope now neutral |
| 12 | LLM / AI disclosure | n/a | **Not mandated.** TMLR LLM policy: LLMs may be used as assistive tools, authors take full responsibility, LLMs cannot be authors. No required statement section. **No AI statement added to the manuscript** |
| 13 | Solo-author quota (Generalized Harmonic Quota, N1 = 2; doubled to 4 for TMLR reviewers/AEs) | n/a | **Author must check** the remaining budget with the quota tool on the TMLR site before submitting. A solo paper uses the largest share. Desk rejects also count |
| 14 | OpenReview profiles complete (affiliation, conflicts, publication history); suggest action editors; IRB/funding/competing interests | n/a | **BLOCKER (author action)**: needs a complete, active OpenReview profile. Ideally use the institutional email (University of the Cumberlands); new profiles with personal email may need moderation, which can take days |
| 15 | License CC BY 4.0 from submission | n/a | Note only. Author must agree at submission |
| 16 | Compiles cleanly | PASS | PASS: `latexmk -pdf` exits 0. No undefined refs or citations. One 1.5 pt overfull box in Table 1 (cosmetic). Font-shape substitutions are harmless |

## 3. What changed in the rewrite

- Moved to the official TMLR template and anonymized the author block. The real author block stays in the source and appears only with `[accepted]`.
- Compressed the main text from ~11 to ~9 pages. Intro motivation is now prose. Related work, protocol principles (P1–P7 as one paragraph), and open problems are tightened. Interpretability is folded into Limitations.
- **Kept intact:** Definition 1 and the unified operator table. **Proposition 1** now has a full short proof (the rounding is explicit) instead of a "proof sketch". The **CDLR specification** (fast state, consolidation κ, gated reads, workspace, adapter, audit, training/complexity) and H1–H4 are kept. So are the **critique table** (Table 2, unchanged content) and **protocol tracks E1–E5**, plus the compute envelope.
- **New conceptual TikZ figures (no results):**
  - Fig. 1: closed-form byte crossover T★ = nd/(2 d_model). KV-cache vs. BDH-GPU state, with T★ ≈ 5.46k, and the CDLR M=1 crossover ≈ 10.9k. Only Eq. 1 is plotted.
  - Fig. 4: the E3 ablation ladder (a)→(i), with the byte-transfer and backbone controls. (Fig. 3 is the E2 N50 PILOT.)
- **Probes demoted:** "Preliminary Smoke Tests (Not Main Results)" sit in Appendix A only. The main text points to them once, in Scope.
- Removed the "NeurIPS checklist" phrasing (the citation is kept), the keywords line, and all venue names from the body.
- Code availability now points to the anonymized supplementary material.

## 3b. E2 fold-in (2026-10-28): claim-scope checklist

The PDF was rebuilt with `latexmk -pdf` (exit 0, 15 pp, no undefined refs). Anonymization was re-checked: `pdftotext main.pdf | grep -i 'jalendar|maligireddy|cumberland|gmail'` finds 0 hits, and the PDF Author field is empty.

| # | Claim-scope check | Status | Where |
|---|---|---|---|
| S1 | Every empirical claim is limited to **regime characterisation at toy n ≤ 4096** (d = 32, synthetic k-WTA keys, closed-set recall, 3 seeds, CPU) | PASS | Abstract (last sentence), Scope ¶, Fig. 3 caption, Remark 2, App. A P5, Limitations (vii) |
| S2 | Raw positive Hebbian **plateaus** (N50 ≈ 530–600 for n ≥ 512; exponent 0.29 ± 0.07 overall) | PASS, stated | Abstract, Remark 2(a), Fig. 3, Table 3 |
| S3 | Centred Hebbian and delta with random keys: **slopes 0.86 ± 0.01 / 0.94 ± 0.01** | PASS, stated | Abstract, Remark 2(b), Fig. 3, Table 3 |
| S4 | Keys whose shared structure the write rule cannot remove (raw fixed-ρ; strongly correlated delta; clustered) are **flat (exponent ≈ 0)**; ≠ √n regime. Centred fixed-ρ is *not* flat (exponents ~0.86–0.88). Not a Claim 7 refutation | PASS after abstract fix 2026-10-28 | Abstract (fixed), Remark 2(c), Fig. 3 caption, P5 |
| S5 | **No** claim of general Õ(n) or Ω̃(√n) capacity | PASS: explicit disclaimer | Scope ¶ (i), P5 last sentence |
| S6 | **No** claim of a Transformer-matched (param/token/FLOP) bakeoff result | PASS: explicit disclaimer. P4 (unmatched) is still labelled "supports no ranking" | Scope ¶ (ii), Fig. 3 caption ("no Transformer baseline") |
| S7 | **No** claim about trained-encoder behaviour | PASS: explicit disclaimer | Scope ¶ (iii), Open problem (1), Limitations (vii) |
| S8 | Pilot evidence is labelled **PILOT** everywhere it appears | PASS | C6, Fig. 3 caption, E2 ¶, Table 3, App. A P5 heading |
| S9 | H1 left **as preregistered**. Pilot-informed refinements go in a separate Remark, not a revised hypothesis | PASS | Remark 2 after H1 |
| S10 | Numbers traceable to run files | PASS | `../experiments/e2_capacity/results_sweep_n50.csv`, `results_sweep.json`; supplementary `e2_capacity/` |
| S11 | The E3 ablation ladder (Fig. 4) is still **conceptual** in the PDF. The CPU toy E3 pilot in `../experiments/e3_ablation/` is **not** cited in the TMLR draft yet | Note | Fold it in only after the review of the toy E3 results |

## 4. Remaining blockers before the author submits (I did NOT submit)

1. **OpenReview account/profile**: complete it (affiliation history, conflicts, DBLP or publication list). Add ORCID 0009-0002-5881-0084 on the profile. The TMLR style has no ORCID field.
2. **Quota check**: confirm solo-author TMLR budget remains for 2026 (N1 = 2).
3. **Originality confirmation**: no parallel archival submission. If an arXiv version exists, do not link it.
4. **Submission form**: suggest 3–5 action editors (sequence models, continual learning, or efficient Transformers expertise). Answer the IRB (n/a), funding, and competing-interests questions.
5. **AI statement**: none required by TMLR. Nothing added.
6. **Optional, recommended**: an anonymous.4open.science mirror of the repo if you prefer a link over the ZIP. That needs the author's GitHub authorization, so I did not create one.
7. **Scientific risk (honest)**: a toy E2 PILOT is now included (n ≤ 4096; regime characterisation only). TMLR reviewers may still ask for E2 at the preregistered widths with trained encoders, and for E3 (ablation ladder) at small scale. These are about an order of magnitude cheaper than E1. Running them before or during rebuttal would strengthen acceptance odds a lot. No new numbers were invented here.

## 5. Camera-ready switch

Change `\usepackage{tmlr}` → `\usepackage[accepted]{tmlr}`. Set `\month`, `\year`, `\openreview`. Restore the GitHub URL in "Code availability".
