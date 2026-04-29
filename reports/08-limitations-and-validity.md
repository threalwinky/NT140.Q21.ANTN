# Limitations And Threats To Validity

This project is a reduced reproduction, not a full hardware reproduction.

## Main limitations

1. No real programmable switch hardware
   - we do not claim exact Tofino-level reproduction

2. No exact P4/BMv2 resource measurement in the final experiments
   - therefore SRAM/TCAM/stage usage from the paper is not re-validated directly

3. Binary classification simplification
   - the project converts Wednesday traffic into `benign` vs `attack`
   - this is simpler than a fine-grained multi-class detection setting

4. Reduced feature set
   - only 5 features were used to stay aligned with the paper and keep the experiment understandable

5. Simplified pushback topology
   - the mitigation experiment uses a reduced logical topology instead of a full programmable network

## Why the results are still meaningful

- the classification experiment still measures the trade-off between raw performance and deployment-oriented compactness
- the threshold experiment directly reflects the paper's main deployment idea
- the pushback experiment still demonstrates the systems-level intuition of mitigating attack traffic earlier in the path

## Threats to validity

- the exact metrics may vary with a different sample from Wednesday
- model performance may change under different feature choices
- the pushback simulation is less realistic than a full P4 or Mininet deployment

Suggested wording for the report:

> The goal of this project is not to exactly reproduce the hardware-level claims of SISTAR, but to reproduce its main design principles in a reduced and executable software environment.
