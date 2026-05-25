from __future__ import annotations

import sys
from pathlib import Path


SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from generate_and_benchmark import main as run_generated_benchmarks
from pathlib import Path


def main() -> None:
    output_dir = Path(__file__).resolve().parent.parent / "output"
    # clear output directory
    if output_dir.exists():
        for p in output_dir.iterdir():
            try:
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    import shutil

                    shutil.rmtree(p)
            except Exception:
                pass

    print("\n" + "=" * 80)
    print("Train on full CICIDS2017, generate traffic variants, and benchmark")
    print("=" * 80)
    # Run generated benchmarks (this will train on full dataset by default)
    run_generated_benchmarks()

    print("\n" + "=" * 80)
    print("DONE: Generated training and traffic benchmark outputs in reproduction/output/")
    print("=" * 80)


if __name__ == "__main__":
    main()