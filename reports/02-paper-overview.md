# Paper Overview

Paper:

- Title: `SISTAR: An Efficient DDoS Detection and Mitigation Framework Utilizing Programmable Data Planes`
- Venue: `ACM CCS 2025`

Problem addressed by the paper:

- DDoS detection must be accurate enough to detect complex attacks.
- However, programmable switches have strict hardware constraints.
- Existing approaches often either:
  - use too many features,
  - use too many thresholds and table entries,
  - fail to consider flow behavior,
  - or do not coordinate across multiple switches.

Core ideas in the paper:

1. `In-switch detection`
   - perform detection directly in the data plane instead of sending everything to a central server or controller

2. `DT-CTS`
   - constrain the number of thresholds used by each feature during decision-tree construction
   - goal: keep the model lighter and easier to deploy

3. `Feature encoding`
   - transform feature decisions into compact encoded values that can be matched efficiently

4. `Distributed pushback`
   - if one switch detects an attack, it alerts upstream switches
   - upstream switches can then mitigate the attack earlier

Why the paper is suitable for this course:

- it is clearly in network security
- it is recent and published in a top venue
- it contains both a systems idea and an implementation idea
- it can be reproduced partially without full hardware access

Paper strengths:

- addresses both detection and mitigation
- considers deployment constraints, not only ML accuracy
- proposes a concrete deployment-oriented algorithmic change, namely `DT-CTS`
- evaluates both model quality and deployment/resource aspects

Paper limitations:

- full reproduction is difficult without P4/BMv2 or Tofino environment
- hardware-resource claims cannot be verified exactly without the original switch stack
- real-world deployment assumptions are stronger than a typical student environment can satisfy

For a simpler explanation of the paper, see:

- `../paper-summary.md`
