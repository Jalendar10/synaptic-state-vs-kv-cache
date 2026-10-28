# Abstract

**Synaptic State or KV-Cache? A Unified Account of Softmax Attention, Hebbian Synaptic State, and Recurrent Latent Reasoning, with a Dual-Timescale Architecture Proposal and a Matched-Compute Evaluation Protocol**

*Jalendar Reddy Maligireddy, Ph.D. Candidate, Information Technology, University of the Cumberlands, Edison, NJ, USA, jalendarreddy97@gmail.com*

Softmax attention stores context as an explicit key–value cache whose size grows with sequence length. Hebbian "synaptic" models such as the Dragon Hatchling (BDH) store it in a fixed-size, positive, high-dimensional state that is rewritten at every token. Recurrent latent reasoners such as BDH-CQ learn tasks from demonstrations by writing them into such a state and then iterating in latent space. We ask one question: **when, and at what cost, should inference-time memory be synaptic rather than a cache?**

We (i) formalise all three families as instances of one associative-memory operator with explicit write, read, forgetting, consolidation, and workspace maps; (ii) show that any single-timescale decaying state couples retention and interference, so it cannot both adapt quickly and keep earlier episodes; (iii) propose **Compact Dual-Timescale Latent Reasoning (CDLR)**, which pairs a fast episodic Hebbian state with a slow, gated, consolidated memory bank, a halting latent workspace, a local readout adapter, and a built-in audit trail; (iv) critically audit the empirical claims of BDH and BDH-CQ, separating paper-stated limits from inferred gaps; and (v) specify a preregistrable, matched-parameter, matched-token, and matched-compute evaluation protocol that reports accuracy, memory, and latency jointly and treats negative results as first-class.

We report no large-scale results. The contribution is the framework, the analysis, the falsifiable hypotheses, and the protocol needed to test them.

> Status: preprint draft. Small CPU "preliminary probes" appear only in Appendix A and are not evidence for the hypotheses.
