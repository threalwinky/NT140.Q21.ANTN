"""
Generate visualization plots from benchmark metrics.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUTPUT = Path(__file__).parent.parent / "output"

# Load benchmark data
benchmark_df = pd.read_csv(OUTPUT / "benchmark_metrics.csv")
models = benchmark_df["model"].tolist()

# ============================================================================
# 1. Detection Latency (mean, p95, p99)
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(models))
width = 0.25

mean_latency = benchmark_df["mean_latency_ms"].values
p95_latency = benchmark_df["p95_latency_ms"].values
p99_latency = benchmark_df["p99_latency_ms"].values

ax.bar(x - width, mean_latency, width, label="Mean", color="#1E3A5F")
ax.bar(x, p95_latency, width, label="P95", color="#00BCD4")
ax.bar(x + width, p99_latency, width, label="P99", color="#FF6B6B")

ax.set_ylabel("Latency (milliseconds)", fontsize=12, fontweight="bold")
ax.set_title("Detection Latency Comparison", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend()
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT / "benchmark_latency.png", dpi=150, bbox_inches="tight")
print("✓ Saved: benchmark_latency.png")
plt.close()

# ============================================================================
# 2. False Positive & False Negative Rate
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(models))
width = 0.35

fpr = benchmark_df["fpr"].values * 100  # convert to percentage
fnr = benchmark_df["fnr"].values * 100

ax.bar(x - width/2, fpr, width, label="FPR (False Positive Rate)", color="#FF6B6B")
ax.bar(x + width/2, fnr, width, label="FNR (False Negative Rate)", color="#FFA726")

ax.set_ylabel("Error Rate (%)", fontsize=12, fontweight="bold")
ax.set_title("Robustness: False Positive & Negative Rates", fontsize=14, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend()
ax.grid(axis="y", alpha=0.3)

# Add value labels on bars
for i, (f, fn) in enumerate(zip(fpr, fnr)):
    ax.text(i - width/2, f + 0.2, f"{f:.2f}%", ha="center", fontsize=10)
    ax.text(i + width/2, fn + 0.2, f"{fn:.2f}%", ha="center", fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT / "benchmark_false_rates.png", dpi=150, bbox_inches="tight")
print("✓ Saved: benchmark_false_rates.png")
plt.close()

# ============================================================================
# 3. Number of Rules (Deployment Efficiency)
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

n_rules = benchmark_df["n_rules"].values
# Filter out -1 (RF doesn't have clear rule count)
filtered_models = []
filtered_rules = []
for m, r in zip(models, n_rules):
    if r > 0:
        filtered_models.append(m)
        filtered_rules.append(r)

colors = ["#1E3A5F", "#00BCD4"]  # DT, DT-CTS
bars = ax.bar(filtered_models, filtered_rules, color=colors, width=0.6)

ax.set_ylabel("Number of Rules", fontsize=12, fontweight="bold")
ax.set_title("Model Complexity: Number of Decision Rules", fontsize=14, fontweight="bold")
ax.grid(axis="y", alpha=0.3)

# Add value labels on top of bars
for bar, val in zip(bars, filtered_rules):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f"{int(val)}", ha="center", va="bottom", fontsize=12, fontweight="bold")

# Add reduction percentage
dt_rules = filtered_rules[0]
dtcts_rules = filtered_rules[1]
reduction = (1 - dtcts_rules / dt_rules) * 100
ax.text(0.5, max(filtered_rules) * 0.9,
        f"DT-CTS reduces rules by {reduction:.1f}%",
        ha="center", fontsize=11,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#00BCD4", alpha=0.3))

plt.tight_layout()
plt.savefig(OUTPUT / "benchmark_rules.png", dpi=150, bbox_inches="tight")
print("✓ Saved: benchmark_rules.png")
plt.close()

# ============================================================================
# 4. Training Time Comparison
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

training_time = benchmark_df["training_time_sec"].values
colors = ["#1E3A5F", "#FFA726", "#00BCD4"]

bars = ax.bar(models, training_time, color=colors, width=0.6)

ax.set_ylabel("Training Time (seconds)", fontsize=12, fontweight="bold")
ax.set_title("Model Training Time Comparison", fontsize=14, fontweight="bold")
ax.grid(axis="y", alpha=0.3)

# Add value labels on top of bars
for bar, val in zip(bars, training_time):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f"{val:.3f}s", ha="center", va="bottom", fontsize=11, fontweight="bold")

plt.tight_layout()
plt.savefig(OUTPUT / "benchmark_training_time.png", dpi=150, bbox_inches="tight")
print("✓ Saved: benchmark_training_time.png")
plt.close()

# ============================================================================
# 5. Combined Benchmark Dashboard (4 subplots)
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Subplot 1: Latency
ax = axes[0, 0]
x = np.arange(len(models))
width = 0.25
ax.bar(x - width, benchmark_df["mean_latency_ms"].values, width, label="Mean", color="#1E3A5F")
ax.bar(x, benchmark_df["p95_latency_ms"].values, width, label="P95", color="#00BCD4")
ax.bar(x + width, benchmark_df["p99_latency_ms"].values, width, label="P99", color="#FF6B6B")
ax.set_ylabel("Latency (ms)", fontweight="bold")
ax.set_title("Detection Latency", fontweight="bold", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)

# Subplot 2: False Rates
ax = axes[0, 1]
x = np.arange(len(models))
width = 0.35
fpr_pct = benchmark_df["fpr"].values * 100
fnr_pct = benchmark_df["fnr"].values * 100
ax.bar(x - width/2, fpr_pct, width, label="FPR", color="#FF6B6B")
ax.bar(x + width/2, fnr_pct, width, label="FNR", color="#FFA726")
ax.set_ylabel("Error Rate (%)", fontweight="bold")
ax.set_title("Robustness: False Rates", fontweight="bold", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)

# Subplot 3: Number of Rules
ax = axes[1, 0]
n_rules_filtered = [r if r > 0 else 0 for r in benchmark_df["n_rules"].values]
colors_rules = ["#1E3A5F", "#FFA726", "#00BCD4"]
bars = ax.bar(models, n_rules_filtered, color=colors_rules, width=0.6)
ax.set_ylabel("Number of Rules", fontweight="bold")
ax.set_title("Deployment: Model Complexity", fontweight="bold", fontsize=12)
ax.grid(axis="y", alpha=0.3)
for bar, val in zip(bars, n_rules_filtered):
    if val > 0:
        ax.text(bar.get_x() + bar.get_width()/2., val,
                f"{int(val)}", ha="center", va="bottom", fontsize=10, fontweight="bold")

# Subplot 4: Training Time
ax = axes[1, 1]
bars = ax.bar(models, benchmark_df["training_time_sec"].values, color=colors_rules, width=0.6)
ax.set_ylabel("Training Time (s)", fontweight="bold")
ax.set_title("Training Efficiency", fontweight="bold", fontsize=12)
ax.grid(axis="y", alpha=0.3)
for bar, val in zip(bars, benchmark_df["training_time_sec"].values):
    ax.text(bar.get_x() + bar.get_width()/2., val,
            f"{val:.3f}s", ha="center", va="bottom", fontsize=10, fontweight="bold")

plt.suptitle("SISTAR Benchmark Summary", fontsize=16, fontweight="bold", y=1.00)
plt.tight_layout()
plt.savefig(OUTPUT / "benchmark_dashboard.png", dpi=150, bbox_inches="tight")
print("✓ Saved: benchmark_dashboard.png")
plt.close()

print("\n✅ All benchmark visualizations created!")
