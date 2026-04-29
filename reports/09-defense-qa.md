# Defense Q&A

## Q1. Why did you choose this paper?

Suggested answer:

> We chose this paper because it is recent, published at ACM CCS 2025, clearly belongs to network security, and contains both an algorithmic contribution and a systems contribution. It is also suitable for a reduced student reproduction because its core ideas can be simulated without requiring full hardware access.

## Q2. What is the main contribution of the paper?

Suggested answer:

> The main contribution is combining threshold-constrained tree-based DDoS detection with distributed pushback mitigation inside the programmable data plane.

## Q3. What exactly did your project reproduce?

Suggested answer:

> We reproduced the core ideas of the paper in a reduced software setting: `DT-CTS` style threshold-constrained detection, threshold-count comparison against baselines, and pushback mitigation in a simplified topology.

## Q4. Why did you not reproduce the Tofino part?

Suggested answer:

> We do not have access to real programmable switch hardware, and the local environment also lacks the full P4/BMv2 stack needed for a faithful hardware-like run. Therefore, we focused on a reduced reproduction that still tests the paper's main ideas quantitatively.

## Q5. Why did you use CICIDS2017 Wednesday?

Suggested answer:

> The paper itself discusses DDoS and DoS behavior and uses CICIDS2017 in its evaluation. The Wednesday subset is especially relevant because it contains several DoS-related attack types such as Hulk, GoldenEye, slowloris, and Slowhttptest.

## Q6. Why is DT-CTS interesting if its F1 is lower than DT here?

Suggested answer:

> Because the goal is not only to maximize raw F1. The paper is about deployability under constrained switch resources. In our reproduction, `DT-CTS` reduces thresholds by `31.82%`, which captures the main deployment-oriented trade-off.

## Q7. Why is RF not the final chosen model if it performs well?

Suggested answer:

> RF performs well in pure classification, but it uses many more thresholds than DT-CTS, which makes it less attractive from a deployment perspective. In our run, RF used `115` thresholds while DT-CTS used only `15`.

## Q8. What is your own contribution beyond the paper?

Suggested answer:

> We proposed `gated_pushback`, where upstream blocking only activates after two consecutive malicious detections. This reduced false blocking from `20` to `3` while still reducing attack traffic strongly.

## Q9. What is the most important result from your project?

Suggested answer:

> The most important result is that a reduced SISTAR-style design still works: we observed a clear threshold reduction in the model and a `97.04%` reduction in attack bytes reaching the victim with `gated_pushback` compared to `no_pushback`.

## Q10. What would you do next if you had more time?

Suggested answer:

> We would run the BMv2 part with a full P4 toolchain, expand the topology, and compare more feature-selection strategies or threshold budgets.
