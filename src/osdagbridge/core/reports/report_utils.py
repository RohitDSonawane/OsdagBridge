from osdagbridge.core.utils.common import (
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_DEPTH,
    KEY_TS_NO_OF_GIRDERS
)


def _tex(value):
    """Escape a Python value for safe LaTeX embedding."""
    s = str(value) if value is not None else ''
    if not s:
        return r''
    # Normalise non-ASCII glyphs from section designations (e.g. "∠ 100 ⅹ 100ⅹ 10")
    # that pdflatex cannot render.
    for uni, ascii_ in [('∠', 'L'), ('ⅹ', 'x'), ('×', 'x')]:
        s = s.replace(uni, ascii_)
    s = s.replace('\\', r'\textbackslash{}')
    for ch, esc in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
                    ('{', r'\{'), ('}', r'\}'),          
                    ('_', r'\_\allowbreak{}'),            
                    ('~', r'\textasciitilde{}'), ('^', r'\^{}')]:
        s = s.replace(ch, esc)
    s = s.replace(':', r':\allowbreak{}')
    return s


def _render_value(source_dict, key, unit=""):
    val = source_dict.get(key)
    if val in ("", None):
        return ""
    return _tex(val) + unit


def get_girder_entries(input_dict):
    """
    Retrieve all girder labels and member IDs from backend keys.

    Usage Example:
    --------------------------
    girder_entries = get_girder_entries(bridge.input_dict)
    
    # 1. Fallback handling (if backend hasn't populated keys yet)
    if not girder_entries:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1))
        girder_entries = [(f"Girder {i}", f"M1") for i in range(1, n + 1)]
        
    # 2. Get total number of girders safely
    n_girders = len(girder_entries)
    
    # 3. Iterate over the girders to build table rows
    for lbl, mid in girder_entries:
        # lbl will be e.g., "G1", mid will be e.g., "G1M1"
        # Access girder specific keys dynamically:
        # val = input_dict.get(f"{KEY_MP_GIRDER_DEPTH}.{lbl}.{mid}")
        pass

    Returns:
        List[Tuple[str, str]]
    """
    n = int(input_dict.get(KEY_TS_NO_OF_GIRDERS, 0))

    entries = []

    for i in range(1, n + 1):
        entries.append(
            (
                input_dict.get(f"{KEY_MP_GD_SELECT_GIRDER}.G{i}", ""),
                input_dict.get(f"{KEY_MP_GD_MEMBER_ID}.G{i}.M1", ""),
            )
        )

    return entries


def _fig_or_placeholder(path, caption, width=r'0.9\textwidth'):
    """Embed figure if path is provided (file already copied to assets), else show placeholder box.
    path is the relative path as pdflatex will see it (e.g. 'assets/plan.png').
    """
    if path:
        p = path.replace('\\', '/')
        return (r'\begin{figure}[H]' + '\n'
                r'\centering' + '\n'
                r'\includegraphics[width=' + width + ']{' + p + '}\n'
                r'\caption*{' + caption + '}\n'
                r'\end{figure}')
    return (r'\begin{figure}[H]' + '\n'
            r'\centering' + '\n'
            r'\fbox{\parbox{0.97\textwidth}{' + '\n'
            r'\textit{[ PLACEHOLDER: ' + caption + r' ]}' + '\n'
            r'}}' + '\n'
            r'\caption*{' + caption + '}\n'
            r'\end{figure}')

def _fig_embed(path, caption, width=r'\textwidth', height=None):
    """Embed a real figure when path is provided (already copied); otherwise use an fbox placeholder."""
    if path:
        p = path.replace('\\', '/')
        opts = 'width=' + width
        if height:
            opts += ',height=' + height + ',keepaspectratio'
        return (r'\begin{figure}[H]' + '\n'
                r'\vspace{-0.5em}' + '\n'
                r'\centering' + '\n'
                r'\includegraphics[' + opts + ']{' + p + '}\n'
                r'\vspace{0.5em}' + '\n'
                r'\caption*{\small ' + caption + '}\n'
                r'\vspace{-0.5em}' + '\n'
                r'\end{figure}')
    # fbox placeholder — matches template exactly
    return (r'\noindent\fbox{\parbox{0.97\textwidth}{' + '\n'
            r'\textit{[ PLACEHOLDER: ' + caption + r' ]}' + '\n'
            r'}}')


