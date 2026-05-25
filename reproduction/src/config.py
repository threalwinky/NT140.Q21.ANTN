from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parent
REPRO_ROOT = SRC_ROOT.parent
NT140_ROOT = REPRO_ROOT.parent
WORKSPACE = NT140_ROOT.parent
SISTAR_MODEL = NT140_ROOT / "SISTAR" / "model" / "DT-CTS.py"
OUTPUT = REPRO_ROOT / "output"
KAGGLE_DATASET_SLUG = "dhoogla/cicids2017"
KAGGLE_WEDNESDAY_PARQUET = "DoS-Wednesday-no-metadata.parquet"
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Medium scale: 6 RF trees, tree depth 6. DT and DT-CTS use the same depth.
MODEL_SCALE_MEDIUM = {
    "max_depth": 6,
    "n_estimators": 6,
    "min_samples_split": 2,
    "dt_ccp_alpha": 0.0,
    "dtcts_max_candidate_thresholds": 512,
    "dtcts_max_thresholds_per_feature": 2,
}

PAPER_DOS_LABELS = {
    "dos hulk",
    "dos goldeneye",
    "dos slowloris",
    "dos slowhttptest",
}

PAPER_REQUIRED_FEATURES = [
    "destination_port",
    "flow_packets_persecond",
    "packet_length_mean",
]

FEATURE_NAMES = [
    "protocol",
    "init_win_bytes_forward",
    "fwd_header_length",
    "packet_length_mean",
    "flow_packets_persecond",
]

BENCHMARK_7_FEATURES = [
    "flow_packets_persecond",
    "packet_length_mean",
    "protocol",
    "init_win_bytes_forward",
    "fwd_header_length",
    "packet_length_max",
    "packet_length_min",
]

PAPER_FEATURE_CANDIDATES = [
    "destination_port",
    "flow_packets_persecond",
    "packet_length_mean",
    "bwd_packet_length_max",
    "packet_length_max",
    "fwd_packet_length_max",
    "subflow_bwd_bytes",
    "fwd_iat_std",
    "flow_iat_std",
    "packet_length_min",
    "total_length_bwd_packets",
    "subflow_fwd_bytes",
    "bwd_packet_length_std",
    "fwd_iat_max",
    "fwd_iat_mean",
    "subflow_fwd_packets",
    "total_backward_packets",
    "bwd_packet_length_mean",
    "fwd_packet_length_mean",
    "bwd_packets_persecond",
    "init_win_bytes_forward",
    "total_fwd_packets",
    "fwd_header_length",
    "flow_iat_mean",
    "flow_iat_max",
    "flow_duration",
    "flow_bytes_persecond",
    "packet_length_std",
    "flow_iat_min",
    "fwd_iat_min",
    "fwd_packets_persecond",
]

PARQUET_TO_CANONICAL = {
    "Protocol": "protocol",
    "Init Fwd Win Bytes": "init_win_bytes_forward",
    "Fwd Header Length": "fwd_header_length",
    "Packet Length Mean": "packet_length_mean",
    "Flow Packets/s": "flow_packets_persecond",
    "Packet Length Max": "packet_length_max",
    "Packet Length Min": "packet_length_min",
    "Label": "raw_label",
}
