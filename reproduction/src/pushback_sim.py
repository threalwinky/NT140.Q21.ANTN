from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from config import FEATURE_NAMES
from paper_features import sanitize_feature_matrix


NON_FEATURE_COLUMNS = {"label", "raw_label", "traffic_type", "window", "source_id", "bytes"}
POLICY_ORDER = ["no_pushback", "immediate_pushback", "hierarchical_confidence_pushback"]
RESPONSE_LEVELS = ["none", "monitor", "local_rate_limit", "upstream_pushback", "hard_block"]
LEVEL_SEVERITY = {level: idx for idx, level in enumerate(RESPONSE_LEVELS)}
FORWARD_FRACTIONS = {
    "none": 1.0,
    "monitor": 1.0,
    "local_rate_limit": 0.65,
    "upstream_pushback": 0.25,
    "hard_block": 0.0,
}
DEFAULT_SCORE_WEIGHTS = {
    "edge": 2.0,
    "core": 4.0,
    "spike": 2.0,
    "agreement": 3.0,
    "decay": 1.0,
}
DEFAULT_SCORE_THRESHOLDS = {
    "monitor": 3.0,
    "local_rate_limit": 6.0,
    "upstream_pushback": 12.0,
    "hard_block": 24.0,
}


def _feature_columns(frame: pd.DataFrame) -> List[str]:
    numeric_columns = []
    for column in frame.columns:
        if column in NON_FEATURE_COLUMNS:
            continue
        if pd.api.types.is_numeric_dtype(frame[column]):
            numeric_columns.append(column)
    if numeric_columns:
        return numeric_columns
    return [feature for feature in FEATURE_NAMES if feature in frame.columns]


