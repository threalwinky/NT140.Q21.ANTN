from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional


def generate_data_benchmark_from_template(df: pd.DataFrame, out_path: Path, n_samples: int = 50000, seed: int = 42) -> Path:
    """Generate a synthetic benchmark CSV by sampling rows from `df` and
    applying small perturbations to numeric features. Saves to `out_path`.

    This keeps column layout identical to the source `df` so downstream code
    can consume it as if it were another capture.
    """
    rng = np.random.default_rng(seed)

    if n_samples <= 0:
        raise ValueError("n_samples must be > 0")

    # sample with replacement to get desired size
    src = df.sample(n=n_samples, replace=True, random_state=seed).reset_index(drop=True)

    # Only perturb actual feature columns. Keep labels and other annotations intact.
    feature_cols = [
        c
        for c in src.columns
        if c not in {"label", "raw_label", "attack_type"}
        and pd.api.types.is_numeric_dtype(src[c])
    ]

    # compute robust scale (median absolute deviation) per feature to guide perturbation
    mad = {}
    for c in feature_cols:
        col = pd.to_numeric(df[c], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
        mad[c] = float(np.median(np.abs(col - np.median(col)))) if len(col) > 0 else 0.0

    # Add small gaussian noise proportional to MAD, clip to non-negative where sensible
    for c in feature_cols:
        scale = mad.get(c, 0.0) * 0.1
        if scale <= 0:
            continue
        noise = rng.normal(loc=0.0, scale=scale, size=len(src))
        newvals = pd.to_numeric(src[c], errors="coerce").fillna(0.0) + noise
        # keep flows non-negative
        src[c] = newvals.clip(lower=0.0)

    # Make sure labels remain clean integers.
    if "label" in src.columns:
        src["label"] = pd.to_numeric(src["label"], errors="coerce").fillna(0).round().astype(int)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    src.to_csv(out_path, index=False)
    return out_path


def generate_data_benchmark_from_file(input_csv: str, output_csv: str, n_samples: int = 50000, seed: int = 42) -> str:
    df = pd.read_csv(input_csv)
    out = generate_data_benchmark_from_template(df, Path(output_csv), n_samples=n_samples, seed=seed)
    return str(out)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Generate synthetic data_benchmark CSV from combine template")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--n", type=int, default=50000)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    print(generate_data_benchmark_from_file(args.input, args.output, n_samples=args.n, seed=args.seed))
