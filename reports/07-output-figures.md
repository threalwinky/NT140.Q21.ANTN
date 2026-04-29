# Output Figures

This file explains the figures produced by the reduced reproduction.

## 1. `classification_accuracy.png`

Meaning:

- compares `Accuracy` of `DT`, `RF`, and `DT-CTS`

How to explain it:

- `DT` and `RF` are the strongest baselines for classification quality
- `DT-CTS` is slightly lower
- this is expected because `DT-CTS` constrains thresholds for deployability

Main message:

> `DT-CTS` loses some accuracy, but it is not trying to maximize raw accuracy only; it is trying to be easier to deploy.

## 2. `classification_f1.png`

Meaning:

- compares `F1-score` of `DT`, `RF`, and `DT-CTS`

How to explain it:

- F1 is a better intrusion-detection metric than accuracy alone because it balances precision and recall
- `DT` and `RF` are both around `0.991`
- `DT-CTS` remains strong at `0.9646`

Main message:

> Even after reducing model complexity, `DT-CTS` remains effective enough for detection.

## 3. `threshold_usage.png`

Meaning:

- compares the total number of thresholds used by `DT`, `RF`, and `DT-CTS`

How to explain it:

- `RF` uses by far the most thresholds
- `DT` is much smaller
- `DT-CTS` is the most deployment-friendly tree among the tree models

Main numbers:

- `DT`: `22`
- `DT-CTS`: `15`
- reduction: `31.82%`

Main message:

> This figure is the closest reduced reproduction of the paper's main systems contribution.

## 4. `pushback_attack_bytes.png`

Meaning:

- shows attack bytes reaching the victim over time under 3 policies:
  - `no_pushback`
  - `immediate_pushback`
  - `gated_pushback`

How to explain it:

- `no_pushback` stays high because the network never blocks upstream
- `immediate_pushback` drops fastest, but is too aggressive
- `gated_pushback` also drops strongly and is more balanced

Main message:

> Pushback matters, and the improved gated version is more practical because it keeps more benign traffic while still reducing attack traffic sharply.