def build_longtable_header(col_spec, col_headers, caption, n_cols, label=None):
    """Build standardized longtable header with \\endfirsthead, \\endhead, \\endfoot, \\endlastfoot."""
    header_row = " & ".join(col_headers) + r" \\[6pt]"
    label_str = f"\\label{{{label}}}" if label else ""
    return (
        f"\\begin{{longtable}}{{{col_spec}}}\n"
        f"\\caption{{{caption}}} {label_str} \\\\\n"
        f"\\hline\n"
        f"{header_row}\n"
        f"\\hline\n"
        f"\\endfirsthead\n\n"
        f"\\hline\n"
        f"\\multicolumn{{{n_cols}}}{{|c|}}{{\\small\\itshape \\tablename\\ \\thetable{{}} -- Continued from previous page}} \\\\\n"
        f"\\hline\n"
        f"{header_row}\n"
        f"\\hline\n"
        f"\\endhead\n\n"
        f"\\hline\n"
        f"\\multicolumn{{{n_cols}}}{{|r|}}{{\\small\\itshape Continued on next page\\ldots}} \\\\\n"
        f"\\endfoot\n\n"
        f"\\hline\n"
        f"\\endlastfoot\n"
    )


def _max_member_efficiency(pair_designs):
    """Maximum Osdag 'efficiency' (utilization ratio) over a cross-bracing or
    end-diaphragm result dump (nested pair -> member -> force_type -> raw).
    Reads already-computed results only; nothing is recalculated here."""
    from osdagbridge.core.bridge_types.plate_girder.results_data import _extract_osdag_summary
    if not isinstance(pair_designs, dict):
        return None
    best = None
    for members in pair_designs.values():
        if not isinstance(members, dict):
            continue
        for force_types in members.values():
            if not isinstance(force_types, dict):
                continue
            for raw in force_types.values():
                try:
                    val = _extract_osdag_summary(raw or {}).get("efficiency")
                    if val is None:
                        continue
                    f = float(val)
                except (TypeError, ValueError, AttributeError):
                    continue
                if best is None or f > best:
                    best = f
    return best


def get_deck_max_ur(deck_report_values, deck_design_results=None):
    """
    Computes governing Deck Slab UR from deck_report_values (sagging flexure,
    hogging flexure, cantilever overhang, punching shear, and one-way shear)
    to match Chapter 5 Table 5.29 exactly.
    """
    from osdagbridge.core.utils.common import (
        KEY_DD_M_ULS_SAG, KEY_DD_MU_BOT,
        KEY_DD_M_ULS_HOG, KEY_DD_MU_TOP,
        KEY_DD_M_ULS_OH, KEY_DD_MU_OH,
        KEY_DD_PUNCH_VED, KEY_DD_VRD_C_MPA,
        KEY_DD_SHEAR_VED, KEY_DD_SHEAR_VRDC,
    )
    def _to_f(v):
        if v in (None, "", "N.A.", "---"):
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    deck_urs = []
    if isinstance(deck_report_values, dict):
        _m_sag = _to_f(deck_report_values.get(KEY_DD_M_ULS_SAG))
        _mu_bot = _to_f(deck_report_values.get(KEY_DD_MU_BOT))
        if _m_sag is not None and _mu_bot and _mu_bot > 0:
            deck_urs.append(_m_sag / _mu_bot)

        _m_hog = _to_f(deck_report_values.get(KEY_DD_M_ULS_HOG))
        _mu_top = _to_f(deck_report_values.get(KEY_DD_MU_TOP))
        if _m_hog is not None and _mu_top and _mu_top > 0:
            deck_urs.append(_m_hog / _mu_top)

        _m_oh = _to_f(deck_report_values.get(KEY_DD_M_ULS_OH))
        _mu_oh = _to_f(deck_report_values.get(KEY_DD_MU_OH))
        if _m_oh is not None and _mu_oh and _mu_oh > 0:
            deck_urs.append(_m_oh / _mu_oh)

        _p_ved = _to_f(deck_report_values.get(KEY_DD_PUNCH_VED))
        _vrd_c = _to_f(deck_report_values.get(KEY_DD_VRD_C_MPA))
        if _p_ved is not None and _vrd_c and _vrd_c > 0:
            deck_urs.append(_p_ved / _vrd_c)

        _s_ved = _to_f(deck_report_values.get(KEY_DD_SHEAR_VED))
        _vrdc = _to_f(deck_report_values.get(KEY_DD_SHEAR_VRDC))
        if _s_ved is not None and _vrdc and _vrdc > 0:
            deck_urs.append(_s_ved / _vrdc)

    if deck_urs:
        return max(deck_urs)

    if isinstance(deck_design_results, dict):
        primary_keys = ["ur_bot_uls", "ur_top_uls", "ur_oh_uls", "ur_bot_shear", "ur_bot_punch", "ur_oh_shear", "ur_oh_punch"]
        vals = [_to_f(deck_design_results.get(k)) for k in primary_keys]
        valid_vals = [v for v in vals if v is not None]
        if valid_vals:
            return max(valid_vals)

    return None


