# =============================================================================
# Chapter 3: Loads and Load Combinations
# Extracted from report_generator.py — DO NOT add business logic here.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CARRIAGEWAY_WIDTH,
    KEY_CB_LOAD,
    KEY_FOOTPATH,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value

def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span = input_dict.get(KEY_SPAN)
    span_m = None
    if span not in (None, ""):
        try:
            span_m = float(span)
        except Exception:
            span_m = None

    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    if not lanes:
        cw = input_dict.get(KEY_CARRIAGEWAY_WIDTH)
        if cw not in (None, ""):
            try:
                lanes = IRC6_2017.table_6(float(cw))
            except Exception:
                lanes = 2
        else:
            lanes = 2

    braking_force_val_str = "---"
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
            braking_force_raw = IRC6_2017.cl_211_2_braking_force(lanes_int)
            if braking_force_raw > 1000.0:
                braking_force_kN = braking_force_raw / 1000.0
            else:
                braking_force_kN = braking_force_raw * 9.81
            braking_force_val_str = f"{braking_force_kN:.2f} kN"
        except Exception:
            braking_force_val_str = "N/A"

    # Per-vehicle records for Table 3.3(a)
    vehicle_rows = []
    def _total_load_from_vehicle(vehicle_fn, direct_total_kN=None):
        if direct_total_kN is not None:
            return f"{float(direct_total_kN):.2f}"
        if not vehicle_fn:
            return "N/A"
        try:
            data = vehicle_fn()
            if "total_load_kN" in data:
                return f"{float(data['total_load_kN']):.2f}"
            if "wheel_loads" in data:
                return f"{sum(data['wheel_loads']) / 1000.0:.2f}"
            if "wheel_loads_udl" in data and "x" in data and len(data["x"]) >= 2:
                track_length = abs(float(data["x"][-1]) - float(data["x"][0]))
                return f"{float(data['wheel_loads_udl']) * track_length * 2.0 / 1000.0:.2f}"
        except Exception:
            return "N/A"
        return "N/A"

    def _add_vrow(name, if_clause_fn, has_braking=True, custom_if=None, custom_ecc=None, vehicle_fn=None, direct_total_kN=None):
        if custom_if is not None:
            if_str = custom_if
        elif if_clause_fn and span_m is not None:
            try:
                inc = if_clause_fn(span_m)
                if_str = f"{1.0 + inc:.3f}"
            except Exception:
                if_str = "N/A"
        else:
            if_str = "---"

        if has_braking:
            brk_cons = "Yes"
            brk_val = braking_force_val_str
            brk_ecc = custom_ecc if custom_ecc else r"At road surface level (IRC:6 Cl. 211.4)"
        else:
            brk_cons = "No"
            brk_val = "---"
            brk_ecc = "---"

        total_load = _total_load_from_vehicle(vehicle_fn, direct_total_kN)
        return f"{name} & {total_load} & {if_str} & {brk_cons} & {brk_val} & {brk_ecc}" + r" \\[6pt]" + "\n" + r"\hline"

    if input_dict.get(KEY_LL_IRC_CLASS_A):
        vehicle_rows.append(_add_vrow("Class A", IRC6_2017.cl_208_2_impact_factor, True, vehicle_fn=IRC6_2017.cl_204_1_ClassA_vehicle))
    if input_dict.get(KEY_LL_IRC_70R_WHEELED):
        vehicle_rows.append(_add_vrow("Class 70R (Wheeled)", IRC6_2017.cl_208_3_impact_factor, True, vehicle_fn=IRC6_2017.cl_204_1_Class70R_vehicle_wheel))
    if input_dict.get(KEY_LL_IRC_70R_TRACKED):
        vehicle_rows.append(_add_vrow("Class 70R (Tracked)", IRC6_2017.cl_208_3_impact_factor, True, vehicle_fn=IRC6_2017.cl_204_1_Class70R_vehicle_track))
    if input_dict.get(KEY_LL_IRC_70R_BOGIE):
        vehicle_rows.append(_add_vrow("Class 70R (Bogie)", IRC6_2017.cl_208_3_impact_factor, True, direct_total_kN=392.40))
    if input_dict.get(KEY_LL_IRC_AA_WHEELED):
        vehicle_rows.append(_add_vrow("Class AA (Wheeled)", IRC6_2017.cl_208_3_impact_factor, True, direct_total_kN=392.40))
    if input_dict.get(KEY_LL_IRC_AA_TRACKED):
        vehicle_rows.append(_add_vrow("Class AA (Tracked)", IRC6_2017.cl_208_3_impact_factor, True, direct_total_kN=686.70))
    if input_dict.get(KEY_LL_IRC_CLASS_SV):
        vehicle_rows.append(_add_vrow("Class SV", None, False, custom_if="---", vehicle_fn=IRC6_2017.cl_204_5_1_special_vehicle))
    if input_dict.get(KEY_LL_IRC_CLASS_FATIGUE):
        vehicle_rows.append(_add_vrow("Class Fatigue", IRC6_2017.cl_208_2_impact_factor, True, vehicle_fn=IRC6_2017.cl_204_6_fatigue_load))
    
    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            cname = c.get('name') if isinstance(c, dict) else str(c)
            if cname:
                vehicle_rows.append(_add_vrow(_tex(cname), None, False, custom_if="N/A", custom_ecc="User-defined"))

    if not vehicle_rows:
        vehicle_rows.append(r"None Selected & --- & --- & --- & --- & --- \\[6pt]" + "\n" + r"\hline")

    vehicle_rows_str = "\n".join(vehicle_rows)

    # Footpath / Footway loading (Table 3.3b)
    has_fp = str(input_dict.get(KEY_FOOTPATH, "")).strip().lower() not in ("", "none", "false", "0")
    fp_mode  = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")

    if has_fp:
        has_fp_str = f"Yes ({input_dict.get(KEY_FOOTPATH)})"
        if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
            try:
                fp_str = f"{IRC6_2017.cl_206_1_footway_load():.3f} kN/m²"
                fp_mode_str = "As Per IRC 6 (Automatic)"
            except Exception:
                fp_str = "N/A"
                fp_mode_str = "As Per IRC 6"
        elif fp_value not in (None, ""):
            fp_str = f"{fp_value} kN/m²"
            fp_mode_str = "Custom (User-defined)"
        else:
            fp_str = "N/A"
            fp_mode_str = "User-defined"
    else:
        has_fp_str = "No (Footway loading not applicable)"
        fp_mode_str = "---"
        fp_str = "---"

    # Vz / Pz — prefer stored computed values; fall back to IRC6 Table 12
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb  = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h   = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m²" if pz_val not in (None, "") else "N/A"

    # Table 3.5 — Seismic: prefer stored computed values; fall back to IRC6 cl_218_5_1
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral    = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah          = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av          = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z    = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st   = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp   = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res  = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral    = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah          = _res.get("Ah")
            if not sl_av:
                sl_av          = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _sl(v, unit=""):
        return f"{float(v):.4f}{unit}" if v not in (None, "") else "N/A"

    # Table 3.6 — Temperature: compute effective bridge temp range from shade temps
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP)  or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res    = IRC6_2017.cl_215_2_effective_bridge_temperature(
                          float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean   = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise     = f"{_bt_max - _mean:.2f}"
            tl_fall     = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # --- Table 3.7: Load Combinations (dynamically generated from IRC 6) ---
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        """Format a factors dict into a compact load-case string for the table."""
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):  # permanent load with adding/relieving
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue  # skip N/A factors
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"ULS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"SLS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )

    lc_rows_str = "\n".join(lc_rows)

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load -- Self Weight}} \label{subsec:dl-selfweight} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endfirsthead

