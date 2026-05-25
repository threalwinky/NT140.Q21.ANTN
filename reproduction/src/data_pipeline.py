from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from pandas.errors import ParserError

from config import FEATURE_NAMES, PAPER_DOS_LABELS, PAPER_FEATURE_CANDIDATES


CICIDS2017_ZIP = Path(__file__).resolve().parent.parent / "datasets" / "CICIDS2017 .zip"
CICIDS2017_COMBINE_CSV = Path(__file__).resolve().parent.parent / "datasets" / "combine.csv"
CICIDS2017_EXTRACT_DIR = Path(__file__).resolve().parent.parent / "datasets" / "_extracted_cicids2017"
CICIDS2017_EXTRACTED_CSV = CICIDS2017_EXTRACT_DIR / "combine.csv"


CICIDS2017_COMBINE_TO_CANONICAL = {
    "Destination Port": "destination_port",
    "Flow Duration": "flow_duration",
    "Total Fwd Packets": "total_fwd_packets",
    "Total Backward Packets": "total_backward_packets",
    "Total Length of Fwd Packets": "total_length_fwd_packets",
    "Total Length of Bwd Packets": "total_length_bwd_packets",
    "Fwd Packet Length Max": "fwd_packet_length_max",
    "Fwd Packet Length Min": "fwd_packet_length_min",
    "Fwd Packet Length Mean": "fwd_packet_length_mean",
    "Fwd Packet Length Std": "fwd_packet_length_std",
    "Bwd Packet Length Max": "bwd_packet_length_max",
    "Bwd Packet Length Min": "bwd_packet_length_min",
    "Bwd Packet Length Mean": "bwd_packet_length_mean",
    "Bwd Packet Length Std": "bwd_packet_length_std",
    "Flow Bytes/s": "flow_bytes_persecond",
    "Flow Packets/s": "flow_packets_persecond",
    "Flow IAT Mean": "flow_iat_mean",
    "Flow IAT Std": "flow_iat_std",
    "Flow IAT Max": "flow_iat_max",
    "Flow IAT Min": "flow_iat_min",
    "Fwd IAT Mean": "fwd_iat_mean",
    "Fwd IAT Std": "fwd_iat_std",
    "Fwd IAT Max": "fwd_iat_max",
    "Fwd IAT Min": "fwd_iat_min",
    "Bwd IAT Std": "bwd_iat_std",
    "Bwd IAT Max": "bwd_iat_max",
    "Packet Length Mean": "packet_length_mean",
    "Packet Length Std": "packet_length_std",
    "Average Packet Size": "average_packet_size",
    "Protocol": "protocol",
    "Init_Win_bytes_forward": "init_win_bytes_forward",
    "Init_Win_bytes_backward": "init_win_bytes_backward",
    "Fwd Header Length": "fwd_header_length",
    "Fwd Packets/s": "fwd_packets_persecond",
    "Bwd Packets/s": "bwd_packets_persecond",
    "Max Packet Length": "packet_length_max",
    "Min Packet Length": "packet_length_min",
    "Subflow Fwd Packets": "subflow_fwd_packets",
    "Subflow Fwd Bytes": "subflow_fwd_bytes",
    "Subflow Bwd Packets": "subflow_bwd_packets",
    "Subflow Bwd Bytes": "subflow_bwd_bytes",
    "min_seg_size_forward": "min_seg_size_forward",
    "Active Mean": "active_mean",
    "Active Std": "active_std",
    "Idle Mean": "idle_mean",
    "Idle Std": "idle_std",
    "Idle Max": "idle_max",
    "Idle Min": "idle_min",
    "Label": "raw_label",
}


UDP_PORTS = {53, 67, 68, 69, 123, 161, 162, 500, 514, 520, 1900, 4500, 5353}


def _derive_protocol(frame: pd.DataFrame) -> pd.Series:
    if "protocol" in frame.columns:
        return pd.to_numeric(frame["protocol"], errors="coerce")

    destination_port = pd.to_numeric(frame.get("destination_port"), errors="coerce")
    tcp_flag_columns = [
        "SYN Flag Count",
        "ACK Flag Count",
        "FIN Flag Count",
        "RST Flag Count",
        "PSH Flag Count",
        "URG Flag Count",
    ]
    tcp_flags = None
    for column in tcp_flag_columns:
        if column in frame.columns:
            values = pd.to_numeric(frame[column], errors="coerce").fillna(0)
            tcp_flags = values if tcp_flags is None else tcp_flags + values

    protocol = pd.Series(6, index=frame.index, dtype="float64")
    if destination_port is not None:
        protocol = protocol.where(~destination_port.isin(list(UDP_PORTS)), 17)

    if tcp_flags is not None:
        protocol = protocol.where(tcp_flags > 0, 17)

    return protocol.fillna(6).astype(int)


