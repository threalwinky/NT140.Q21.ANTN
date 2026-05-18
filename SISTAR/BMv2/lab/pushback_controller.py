from __future__ import annotations

import argparse
import ipaddress
import subprocess
import sys
from pathlib import Path

BMV2_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = BMV2_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from cli_templates import source_block_command

LAB_NETWORKS = tuple(ipaddress.ip_network(net) for net in ("10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"))
THRIFT_PORTS = {"s1": 9090, "s2": 9091, "s3": 9092}


def _is_lab_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return any(ip in network for network in LAB_NETWORKS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install a SISTAR source-block pushback rule in the BMv2 lab")
    parser.add_argument("--source-ip", required=True)
    parser.add_argument("--upstream-switch", choices=tuple(THRIFT_PORTS), default="s2")
    parser.add_argument("--thrift-port", type=int)
    parser.add_argument("--cli", default="simple_switch_CLI")
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not _is_lab_ip(args.source_ip):
        raise SystemExit("source-ip must be in the Mininet lab subnets")

    thrift_port = args.thrift_port or THRIFT_PORTS[args.upstream_switch]
    command = source_block_command(args.source_ip)
    print(f"Switch: {args.upstream_switch}")
    print(f"Thrift port: {thrift_port}")
    print(command)

    if not args.apply:
        print("Dry run only. Add --apply to install the rule.")
        return

    subprocess.run(
        [args.cli, "--thrift-port", str(thrift_port)],
        input=(command + "\n").encode(),
        check=True,
    )
    print("Pushback source-block rule installed")


if __name__ == "__main__":
    main()
