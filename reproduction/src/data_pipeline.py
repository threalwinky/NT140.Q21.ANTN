from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from pandas.errors import ParserError

from config import FEATURE_NAMES, KAGGLE_DATASET_SLUG, KAGGLE_WEDNESDAY_PARQUET, PARQUET_TO_CANONICAL

try:
    import kagglehub
except ImportError:  # pragma: no cover - runtime fallback when kagglehub is unavailable
    kagglehub = None


def synthesize_flows(n_benign: int = 2400, n_attack: int = 2400, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    benign_protocol = rng.choice([6, 17], size=n_benign, p=[0.8, 0.2])
    benign_win = np.clip(rng.normal(22000, 9000, n_benign), 1024, 65535)
    benign_hdr = np.clip(rng.normal(420, 120, n_benign), 60, 1600)
    benign_pkt_mean = np.clip(rng.normal(820, 220, n_benign), 64, 1500)
    benign_pps = np.clip(rng.normal(180, 85, n_benign), 5, 700)

    attack_kind = rng.choice(["syn", "udp", "app"], size=n_attack, p=[0.45, 0.25, 0.30])
    attack_protocol = np.empty(n_attack)
    attack_win = np.empty(n_attack)
    attack_hdr = np.empty(n_attack)
    attack_pkt_mean = np.empty(n_attack)
    attack_pps = np.empty(n_attack)

    for i, kind in enumerate(attack_kind):
        if kind == "syn":
            attack_protocol[i] = 6
            attack_win[i] = np.clip(rng.normal(256, 128, 1)[0], 0, 4096)
            attack_hdr[i] = np.clip(rng.normal(72, 18, 1)[0], 40, 180)
            attack_pkt_mean[i] = np.clip(rng.normal(88, 25, 1)[0], 40, 250)
            attack_pps[i] = np.clip(rng.normal(1500, 320, 1)[0], 250, 4000)
        elif kind == "udp":
            attack_protocol[i] = 17
            attack_win[i] = np.clip(rng.normal(2048, 1024, 1)[0], 0, 8192)
            attack_hdr[i] = np.clip(rng.normal(110, 35, 1)[0], 40, 400)
            attack_pkt_mean[i] = np.clip(rng.normal(180, 50, 1)[0], 60, 400)
            attack_pps[i] = np.clip(rng.normal(1250, 280, 1)[0], 250, 3500)
        else:
            attack_protocol[i] = 6
            attack_win[i] = np.clip(rng.normal(512, 256, 1)[0], 0, 4096)
            attack_hdr[i] = np.clip(rng.normal(150, 40, 1)[0], 60, 500)
            attack_pkt_mean[i] = np.clip(rng.normal(320, 80, 1)[0], 80, 700)
            attack_pps[i] = np.clip(rng.normal(900, 200, 1)[0], 150, 2500)

    benign = pd.DataFrame(
        {
            "protocol": benign_protocol.astype(int),
            "init_win_bytes_forward": benign_win.astype(float),
            "fwd_header_length": benign_hdr.astype(float),
            "packet_length_mean": benign_pkt_mean.astype(float),
            "flow_packets_persecond": benign_pps.astype(float),
            "label": 0,
            "traffic_type": "benign",
        }
    )

    attack = pd.DataFrame(
        {
            "protocol": attack_protocol.astype(int),
            "init_win_bytes_forward": attack_win.astype(float),
            "fwd_header_length": attack_hdr.astype(float),
            "packet_length_mean": attack_pkt_mean.astype(float),
            "flow_packets_persecond": attack_pps.astype(float),
            "label": 1,
            "traffic_type": attack_kind,
        }
    )

    df = pd.concat([benign, attack], ignore_index=True)
    return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def resolve_kaggle_wednesday_parquet() -> Path:
    if kagglehub is None:
        raise ImportError("kagglehub is not installed")

    dataset_root = Path(kagglehub.dataset_download(KAGGLE_DATASET_SLUG))
    parquet_path = dataset_root / KAGGLE_WEDNESDAY_PARQUET
    if not parquet_path.exists():
        raise FileNotFoundError(f"Expected Wednesday parquet not found at {parquet_path}")
    return parquet_path


def load_kaggle_wednesday_subset(per_class: int = 2500, seed: int = 42) -> pd.DataFrame:
    parquet_path = resolve_kaggle_wednesday_parquet()
    usecols = list(PARQUET_TO_CANONICAL.keys())
    df = pd.read_parquet(parquet_path, columns=usecols)
    df = df.rename(columns=PARQUET_TO_CANONICAL)

    for feature_name in FEATURE_NAMES:
        df[feature_name] = pd.to_numeric(df[feature_name], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan).dropna().copy()
    for feature_name in FEATURE_NAMES:
        df[feature_name] = df[feature_name].clip(lower=0)

    df["raw_label"] = df["raw_label"].astype(str)
    df["label"] = (df["raw_label"].str.casefold() != "benign").astype(int)
    df["traffic_type"] = df["raw_label"].where(df["label"] == 1, "benign")

    benign = df[df["label"] == 0].sample(n=min(per_class, (df["label"] == 0).sum()), random_state=seed)
    attack = df[df["label"] == 1].sample(n=min(per_class, (df["label"] == 1).sum()), random_state=seed)

    subset = pd.concat([benign, attack], ignore_index=True)
    return subset.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def build_dataset(seed: int = 42) -> Tuple[pd.DataFrame, str]:
    try:
        df = load_kaggle_wednesday_subset(seed=seed)
        return (
            df,
            f"Raw Kaggle parquet {KAGGLE_DATASET_SLUG}/{KAGGLE_WEDNESDAY_PARQUET}",
        )
    except (ImportError, FileNotFoundError, OSError, ParserError, ValueError, KeyError):
        pass

    return synthesize_flows(seed=seed), "Synthetic DDoS-like flow dataset"
