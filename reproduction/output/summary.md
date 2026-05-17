# Reduced SISTAR reproduction summary

## Dataset
- Source: `Raw Kaggle parquet dhoogla/cicids2017/DoS-Wednesday-no-metadata.parquet`

## Classification
- Best F1 in this reduced run: `DT` with `0.9864`
- `DT-CTS` F1: `0.9574`
- `DT` F1: `0.9864`
- `RF` F1: `0.9712`

## Threshold efficiency
- `DT` total thresholds: `30`
- `DT-CTS` total thresholds: `13`
- Threshold reduction vs DT: `56.67%`

## Pushback simulation
- Attack bytes reaching victim without pushback: `2938459`
- Attack bytes reaching victim with gated pushback: `64791`
- Attack-byte reduction from the small improvement: `97.80%`
- Benign bytes preserved with gated pushback: `305761878`
- False block events with gated pushback: `2`

## Small improvement beyond the paper
- This reduced reproduction adds `gated_pushback`: only trigger upstream blocking after two consecutive malicious detections.
- Goal: preserve more benign traffic than naive immediate pushback while still reducing attack traffic strongly.