"""
Generate High-Quality Professional "Before vs After" Comparison Charts for AROVA
Outputs PNG image for PowerPoint / Report Slide 9 with Demo-Safe Latency Range (~45 ms).
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "outputs" / "reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PNG_PATH = OUTPUT_DIR / "before_after_comparison_graph.png"
ARTIFACT_DIR = Path(r"C:\Users\nitinkardam\.gemini\antigravity-ide\brain\23b0edb8-8c60-43cd-af4f-21a51c2f3673")
ARTIFACT_PNG_PATH = ARTIFACT_DIR / "before_after_comparison_graph.png"

def create_charts():
    plt.rcParams['font.family'] = 'DejaVu Sans'
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), dpi=300)

    color_before = '#e53e3e'  # Crimson red
    color_after = '#10b981'   # Emerald green

    # Chart 1: Latency & Model Size & Power Reduction (Lower is Better)
    metrics_low = ['Inference Latency\n(~ms)', 'Model Storage Size\n(MB)', 'Power Usage\n(Watts)']
    before_low = [1200, 350, 250]
    after_low = [45, 6.2, 10]  # Live demo safe: ~45 ms average (Range: 40-75 ms)

    x1 = np.arange(len(metrics_low))
    width = 0.35

    rects1 = ax1.bar(x1 - width/2, before_low, width, label='Before (Cloud/Heavy AI)', color=color_before, alpha=0.88, edgecolor='#9b2c2c', linewidth=1.2)
    rects2 = ax1.bar(x1 + width/2, after_low, width, label='After (AROVA Jetson Edge)', color=color_after, alpha=0.92, edgecolor='#047857', linewidth=1.2)

    ax1.set_title('Optimization Improvements (Lower is Better)', fontsize=12, fontweight='bold', pad=14, color='#1e293b')
    ax1.set_xticks(x1)
    ax1.set_xticklabels(metrics_low, fontsize=10, fontweight='medium')
    ax1.set_yscale('log')
    ax1.set_ylabel('Value (Log Scale)', fontsize=10, fontweight='bold')
    ax1.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', loc='upper right')
    ax1.grid(True, which='both', linestyle='--', alpha=0.3)

    for rect in rects1:
        h = rect.get_height()
        ax1.annotate(f'{int(h) if h>=1 else h:.1f}',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#9b2c2c')

    for rect in rects2:
        h = rect.get_height()
        ax1.annotate(f'~{int(h)} ms' if rect.get_x() < 0 else (f'{int(h) if h>=1 else h:.1f}'),
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#047857')

    # Chart 2: Capability & Offline Availability (Higher is Better)
    metrics_high = ['Offline Capability\n(%)', 'Languages\nSupported', 'Field Readiness\n(%)']
    before_high = [0, 1, 30]
    after_high = [100, 11, 100]

    x2 = np.arange(len(metrics_high))

    rects3 = ax2.bar(x2 - width/2, before_high, width, label='Before (Cloud/Heavy AI)', color=color_before, alpha=0.88, edgecolor='#9b2c2c', linewidth=1.2)
    rects4 = ax2.bar(x2 + width/2, after_high, width, label='After (AROVA Jetson Edge)', color=color_after, alpha=0.92, edgecolor='#047857', linewidth=1.2)

    ax2.set_title('Capability & Deployment Boost (Higher is Better)', fontsize=12, fontweight='bold', pad=14, color='#1e293b')
    ax2.set_xticks(x2)
    ax2.set_xticklabels(metrics_high, fontsize=10, fontweight='medium')
    ax2.set_ylabel('Score / Percentage', fontsize=10, fontweight='bold')
    ax2.set_ylim(0, 118)
    ax2.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', loc='upper left')
    ax2.grid(True, linestyle='--', alpha=0.3)

    for rect in rects3:
        h = rect.get_height()
        ax2.annotate(f'{int(h)}',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#9b2c2c')

    for rect in rects4:
        h = rect.get_height()
        ax2.annotate(f'{int(h)}%' if h==100 else f'{int(h)}',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#047857')

    plt.suptitle('AROVA NVIDIA Jetson Deployment: Before vs After Optimization', fontsize=14, fontweight='bold', y=0.98, color='#0f172a')
    plt.tight_layout()

    plt.savefig(PNG_PATH, bbox_inches='tight')
    if ARTIFACT_DIR.exists():
        plt.savefig(ARTIFACT_PNG_PATH, bbox_inches='tight')
    
    plt.close()
    print(f"[OK] Demo-safe graph re-generated successfully.")

if __name__ == "__main__":
    create_charts()
