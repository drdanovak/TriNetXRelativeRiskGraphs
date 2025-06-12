import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

st.set_page_config(page_title="2-Cohort Outcome Bar Chart", layout="centered")

st.title("Two-Cohort Outcome Bar Chart")
st.markdown("""
Enter each outcome and the risk percentage for both cohorts.  
Adjust the space between outcome groups and between each pair of bars!
""")

# Sidebar: cohort and chart controls
st.sidebar.header("Cohort Settings")
cohort1_name = st.sidebar.text_input("Cohort 1 Name", "Cohort 1")
cohort2_name = st.sidebar.text_input("Cohort 2 Name", "Cohort 2")
cohort1_color = st.sidebar.color_picker(f"Color for {cohort1_name}", "#8e44ad")
cohort2_color = st.sidebar.color_picker(f"Color for {cohort2_name}", "#27ae60")

def initialize_data():
    return pd.DataFrame({
        "Outcome Name": ["Diabetes", "Anemia", "Cancer"],
        "Cohort 1 Risk (%)": [11.2, 13.5, 9.7],
        "Cohort 2 Risk (%)": [8.9, 15.2, 10.1]
    })

if "data" not in st.session_state:
    st.session_state.data = initialize_data()

df = st.session_state.data.copy()

# Only rename columns if there are exactly three columns (robust to accidental changes)
expected_cols = ["Outcome Name", f"{cohort1_name} Risk (%)", f"{cohort2_name} Risk (%)"]
if list(df.columns) != expected_cols:
    if len(df.columns) == 3:
        df.columns = expected_cols
    else:
        # Reset to a blank template to fix any accidental column additions/deletions
        df = pd.DataFrame({
            "Outcome Name": [],
            f"{cohort1_name} Risk (%)": [],
            f"{cohort2_name} Risk (%)": []
        })

# Editable data table
df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Outcome Name": st.column_config.TextColumn("Outcome Name"),
        f"{cohort1_name} Risk (%)": st.column_config.NumberColumn(f"{cohort1_name} Risk (%)", min_value=0.0, max_value=100.0, step=0.01),
        f"{cohort2_name} Risk (%)": st.column_config.NumberColumn(f"{cohort2_name} Risk (%)", min_value=0.0, max_value=100.0, step=0.01),
    },
    key="data_editor"
)
st.session_state.data = df

st.sidebar.header("Chart Appearance")
orientation = st.sidebar.radio("Bar Orientation", ["Vertical", "Horizontal"], index=1)
font_size = st.sidebar.slider("Font Size", 8, 28, 14)
bar_width = st.sidebar.slider("Bar Width", 0.15, 0.45, 0.28)
group_gap = st.sidebar.slider("Distance Between Bar Groups", 1.0, 4.0, 2.0, step=0.05)
pair_gap = st.sidebar.slider("Spacing Between Cohort Bars in a Group", 0.10, 1.0, 0.40, step=0.01)
gridlines = st.sidebar.checkbox("Show gridlines", value=True)
show_legend = st.sidebar.checkbox("Show legend", value=True)
show_values = st.sidebar.checkbox("Show values on bars", value=True)

st.subheader("Bar Chart")

def plot_2cohort_outcomes(
    df, cohort1, cohort2, color1, color2, orientation, font_size, bar_width, gridlines,
    show_values, show_legend, group_gap, pair_gap
):
    if len(df) == 0:
        fig, ax = plt.subplots()
        ax.set_title("No data to plot.")
        return fig

    outcomes = df["Outcome Name"].tolist()
    cohort1_vals = df[f"{cohort1} Risk (%)"].tolist()
    cohort2_vals = df[f"{cohort2} Risk (%)"].tolist()
    n = len(outcomes)
    
    # The center of each outcome group
    group_centers = np.arange(n) * group_gap
    # Offset for the bar pairs in each group
    pair_offset = pair_gap / 2

    fig, ax = plt.subplots(figsize=(max(6, 1.1 * n * group_gap), 5))
    if orientation == "Vertical":
        bars1 = ax.bar(group_centers - pair_offset, cohort1_vals, bar_width, label=cohort1, color=color1, edgecolor="#444")
        bars2 = ax.bar(group_centers + pair_offset, cohort2_vals, bar_width, label=cohort2, color=color2, edgecolor="#444")
        ax.set_xticks(group_centers)
        ax.set_xticklabels(outcomes, fontsize=font_size, rotation=20, ha='right')
        ax.set_ylabel("Risk (%)", fontsize=font_size + 2)
        ax.set_xlabel("Outcome", fontsize=font_size + 2)
        if show_values:
            for rect in bars1:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., height, f'{height:.2f}%', ha='center', va='bottom', fontsize=font_size)
            for rect in bars2:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., height, f'{height:.2f}%', ha='center', va='bottom', fontsize=font_size)
        if show_legend:
            ax.legend(fontsize=font_size, bbox_to_anchor=(1.04, 1), loc="upper left", borderaxespad=0)
        ax.grid(gridlines, axis='y', linestyle='--', alpha=0.4)
    else:
        bars1 = ax.barh(group_centers - pair_offset, cohort1_vals, bar_width, label=cohort1, color=color1, edgecolor="#444")
        bars2 = ax.barh(group_centers + pair_offset, cohort2_vals, bar_width, label=cohort2, color=color2, edgecolor="#444")
        ax.set_yticks(group_centers)
        ax.set_yticklabels(outcomes, fontsize=font_size)
        ax.set_xlabel("Risk (%)", fontsize=font_size + 2)
        ax.set_ylabel("Outcome", fontsize=font_size + 2)
        if show_values:
            for rect in bars1:
                width_val = rect.get_width()
                ax.text(width_val, rect.get_y() + rect.get_height()/2., f'{width_val:.2f}%', va='center', ha='left', fontsize=font_size)
            for rect in bars2:
                width_val = rect.get_width()
                ax.text(width_val, rect.get_y() + rect.get_height()/2., f'{width_val:.2f}%', va='center', ha='left', fontsize=font_size)
        if show_legend:
            ax.legend(fontsize=font_size, bbox_to_anchor=(1.04, 1), loc="upper left", borderaxespad=0)
        ax.grid(gridlines, axis='x', linestyle='--', alpha=0.4)

    plt.tight_layout(rect=[0, 0, 0.88, 1]) if show_legend else plt.tight_layout()
    plt.box(False)
    ax.spines[['top', 'right']].set_visible(False)
    return fig

fig = plot_2cohort_outcomes(
    df,
    cohort1=cohort1_name,
    cohort2=cohort2_name,
    color1=cohort1_color,
    color2=cohort2_color,
    orientation=orientation,
    font_size=font_size,
    bar_width=bar_width,
    gridlines=gridlines,
    show_values=show_values,
    show_legend=show_legend,
    group_gap=group_gap,
    pair_gap=pair_gap
)

st.pyplot(fig)

buf = BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
st.download_button(
    "📥 Download Chart as PNG",
    data=buf.getvalue(),
    file_name="2Cohort_Bargraph.png",
    mime="image/png"
)
