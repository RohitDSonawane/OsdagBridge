"""Centralized formatting and styling constants for OsdagBridge PDF Reports."""

# =============================================================================
# Color Palette
# =============================================================================
OSDAG_GREEN_HEX = "#91B014"
OSDAG_GREEN_LATEX = "osdagGreen"
FAIL_RED_LATEX = "red"
HEADER_RULE_COLOR = OSDAG_GREEN_LATEX
FOOTER_RULE_COLOR = OSDAG_GREEN_LATEX

# =============================================================================
# Document Geometry Tokens
# =============================================================================
PAGE_MARGIN = "1in"
BOTTOM_MARGIN = "1.3in"
FOOT_SKIP_PT = 30
TEXT_STRETCH = 1.15

# =============================================================================
# Table Formatting Tokens
# =============================================================================
TABCOLSEP_DEFAULT = 6.0
TABCOLSEP_NARROW_4 = 4.0
TABCOLSEP_NARROW_35 = 3.5
TABCOLSEP_NARROW_3 = 3.0

ARRAY_STRETCH_DEFAULT = 1.10
ARRAY_STRETCH_DENSE = 1.25
ARRAY_RULE_WIDTH_PT = 0.5
EXTRA_ROW_HEIGHT_PT = 0.6
LT_PRE_PT = 0
LT_POST_PT = 6

# =============================================================================
# Page Break Guard Tokens
# =============================================================================
NEEDSPACE_LONGTABLE_LINES = 8

# =============================================================================
# Caption Spacing Tokens
# =============================================================================
ABOVE_CAPTION_PT = 2
BELOW_CAPTION_PT = 2

# =============================================================================
# Longtable Continued-On-Page Banner Tokens
# =============================================================================
LONGTABLE_CONTINUED_TEXT = (
    r"{\small\itshape \tablename\ \thetable{} -- Continued from previous page}"
)
LONGTABLE_END_TEXT = r"\hline"

# =============================================================================
# Matplotlib Chart Constants
# =============================================================================
CHART_DPI = 150
CHART_FIGSIZE_WIDE = (9, 4)
CHART_FIGSIZE_MATERIAL = (8, 5)

CHART_COLOR_PASS = "#2E86AB"
CHART_COLOR_FAIL = "#E84855"
CHART_COLOR_STEEL = "#4A4E69"
CHART_COLOR_CONCRETE = "#9A8C98"
CHART_COLOR_REBAR = "#C9ADA7"

CHART_UR_LIMIT_COLOR = "red"
CHART_UR_LIMIT_STYLE = "--"

CHART_FONT_TITLE = 11
CHART_FONT_AXIS = 10
CHART_FONT_LABEL = 8


def preamble_style_block() -> str:
    """Return LaTeX string containing global spacing, rules, and geometry definitions."""
    return f"""% Table layout and spacing: consistent padding, row height, and longtable pre/post skips
\\setlength{{\\tabcolsep}}{{{TABCOLSEP_DEFAULT:.1f}pt}}
\\renewcommand{{\\arraystretch}}{{{ARRAY_STRETCH_DEFAULT:.2f}}}
\\setlength{{\\LTpre}}{{{LT_PRE_PT}pt}}
\\setlength{{\\LTpost}}{{{LT_POST_PT}pt}}
% Table rules (outline thickness) and small extra row height for clarity
\\setlength{{\\arrayrulewidth}}{{{ARRAY_RULE_WIDTH_PT:.1f}pt}}
\\setlength{{\\extrarowheight}}{{{EXTRA_ROW_HEIGHT_PT:.1f}pt}}
\\setlength{{\\footskip}}{{{FOOT_SKIP_PT}pt}}

% Prevent tables from overflowing past the page bottom:
\\BeforeBeginEnvironment{{table}}{{\\needspace{{{NEEDSPACE_LONGTABLE_LINES}\\baselineskip}}}}
\\BeforeBeginEnvironment{{longtable}}{{\\needspace{{{NEEDSPACE_LONGTABLE_LINES}\\baselineskip}}}}"""
