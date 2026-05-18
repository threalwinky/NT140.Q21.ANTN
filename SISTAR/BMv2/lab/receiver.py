from __future__ import annotations

import argparse
import threading
from collections import Counter
from typing import Tuple

from scapy.all import IP, conf, sniff

PROTO_NAMES = {1: "ICMP", 6: "TCP", 17: "UDP"}


def _format_key(key: Tuple[str, int]) -> str:
    src, proto = key
    return f"{src}/{PROTO_NAMES.get(proto, str(proto))}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Count IP packets reaching the SISTAR victim host")
    parser.add_argument("--iface")
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--interval", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    conf.verb = 0
    counts: Counter[Tuple[str, int]] = Counter()
    lock = threading.Lock()
    stop_event = threading.Event()

    def print_summary(final: bool = False) -> None:
        with lock:
            snapshot = counts.copy()
        label = "final" if final else "interval"
        total = sum(snapshot.values())
        print(f"[{label}] total packets: {total}")
        for key, value in snapshot.most_common():
            print(f"  {_format_key(key)}: {value}")

    def periodic_printer() -> None:
        while not stop_event.wait(args.interval):
            print_summary()

    def handle_packet(packet) -> None:
        if IP not in packet:
            return
        ip = packet[IP]
        with lock:
            counts[(ip.src, int(ip.proto))] += 1

    printer = threading.Thread(target=periodic_printer, daemon=True)
    printer.start()
    try:
        sniff(iface=args.iface, filter="ip", prn=handle_packet, store=False, timeout=args.duration)
    finally:
        stop_event.set()
        printer.join(timeout=1)
        print_summary(final=True)


if __name__ == "__main__":
    main()