\hline
\multicolumn{2}{|c|}{{\small\itshape \tablename\ \thetable{} -- Continued from previous page}} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endhead

\hline
\multicolumn{2}{|r|}{{\small\itshape Continued on next page\ldots}} \\
\endfoot

\hline
\endlastfoot
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Dead Load for Surfacing (DW)}} \label{subsec:dl-surfacing} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endfirsthead

\hline
\multicolumn{2}{|c|}{{\small\itshape \tablename\ \thetable{} -- Continued from previous page}} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endhead

\hline
\multicolumn{2}{|r|}{{\small\itshape Continued on next page\ldots}} \\
\endfoot

\hline
\endlastfoot
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[6pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[6pt]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[6pt]
\hline
\end{longtable}

\clearpage
\begin{longtable}{|L{2.5cm}|C{2.0cm}|C{1.8cm}|C{1.8cm}|C{2.2cm}|L{3.8cm}|}
\caption{\textbf{Live Loads (LL) --- Vehicle Summary (IRC:6-2017)}} \label{subsec:live-loads-vehicles} \\
\hline
\textbf{Vehicle Class} & \makecell{\textbf{Total Load}\\\textbf{(kN)}} & \textbf{Impact Factor} & \makecell{\textbf{Braking}\\\textbf{Considered?}} & \textbf{Braking Force} & \textbf{Braking Eccentricity} \\[6pt]
\hline
\endfirsthead

\hline
\multicolumn{6}{|c|}{{\small\itshape \tablename\ \thetable{} -- Continued from previous page}} \\
\hline
\textbf{Vehicle Class} & \makecell{\textbf{Total Load}\\\textbf{(kN)}} & \textbf{Impact Factor} & \makecell{\textbf{Braking}\\\textbf{Considered?}} & \textbf{Braking Force} & \textbf{Braking Eccentricity} \\[6pt]
\hline
\endhead

\hline
\multicolumn{6}{|r|}{{\small\itshape Continued on next page\ldots}} \\
\endfoot

\hline
\endlastfoot
""" + vehicle_rows_str + r"""
\end{longtable}
\noindent\textit{Note: Impact factor computed per IRC:6-2017 Cl. 208.2 (Class A / Fatigue) and Cl. 208.3 (Class 70R / AA). Longitudinal braking force per IRC:6-2017 Cl. 211.2 acting at road surface level per Cl. 211.4.}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Footway Live Load (IRC:6 Cl. 206.1)}} \label{subsec:footway-load} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endfirsthead

