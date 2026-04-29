# Reproduction Scope

The reproduction scope in this project is intentionally reduced.

What is reproduced faithfully:

- the idea of comparing a standard `Decision Tree` against a threshold-constrained version
- the idea that deployment efficiency can be approximated by threshold count
- the idea of `pushback` as a mitigation mechanism
- the idea of adding a small engineering improvement to mitigation logic

What is simplified:

- no real programmable switch hardware
- no full P4 runtime stack in the final experiment
- no exact SRAM/TCAM resource measurements
- no exact Tofino or BMv2 execution in the final evaluation

Why this reduced scope is still valid:

- the course requires a `prototype / simulation / reduced reproduction`, not an exact industrial deployment
- the reduced reproduction still tests the paper's central trade-off:
  - more compact model vs classification performance
- it also tests the paper's mitigation idea:
  - pushback can reduce attack traffic earlier than victim-side-only handling

Final scope used in the project:

1. Dataset
   - `CICIDS2017 Wednesday` subset from Kaggle

2. Features
   - `destination_port`
   - `init_win_bytes_forward`
   - `fwd_header_length`
   - `packet_length_mean`
   - `flow_packets_persecond`

3. Models
   - `DT`
   - `RF`
   - `DT-CTS`

4. Mitigation modes
   - `no_pushback`
   - `immediate_pushback`
   - `gated_pushback`

Claim that should be used in the report:

> We reproduce the core deployment-oriented ideas of SISTAR in a reduced software environment, focusing on threshold-constrained tree-based detection and upstream pushback mitigation.
