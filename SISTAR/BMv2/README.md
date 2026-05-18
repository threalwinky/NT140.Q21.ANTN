# SISTAR BMv2 Lab

This folder contains the BMv2/P4 implementation used to simulate SISTAR-style in-switch DDoS detection and mitigation in a local Mininet lab.

## Recommended workflow

Use the new Vietnamese guide:

- [`HOW_TO_RUN_MININET_VI.md`](HOW_TO_RUN_MININET_VI.md)

Quick commands from the project root:

```bash
python3 -m pip install -r SISTAR/BMv2/requirements-lab.txt

python3 SISTAR/BMv2/tools/export_dtcts_rules.py \
  --dataset synthetic \
  --output-dir SISTAR/BMv2/generated \
  --topology lab3

sudo python3 SISTAR/BMv2/lab/mininet_sistar.py \
  --p4 SISTAR/BMv2/DT.p4 \
  --commands-dir SISTAR/BMv2/generated
```

Inside the Mininet CLI:

```bash
h3 python3 SISTAR/BMv2/lab/receiver.py --duration 60
h1 python3 SISTAR/BMv2/lab/traffic_generator.py --mode benign --dst 10.0.3.3 --count 20 --pps 2
h2 python3 SISTAR/BMv2/lab/traffic_generator.py --mode attack-lab --dst 10.0.3.3 --count 200 --pps 20 --i-understand-this-is-mininet-only
```

Apply pushback from another terminal:

```bash
python3 SISTAR/BMv2/lab/pushback_controller.py \
  --source-ip 10.0.2.2 \
  --upstream-switch s2 \
  --apply
```

## Main files

| Path | Purpose |
|---|---|
| `DT.p4` | BMv2 P4 pipeline with feature extraction, DT-CTS ternary detection, source-block pushback, and IPv4 forwarding |
| `tools/export_dtcts_rules.py` | Trains DT-CTS and exports BMv2 CLI rules |
| `tools/tree_to_ternary.py` | Converts DT-CTS attack leaves to 10-bit feature-bin values |
| `tools/cli_templates.py` | Builds `simple_switch_CLI` commands |
| `lab/mininet_sistar.py` | Starts the 3-switch Mininet/BMv2 topology |
| `lab/traffic_generator.py` | Generates low-rate lab-only benign and attack-like traffic |
| `lab/receiver.py` | Counts packets that reach the victim host |
| `lab/pushback_controller.py` | Installs upstream `source_block` mitigation rules |
| `lab/pcap_replay.py` | Replays user-provided PCAPs into lab destinations with rate limits |

## Legacy scripts

The old `entry*.sh` scripts are kept as manual BMv2 CLI examples. Prefer the generated `SISTAR/BMv2/generated/*_commands.cli` files for the Mininet lab because they are derived from the current DT-CTS model and match the current `DT.p4` feature layout.

## Safety

The lab scripts are intended for local Mininet experiments only. Do not send attack-like traffic or replay PCAPs toward real networks.
