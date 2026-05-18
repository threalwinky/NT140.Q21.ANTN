from __future__ import annotations

from math import floor
from typing import Dict, Iterable, List, Sequence

FEATURE_ORDER = [
    "protocol",
    "init_win_bytes_forward",
    "fwd_header_length",
    "packet_length_mean",
    "flow_packets_persecond",
]

REGISTER16_FEATURES = ["protocol", "init_win_bytes_forward"]
REGISTER32_FEATURES = ["fwd_header_length", "packet_length_mean", "flow_packets_persecond"]

HOSTS = {
    "h1": {"ip": "10.0.1.1", "mac": "08:00:00:00:01:11"},
    "h2": {"ip": "10.0.2.2", "mac": "08:00:00:00:02:22"},
    "h3": {"ip": "10.0.3.3", "mac": "08:00:00:00:03:33"},
}

LAB3_ROUTES = {
    "s1": {"h1": 1, "h2": 2, "h3": 2},
    "s2": {"h1": 2, "h2": 1, "h3": 2},
    "s3": {"h1": 1, "h2": 2, "h3": 3},
}


def _as_int(value: float | int) -> int:
    return max(0, floor(float(value)))


def threshold_register_commands(thresholds: Dict[str, Sequence[int]]) -> List[str]:
    lines: List[str] = []
    register_index = 0
    for feature in REGISTER16_FEATURES:
        for value in thresholds[feature]:
            lines.append(f"register_write MyIngress.threshold_register16 {register_index} {_as_int(value)}")
            register_index += 1

    register_index = 0
    for feature in REGISTER32_FEATURES:
        for value in thresholds[feature]:
            lines.append(f"register_write MyIngress.threshold_register32 {register_index} {_as_int(value)}")
            register_index += 1
    return lines


def ddos_ternary_commands(bin_values: Iterable[int]) -> List[str]:
    return [
        f"table_add MyIngress.DDoS_ternary MyIngress.drop 0x{value:03x}&&&0x3ff =>"
        for value in sorted(set(bin_values))
    ]


def ipv4_lpm_commands(switch_name: str) -> List[str]:
    if switch_name not in LAB3_ROUTES:
        raise ValueError(f"Unknown lab3 switch: {switch_name}")

    lines: List[str] = []
    for host_name, port in LAB3_ROUTES[switch_name].items():
        host = HOSTS[host_name]
        lines.append(
            f"table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward "
            f"{host['ip']}/32 => {host['mac']} {port}"
        )
    return lines


def source_block_command(source_ip: str) -> str:
    return f"table_add MyIngress.source_block MyIngress.drop {source_ip} =>"


def switch_commands(
    switch_name: str,
    thresholds: Dict[str, Sequence[int]],
    attack_bin_values: Iterable[int],
) -> str:
    sections = [
        threshold_register_commands(thresholds),
        ddos_ternary_commands(attack_bin_values),
        ipv4_lpm_commands(switch_name),
    ]
    lines = [line for section in sections for line in section]
    return "\n".join(lines) + "\n"