def synthesize_flows(n_benign: int = 2400, n_attack: int = 2400, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    benign_protocol = rng.choice([6, 17], size=n_benign, p=[0.8, 0.2])
    benign_win = np.clip(rng.normal(22000, 9000, n_benign), 1024, 65535)
    benign_hdr = np.clip(rng.normal(420, 120, n_benign), 60, 1600)
    benign_pkt_mean = np.clip(rng.normal(820, 220, n_benign), 64, 1500)
    benign_pps = np.clip(rng.normal(180, 85, n_benign), 5, 700)
    benign_pkt_max = np.clip(benign_pkt_mean + rng.normal(300, 100, n_benign), benign_pkt_mean, 1500)
    benign_pkt_min = np.clip(benign_pkt_mean - rng.normal(300, 100, n_benign), 0, benign_pkt_mean)

    attack_kind = rng.choice(["syn", "udp", "app"], size=n_attack, p=[0.45, 0.25, 0.30])
    attack_protocol = np.empty(n_attack)
    attack_win = np.empty(n_attack)
    attack_hdr = np.empty(n_attack)
    attack_pkt_mean = np.empty(n_attack)
    attack_pps = np.empty(n_attack)
    attack_pkt_max = np.empty(n_attack)
    attack_pkt_min = np.empty(n_attack)

    for i, kind in enumerate(attack_kind):
        if kind == "syn":
            attack_protocol[i] = 6
            attack_win[i] = np.clip(rng.normal(256, 128, 1)[0], 0, 4096)
            attack_hdr[i] = np.clip(rng.normal(72, 18, 1)[0], 40, 180)
            attack_pkt_mean[i] = np.clip(rng.normal(88, 25, 1)[0], 40, 250)
            attack_pps[i] = np.clip(rng.normal(1500, 320, 1)[0], 250, 4000)
            attack_pkt_max[i] = np.clip(rng.normal(120, 30), 40, 300)
            attack_pkt_min[i] = np.clip(rng.normal(60, 15), 0, 120)
        elif kind == "udp":
            attack_protocol[i] = 17
            attack_win[i] = np.clip(rng.normal(2048, 1024, 1)[0], 0, 8192)
            attack_hdr[i] = np.clip(rng.normal(110, 35, 1)[0], 40, 400)
            attack_pkt_mean[i] = np.clip(rng.normal(180, 50, 1)[0], 60, 400)
            attack_pps[i] = np.clip(rng.normal(1250, 280, 1)[0], 250, 3500)
            attack_pkt_max[i] = np.clip(rng.normal(250, 60), 60, 500)
            attack_pkt_min[i] = np.clip(rng.normal(120, 30), 0, 250)
        else:
            attack_protocol[i] = 6
            attack_win[i] = np.clip(rng.normal(512, 256, 1)[0], 0, 4096)
            attack_hdr[i] = np.clip(rng.normal(150, 40, 1)[0], 60, 500)
            attack_pkt_mean[i] = np.clip(rng.normal(320, 80, 1)[0], 80, 700)
            attack_pps[i] = np.clip(rng.normal(900, 200, 1)[0], 150, 2500)
            attack_pkt_max[i] = np.clip(rng.normal(400, 100), 80, 900)
            attack_pkt_min[i] = np.clip(rng.normal(200, 50), 0, 400)

    benign = pd.DataFrame(
        {
            "protocol": benign_protocol.astype(int),
            "init_win_bytes_forward": benign_win.astype(float),
            "fwd_header_length": benign_hdr.astype(float),
            "packet_length_mean": benign_pkt_mean.astype(float),
            "flow_packets_persecond": benign_pps.astype(float),
            "packet_length_max": benign_pkt_max.astype(float),
            "packet_length_min": benign_pkt_min.astype(float),
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
            "packet_length_max": attack_pkt_max.astype(float),
            "packet_length_min": attack_pkt_min.astype(float),
            "label": 1,
            "traffic_type": attack_kind,
        }
    )

    df = pd.concat([benign, attack], ignore_index=True)
    return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def extract_cicids2017_zip(zip_path: Path = CICIDS2017_ZIP, extract_dir: Path = CICIDS2017_EXTRACT_DIR) -> Path:
    if not zip_path.exists():
        raise FileNotFoundError(f"CICIDS2017 zip not found: {zip_path}")

    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not members:
            raise ValueError(f"No CSV file found inside {zip_path}")
        for member in members:
            archive.extract(member, path=extract_dir)

    extracted_csv = extract_dir / members[0]
    if not extracted_csv.exists():
        raise FileNotFoundError(f"Expected extracted CSV not found at {extracted_csv}")
    return extracted_csv


def load_cicids2017_from_csv(csv_path: Path, paper_subset: bool = True) -> pd.DataFrame:
    header = pd.read_csv(csv_path, nrows=0)
    header.columns = [c.strip() for c in header.columns]
    canonical_needed = set(PAPER_FEATURE_CANDIDATES) | set(FEATURE_NAMES) | {"raw_label"}
    present_cols = [
        c
        for c, canonical in CICIDS2017_COMBINE_TO_CANONICAL.items()
        if c in header.columns and canonical in canonical_needed
    ]
    if "Label" not in present_cols:
        raise ValueError(f"Column 'Label' not found in {csv_path}")

    wanted = set(present_cols)
    chunks = pd.read_csv(
        csv_path,
        usecols=lambda c: c.strip() in wanted,
        low_memory=False,
        chunksize=200000,
    )

    full_parts = []
    for chunk in chunks:
        chunk.columns = [c.strip() for c in chunk.columns]
        present_mapping = {k: v for k, v in CICIDS2017_COMBINE_TO_CANONICAL.items() if k in chunk.columns}
        chunk = chunk.rename(columns=present_mapping)

        if "protocol" not in chunk.columns:
            chunk["protocol"] = _derive_protocol(chunk)
        else:
            chunk["protocol"] = pd.to_numeric(chunk["protocol"], errors="coerce")

        needed = [f for f in FEATURE_NAMES if f in chunk.columns]
        for feature_name in needed:
            chunk[feature_name] = pd.to_numeric(chunk[feature_name], errors="coerce")

        if "raw_label" not in chunk.columns:
            raise ValueError(f"Missing raw_label in {csv_path}")
        raw_label = chunk["raw_label"].astype(str).str.strip()
        normalized_label = raw_label.str.casefold()
        if paper_subset:
            allowed_labels = {"benign", *PAPER_DOS_LABELS}
            chunk = chunk[normalized_label.isin(allowed_labels)].copy()
            raw_label = raw_label.loc[chunk.index]
            normalized_label = normalized_label.loc[chunk.index]
        if chunk.empty:
            continue

        chunk["label"] = normalized_label.ne("benign").astype(int).to_numpy()

        needed = [f for f in PAPER_FEATURE_CANDIDATES if f in chunk.columns]
        if len(needed) < 3:
            needed = [f for f in FEATURE_NAMES if f in chunk.columns]
        for feature_name in needed:
            chunk[feature_name] = pd.to_numeric(chunk[feature_name], errors="coerce")

        chunk = chunk.replace([np.inf, -np.inf], np.nan).dropna(subset=needed + ["label"])
        for feature_name in needed:
            chunk[feature_name] = chunk[feature_name].clip(lower=0).astype("float32")
        chunk["label"] = chunk["label"].astype("int8")
        chunk["traffic_type"] = raw_label.loc[chunk.index].where(chunk["label"] == 1, "benign")
        keep_columns = needed + ["raw_label", "label", "traffic_type"]
        if "protocol" in chunk.columns and "protocol" not in keep_columns:
            keep_columns.append("protocol")
        full_parts.append(chunk[keep_columns])

    if not full_parts:
        raise ValueError(f"No valid rows found in {csv_path}")

    df = pd.concat(full_parts, ignore_index=True)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df


def build_dataset(seed: int = 42) -> Tuple[pd.DataFrame, str]:
    for csv_path, source in (
        (CICIDS2017_COMBINE_CSV, f"Loaded CICIDS2017 combine.csv from {CICIDS2017_COMBINE_CSV.name}"),
        (CICIDS2017_EXTRACTED_CSV, f"Loaded extracted CICIDS2017 combine.csv from {CICIDS2017_EXTRACTED_CSV.name}"),
    ):
        if csv_path.exists():
            try:
                df = load_cicids2017_from_csv(csv_path)
                return df, f"{source} (paper-compatible BENIGN vs Wednesday DoS subset)"
            except (ParserError, ValueError, KeyError, OSError):
                pass

    try:
        extracted_csv = extract_cicids2017_zip()
        df = load_cicids2017_from_csv(extracted_csv)
        return df, f"Extracted CICIDS2017 zip {CICIDS2017_ZIP.name} -> {extracted_csv.name} (paper-compatible BENIGN vs Wednesday DoS subset)"
    except (FileNotFoundError, OSError, zipfile.BadZipFile, ParserError, ValueError, KeyError):
        pass

    return synthesize_flows(seed=seed), "Synthetic DDoS-like flow dataset"


def load_kaggle_wednesday_subset(per_class: int = 2500, seed: int = 42) -> pd.DataFrame:
    """Compatibility loader used by the BMv2 rule exporter.

    The current reproduction keeps the paper-compatible Wednesday DoS subset
    in `combine.csv`/the extracted zip instead of reading the raw Kaggle
    parquet directly. This helper returns a balanced sample with the same
    canonical columns expected by the exporter.
    """
    df, _ = build_dataset(seed=seed)
    parts = []
    for _, subset in df.groupby("label", sort=False):
        n = min(per_class, len(subset))
        parts.append(subset.sample(n=n, random_state=seed) if len(subset) > n else subset)
    return pd.concat(parts, ignore_index=True).sample(frac=1.0, random_state=seed).reset_index(drop=True)
