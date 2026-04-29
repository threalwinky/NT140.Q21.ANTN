# Experimental Results

Dataset source:

- `CICIDS2017 Wednesday subset from Kaggle`

Selected labels on Wednesday:

- `BENIGN`
- `DoS Hulk`
- `DoS GoldenEye`
- `DoS slowloris`
- `DoS Slowhttptest`
- `Heartbleed`

The reproduction converts this into a binary task:

- `BENIGN` -> benign
- all other labels -> attack

## Classification results

From `../reproduction/output/classification_metrics.csv`:

| Model | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| DT | 0.9912 | 0.9873 | 0.9952 | 0.9912 |
| RF | 0.9912 | 0.9936 | 0.9888 | 0.9912 |
| DT-CTS | 0.9640 | 0.9489 | 0.9808 | 0.9646 |

Interpretation:

- `DT` and `RF` provide the strongest pure classification quality in this reduced run.
- `DT-CTS` is weaker in F1, but still performs strongly enough to be useful.
- The result supports the main paper trade-off:
  - some loss in predictive quality may be accepted to improve deployability.

## Threshold-efficiency results

From `../reproduction/output/threshold_metrics.csv`:

| Model | Total thresholds | Features used | Max thresholds on one feature |
| --- | ---: | ---: | ---: |
| DT | 22 | 5 | 7 |
| RF | 115 | 5 | 34 |
| DT-CTS | 15 | 5 | 3 |

Interpretation:

- `DT-CTS` reduces total thresholds from `22` to `15` compared with `DT`.
- This corresponds to a threshold reduction of `31.82%`.
- The strongest deployment-oriented constraint is visible in the last column:
  - `DT-CTS` caps per-feature threshold usage at `3`,
  - while plain `DT` and especially `RF` use many more.

This is the clearest reduced reproduction of the paper's main deployment idea.

## Pushback results

From `../reproduction/output/pushback_metrics.csv`:

| Policy | Attack bytes to victim | Benign bytes to victim | Attack flows to victim | Benign flows to victim | False block events |
| --- | ---: | ---: | ---: | ---: | ---: |
| no_pushback | 1,731,491 | 3,509,171,465 | 240 | 1200 | 0 |
| immediate_pushback | 362 | 693,712,885 | 3 | 347 | 20 |
| gated_pushback | 51,302 | 2,020,443,640 | 16 | 1007 | 3 |

Interpretation:

- `immediate_pushback` is the most aggressive policy.
- It nearly eliminates attack traffic, but blocks too much benign traffic and creates many false block events.
- `gated_pushback` is more balanced:
  - it still reduces attack bytes by `97.04%` relative to `no_pushback`,
  - while preserving much more benign traffic than `immediate_pushback`,
  - and reducing false block events from `20` to `3`.

Main conclusion:

> The reduced reproduction supports the SISTAR design direction: compact threshold-constrained detection combined with upstream pushback can reduce attack traffic effectively, and a slightly more conservative pushback policy can improve benign-traffic preservation.
