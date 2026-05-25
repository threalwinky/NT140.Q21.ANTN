from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from config import FEATURE_NAMES
from paper_features import sanitize_feature_matrix


NON_FEATURE_COLUMNS = {"label", "raw_label", "traffic_type", "window", "source_id", "bytes"}


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


def simulate_pushback(model, trace_df: pd.DataFrame, policy: str) -> Tuple[pd.DataFrame, dict]:
    feature_columns = list(getattr(model, "feature_names", [feature for feature in FEATURE_NAMES if feature in trace_df.columns]))
    feature_caps = getattr(model, "feature_caps", None)
    blocked_sources = set()
    consecutive_malicious: Dict[int, int] = {}
    false_blocks = 0
    total_block_events = 0
    detail_rows = []

    X_trace, _ = sanitize_feature_matrix(trace_df, feature_columns, caps=feature_caps)
    predictions = model.predict(X_trace)

    for row_idx, (_, row) in enumerate(trace_df.iterrows()):
        source_id = int(row["source_id"])
        label = int(row["label"])
        pred = int(predictions[row_idx])
        forwarded = source_id not in blocked_sources

        if policy == "no_pushback":
            pass
        elif policy == "immediate_pushback":
            if pred == 1 and source_id not in blocked_sources:
                blocked_sources.add(source_id)
                total_block_events += 1
                if label == 0:
                    false_blocks += 1
        elif policy == "gated_pushback":
            if pred == 1:
                consecutive_malicious[source_id] = consecutive_malicious.get(source_id, 0) + 1
            else:
                consecutive_malicious[source_id] = 0
            if consecutive_malicious[source_id] >= 2 and source_id not in blocked_sources:
                blocked_sources.add(source_id)
                total_block_events += 1
                if label == 0:
                    false_blocks += 1
        else:
            raise ValueError(f"Unknown policy: {policy}")

        detail_rows.append(
            {
                "window": int(row["window"]),
                "source_id": source_id,
                "label": label,
                "prediction": pred,
                "policy": policy,
                "forwarded": int(forwarded),
                "attack_bytes_reaching_victim": float(row["bytes"]) if forwarded and label == 1 else 0.0,
                "benign_bytes_reaching_victim": float(row["bytes"]) if forwarded and label == 0 else 0.0,
                "blocked_sources_count": len(blocked_sources),
            }
        )

    detail_df = pd.DataFrame(detail_rows)
    summary = {
        "policy": policy,
        "attack_bytes_reaching_victim": detail_df["attack_bytes_reaching_victim"].sum(),
        "benign_bytes_reaching_victim": detail_df["benign_bytes_reaching_victim"].sum(),
        "attack_flows_reaching_victim": int(((detail_df["label"] == 1) & (detail_df["forwarded"] == 1)).sum()),
        "benign_flows_reaching_victim": int(((detail_df["label"] == 0) & (detail_df["forwarded"] == 1)).sum()),
        "false_block_events": int(false_blocks),
        "total_block_events": int(total_block_events),
    }
    return detail_df, summary
