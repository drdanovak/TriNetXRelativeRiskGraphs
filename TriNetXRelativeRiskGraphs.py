
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from matplotlib.ticker import AutoMinorLocator

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

st.set_page_config(page_title="2-Cohort Outcome Bar Chart", layout="centered", initial_sidebar_state="expanded")

st.title("Two-Cohort Outcome Bar Chart")
st.markdown("""
Enter each outcome and the risk percentage for both cohorts.  
Each outcome will appear with Cohort 1 on top and Cohort 2 below (or side-by-side vertically).
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
        "Outcome Name": ["Diabetes", "Anemia", "Cancer"],
        "Cohort 1 Risk (%)": [11.2, 13.5, 9.7],
        "Cohort 2 Risk (%)": [8.9, 15.2, 10.1]
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

df = st.session_state.data.copy()

st.sidebar.header("Chart Appearance")
orientation = st.sidebar.radio("Bar Orientation", ["Vertical", "Horizontal"], index=1)
font_family = st.sidebar.selectbox("Font Family", ["DejaVu Sans", "Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana"], index=0)
font_size = st.sidebar.slider("Font Size", 8, 32, 14)
tick_fontsize = st.sidebar.slider("Tick Mark Font Size", 6, 28, 11)
major_tick_length = st.sidebar.slider("Major Tick Length", 2, 15, 8)
minor_ticks = st.sidebar.checkbox("Show Minor Ticks", value=True)
bar_width = st.sidebar.slider("Bar Width", 0.1, 0.6, 0.26)
gridlines = st.sidebar.checkbox("Show gridlines", value=True)
show_legend = st.sidebar.checkbox("Show legend", value=True)
show_values = st.sidebar.checkbox("Show values on bars", value=True)

def plot_interleaved_chart(df):
    outcomes = df["Outcome Name"].tolist()
    cohort1_vals = df[f"{cohort1_name} Risk (%)"].tolist()
    cohort2_vals = df[f"{cohort2_name} Risk (%)"].tolist()

    if orientation == "Horizontal":
        y_labels, all_vals, bar_colors = [], [], []
        for outcome, v1, v2 in zip(outcomes, cohort1_vals, cohort2_vals):
            y_labels.extend([f"{outcome} ({cohort1_name})", f"{outcome} ({cohort2_name})"])
            all_vals.extend([v1, v2])
            bar_colors.extend([color1, color2])

        y_pos = np.arange(len(y_labels))
        fig, ax = plt.subplots(figsize=(max(7, 1.2 * len(outcomes)), 0.45 * len(y_labels) + 2.5))
        bars = ax.barh(y_pos, all_vals, color=bar_colors, height=bar_width, zorder=3)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(y_labels, fontsize=font_size, fontweight="bold", fontname=font_family)
        ax.set_xlabel("Risk (%)", fontsize=font_size + 3, fontweight="bold", fontname=font_family)
        ax.set_ylabel("Outcome + Cohort", fontsize=font_size + 2, fontname=font_family)
        xlims = ax.get_xlim()
        ax.set_xlim([0, max(xlims[1], max(all_vals) * 1.12 + 1)])

        if show_values:
            for rect, val in zip(bars, all_vals):
                if val > 0:
                    ax.text(val + (xlims[1]*0.012), rect.get_y() + rect.get_height()/2.,
                            f'{val:.2f}%', va='center', ha='left', fontsize=font_size-1, fontweight="medium", fontname=font_family)

    else:  # Vertical
        x_labels, all_vals, bar_colors = [], [], []
        for outcome, v1, v2 in zip(outcomes, cohort1_vals, cohort2_vals):
            x_labels.extend([f"{outcome} ({cohort1_name})", f"{outcome} ({cohort2_name})"])
            all_vals.extend([v1, v2])
            bar_colors.extend([color1, color2])

        x_pos = np.arange(len(x_labels))
        fig, ax = plt.subplots(figsize=(max(7, 0.7 * len(x_labels) + 2), 5.5))
        bars = ax.bar(x_pos, all_vals, color=bar_colors, width=bar_width, zorder=3)

        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels, fontsize=font_size, fontweight="bold", rotation=45, ha='right', fontname=font_family)
        ax.set_ylabel("Risk (%)", fontsize=font_size + 3, fontweight="bold", fontname=font_family)
        ax.set_xlabel("Outcome + Cohort", fontsize=font_size + 2, fontname=font_family)
        ylims = ax.get_ylim()
        ax.set_ylim([0, max(ylims[1], max(all_vals) * 1.12 + 1)])

        if show_values:
            for rect, val in zip(bars, all_vals):
                if val > 0:
                    ax.text(rect.get_x() + rect.get_width()/2., val + (ylims[1]*0.01),
                            f'{val:.2f}%', ha='center', va='bottom', fontsize=font_size-1, fontweight="medium", fontname=font_family)

    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    if show_legend:
        custom_legend = [
            plt.Line2D([0], [0], color=color1, lw=6, label=cohort1_name),
            plt.Line2D([0], [0], color=color2, lw=6, label=cohort2_name),
        ]
        ax.legend(handles=custom_legend, fontsize=font_size+1, frameon=False,
                  loc="upper left", bbox_to_anchor=(1.01, 1.01), borderaxespad=0)

    if gridlines:
        (ax.xaxis if orientation == "Vertical" else ax.yaxis).grid(True, color="#DDDDDD", zorder=0)

    ax.xaxis.set_tick_params(labelsize=tick_fontsize, length=major_tick_length)
    ax.yaxis.set_tick_params(labelsize=tick_fontsize, length=major_tick_length)

    if minor_ticks:
        if orientation == "Vertical":
            ax.yaxis.set_minor_locator(AutoMinorLocator())
            ax.yaxis.set_tick_params(which='minor', length=int(major_tick_length*0.7), width=0.8)
        else:
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.xaxis.set_tick_params(which='minor', length=int(major_tick_length*0.7), width=0.8)

    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    plt.tight_layout(rect=[0, 0, 0.89 if show_legend else 1, 1])
    return fig

fig = plot_interleaved_chart(df)
st.pyplot(fig)

buf = BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
st.download_button("📥 Download Chart as PNG", data=buf.getvalue(), file_name="2Cohort_Outcome_Bargraph.png", mime="image/png")
