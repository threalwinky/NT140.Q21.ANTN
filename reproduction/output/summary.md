# Reduced SISTAR reproduction summary

## Dataset
- Source: `Synthetic DDoS-like flow dataset (local Wednesday CSV is unavailable, incompatible, or only a Git LFS pointer)`

## Classification
- Best F1 in this reduced run: `RF` with `1.0000`
- `DT-CTS` F1: `0.9983`
- `DT` F1: `0.9983`
- `RF` F1: `1.0000`

## Threshold efficiency
- `DT` total thresholds: `2`
- `DT-CTS` total thresholds: `2`
- Threshold reduction vs DT: `0.00%`

## Pushback simulation
- Attack bytes reaching victim without pushback: `47573670`
- Attack bytes reaching victim with gated pushback: `2883138`
- Attack-byte reduction from the small improvement: `93.94%`
- Benign bytes preserved with gated pushback: `144941321`
- False block events with gated pushback: `0`

## Small improvement beyond the paper
- This reduced reproduction adds `gated_pushback`: only trigger upstream blocking after two consecutive malicious detections.
- Goal: preserve more benign traffic than naive immediate pushback while still reducing attack traffic strongly.