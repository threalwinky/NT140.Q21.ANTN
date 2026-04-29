# Small Improvement Beyond The Paper

The project adds one small improvement to the original pushback idea:

- `gated_pushback`

Definition:

- Instead of pushing back immediately after a single malicious detection,
- the system only activates upstream blocking after the same source is detected as malicious in `2` consecutive windows.

Why this is a reasonable improvement:

- real detectors can produce occasional false positives
- an immediate block is risky in practical networks
- a small confirmation gate can preserve more benign traffic

Improvement goal:

- reduce false positives in mitigation
- reduce benign traffic loss
- still keep attack traffic low

Comparison:

### Immediate pushback

- strongest attack suppression
- highest collateral damage
- false block events: `20`

### Gated pushback

- slightly weaker attack suppression than immediate pushback
- much lower collateral damage
- false block events: `3`
- benign bytes preserved: `2,020,443,640`

Conclusion:

> `gated_pushback` is a practical engineering refinement of SISTAR's pushback logic. It trades a small amount of aggressiveness for a large improvement in benign-traffic preservation.

Suggested sentence for the report:

> In addition to reproducing the paper's threshold-constrained detection and pushback ideas, we propose `gated_pushback`, which requires two consecutive malicious detections before upstream blocking is activated. This reduces false blocking significantly while still preserving most of the mitigation benefit.
