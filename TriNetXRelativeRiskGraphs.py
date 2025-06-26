
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from matplotlib.ticker import AutoMinorLocator

# ---------- COLOR PALETTES ----------
PALETTES = {
    "Classic TriNetX": ["#8e44ad", "#27ae60"],
    "University of California": ["#1295D8", "#FFB511"],
    "Colorblind-safe": ["#0072B2", "#D55E00"],
    "Tol (bright)": ["#4477AA", "#EE6677"],
    "Blue-Green": ["#1B9E77", "#7570B3"],
    "Red-Green": ["#D7263D", "#21A179"],
    "High-Contrast": ["#000000", "#E69F00"],
    "Grayscale": ["#888888", "#BBBBBB"],
}

st.set_page_config(page_title="2-Cohort Outcome Bar Chart", layout="centered")

st.title("Two-Cohort Outcome Bar Chart with Groupings")
st.markdown("""
Enter each outcome and the risk percentage for both cohorts.  
Use rows beginning with "##" to define group headings (e.g., "##Cardiac").  
These will be used to visually group outcomes in the chart.
""")

st.sidebar.header("Graph Settings")
cohort1_name = st.sidebar.text_input("Cohort 1 Name", "Cohort 1")
cohort2_name = st.sidebar.text_input("Cohort 2 Name", "Cohort 2")

palette_name = st.sidebar.selectbox("Color Palette", list(PALETTES.keys()), index=1)
color1, color2 = PALETTES[palette_name]
color1 = st.sidebar.color_picker(f"Bar Color for {cohort1_name}", color1)
color2 = st.sidebar.color_picker(f"Bar Color for {cohort2_name}", color2)

def initialize_data():
    return pd.DataFrame({
        "Outcome Name": ["##Cancers", "Breast Cancer", "Colon Cancer", "##Cardiac", "Heart Failure", "MI"],
        f"{cohort1_name} Risk (%)": [None, 12.1, 9.4, None, 15.3, 11.2],
        f"{cohort2_name} Risk (%)": [None, 10.8, 8.7, None, 14.9, 10.5]
    })

if "data" not in st.session_state:
    st.session_state.data = initialize_data()

edited_df = st.data_editor(
    st.session_state.data,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Outcome Name": st.column_config.TextColumn("Outcome Name"),
        f"{cohort1_name} Risk (%)": st.column_config.NumberColumn(f"{cohort1_name} Risk (%)", min_value=0.0, max_value=100.0, step=0.01),
        f"{cohort2_name} Risk (%)": st.column_config.NumberColumn(f"{cohort2_name} Risk (%)", min_value=0.0, max_value=100.0, step=0.01),
    },
    key="data_editor"
)

if not edited_df.equals(st.session_state.data):
    st.session_state.data = edited_df.copy()

# Extract groupings
raw_df = st.session_state.data.copy()
grouped_data = []
current_group = None

for _, row in raw_df.iterrows():
    outcome = row["Outcome Name"]
    if isinstance(outcome, str) and outcome.startswith("##"):
        current_group = outcome.lstrip("#").strip()
    elif isinstance(outcome, str):
        grouped_data.append({
            "Group": current_group,
            "Outcome Name": outcome,
            f"{cohort1_name} Risk (%)": row[f"{cohort1_name} Risk (%)"],
            f"{cohort2_name} Risk (%)": row[f"{cohort2_name} Risk (%)"]
        })

df = pd.DataFrame(grouped_data)

# Sidebar chart appearance
st.sidebar.header("Chart Appearance")
orientation = st.sidebar.radio("Bar Orientation", ["Vertical", "Horizontal"], index=1)
font_family = st.sidebar.selectbox("Font Family", ["DejaVu Sans", "Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana"], index=0)
font_size = st.sidebar.slider("Font Size", 8, 32, 14)
tick_fontsize = st.sidebar.slider("Tick Mark Font Size", 6, 28, 11)
major_tick_length = st.sidebar.slider("Major Tick Length", 2, 15, 8)
minor_ticks = st.sidebar.checkbox("Show Minor Ticks", value=True)
bar_width = st.sidebar.slider("Bar Width", 0.1, 0.6, 0.26)
group_gap = st.sidebar.slider("Distance Between Bar Groups", 1.0, 5.0, 2.3, step=0.05)
pair_gap = st.sidebar.slider("Spacing Between Cohort Bars in a Group", 0.05, 1.2, 0.32, step=0.01)
gridlines = st.sidebar.checkbox("Show gridlines", value=True)
show_legend = st.sidebar.checkbox("Show legend", value=True)
show_values = st.sidebar.checkbox("Show values on bars", value=True)

def plot_grouped_chart(df):
    if df.empty:
        fig, ax = plt.subplots()
        ax.set_title("No data to plot.")
        return fig

    outcomes = df["Outcome Name"].tolist()
    cohort1_vals = df[f"{cohort1_name} Risk (%)"].tolist()
    cohort2_vals = df[f"{cohort2_name} Risk (%)"].tolist()
    groups = df["Group"].tolist()

    n = len(outcomes)
    group_centers = np.arange(n) * group_gap
    pair_offset = pair_gap / 2

    fig, ax = plt.subplots(figsize=(max(7, 1.2 * n * group_gap), 5.2))
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    bars1 = ax.bar(
        group_centers - pair_offset, cohort1_vals, bar_width, label=cohort1_name, color=color1,
        linewidth=0, zorder=3
    )
    bars2 = ax.bar(
        group_centers + pair_offset, cohort2_vals, bar_width, label=cohort2_name, color=color2,
        linewidth=0, zorder=3
    )

    ax.set_xticks(group_centers)
    ax.set_xticklabels(outcomes, fontsize=font_size, fontweight="bold", rotation=15, ha='right', fontname=font_family)
    ax.set_ylabel("Risk (%)", fontsize=font_size + 3, fontweight="bold", fontname=font_family)
    ax.set_xlabel("Outcome", fontsize=font_size + 2, fontname=font_family)

    ylims = ax.get_ylim()
    ax.set_ylim([0, max(ylims[1], max(cohort1_vals + cohort2_vals) * 1.12 + 1)])

    if show_values:
        for rect in list(bars1) + list(bars2):
            height = rect.get_height()
            if height > 0:
                ax.text(rect.get_x() + rect.get_width()/2., height + (ylims[1]*0.01), f'{height:.2f}%',
                        ha='center', va='bottom', fontsize=font_size-1, fontweight="medium", fontname=font_family)

    if show_legend:
        ax.legend(fontsize=font_size+1, frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1.01), borderaxespad=0)

    if gridlines:
        ax.yaxis.grid(True, color="#DDDDDD", zorder=0)

    ax.xaxis.set_tick_params(labelsize=tick_fontsize, length=major_tick_length)
    ax.yaxis.set_tick_params(labelsize=tick_fontsize, length=major_tick_length)

    if minor_ticks:
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_tick_params(which='minor', length=int(major_tick_length*0.7), width=0.8)

    # Add group labels
    for i, group in enumerate(groups):
        if i == 0 or groups[i] != groups[i-1]:
            ax.text(group_centers[i], max(cohort1_vals + cohort2_vals) * 1.15,
                    group, fontsize=font_size + 1, ha="center", va="bottom", fontweight="bold", fontname=font_family)

    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout(rect=[0, 0, 0.89 if show_legend else 1, 1])
    return fig

fig = plot_grouped_chart(df)
st.pyplot(fig)

buf = BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
st.download_button("📥 Download Chart as PNG", data=buf.getvalue(), file_name="Grouped_2Cohort_Bargraph.png", mime="image/png")
