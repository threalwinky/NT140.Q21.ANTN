# Reduced SISTAR reproduction summary

## Dataset
- Source: `Loaded CICIDS2017 combine.csv from combine.csv (paper-compatible BENIGN vs Wednesday DoS subset)`

## Classification
- Best F1 in this reduced run: `DT` with `0.9620`
- `DT-CTS` F1: `0.9249`
- `DT` F1: `0.9620`
- `RF` F1: `0.9327`

## Threshold efficiency
- `DT` total thresholds: `36`
- `DT-CTS` total thresholds: `14`
- Threshold reduction vs DT: `61.11%`

## Hierarchical Confidence-Aware Pushback
- Attack bytes reaching victim without pushback: `5876251`
- Attack bytes reaching victim with hierarchical confidence-aware pushback: `4591`
- Attack-byte reduction from the new mitigation design: `99.92%`
- Benign bytes preserved with hierarchical confidence-aware pushback: `2052047683`
- False block events with hierarchical confidence-aware pushback: `0`
- Local rate-limit events: `23`
- Upstream pushback events: `10`
- Hard block events: `8`

## Improvement beyond the paper
- This reduced reproduction adds `hierarchical_confidence_pushback`: edge and core DT-CTS detectors accumulate a suspicion score before mitigation escalates.
- Goal: react in stages (`monitor -> local rate-limit -> upstream pushback -> hard block`) so benign bursts are less likely to be blocked too early.