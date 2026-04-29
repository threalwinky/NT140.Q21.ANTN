# Executive Summary

This project studies the paper `SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes` and reproduces its core ideas in a reduced software setting.

The paper's main idea is:

- detect DDoS traffic in the programmable data plane,
- compress model complexity using `DT-CTS`,
- and reduce attack traffic earlier in the network using `pushback`.

Because we do not have real programmable switch hardware, the project intentionally reproduces a reduced but defensible subset:

- a baseline `Decision Tree`,
- a baseline `Random Forest`,
- the repository's `DT-CTS` implementation,
- threshold-count comparison as a deployment-efficiency proxy,
- and a simplified pushback simulation on a 3-hop logical topology.

The reproduction is run on the `CICIDS2017 Wednesday` subset downloaded from Kaggle. This aligns well with the paper because the Wednesday subset contains DoS/DDoS behavior and is explicitly discussed in the paper.

Main results of the reduced reproduction:

- `DT` F1: `0.9912`
- `RF` F1: `0.9912`
- `DT-CTS` F1: `0.9646`
- `DT-CTS` reduces thresholds from `22` to `15` compared with `DT`
- threshold reduction vs `DT`: `31.82%`
- `gated_pushback` reduces attack bytes reaching the victim by `97.04%` relative to `no_pushback`

Project claim:

> This project reproduces the core ideas of SISTAR in a reduced software prototype: threshold-constrained tree-based DDoS detection with alert-triggered pushback mitigation, evaluated on a real subset of CICIDS2017.
