from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parent
REPRO_ROOT = SRC_ROOT.parent
NT140_ROOT = REPRO_ROOT.parent
WORKSPACE = NT140_ROOT.parent
SISTAR_MODEL = NT140_ROOT / "SISTAR" / "model" / "DT-CTS.py"
OUTPUT = REPRO_ROOT / "output"
REAL_WEDNESDAY_CSV = (
    NT140_ROOT / "datasets" / "cicids2017" / "Wednesday-workingHours.pcap_ISCX.csv"
)

FEATURE_NAMES = [
    "destination_port",
    "init_win_bytes_forward",
    "fwd_header_length",
    "packet_length_mean",
    "flow_packets_persecond",
]

REAL_TO_CANONICAL = {
    " Destination Port": "destination_port",
    "Init_Win_bytes_forward": "init_win_bytes_forward",
    " Fwd Header Length": "fwd_header_length",
    " Packet Length Mean": "packet_length_mean",
    " Flow Packets/s": "flow_packets_persecond",
    " Label": "raw_label",
}
