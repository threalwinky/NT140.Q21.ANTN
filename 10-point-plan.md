# NT140 10-point plan for SISTAR

## 1. Executive summary

Your paper choice is strong for this course.

- Domain fit: network security
- Venue fit: ACM CCS 2025
- Reproducibility fit: good, if you reproduce a reduced version
- Risk: full P4/Tofino reproduction is too heavy for a course project

The correct strategy is not "rebuild the whole paper".
The correct strategy is:

1. Understand the paper correctly.
2. Reproduce the core idea in a reduced software prototype.
3. Evaluate it with clean baselines and metrics.
4. Show one extra engineering insight beyond a plain summary.

If you do that well, this topic is absolutely capable of getting full marks.

## 2. What the paper actually contributes

Paper: `SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes`

Main idea:

- Detect DDoS inside the programmable data plane instead of forwarding all analysis to a centralized detector.
- Use a constrained decision-tree training method called `DT-CTS` to reduce the number of thresholds, so the model is easier to deploy on switches.
- Encode model decisions into compact feature classes for efficient matching.
- Deploy models across multiple switches and use an alert/pushback mechanism so upstream switches can mitigate attack traffic earlier.

Problem the paper tries to solve:

- Existing PDP/P4 detection methods either:
  - use too many features and table entries,
  - ignore flow-level behavior,
  - are too expensive in hardware resources,
  - or do not coordinate between multiple switches.

Threat/assumption model inferred from the paper:

- DDoS traffic may be protocol-based or application-layer.
- The system works inside one administrative domain with multiple programmable switches that can cooperate.
- Switches can exchange alert information.
- The paper assumes programmable switch support exists; this is the main part you should simplify in your course project.

Key design components:

- Feature engineering:
  - packet-level + flow-level features
  - paper explicitly discusses low/medium/high hardware-cost features
- Model optimization:
  - `DT-CTS` limits threshold usage per feature
  - goal is similar accuracy with fewer thresholds and lower deployment cost
- Model encoding:
  - turn threshold outcomes into compact bit encodings
  - use ternary matching for efficient classification
- Distributed deployment:
  - lighter models near gateway
  - stronger models near core/spine
- Pushback:
  - once an attack is detected, send alerts upstream and install rules earlier in the path

Important reported results from the paper:

- `DT-CTS` reduces thresholds by about 70%
- the paper claims around 98% F1 with only a small number of features
- hardware resource usage on Tofino is low
- pushback can reduce attack traffic bandwidth utilization significantly

## 3. What requirements.md really means for you

From `requirements.md`, to score high you must satisfy three things:

1. Understand the paper correctly.
2. Implement something real, not only summarize.
3. Evaluate it with baseline + metrics.

That means your project must include all of these:

- correct paper analysis
- a working prototype or simulation
- at least one baseline comparison
- quantitative experiments
- code with commit history
- report + demo

If any of these is weak, your score will drop fast.

## 4. Best scope for this course

## Recommended scope

Do a reduced reproduction with software, not full hardware reproduction.

Your project should implement:

1. Offline DDoS detection model:
   - Baseline A: normal Decision Tree
   - Baseline B: Random Forest or a simple rule-based detector
   - Your main method: a simplified `DT-CTS`

2. Flow feature extraction:
   - extract packet/flow features from pcap or csv flows
   - use a public dataset, preferably the CICIDS2017 Wednesday subset because the paper uses it in core evaluation

3. Software pushback simulation:
   - build a small 3-switch logical topology:
     - gateway -> core -> victim
   - when detector labels a source/flow as attack, install upstream block/drop rules in the simulation

4. Evaluation:
   - compare before vs after pushback
   - compare DT vs DT-CTS
   - report accuracy/F1 and mitigation effect

This is the best cost/benefit path.

## Avoid this scope

Do not make your grade depend on:

- real Tofino hardware
- full P4/Tofino deployment
- reproducing all six datasets
- reproducing every figure in the paper
- reproducing exact hardware resource counters from the paper

Those are high-cost, high-risk, low-return for a course project.

## 5. What you should build

## Minimum architecture that still looks strong

Build these modules:

1. `dataset/`
   - scripts to load or preprocess CICIDS2017
   - optionally one second dataset for generalization

2. `features/`
   - flow aggregation by 5-tuple and time window
   - packet/flow statistics

3. `models/`
   - `dt_baseline.py`
   - `rf_baseline.py`
   - `dt_cts.py`

4. `simulator/`
   - simple topology simulator or Mininet-based pipeline
   - alert generation
   - pushback rule installation

5. `evaluation/`
   - classification metrics
   - threshold-count and model-size metrics
   - attack traffic reaching victim before/after pushback

6. `report-assets/`
   - plots
   - topology figure
   - pipeline figure

## Best implementation choice

If you want the safest route to 10:

- use Python for the entire prototype
- represent the "switch data plane" as a software pipeline
- emulate alert packets and pushback as events/rules

If you want a stronger demo and you have time:

- use Mininet plus simple Open vSwitch/Linux tc/iptables for traffic control
- keep the detector in Python
- still do not depend on real P4 hardware

## 6. What your DT-CTS reproduction should do

You do not need to exactly reproduce the authors' full training pipeline.
You need to reproduce the core idea faithfully:

- train a decision tree
- constrain the number of thresholds per feature during split selection
- show that threshold count decreases
- show that accuracy/F1 stays close enough

Your `DT-CTS` can be presented as:

- a constrained decision tree training algorithm
- or a post-processing pruning algorithm that merges thresholds per feature

The first is closer to the paper.
The second is easier to implement.
If time is short, implement the second but state clearly:

"This project reproduces the core deployment-oriented idea of threshold-constrained trees, not the exact vendor-specific training pipeline."

