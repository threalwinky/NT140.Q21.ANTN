from __future__ import annotations

import shutil
import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent
REPRO_ROOT = SRC_DIR.parent
IMPROVEMENT_DIR = REPRO_ROOT / "improvement"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(IMPROVEMENT_DIR) not in sys.path:
    sys.path.insert(0, str(IMPROVEMENT_DIR))

from paper_benchmark_3models import main as run_paper_benchmark
from run_reproduction import main as run_reproduction
from run_hierarchical_improvement import main as run_hierarchical_improvement


def _clear_directory(path: Path) -> None:
    if not path.exists():
        return
    for entry in path.iterdir():
        try:
            if entry.is_file():
                entry.unlink()
            elif entry.is_dir():
                shutil.rmtree(entry)
        except Exception:
            pass


def main() -> None:
    output_dir = REPRO_ROOT / "output"
    improvement_output_dir = IMPROVEMENT_DIR / "output"
    _clear_directory(output_dir)
    _clear_directory(improvement_output_dir)

    print("\n" + "=" * 80)
    print("1/3 - Core reproduction with hierarchical confidence-aware pushback")
    print("=" * 80)
    run_reproduction()

    print("\n" + "=" * 80)
    print("2/3 - Paper-style DT/RF/DT-CTS benchmark")
    print("=" * 80)
    run_paper_benchmark()

    print("\n" + "=" * 80)
    print("3/3 - Improvement comparison outputs")
    print("=" * 80)
    run_hierarchical_improvement()

    print("\n" + "=" * 80)
    print("DONE: refreshed reproduction/output and reproduction/improvement/output")
    print("=" * 80)


if __name__ == "__main__":
    main()
