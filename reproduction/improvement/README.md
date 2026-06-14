# Hierarchical Confidence-Aware Pushback

This directory contains the dedicated improvement experiment for the project.

## Why this is stronger than a fixed gate

The previous fixed-gate idea only changed the blocking rule from:

- block after one malicious detection

to:

- block after two malicious detections in a row

That helped reduce false blocks, but it was still a small policy tweak.

The new `Hierarchical Confidence-Aware Pushback` is stronger because it changes the mitigation logic at the system level:

- `edge DT-CTS` detects early
- `core DT-CTS` confirms more carefully
- each source gets a `suspicion score`
- mitigation escalates through:
  - `monitor`
  - `local rate-limit`
  - `upstream pushback`
  - `hard block`

## Run the experiment

From the project root:

```bash
python3 reproduction/improvement/run_hierarchical_improvement.py
```

Or from this directory:

```bash
cd reproduction/improvement
python3 run_hierarchical_improvement.py
```

## Important Outputs

After running, the key files are:

- `output/TEACHER_SUMMARY.md`
- `output/teacher_comparison_table.csv`
- `output/teacher_policy_comparison.png`
- `output/teacher_attack_timeline.png`
- `output/hierarchical_improvement_dashboard.png`
- `output/improvement_pushback_metrics.csv`
- `output/improvement_pushback_detail.csv`

## How to read the policies

- `no_pushback`: baseline, no upstream mitigation
- `immediate_pushback`: original paper-like behavior, block immediately after one malicious decision
- `hierarchical_confidence_pushback`: improved behavior with accumulated confidence and staged response

## What to emphasize in the report

- `immediate_pushback` can suppress attack traffic very aggressively, but it is also the easiest one to over-block.
- `hierarchical_confidence_pushback` is more realistic as a system improvement because it does not jump straight to hard blocking.
- The improvement should be presented as a coordination and mitigation redesign, not just as a threshold tweak.