That is acceptable if your experiments are clean.

## 7. Experiments you must have

These are the experiments that matter most.

## E1. Model quality

Compare:

- DT
- DT-CTS
- RF

Metrics:

- Accuracy
- Precision
- Recall
- F1

Output:

- one table
- one bar chart

## E2. Deployment efficiency proxy

Compare:

- number of unique thresholds per feature
- total thresholds in the model
- tree depth
- total number of decision nodes
- estimated rule count or encoded entries

This experiment is essential because it is the heart of the paper.

## E3. Pushback effectiveness

Topology:

- gateway -> core -> victim

Scenarios:

- no pushback
- pushback enabled

Metrics:

- attack packets reaching victim
- benign packets reaching victim
- victim bandwidth consumption
- mitigation response time

This experiment is what separates your work from "just ML classification".

## E4. Generalization

At minimum do one of these:

- train on CICIDS2017 and test on a held-out split
- 5-fold cross validation
- or evaluate on one extra dataset/sample

You do not need six datasets.
One main dataset plus one robustness check is enough for a student project.

## 8. What to put in the report

Your report should be structured like this:

1. Introduction
   - DDoS problem
   - why data-plane detection matters
   - why this paper was chosen

2. Paper analysis
   - problem
   - assumptions
   - architecture
   - DT-CTS idea
   - distributed pushback idea
   - strengths and limitations

3. Proposed reproduction scope
   - what you reproduced exactly
   - what you simplified
   - why those simplifications are reasonable

4. System design
   - data pipeline
   - flow extraction
   - model training
   - pushback logic
   - topology

5. Implementation
   - environment
   - tools
   - dataset
   - modules

6. Evaluation
   - baselines
   - metrics
   - results
   - discussion

7. Limitations and future work
   - no real Tofino
   - software approximation
   - future work: BMv2/P4, larger topology, real packet replay

8. Conclusion

## 9. What the demo should show

Your demo should be short and concrete.

Demo sequence:

1. Show topology.
2. Start normal traffic.
3. Inject attack traffic.
4. Show detector labels attack.
5. Show pushback rule being installed upstream.
6. Show attack traffic at victim drops.
7. Show benign traffic remains mostly available.
8. Show one chart/table of DT vs DT-CTS.

If your demo shows both "detection" and "mitigation", you are in a strong scoring position.

## 10. How to maximize points by category

## A. Presentation: 3 points

You said you can handle slides, so focus on these messages:

- Why this paper matters
- What is the core idea
- What exactly you reproduced
- What result you achieved
- What limitation remains

Do not spend too much time on literature survey.
Spend time on your system and your measurements.

## B. Content: 3 points

To get full content points, your report must prove:

- you understood the paper
- you did not just translate it
- you made reasonable engineering simplifications
- you analyzed strengths and weaknesses honestly

The biggest content mistake would be pretending a software simulator is the full paper reproduction.
Do not do that.
State the scope precisely.

## C. Demo: 4 points

This is likely the easiest place to separate yourself from weaker groups.
To get full demo points, your demo must show:

- working code
- measurable effect
- attack and mitigation
- baseline comparison

If your demo is only "train a classifier and print accuracy", that is not enough.

## 11. A concrete 2-level plan

## Level 1: enough for a very good grade

- Read and summarize the paper correctly
- Implement DT baseline
- Implement simplified DT-CTS
- Use one public dataset
- Show accuracy/F1 and threshold reduction
- Build pushback simulation
- Show before/after mitigation

## Level 2: enough to push toward full marks

- Add RF baseline
- Add one more dataset or 5-fold cross validation
- Add latency/response-time measurement
- Add encoded-rule-count metric
- Add one small improvement of your own

## 12. Best "small improvement" ideas

You should include one small extension beyond the paper summary.
Pick one of these:

1. Adaptive threshold budget
   - instead of fixed max thresholds per feature, allocate threshold budget according to feature importance

2. Confidence-gated pushback
   - only trigger upstream mitigation when attack confidence is sustained for N windows

3. Benign-preserving pushback
   - compare full-source blocking vs rate-limited pushback and show which preserves more legitimate traffic

4. Time-window sensitivity
   - compare detection quality at different flow aggregation windows

Option 2 is the safest and most demo-friendly.

## 13. Risks that can kill your score

- Only summarizing the paper
- No baseline
- No real experiment
- No quantitative metrics
- No mitigation demo
- Claiming exact reproduction when it is not exact
- Overbuilding P4/BMv2 and failing to finish

## 14. My recommendation for your final project claim

Your project claim should be:

"We reproduce the core ideas of SISTAR in a reduced software prototype: threshold-constrained tree-based DDoS detection with distributed alert-triggered pushback. We evaluate both detection accuracy and mitigation effectiveness under a small multi-switch topology."

That claim is realistic, defensible, and strong.

## 15. What you should do next

Immediate next steps:

1. Freeze scope:
   - software reproduction, not full hardware reproduction
2. Choose dataset:
   - CICIDS2017 Wednesday subset first
3. Implement baselines:
   - DT and RF
4. Implement simplified DT-CTS
5. Build topology simulator with pushback
6. Run the four key experiments
7. Write report as you build, not after

## 16. Recommendation on time allocation

Use your effort roughly like this:

- 20% paper understanding and report skeleton
- 35% model + feature pipeline
- 25% pushback simulation + demo
- 20% experiments, plots, polishing

## 17. Bottom line

If you want 10 points, do not chase the hardest part of the paper.
Chase the most defensible combination of:

- faithful paper understanding
- reduced but real implementation
- strong quantitative evaluation
- clear mitigation demo

For this topic, the highest-value deliverable is:

"DT-CTS style DDoS detector + distributed pushback simulation + baseline comparison + clean report."
