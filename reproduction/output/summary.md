# Reduced SISTAR reproduction summary

## Dataset
- Source: `CICIDS2017 Wednesday subset from Kaggle`

## Classification
- Best F1 in this reduced run: `DT` with `0.9912`
- `DT-CTS` F1: `0.9646`
- `DT` F1: `0.9912`
- `RF` F1: `0.9912`

## Threshold efficiency
- `DT` total thresholds: `22`
- `DT-CTS` total thresholds: `15`
- Threshold reduction vs DT: `31.82%`

## Pushback simulation
- Attack bytes reaching victim without pushback: `1731491`
- Attack bytes reaching victim with gated pushback: `51302`
- Attack-byte reduction from the small improvement: `97.04%`
- Benign bytes preserved with gated pushback: `2020443640`
- False block events with gated pushback: `3`

## Small improvement beyond the paper
- This reduced reproduction adds `gated_pushback`: only trigger upstream blocking after two consecutive malicious detections.
- Goal: preserve more benign traffic than naive immediate pushback while still reducing attack traffic strongly.