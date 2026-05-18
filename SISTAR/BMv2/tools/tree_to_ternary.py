from __future__ import annotations

from itertools import product
from math import floor
from typing import Dict, Iterable, List, Sequence, Set, Tuple

FEATURE_ORDER = [
    "protocol",
    "init_win_bytes_forward",
    "fwd_header_length",
    "packet_length_mean",
    "flow_packets_persecond",
]

Constraint = Tuple[str, float, str]


def _bin_bounds(thresholds: Sequence[int]) -> List[Tuple[float, float]]:
    t0, t1, t2 = thresholds
    return [
        (float("-inf"), float(t0)),
        (float(t0), float(t1)),
        (float(t1), float(t2)),
        (float(t2), float("inf")),
    ]


def _bins_for_constraint(thresholds: Sequence[int], op: str, threshold: float) -> Set[int]:
    allowed: Set[int] = set()
    for idx, (lower, upper) in enumerate(_bin_bounds(thresholds)):
        if op == "<=":
            if upper <= threshold:
                allowed.add(idx)
        elif op == ">":
            if lower >= threshold:
                allowed.add(idx)
        else:
            raise ValueError(f"Unsupported constraint operator: {op}")
    return allowed


def collect_attack_paths(tree: dict, feature_order: Sequence[str] = FEATURE_ORDER) -> List[List[Constraint]]:
    paths: List[List[Constraint]] = []

    def walk(node: dict, path: List[Constraint]) -> None:
        if "class" in node:
            if int(node["class"]) == 1:
                paths.append(path.copy())
            return

        feature_name = feature_order[int(node["feature"])]
        threshold = float(max(0, floor(float(node["threshold"]))))

        walk(node["left"], path + [(feature_name, threshold, "<=")])
        walk(node["right"], path + [(feature_name, threshold, ">")])

    walk(tree, [])
    return paths


def path_allowed_bins(
    path: Iterable[Constraint],
    thresholds: Dict[str, Sequence[int]],
    feature_order: Sequence[str] = FEATURE_ORDER,
) -> Dict[str, Set[int]]:
    allowed = {feature: {0, 1, 2, 3} for feature in feature_order}

    for feature_name, threshold, op in path:
        feature_thresholds = thresholds[feature_name]
        allowed[feature_name] &= _bins_for_constraint(feature_thresholds, op, threshold)

    return allowed


def bins_to_value(bins: Sequence[int]) -> int:
    value = 0
    for idx, bin_value in enumerate(bins):
        value |= (int(bin_value) & 0x3) << (idx * 2)
    return value


def expand_allowed_bins(
    allowed: Dict[str, Set[int]],
    feature_order: Sequence[str] = FEATURE_ORDER,
) -> Set[int]:
    choices = [sorted(allowed[feature]) for feature in feature_order]
    if any(len(feature_choices) == 0 for feature_choices in choices):
        return set()
    return {bins_to_value(combo) for combo in product(*choices)}


def tree_to_attack_bin_values(
    tree: dict,
    thresholds: Dict[str, Sequence[int]],
    feature_order: Sequence[str] = FEATURE_ORDER,
) -> List[int]:
    values: Set[int] = set()
    for path in collect_attack_paths(tree, feature_order):
        values.update(expand_allowed_bins(path_allowed_bins(path, thresholds, feature_order), feature_order))
    return sorted(values)
