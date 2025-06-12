import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

st.set_page_config(page_title="2-Cohort Outcome Bar Chart", layout="centered")

st.title("Two-Cohort Outcome Bar Chart")
st.markdown("""
Enter each outcome, and the risk percentage for both cohorts.
""")

# Sidebar: set cohort names/colors
st.sidebar.header("Cohort Settings")
cohort1_name = st.sidebar.text_input("Cohort 1 Name", "Cohort 1")
cohort2_name = st.sidebar.text_input("Cohort 2 Name", "Cohort 2")
cohort1_color = st.sidebar.color_picker(f"Color for {cohort1_name}", "#8e44ad")
cohort2_color = st.sidebar.color_picker(f"Color for {cohort2_name}", "#27ae60")

# Table layout: Outcome Name | Cohort 1 Risk (%) | Cohort 2 Risk (%)
def initialize_data():
    return pd.DataFrame({
        "Outcome Name": ["Diabetes", "Anemia", "Cancer"],
        "Cohort 1 Risk (%)": [11.2, 13.5, 9.7],
        "Cohort 2 Risk (%)": [8.9, 15.2, 10.1]
    })

if "data" not in st.session_state:
    st.session_state.data = initialize_data()

# Adjust column names if user changes cohort names
df = st.session_state.data
new_columns = ["Outcome Name", f"{cohort1_name} Risk (%)", f"{cohort2_name} Risk (%)"]
if list(df.columns) != new_columns:
    df.columns = new_columns

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
orientation = st.sidebar.radio("Bar Orientation", ["Vertical", "Horizontal"], index=0)
font_size = st.sidebar.slider("Font Size", 8, 28, 14)
bar_width = st.sidebar.slider("Bar Group Width", 0.3, 0.9, 0.6)
gridlines = st.sidebar.checkbox("Show gridlines", value=True)
show_values = st.sidebar.checkbox("Show values on bars", value=True)

st.subheader("Bar Chart")

def plot_2cohort_outcomes(df, cohort1, cohort2, color1, color2, orientation, font_size, bar_width, gridlines, show_values):
    outcomes = df["Outcome Name"].tolist()
    cohort1_vals = df[f"{cohort1} Risk (%)"].tolist()
    cohort2_vals = df[f"{cohort2} Risk (%)"].tolist()
    n = len(outcomes)
    ind = np.arange(n)
    width = bar_width / 2

    fig, ax = plt.subplots(figsize=(max(6, 1.5 * n), 5))
    if orientation == "Vertical":
        bars1 = ax.bar(ind - width/2, cohort1_vals, width, label=cohort1, color=color1, edgecolor="#444")
        bars2 = ax.bar(ind + width/2, cohort2_vals, width, label=cohort2, color=color2, edgecolor="#444")
        ax.set_xticks(ind)
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
        ax.legend(fontsize=font_size)
        ax.grid(gridlines, axis='y', linestyle='--', alpha=0.4)
    else:
        bars1 = ax.barh(ind - width/2, cohort1_vals, width, label=cohort1, color=color1, edgecolor="#444")
        bars2 = ax.barh(ind + width/2, cohort2_vals, width, label=cohort2, color=color2, edgecolor="#444")
        ax.set_yticks(ind)
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
        ax.legend(fontsize=font_size)
        ax.grid(gridlines, axis='x', linestyle='--', alpha=0.4)

    plt.tight_layout()
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
    show_values=show_values
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
