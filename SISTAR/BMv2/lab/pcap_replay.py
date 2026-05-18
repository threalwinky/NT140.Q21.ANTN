from __future__ import annotations

import argparse
import ipaddress
import sys
import time
from pathlib import Path

from scapy.all import IP, TCP, UDP, PcapReader, conf, send

LAB_NETWORKS = tuple(ipaddress.ip_network(net) for net in ("10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"))
MAX_COUNT = 1000
MAX_PPS = 100.0


def _is_lab_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    return any(ip in network for network in LAB_NETWORKS)


def _prepare_packet(packet, dst: str):
    if IP not in packet:
        return None
    ip_packet = packet[IP].copy()
    ip_packet.dst = dst
    if hasattr(ip_packet, "len"):
        del ip_packet.len
    if hasattr(ip_packet, "chksum"):
        del ip_packet.chksum
    if TCP in ip_packet and hasattr(ip_packet[TCP], "chksum"):
        del ip_packet[TCP].chksum
    if UDP in ip_packet and hasattr(ip_packet[UDP], "chksum"):
        del ip_packet[UDP].chksum
    return ip_packet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay a user-provided PCAP into the SISTAR Mininet lab with rate limits")
    parser.add_argument("--pcap", type=Path, required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--pps", type=float, default=20.0)
    parser.add_argument("--iface")
    parser.add_argument("--i-understand-this-is-mininet-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.i_understand_this_is_mininet_only:
        raise SystemExit("PCAP replay requires --i-understand-this-is-mininet-only")
    if not args.pcap.exists() or not args.pcap.is_file():
        raise SystemExit(f"PCAP file not found: {args.pcap}")
    if not _is_lab_ip(args.dst):
        raise SystemExit("Destination must be one of the Mininet lab subnets")
    if args.count < 1 or args.count > MAX_COUNT:
        raise SystemExit(f"Count must be between 1 and {MAX_COUNT}")
    if args.pps <= 0 or args.pps > MAX_PPS:
        raise SystemExit(f"PPS must be between 0 and {MAX_PPS}")

    conf.verb = 0
    sent = 0
    interval = 1.0 / args.pps
    with PcapReader(str(args.pcap)) as packets:
        for packet in packets:
            prepared = _prepare_packet(packet, args.dst)
            if prepared is None:
                continue
            send(prepared, iface=args.iface, verbose=False)
            sent += 1
            if sent >= args.count:
                break
            time.sleep(interval)

    print(f"Replayed {sent} IP packets from {args.pcap} to {args.dst}")


if __name__ == "__main__":
    try:
        main()
    except PermissionError:
        sys.exit("Scapy needs root privileges; run inside Mininet host or with sudo")
