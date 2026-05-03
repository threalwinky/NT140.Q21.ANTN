from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parent
REPRO_ROOT = SRC_ROOT.parent
NT140_ROOT = REPRO_ROOT.parent
WORKSPACE = NT140_ROOT.parent
SISTAR_MODEL = NT140_ROOT / "SISTAR" / "model" / "DT-CTS.py"
OUTPUT = REPRO_ROOT / "output"
KAGGLE_DATASET_SLUG = "dhoogla/cicids2017"
KAGGLE_WEDNESDAY_PARQUET = "DoS-Wednesday-no-metadata.parquet"

FEATURE_NAMES = [
    "protocol",
    "init_win_bytes_forward",
    "fwd_header_length",
    "packet_length_mean",
    "flow_packets_persecond",
]

PARQUET_TO_CANONICAL = {
    "Protocol": "protocol",
    "Init Fwd Win Bytes": "init_win_bytes_forward",
    "Fwd Header Length": "fwd_header_length",
    "Packet Length Mean": "packet_length_mean",
    "Flow Packets/s": "flow_packets_persecond",
    "Label": "raw_label",
}