\hline
\multicolumn{2}{|c|}{{\small\itshape \tablename\ \thetable{} -- Continued from previous page}} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endhead

\hline
\multicolumn{2}{|r|}{{\small\itshape Continued on next page\ldots}} \\
\endfoot

\hline
\endlastfoot
\textnormal{Footway / Pedestrian Load Present} & """ + _tex(has_fp_str) + r""" \\[6pt]
\hline
\textnormal{Pressure Mode} & """ + _tex(fp_mode_str) + r""" \\[6pt]
\hline
\textnormal{Intensity} & """ + _tex(fp_str) + r""" \\[6pt]
\hline
\textnormal{IRC 6 Clause Reference} & IRC 6:2017 Cl. 206.1 \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Wind Load (WL) --- per IRC 6}} \label{subsec:wind-load} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endfirsthead

\hline
\multicolumn{2}{|c|}{{\small\itshape \tablename\ \thetable{} -- Continued from previous page}} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endhead

\hline
\multicolumn{2}{|r|}{{\small\itshape Continued on next page\ldots}} \\
\endfoot

\hline
\endlastfoot
\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[6pt]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\[6pt]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\[6pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Earthquake Load (EL) --- per IRC 6}} \label{subsec:earthquake-load} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endfirsthead

\hline
\multicolumn{2}{|c|}{{\small\itshape \tablename\ \thetable{} -- Continued from previous page}} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endhead

\hline
\multicolumn{2}{|r|}{{\small\itshape Continued on next page\ldots}} \\
\endfoot

\hline
\endlastfoot
\textnormal{Seismic Zone} & """ + (_render_value(input_dict,'seismic_zone')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (longitudinal)} & """ + '' + r""" kN \\[6pt]
\hline
\textnormal{Horizontal Seismic Force (transverse)} & """ + '' + r""" kN \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
\caption{\textbf{Temperature Load (TL) --- per IRC 6}} \label{subsec:temperature-load} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endfirsthead

\hline
\multicolumn{2}{|c|}{{\small\itshape \tablename\ \thetable{} -- Continued from previous page}} \\
\hline
\textbf{parameter} & \textbf{value} \\[6pt]
\hline
\endhead

\hline
\multicolumn{2}{|r|}{{\small\itshape Continued on next page\ldots}} \\
\endfoot

\hline
\endlastfoot
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_max')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_min')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[6pt]
\hline
\end{longtable}

\vspace{1em}
\begin{longtable}{|C{4.0cm}|p{11.5cm}|}
\caption{\textbf{Load Combinations}} \label{subsec:load-combinations} \\
\hline
\textbf{Combination ID} & \textbf{Load Cases} \\[6pt]
\hline
\endfirsthead

\hline
\multicolumn{2}{|c|}{{\small\itshape \tablename\ \thetable{} -- Continued from previous page}} \\
\hline
\textbf{Combination ID} & \textbf{Load Cases} \\[6pt]
\hline
\endhead

\hline
\multicolumn{2}{|r|}{{\small\itshape Continued on next page\ldots}} \\
\endfoot

\hline
\endlastfoot
""" + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""


