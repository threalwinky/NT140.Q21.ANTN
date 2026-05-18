from __future__ import annotations

import argparse
import ipaddress
import random
import sys
import time
from typing import Iterable

from scapy.all import IP, TCP, UDP, Raw, conf, send

LAB_NETWORKS = tuple(ipaddress.ip_network(net) for net in ("10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"))
MAX_COUNT = {"benign": 500, "attack-lab": 1000}
MAX_PPS = {"benign": 50.0, "attack-lab": 100.0}


def _is_lab_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return any(ip in network for network in LAB_NETWORKS)


def _validate_args(args: argparse.Namespace) -> None:
    if not _is_lab_ip(args.dst):
        raise SystemExit("Destination must be one of the Mininet lab subnets: 10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24")
    if args.count < 1 or args.count > MAX_COUNT[args.mode]:
        raise SystemExit(f"Count for {args.mode} must be between 1 and {MAX_COUNT[args.mode]}")
    if args.pps <= 0 or args.pps > MAX_PPS[args.mode]:
        raise SystemExit(f"PPS for {args.mode} must be between 0 and {MAX_PPS[args.mode]}")
    if args.mode == "attack-lab" and not args.i_understand_this_is_mininet_only:
        raise SystemExit("attack-lab mode requires --i-understand-this-is-mininet-only")


def _protocol_sequence(mode: str, proto: str, count: int) -> Iterable[str]:
    if proto != "mixed":
        for _ in range(count):
            yield proto
        return

    choices = ("tcp", "udp") if mode == "attack-lab" else ("tcp", "tcp", "udp")
    for _ in range(count):
        yield random.choice(choices)


def _packet(mode: str, dst: str, proto: str, index: int):
    sport = 20000 + (index % 20000)
    dport = 1234
    if mode == "benign":
        payload = Raw(("SISTAR benign packet %04d" % index).encode() * 8)
        if proto == "udp":
            return IP(dst=dst) / UDP(sport=sport, dport=dport) / payload
        return IP(dst=dst) / TCP(sport=sport, dport=dport, flags="PA", window=22000) / payload

    payload = Raw(("lab-ddos-sample-%04d" % index).encode())
    if proto == "udp":
        return IP(dst=dst) / UDP(sport=sport, dport=dport) / payload
    return IP(dst=dst) / TCP(sport=sport, dport=dport, flags="S", window=256) / payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate low-rate lab-only traffic for the SISTAR Mininet demo")
    parser.add_argument("--mode", choices=("benign", "attack-lab"), required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--pps", type=float, default=2.0)
    parser.add_argument("--proto", choices=("tcp", "udp", "mixed"), default="mixed")
    parser.add_argument("--iface")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--i-understand-this-is-mininet-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _validate_args(args)
    random.seed(args.seed)
    conf.verb = 0
    interval = 1.0 / args.pps

    print(f"Sending {args.count} {args.mode} packets to {args.dst} at {args.pps} pps")
    for index, proto in enumerate(_protocol_sequence(args.mode, args.proto, args.count), start=1):
        send(_packet(args.mode, args.dst, proto, index), iface=args.iface, verbose=False)
        if index < args.count:
            time.sleep(interval)
    print("Traffic generation finished")


if __name__ == "__main__":
    try:
        main()
    except PermissionError:
        sys.exit("Scapy needs root privileges; run inside Mininet host or with sudo")
