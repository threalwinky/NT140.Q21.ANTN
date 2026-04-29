# Presentation Outline

This is a short slide sequence that should fit a typical course presentation.

## Slide 1. Title

- Paper title
- Group members
- One-line project claim

## Slide 2. Problem

- DDoS is hard to detect quickly
- centralized detection adds delay
- switch hardware has limited resources

## Slide 3. Paper idea

- in-switch detection
- `DT-CTS`
- feature encoding
- distributed pushback

## Slide 4. Why this paper matters

- recent and strong venue
- not just theory
- combines detection and mitigation

## Slide 5. What we reproduced

- reduced software reproduction
- `DT`, `RF`, `DT-CTS`
- pushback simulation
- one small improvement: `gated_pushback`

## Slide 6. Dataset and features

- Kaggle CICIDS2017 Wednesday
- binary benign/attack setting
- 5 selected features

## Slide 7. Classification results

- show `classification_f1.png`
- explain `DT`, `RF`, `DT-CTS`

## Slide 8. Threshold efficiency

- show `threshold_usage.png`
- explain why fewer thresholds matter for deployment

## Slide 9. Pushback results

- show `pushback_attack_bytes.png`
- compare `no_pushback`, `immediate_pushback`, `gated_pushback`

## Slide 10. Improvement

- define `gated_pushback`
- explain why it reduces false blocking

## Slide 11. Limitations

- no real Tofino
- no full hardware resource reproduction
- reduced topology

## Slide 12. Conclusion

- reproduced the core ideas of SISTAR in reduced form
- demonstrated detection vs deployment trade-off
- demonstrated mitigation gain with upstream pushback