def generate_pushback_trace(flow_pool_df: pd.DataFrame, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: List[dict] = []
    source_count = 24
    attack_sources = set(range(0, 8))
    benign_pool = flow_pool_df[flow_pool_df["label"] == 0].reset_index(drop=True)
    attack_pool = flow_pool_df[flow_pool_df["label"] == 1].reset_index(drop=True)
    feature_columns = _feature_columns(flow_pool_df)

    for window in range(60):
        for source_id in range(source_count):
            is_attack_phase = source_id in attack_sources and 15 <= window <= 44
            burst = source_id in attack_sources and 26 <= window <= 33

            if is_attack_phase:
                sampled = attack_pool.iloc[int(rng.integers(0, len(attack_pool)))]
                kind = str(sampled["traffic_type"])
                label = 1
            else:
                sampled = benign_pool.iloc[int(rng.integers(0, len(benign_pool)))]
                kind = "benign"
                label = 0

            packet_length_mean = float(sampled["packet_length_mean"]) if "packet_length_mean" in sampled else 0.0
            flow_pps = float(sampled["flow_packets_persecond"]) if "flow_packets_persecond" in sampled else 0.0

            if burst and label == 1 and "packet_length_mean" in feature_columns and "flow_packets_persecond" in feature_columns:
                flow_pps *= 1.35
                packet_length_mean *= 0.92

            byte_scale = float(packet_length_mean * flow_pps * rng.uniform(0.75, 1.10))

            feature_values = {feature: sampled[feature] for feature in feature_columns}
            if "packet_length_mean" in feature_values:
                feature_values["packet_length_mean"] = packet_length_mean
            if "flow_packets_persecond" in feature_values:
                feature_values["flow_packets_persecond"] = flow_pps

            row = {
                "window": window,
                "source_id": source_id,
                "traffic_type": kind,
                "label": label,
                "bytes": byte_scale,
            }
            row.update(feature_values)
            rows.append(row)

    return pd.DataFrame(rows)


def _predict(model, trace_df: pd.DataFrame) -> np.ndarray:
    feature_columns = list(getattr(model, "feature_names", [feature for feature in FEATURE_NAMES if feature in trace_df.columns]))
    feature_caps = getattr(model, "feature_caps", None)
    x_trace, _ = sanitize_feature_matrix(trace_df, feature_columns, caps=feature_caps)
    return model.predict(x_trace)


def _hierarchical_level(score: float, core_pred: int) -> str:
    if score >= DEFAULT_SCORE_THRESHOLDS["hard_block"] and core_pred == 1:
        return "hard_block"
    if score >= DEFAULT_SCORE_THRESHOLDS["upstream_pushback"]:
        return "upstream_pushback"
    if score >= DEFAULT_SCORE_THRESHOLDS["local_rate_limit"]:
        return "local_rate_limit"
    if score >= DEFAULT_SCORE_THRESHOLDS["monitor"]:
        return "monitor"
    return "none"


def _spike_signal(row: pd.Series, profile: Dict[str, float]) -> bool:
    pps = float(row.get("flow_packets_persecond", 0.0) or 0.0)
    packet_mean = float(row.get("packet_length_mean", 0.0) or 0.0)
    pps_high = float(profile.get("pps_high", 0.0) or 0.0)
    small_packet = float(profile.get("small_packet_threshold", 0.0) or 0.0)

    if pps_high <= 0:
        return False
    if pps >= pps_high:
        return True
    return bool(small_packet > 0 and packet_mean <= small_packet and pps >= 0.70 * pps_high)


def simulate_pushback(model_bundle: Dict[str, object], trace_df: pd.DataFrame, policy: str) -> Tuple[pd.DataFrame, dict]:
    if policy not in POLICY_ORDER:
        raise ValueError(f"Unknown policy: {policy}")
    if "core" not in model_bundle or "edge" not in model_bundle:
        raise ValueError("model_bundle must contain 'edge' and 'core' detectors")

    edge_model = model_bundle["edge"]
    core_model = model_bundle["core"]
    profile = dict(model_bundle.get("profile", {}))

    edge_predictions = _predict(edge_model, trace_df)
    core_predictions = _predict(core_model, trace_df)

    hard_blocked_sources = set()
    suspicion_scores: Dict[int, float] = {}
    last_window_seen: Dict[int, int] = {}
    active_level: Dict[int, str] = {}
    event_counts = {
        "monitor": 0,
        "local_rate_limit": 0,
        "upstream_pushback": 0,
        "hard_block": 0,
    }
    false_blocks = 0
    total_block_events = 0
    max_suspicion_score = 0.0
    detail_rows = []

    for row_idx, (_, row) in enumerate(trace_df.iterrows()):
        source_id = int(row["source_id"])
        label = int(row["label"])
        window = int(row["window"])
        edge_pred = int(edge_predictions[row_idx])
        core_pred = int(core_predictions[row_idx])

        previous_window = last_window_seen.get(source_id)
        if previous_window is not None and window > previous_window:
            suspicion_scores[source_id] = max(
                0.0,
                suspicion_scores.get(source_id, 0.0) - DEFAULT_SCORE_WEIGHTS["decay"] * (window - previous_window),
            )
        last_window_seen[source_id] = window

        previous_level = active_level.get(source_id, "none")
        suspicion_score = suspicion_scores.get(source_id, 0.0)
        response_level = previous_level

        if source_id in hard_blocked_sources:
            response_level = "hard_block"
        elif policy == "no_pushback":
            response_level = "none"
        elif policy == "immediate_pushback":
            if core_pred == 1:
                response_level = "hard_block"
                if source_id not in hard_blocked_sources:
                    hard_blocked_sources.add(source_id)
                    total_block_events += 1
                    event_counts["hard_block"] += 1
                    if label == 0:
                        false_blocks += 1
            else:
                response_level = "none"
        else:
            evidence = 0.0
            if edge_pred == 1:
                evidence += DEFAULT_SCORE_WEIGHTS["edge"]
            if core_pred == 1:
                evidence += DEFAULT_SCORE_WEIGHTS["core"]
            if edge_pred == 1 and core_pred == 1:
                evidence += DEFAULT_SCORE_WEIGHTS["agreement"]
            if _spike_signal(row, profile):
                evidence += DEFAULT_SCORE_WEIGHTS["spike"]

            suspicion_score = max(0.0, suspicion_score + evidence)
            suspicion_scores[source_id] = suspicion_score
            max_suspicion_score = max(max_suspicion_score, suspicion_score)
            response_level = _hierarchical_level(suspicion_score, core_pred)

            if LEVEL_SEVERITY[response_level] > LEVEL_SEVERITY[previous_level] and response_level in event_counts:
                event_counts[response_level] += 1

            if response_level == "hard_block" and source_id not in hard_blocked_sources:
                hard_blocked_sources.add(source_id)
                total_block_events += 1
                if label == 0:
                    false_blocks += 1

        if policy != "hierarchical_confidence_pushback":
            suspicion_score = suspicion_scores.get(source_id, suspicion_score)

        active_level[source_id] = response_level
        forward_fraction = FORWARD_FRACTIONS[response_level]

        detail_rows.append(
            {
                "window": window,
                "source_id": source_id,
                "label": label,
                "edge_prediction": edge_pred,
                "core_prediction": core_pred,
                "policy": policy,
                "response_level": response_level,
                "forward_fraction": forward_fraction,
                "suspicion_score": suspicion_score,
                "attack_bytes_reaching_victim": float(row["bytes"]) * forward_fraction if label == 1 else 0.0,
                "benign_bytes_reaching_victim": float(row["bytes"]) * forward_fraction if label == 0 else 0.0,
                "attack_flow_reaches_victim": int(label == 1 and forward_fraction > 0),
                "benign_flow_reaches_victim": int(label == 0 and forward_fraction > 0),
                "blocked_sources_count": len(hard_blocked_sources),
            }
        )

    detail_df = pd.DataFrame(detail_rows)
    summary = {
        "policy": policy,
        "attack_bytes_reaching_victim": detail_df["attack_bytes_reaching_victim"].sum(),
        "benign_bytes_reaching_victim": detail_df["benign_bytes_reaching_victim"].sum(),
        "attack_flows_reaching_victim": int(detail_df["attack_flow_reaches_victim"].sum()),
        "benign_flows_reaching_victim": int(detail_df["benign_flow_reaches_victim"].sum()),
        "false_block_events": int(false_blocks),
        "total_block_events": int(total_block_events),
        "monitor_events": int(event_counts["monitor"]),
        "local_rate_limit_events": int(event_counts["local_rate_limit"]),
        "upstream_pushback_events": int(event_counts["upstream_pushback"]),
        "hard_block_events": int(event_counts["hard_block"]),
        "max_suspicion_score": float(max_suspicion_score),
        "mean_suspicion_score": float(detail_df["suspicion_score"].mean()) if not detail_df.empty else 0.0,
    }
    return detail_df, summary
