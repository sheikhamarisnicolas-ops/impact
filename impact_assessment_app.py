"""
Impact Assessment System
DOST SETUP 4.0 iFund Program — Region VI

Tracks MSME project performance across three checkpoints:
  Pre-PIS (Baseline Target) -> Semestral Status Report (Mid-Year Progress) -> Annual PIS (Accomplished)

Run with live data by adding SUPABASE_URL / SUPABASE_KEY to .streamlit/secrets.toml.
Falls back to bundled demo data otherwise.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# --------------------------------------------------------------------------------------
# PAGE CONFIG & GLOBAL STYLES
# --------------------------------------------------------------------------------------

st.set_page_config(
    page_title="Impact Assessment System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

STATUS_COLORS = {
    "Accomplished": "#16a34a",
    "Partially accomplished": "#d97706",
    "Not accomplished": "#dc2626",
    "Not yet due": "#6b7280",
}

STATUS_BG = {
    "Accomplished": "#dcfce7",
    "Partially accomplished": "#fef3c7",
    "Not accomplished": "#fee2e2",
    "Not yet due": "#f3f4f6",
}

STATUS_ICON = {
    "Accomplished": "✓",
    "Partially accomplished": "—",
    "Not accomplished": "✕",
    "Not yet due": "…",
}

CUSTOM_CSS = """
<style>
    .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1150px;}
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 14px 16px 10px 16px;
    }
    div[data-testid="stMetricLabel"] {color: #6b7280; font-size: 0.85rem;}
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .section-header {
        font-size: 0.78rem;
        letter-spacing: 0.06em;
        color: #6b7280;
        font-weight: 700;
        margin-top: 0.4rem;
        margin-bottom: 0.6rem;
        text-transform: uppercase;
    }
    .card {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 14px;
        background: white;
    }
    .obj-card-title {font-weight: 600; font-size: 0.95rem; margin-bottom: 6px;}
    .obj-card-sub {color: #6b7280; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em;}
    .note-text {color: #4b5563; font-size: 0.85rem; margin-top: 6px;}
    hr {margin: 1.2rem 0;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------------------
# DEMO DATA
# --------------------------------------------------------------------------------------
# Structure per project:
#   program, general_objective
#   specific_objectives: [{id, text, pre_pis_target, semestral: {status, progress, note}, annual: {status, progress, note}}]
#   quantifiable_outputs: [{name, unit, target, pre_pis, actual, status, note}]
#   non_quantifiable: [{name, note, status}]
#   periods: ordered list of checkpoint labels used in the PIS progression trend
#   financials: {metric: {period_label: value or None}}

def build_demo_data():
    periods = [
        "Pre-PIS",
        "PIS 1 (Year 1)",
        "PIS 2 (Year 2)",
        "PIS 3 (Year 3)",
    ]

    honore = {
        "program": "DOST SETUP 4.0 iFund Program — Region VI",
        "general_objective": "This project aims to improve the production facilities of Honoré Café through the acquisition of S&T technologies.",
        "periods": periods,
        "semestral_cycles": ["S1 2021 (Jan–Jun)", "S2 2021 (Jul–Dec)", "S1 2022 (Jan–Jun)"],
        "current_semestral_cycle": "S2 2021 (Jul–Dec)",
        "specific_objectives": [
            {
                "id": 1,
                "text": "To improve product quality by producing consistent appearance of finished products through an evenly distributed temperature of the three-deck oven",
                "pre_pis_target": "Stainless LPG 3-deck oven acquired and operational",
                "semestral": {"status": "Accomplished", "progress": 100,
                              "note": "Stainless LPG oven in good working condition as of December 2021."},
                "annual": {"status": "Accomplished", "progress": 100,
                           "note": "Consistent product appearance sustained through Year 1."},
            },
            {
                "id": 2,
                "text": "To improve the production process by reducing baking time by at least 50% (four hours to two hours) and increasing baking capacity to 100%",
                "pre_pis_target": "Baking time: 4 hrs → 2 hrs · Capacity: 792 → 1,584 pcs/day",
                "semestral": {"status": "Partially accomplished", "progress": 57,
                              "note": "Baking time target met; capacity increase lagging due to COVID-19."},
                "annual": {"status": "Partially accomplished", "progress": 62,
                           "note": "Baking time sustained at 2 hrs; capacity still below target."},
            },
            {
                "id": 3,
                "text": "To improve the production management system and reduce production delays by introducing an inventory system software",
                "pre_pis_target": "POS / inventory system deployed and in active use",
                "semestral": {"status": "Not accomplished", "progress": 0,
                              "note": "POS not utilized due to lack of training for new employees."},
                "annual": {"status": "Partially accomplished", "progress": 40,
                           "note": "Staff training conducted; partial adoption of POS module."},
            },
            {
                "id": 4,
                "text": "To enhance compliance with food safety standards",
                "pre_pis_target": "Certified compliance with DOST-VI food safety standards",
                "semestral": {"status": "Accomplished", "progress": 100,
                              "note": "Enhanced compliance via procured stainless steel equipment and DOST-VI Food Safety Consultancy."},
                "annual": {"status": "Accomplished", "progress": 100,
                           "note": "Compliance maintained; no citations in Year 1 inspection."},
            },
        ],
        "quantifiable_outputs": [
            {"name": "Improve product quality (consistent appearance via 3-deck oven)",
             "unit": "n/a", "target": 100, "pre_pis": 0, "actual": 100,
             "status": "Accomplished", "note": "Stainless LPG Oven in good working condition as of December 2021."},
            {"name": "Reduce baking time by 50% (4 hrs → 2 hrs)",
             "unit": "%", "target": 50, "pre_pis": 0, "actual": 50,
             "status": "Accomplished", "note": "Target baking time achieved and sustained."},
            {"name": "Improve baking capacity by 100% (792 → 1,584 pcs/day)",
             "unit": "pcs/day", "target": 1584, "pre_pis": 792, "actual": 214,
             "status": "Not accomplished", "note": "COVID-19 significantly affected operations during the first year."},
            {"name": "Increase production volume by 45% (247,200 → 358,320 pcs)",
             "unit": "pcs", "target": 358320, "pre_pis": 247200, "actual": 77040,
             "status": "Not accomplished", "note": "Production volume decreased by 69% due to COVID-19."},
            {"name": "Increase sales by 78% (₱3.06M → ₱5.46M)",
             "unit": "₱", "target": 5455510, "pre_pis": 3060000, "actual": 2404800,
             "status": "Not accomplished", "note": "Sales decreased by 21% due to COVID-19 pandemic."},
            {"name": "Establish at least 2 additional markets in Aklan",
             "unit": "outlets", "target": 2, "pre_pis": 0, "actual": 1,
             "status": "Partially accomplished", "note": "Only one additional outlet established in Kalibo, Aklan."},
            {"name": "Generate at least 1 additional worker",
             "unit": "workers", "target": 1, "pre_pis": 0, "actual": 4,
             "status": "Accomplished", "note": "Four additional workers hired during the semester."},
        ],
        "non_quantifiable": [
            {"name": "Enhance compliance with food safety standards",
             "note": "Enhanced compliance via procured stainless steel equipment and DOST-VI Food Safety Consultancy.",
             "status": "Accomplished"},
            {"name": "Improve production management using inventory/POS system software",
             "note": "No improvement in production management. POS not utilized due to lack of training for new employees.",
             "status": "Not accomplished"},
        ],
        "financials": {
            "Assets": {"Pre-PIS": 2230000, "PIS 1 (Year 1)": 2230000, "PIS 2 (Year 2)": 2410000, "PIS 3 (Year 3)": None},
            "Employment": {"Pre-PIS": 17, "PIS 1 (Year 1)": 21, "PIS 2 (Year 2)": None, "PIS 3 (Year 3)": None},
            "Gross Sales": {"Pre-PIS": 58000000, "PIS 1 (Year 1)": 45820000, "PIS 2 (Year 2)": None, "PIS 3 (Year 3)": None},
        },
        "asset_breakdown": {
            "metric": ["Land", "Building", "Equipment", "Working Cap."],
            "pre_pis": [1500000, 250000, 375000, 100000],
            "current": [1500000, 250000, 375000, 100000],
        },
    }

    hanjim = {
        "program": "DOST SETUP 4.0 iFund Program — Region VI",
        "general_objective": "This project aims to modernize the meat-processing line of Han Jim Marketing Corporation through the acquisition of S&T technologies.",
        "periods": periods,
        "semestral_cycles": ["S1 2022 (Jan–Jun)", "S2 2022 (Jul–Dec)"],
        "current_semestral_cycle": "S2 2022 (Jul–Dec)",
        "specific_objectives": [
            {
                "id": 1,
                "text": "To improve product shelf life through acquisition of a vacuum sealing machine",
                "pre_pis_target": "Vacuum sealing machine installed and operational",
                "semestral": {"status": "Accomplished", "progress": 100, "note": "Vacuum sealer installed and running since Q2 2022."},
                "annual": {"status": "Accomplished", "progress": 100, "note": "Shelf life extended from 3 to 10 days as planned."},
            },
            {
                "id": 2,
                "text": "To increase production capacity by upgrading the chiller and freezer units",
                "pre_pis_target": "Capacity: 300 → 600 kg/day",
                "semestral": {"status": "Partially accomplished", "progress": 65, "note": "Chiller upgraded; freezer upgrade delayed by supplier backorder."},
                "annual": {"status": "Accomplished", "progress": 95, "note": "Freezer unit installed Q1; capacity near target by year-end."},
            },
            {
                "id": 3,
                "text": "To expand market reach to at least 3 new municipalities",
                "pre_pis_target": "3 new municipalities served",
                "semestral": {"status": "Not accomplished", "progress": 0, "note": "Focus remained on local market during equipment transition."},
                "annual": {"status": "Partially accomplished", "progress": 33, "note": "1 of 3 target municipalities reached."},
            },
        ],
        "quantifiable_outputs": [
            {"name": "Increase production capacity by 100% (300 → 600 kg/day)",
             "unit": "kg/day", "target": 600, "pre_pis": 300, "actual": 480,
             "status": "Partially accomplished", "note": "Chiller upgrade complete; freezer upgrade completed late in the year."},
            {"name": "Extend product shelf life (3 → 10 days)",
             "unit": "days", "target": 10, "pre_pis": 3, "actual": 10,
             "status": "Accomplished", "note": "Vacuum sealing fully adopted across product lines."},
            {"name": "Increase sales by 40% (₱1.8M → ₱2.52M)",
             "unit": "₱", "target": 2520000, "pre_pis": 1800000, "actual": 2350000,
             "status": "Partially accomplished", "note": "Strong Q4 sales narrowed the gap to target."},
            {"name": "Generate at least 2 additional workers",
             "unit": "workers", "target": 2, "pre_pis": 0, "actual": 3,
             "status": "Accomplished", "note": "Three new hires to support the expanded line."},
        ],
        "non_quantifiable": [
            {"name": "Improve HACCP-aligned handling practices",
             "note": "Staff completed food-handling refresher training; documentation still pending sign-off.",
             "status": "Partially accomplished"},
        ],
        "financials": {
            "Assets": {"Pre-PIS": 1450000, "PIS 1 (Year 1)": 1980000, "PIS 2 (Year 2)": None, "PIS 3 (Year 3)": None},
            "Employment": {"Pre-PIS": 9, "PIS 1 (Year 1)": 12, "PIS 2 (Year 2)": None, "PIS 3 (Year 3)": None},
            "Gross Sales": {"Pre-PIS": 1800000, "PIS 1 (Year 1)": 2350000, "PIS 2 (Year 2)": None, "PIS 3 (Year 3)": None},
        },
        "asset_breakdown": {
            "metric": ["Land", "Building", "Equipment", "Working Cap."],
            "pre_pis": [500000, 300000, 500000, 150000],
            "current": [500000, 300000, 980000, 200000],
        },
    }

    return {
        "Honore Cafe": honore,
        "Han Jim Marketing Corporation": hanjim,
    }


DATA = build_demo_data()


# --------------------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------------------

def peso(v):
    if v is None:
        return "—"
    if abs(v) >= 1_000_000:
        return f"₱{v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"₱{v/1_000:.1f}K"
    return f"₱{v:,.0f}"


def fmt_value(v, unit):
    if v is None:
        return "—"
    if unit == "₱":
        return peso(v)
    if unit == "n/a":
        return "—"
    return f"{v:,.0f} {unit}".strip()


def badge_html(status):
    color = STATUS_COLORS.get(status, "#6b7280")
    bg = STATUS_BG.get(status, "#f3f4f6")
    icon = STATUS_ICON.get(status, "")
    return f'<span class="badge" style="color:{color};background:{bg};">{icon} {status}</span>'


def progress_bar_html(pct, status):
    pct = max(0, min(100, pct))
    color = STATUS_COLORS.get(status, "#6b7280")
    return f"""
    <div style="background:#e5e7eb;border-radius:6px;height:8px;width:100%;margin:6px 0;">
        <div style="background:{color};width:{pct}%;height:8px;border-radius:6px;"></div>
    </div>
    """


def pct_change(old, new):
    if old is None or new is None or old == 0:
        return None
    return round((new - old) / old * 100, 1)


# --------------------------------------------------------------------------------------
# SIDEBAR — FILTERS
# --------------------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 📊 Impact Assessment")
    st.caption("DOST SETUP 4.0 iFund Program · Region VI")
    st.markdown("---")

    project_name = st.selectbox("Project / MSME", list(DATA.keys()))
    project = DATA[project_name]

    eval_cycle = st.selectbox(
        "Evaluation cycle (semestral)",
        project["semestral_cycles"],
        index=project["semestral_cycles"].index(project["current_semestral_cycle"]),
    )

    status_filter = st.multiselect(
        "Status filter",
        ["Accomplished", "Partially accomplished", "Not accomplished"],
        default=["Accomplished", "Partially accomplished", "Not accomplished"],
    )

    st.markdown("---")
    data_mode = st.radio("Data source", ["Demo data", "Live (Supabase)"], index=0,
                          help="Add SUPABASE_URL / SUPABASE_KEY to .streamlit/secrets.toml to enable live data.")
    if data_mode == "Live (Supabase)":
        if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
            st.warning("No Supabase credentials found in secrets.toml — showing demo data instead.")
        else:
            st.info("Live data wiring goes here — connect your Supabase client and replace `DATA`.")

    st.markdown("---")
    st.caption(f"Last refreshed: {datetime.now().strftime('%b %d, %Y %I:%M %p')}")


# --------------------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------------------

st.markdown("## Impact Assessment")
st.caption(project["program"])

col_a, col_b = st.columns([3, 1])
with col_a:
    st.markdown(
        f'<div class="card"><span class="obj-card-sub">General Objective</span>'
        f'<div style="margin-top:6px;">{project["general_objective"]}</div></div>',
        unsafe_allow_html=True,
    )
with col_b:
    st.markdown(
        f'<div style="text-align:right;padding-top:8px;">'
        f'<span class="badge" style="background:#dbeafe;color:#1d4ed8;">{eval_cycle}</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")


# --------------------------------------------------------------------------------------
# TOP — QUANTITATIVE EXPECTED OUTPUTS
# --------------------------------------------------------------------------------------

st.markdown('<div class="section-header">Quantitative Expected Outputs</div>', unsafe_allow_html=True)

outputs = project["quantifiable_outputs"]
filtered_outputs = [o for o in outputs if o["status"] in status_filter]

total = len(outputs)
n_acc = sum(1 for o in outputs if o["status"] == "Accomplished")
n_partial = sum(1 for o in outputs if o["status"] == "Partially accomplished")
n_not = sum(1 for o in outputs if o["status"] == "Not accomplished")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total outputs", total, help="Quantifiable outputs tracked this cycle")
k2.metric("Accomplished", n_acc, f"{n_acc/total*100:.0f}% of outputs" if total else "—")
k3.metric("Partially accomplished", n_partial, f"{n_partial/total*100:.0f}% of outputs" if total else "—")
k4.metric("Not accomplished", n_not, f"{n_not/total*100:.0f}% of outputs" if total else "—")

st.write("")

# Target vs Actual grouped bar chart (normalized to % of target so mixed units are comparable)
if filtered_outputs:
    labels, pct_actual = [], []
    for o in filtered_outputs:
        labels.append(o["name"] if len(o["name"]) < 42 else o["name"][:39] + "…")
        pct_actual.append(min(150, (o["actual"] / o["target"] * 100) if o["target"] else 0))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels, x=[100] * len(labels), orientation="h",
        marker=dict(color="rgba(148,163,184,0.35)"), name="Target (100%)",
        hoverinfo="skip",
    ))
    bar_colors = [STATUS_COLORS[o["status"]] for o in filtered_outputs]
    fig.add_trace(go.Bar(
        y=labels, x=pct_actual, orientation="h",
        marker=dict(color=bar_colors), name="Actual (% of target)",
        text=[f"{v:.0f}%" for v in pct_actual], textposition="outside",
    ))
    fig.update_layout(
        barmode="overlay", height=90 + 42 * len(labels),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="% of target achieved", showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No outputs match the current status filter.")

st.write("")

# Detail cards, two per row
for i in range(0, len(filtered_outputs), 2):
    cols = st.columns(2)
    for col, o in zip(cols, filtered_outputs[i:i + 2]):
        pct = min(100, round(o["actual"] / o["target"] * 100)) if o["target"] else 0
        with col:
            st.markdown(
                f"""
                <div class="card" style="border-left:4px solid {STATUS_COLORS[o['status']]};">
                    <span class="obj-card-sub">Quantifiable</span>
                    <div class="obj-card-title">{o['name']}</div>
                    <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#374151;">
                        <span>Target</span><span>{fmt_value(o['target'], o['unit'])}</span>
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#374151;">
                        <span>Actual</span><span>{fmt_value(o['actual'], o['unit'])}</span>
                    </div>
                    {progress_bar_html(pct, o['status'])}
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        {badge_html(o['status'])}
                        <span style="font-size:0.78rem;color:#6b7280;">{pct}% of target</span>
                    </div>
                    <div class="note-text">{o['note']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# Non-quantifiable outputs
if project.get("non_quantifiable"):
    st.markdown('<div class="section-header">Non-Quantifiable Outputs</div>', unsafe_allow_html=True)
    nq_filtered = [n for n in project["non_quantifiable"] if n["status"] in status_filter]
    if nq_filtered:
        cols = st.columns(2)
        for idx, n in enumerate(nq_filtered):
            with cols[idx % 2]:
                st.markdown(
                    f"""
                    <div class="card" style="border-left:4px solid {STATUS_COLORS[n['status']]};">
                        <span class="obj-card-sub">Non-Quantifiable</span>
                        <div class="obj-card-title">{n['name']}</div>
                        <div class="note-text"><b>Actual accomplishment:</b> {n['note']}</div>
                        <div style="margin-top:8px;">{badge_html(n['status'])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No non-quantifiable outputs match the current status filter.")

st.markdown("---")


# --------------------------------------------------------------------------------------
# MIDDLE — SPECIFIC OBJECTIVES FROM PP (COMPARATIVE)
# --------------------------------------------------------------------------------------

st.markdown('<div class="section-header">Specific Objectives — Pre-PIS vs Semestral vs Annual PIS</div>',
            unsafe_allow_html=True)

objs = [o for o in project["specific_objectives"]
        if o["semestral"]["status"] in status_filter or o["annual"]["status"] in status_filter]

if objs:
    rows = []
    for o in objs:
        rows.append({
            "#": o["id"],
            "Specific Objective": o["text"],
            "Pre-PIS Target": o["pre_pis_target"],
            "Semestral Status": f"{STATUS_ICON[o['semestral']['status']]} {o['semestral']['status']} ({o['semestral']['progress']}%)",
            "Annual PIS Status": f"{STATUS_ICON[o['annual']['status']]} {o['annual']['status']} ({o['annual']['progress']}%)",
        })
    df_obj = pd.DataFrame(rows)

    def highlight_status(val):
        for status, color in STATUS_COLORS.items():
            if status in val:
                bg = STATUS_BG[status]
                return f"background-color:{bg};color:{color};font-weight:600;"
        return ""

    styled = df_obj.style.applymap(highlight_status, subset=["Semestral Status", "Annual PIS Status"])
    st.dataframe(styled, use_container_width=True, hide_index=True,
                 column_config={"#": st.column_config.NumberColumn(width="small")})
else:
    st.info("No objectives match the current status filter.")

st.markdown("---")


# --------------------------------------------------------------------------------------
# BOTTOM — PROGRESS CHECK / PIS MODULE PROGRESSION
# --------------------------------------------------------------------------------------

st.markdown('<div class="section-header">Progress Check — PIS Module Progression</div>', unsafe_allow_html=True)

periods = project["periods"]
financials = project["financials"]

view_mode = st.radio("View", ["Pairwise (Year-over-Year)", "Longitudinal (full trajectory)"],
                      horizontal=True, label_visibility="collapsed")

metric_options = list(financials.keys())

if view_mode == "Pairwise (Year-over-Year)":
    pair_labels = [
        ("Year 1", "Pre-PIS", "PIS 1 (Year 1)"),
        ("Year 2", "PIS 1 (Year 1)", "PIS 2 (Year 2)"),
        ("Year 3", "PIS 2 (Year 2)", "PIS 3 (Year 3)"),
    ]
    year_choice = st.selectbox("Comparison pair", [p[0] for p in pair_labels])
    _, base_period, comp_period = next(p for p in pair_labels if p[0] == year_choice)

    metric_cols = st.columns(len(metric_options))
    for col, metric in zip(metric_cols, metric_options):
        base_val = financials[metric].get(base_period)
        comp_val = financials[metric].get(comp_period)
        change = pct_change(base_val, comp_val)
        display_val = peso(comp_val) if metric != "Employment" else (f"{comp_val:,.0f}" if comp_val is not None else "—")
        delta = f"{change:+.1f}%" if change is not None else "not yet reported"
        col.metric(metric, display_val, delta)

    fig2 = go.Figure()
    for metric in metric_options:
        b = financials[metric].get(base_period)
        c = financials[metric].get(comp_period)
        if b is None and c is None:
            continue
        fig2.add_trace(go.Bar(name=metric, x=[base_period, comp_period], y=[b or 0, c or 0]))
    fig2.update_layout(
        barmode="group", height=380, margin=dict(l=10, r=10, t=30, b=10),
        title=f"{base_period} vs {comp_period}", plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig2, use_container_width=True)

else:
    metric_choice = st.selectbox("Metric", metric_options)
    series = financials[metric_choice]
    xs = [p for p in periods if series.get(p) is not None]
    ys = [series[p] for p in xs]

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=periods, y=[series.get(p) for p in periods],
        mode="lines+markers", connectgaps=True,
        line=dict(color="#2563eb", width=3), marker=dict(size=9),
        name=metric_choice,
    ))
    fig3.update_layout(
        height=380, margin=dict(l=10, r=10, t=30, b=10),
        title=f"{metric_choice} — full trajectory (Pre-PIS → PIS 3)",
        plot_bgcolor="white", yaxis_title=metric_choice,
    )
    st.plotly_chart(fig3, use_container_width=True)

    if len(xs) >= 2:
        overall_change = pct_change(ys[0], ys[-1])
        st.caption(f"Change from {xs[0]} to {xs[-1]}: "
                   f"{'+' if overall_change and overall_change > 0 else ''}{overall_change}%"
                   if overall_change is not None else "Insufficient data to compute overall change.")

# Asset breakdown table (kept from original design, tied to selected project)
with st.expander("Asset breakdown (Pre-PIS vs Current)"):
    ab = project["asset_breakdown"]
    df_assets = pd.DataFrame({
        "Metric": ab["metric"],
        "Pre-PIS": [peso(v) for v in ab["pre_pis"]],
        "Current": [peso(v) for v in ab["current"]],
        "Chg": [f"{pct_change(a, b):+.0f}%" if pct_change(a, b) is not None else "+0%"
                for a, b in zip(ab["pre_pis"], ab["current"])],
    })
    total_row = pd.DataFrame([{
        "Metric": "Total",
        "Pre-PIS": peso(sum(ab["pre_pis"])),
        "Current": peso(sum(ab["current"])),
        "Chg": f"{pct_change(sum(ab['pre_pis']), sum(ab['current'])):+.0f}%",
    }])
    st.dataframe(pd.concat([df_assets, total_row], ignore_index=True), hide_index=True, use_container_width=True)

st.markdown("---")


# --------------------------------------------------------------------------------------
# EVALUATION / FEEDBACK FORM
# --------------------------------------------------------------------------------------

st.markdown('<div class="section-header">Reviewer Evaluation & Feedback</div>', unsafe_allow_html=True)

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

with st.form("evaluation_form", clear_on_submit=True):
    fc1, fc2 = st.columns(2)
    with fc1:
        reviewer = st.text_input("Reviewer name")
        criteria_relevance = st.slider("Relevance", 1, 5, 3)
        criteria_effectiveness = st.slider("Effectiveness", 1, 5, 3)
    with fc2:
        overall_rating = st.select_slider(
            "Overall verdict",
            options=["Not accomplished", "Partially accomplished", "Accomplished"],
            value="Partially accomplished",
        )
        criteria_efficiency = st.slider("Efficiency", 1, 5, 3)
        criteria_sustainability = st.slider("Sustainability", 1, 5, 3)

    comment = st.text_area("Qualitative impact comments",
                            placeholder="Observations, risks, or recommendations for this project and cycle…")
    submitted = st.form_submit_button("Submit evaluation", use_container_width=True)

    if submitted:
        if not reviewer.strip():
            st.error("Please enter a reviewer name before submitting.")
        else:
            st.session_state.feedback_log.append({
                "Submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Project": project_name,
                "Cycle": eval_cycle,
                "Reviewer": reviewer,
                "Relevance": criteria_relevance,
                "Effectiveness": criteria_effectiveness,
                "Efficiency": criteria_efficiency,
                "Sustainability": criteria_sustainability,
                "Avg Score": round((criteria_relevance + criteria_effectiveness +
                                     criteria_efficiency + criteria_sustainability) / 4, 1),
                "Verdict": overall_rating,
                "Comments": comment,
            })
            st.success("Evaluation recorded for this session.")

if st.session_state.feedback_log:
    st.markdown("##### Submitted evaluations (this session)")
    st.dataframe(pd.DataFrame(st.session_state.feedback_log), hide_index=True, use_container_width=True)
else:
    st.caption("No evaluations submitted yet this session.")

st.markdown("---")
st.caption("DOST-VI SETUP 4.0 iFund Program · Region VI")
