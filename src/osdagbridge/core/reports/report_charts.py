"""
report_charts.py
----------------
Visualization and chart generation for OsdagBridge design reports.
Uses Matplotlib with the non-interactive Agg backend to generate publication-quality
charts for the LaTeX report generation pipeline.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import logging

from osdagbridge.core.reports import styles

logger = logging.getLogger(__name__)


def generate_ur_chart(ur_data: dict, output_dir: str, filename: str = "ur_summary_chart.png") -> str | None:
    """
    Generate horizontal bar chart of Utilization Ratios for structural checks.
    
    Parameters
    ----------
    ur_data : dict
        Mapping of check/component label to UR float value.
    output_dir : str
        Directory to save the generated PNG.
    filename : str, optional
        Filename of the generated chart.
        
    Returns
    -------
    str | None
        Normalized path to generated PNG image, or None if generation failed.
    """
    if not ur_data:
        return None

    fig, ax = plt.subplots(figsize=styles.CHART_FIGSIZE_WIDE, dpi=styles.CHART_DPI)
    try:
        labels = list(ur_data.keys())
        values = [float(v) for v in ur_data.values()]

        colors = [styles.CHART_COLOR_PASS if v <= 1.0 else styles.CHART_COLOR_FAIL for v in values]
        y_pos = list(range(len(labels)))

        bars = ax.barh(y_pos, values, color=colors, height=0.55, edgecolor="none", zorder=3)

        # Red dashed threshold line at UR = 1.0
        ax.axvline(
            x=1.0,
            color=styles.CHART_UR_LIMIT_COLOR,
            linestyle=styles.CHART_UR_LIMIT_STYLE,
            linewidth=1.5,
            label="UR = 1.0 Limit",
            zorder=4
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=styles.CHART_FONT_AXIS)
        ax.invert_yaxis()  # Highest/first check at top

        max_val = max(values) if values else 1.0
        ax.set_xlim(0, max(1.15, max_val + 0.15))
        ax.set_xlabel("Utilization Ratio (Demand / Capacity)", fontsize=styles.CHART_FONT_AXIS, fontweight="bold")
        ax.set_title("Overall Design Check — Utilization Ratio Summary", fontsize=styles.CHART_FONT_TITLE, fontweight="bold", pad=12)

        # Value annotations on bar ends
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax.text(
                width + 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.2f}",
                va="center",
                ha="left",
                fontsize=styles.CHART_FONT_LABEL,
                fontweight="bold",
                color="#333333"
            )

        ax.grid(axis="x", linestyle=":", alpha=0.6, zorder=0)
        ax.legend(loc="lower right", fontsize=8, framealpha=0.9)
        plt.tight_layout()

        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, filename)
        fig.savefig(out_path, dpi=styles.CHART_DPI, bbox_inches="tight")
        return out_path.replace("\\", "/")
    except Exception as e:
        logger.warning("Failed to generate UR chart: %s", e)
        return None
    finally:
        plt.close(fig)


def generate_steel_tonnage_chart(quantities: dict, output_dir: str, filename: str = "steel_tonnage_chart.png") -> str | None:
    """
    Generate vertical bar chart of structural steel tonnage per member type.
    
    Parameters
    ----------
    quantities : dict
        Dictionary of material quantities from boq_generator.
    output_dir : str
        Directory to save the generated PNG.
    filename : str, optional
        Filename of the generated chart.
        
    Returns
    -------
    str | None
        Normalized path to generated PNG image, or None if generation failed.
    """
    if not quantities:
        return None

    g_wt = quantities.get("steel_girders_wt_total")
    cb_wt = quantities.get("steel_bracing_wt_total")
    if cb_wt in (None, "", "N.A."):
        cb_parts = [
            quantities.get("bracing_top_wt_total"),
            quantities.get("bracing_bot_wt_total"),
            quantities.get("bracing_diag_wt_total"),
        ]
        cb_nums = []
        for p in cb_parts:
            try:
                if p not in (None, "", "N.A."):
                    cb_nums.append(float(p))
            except (ValueError, TypeError):
                pass
        if cb_nums:
            cb_wt = sum(cb_nums)

    ed_wt = quantities.get("end_diaphragm_wt_total", quantities.get("steel_diaphragm_wt_total", 0.0))

    raw_items = [
        ("Girders", g_wt),
        ("Cross Bracing", cb_wt),
        ("End Diaphragms", ed_wt),
    ]

    labels = []
    values = []
    for lbl, val in raw_items:
        if val not in (None, "", "N.A."):
            try:
                v = float(val)
                labels.append(lbl)
                values.append(v)
            except (ValueError, TypeError):
                continue

    if not values or all(v == 0 for v in values):
        return None

    fig, ax = plt.subplots(figsize=styles.CHART_FIGSIZE_MATERIAL, dpi=styles.CHART_DPI)
    try:
        x_pos = list(range(len(labels)))
        bars = ax.bar(x_pos, values, color=styles.CHART_COLOR_STEEL, width=0.45, zorder=3)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, fontsize=styles.CHART_FONT_AXIS)
        ax.set_ylabel("Weight (MT)", fontsize=styles.CHART_FONT_AXIS, fontweight="bold")
        ax.set_title("Structural Steel — Component Tonnage Summary", fontsize=styles.CHART_FONT_TITLE, fontweight="bold", pad=12)

        max_y = max(values) if values else 1.0
        ax.set_ylim(0, max_y * 1.18)

        # Bar top value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + (max_y * 0.02),
                f"{val:.2f} MT",
                ha="center",
                va="bottom",
                fontsize=styles.CHART_FONT_LABEL,
                fontweight="bold",
                color="#333333"
            )

        ax.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
        plt.tight_layout()

        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, filename)
        fig.savefig(out_path, dpi=styles.CHART_DPI, bbox_inches="tight")
        return out_path.replace("\\", "/")
    except Exception as e:
        logger.warning("Failed to generate steel tonnage chart: %s", e)
        return None
    finally:
        plt.close(fig)


def generate_concrete_rebar_chart(quantities: dict, output_dir: str, filename: str = "concrete_rebar_chart.png") -> str | None:
    """
    Generate dual-axis bar chart comparing deck concrete volume and rebar weight.
    
    Parameters
    ----------
    quantities : dict
        Dictionary of material quantities from boq_generator.
    output_dir : str
        Directory to save the generated PNG.
    filename : str, optional
        Filename of the generated chart.
        
    Returns
    -------
    str | None
        Normalized path to generated PNG image, or None if generation failed.
    """
    if not quantities:
        return None

    vol_raw = quantities.get("concrete_deck_vol_total")
    rebar_raw = quantities.get("rebar_deck_wt_total")

    if vol_raw in (None, "", "N.A.") or rebar_raw in (None, "", "N.A."):
        return None

    try:
        vol = float(vol_raw)
        rebar = float(rebar_raw)
    except (ValueError, TypeError):
        return None

    fig, ax1 = plt.subplots(figsize=styles.CHART_FIGSIZE_MATERIAL, dpi=styles.CHART_DPI)
    try:
        ax2 = ax1.twinx()

        bar1 = ax1.bar([0.35], [vol], width=0.25, color=styles.CHART_COLOR_CONCRETE, label="Concrete Volume (m³)", zorder=3)
        bar2 = ax2.bar([0.65], [rebar], width=0.25, color=styles.CHART_COLOR_REBAR, label="Rebar Weight (MT)", zorder=3)

        ax1.set_xlim(0.1, 0.9)
        ax1.set_xticks([0.35, 0.65])
        ax1.set_xticklabels(["Deck Concrete", "Deck Rebar"], fontsize=styles.CHART_FONT_AXIS, fontweight="bold")

        ax1.set_ylabel("Concrete Volume (m³)", color="#555555", fontsize=styles.CHART_FONT_AXIS, fontweight="bold")
        ax2.set_ylabel("Reinforcement Weight (MT)", color="#555555", fontsize=styles.CHART_FONT_AXIS, fontweight="bold")

        ax1.set_ylim(0, vol * 1.25)
        ax2.set_ylim(0, rebar * 1.25)

        # Labels
        ax1.text(0.35, vol + (vol * 0.02), f"{vol:.2f} m³", ha="center", va="bottom", fontsize=styles.CHART_FONT_LABEL, fontweight="bold")
        ax2.text(0.65, rebar + (rebar * 0.02), f"{rebar:.2f} MT", ha="center", va="bottom", fontsize=styles.CHART_FONT_LABEL, fontweight="bold")

        ax1.set_title("Deck Slab — Concrete Volume vs. Reinforcement Steel Weight", fontsize=styles.CHART_FONT_TITLE, fontweight="bold", pad=12)
        ax1.grid(axis="y", linestyle=":", alpha=0.5, zorder=0)

        plt.tight_layout()

        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, filename)
        fig.savefig(out_path, dpi=styles.CHART_DPI, bbox_inches="tight")
        return out_path.replace("\\", "/")
    except Exception as e:
        logger.warning("Failed to generate concrete/rebar chart: %s", e)
        return None
    finally:
        plt.close(fig)
