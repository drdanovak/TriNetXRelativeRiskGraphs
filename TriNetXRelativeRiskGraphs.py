import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO

st.set_page_config(page_title="TriNetX 2-Cohort Grouped Bar Chart", layout="centered")

st.title("TriNetX 2-Cohort Grouped Bar Chart")
st.markdown("""
- Enter as many outcomes as you like (e.g. diabetes, anemia, cancer).
- Enter values for each cohort for every outcome.
- The chart will show side-by-side bars for each outcome.
""")

# Sidebar: set cohort names/colors
st.sidebar.header("Cohort Settings")
cohort1_name = st.sidebar.text_input("Cohort 1 Name", "Cohort 1")
cohort2_name = st.sidebar.text_input("Cohort 2 Name", "Cohort 2")
cohort1_color = st.sidebar.color_picker(f"Color for {cohort1_name}", "#8e44ad")
cohort2_color = st.sidebar.color_picker(f"Color for {cohort2_name}", "#27ae60")

# Data entry table
def initialize_data():
    df = pd.DataFrame({
        "Outcome": ["Diabetes", "Anemia", "Cancer"],
        cohort1_name: [1.1, 1.3, 1.2],
        cohort2_name: [0.9, 1.4, 1.1]
    })
    return df

if "data" not in st.session_state:
    st.session_state.data = initialize_data()

# Update columns if cohort names changed
df = st.session_state.data
if list(df.columns)[1] != cohort1_name or list(df.columns)[2] != cohort2_name:
    df = df.rename(columns={df.columns[1]: cohort1_name, df.columns[2]: cohort2_name})

df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Outcome": st.column_config.TextColumn("Outcome Name"),
        cohort1_name: st.column_config.NumberColumn(cohort1_name, min_value=0.0, step=0.01),
        cohort2_name: st.column_config.NumberColumn(cohort2_name, min_value=0.0, step=0.01),
    },
    key="data_editor"
)
st.session_state.data = df

st.sidebar.header("Chart Appearance")
orientation = st.sidebar.radio("Bar Orientation", ["Vertical", "Horizontal"], index=0)
font_size = st.sidebar.slider("Font Size", 8, 28, 14)
font_family = st.sidebar.selectbox("Font Family", ["DejaVu Sans", "Arial", "Helvetica", "Times New Roman", "Courier New"])
bar_width = st.sidebar.slider("Bar Group Width", 0.3, 0.9, 0.6)
gridlines = st.sidebar.checkbox("Show gridlines", value=True)
show_values = st.sidebar.checkbox("Show values on bars", value=True)
grayscale = st.sidebar.checkbox("Grayscale (ignore color pickers)", value=False)
x_label = st.sidebar.text_input("X-axis Label", "Outcome")
y_label = st.sidebar.text_input("Y-axis Label", "Relative Risk")
axis_label_weight = st.sidebar.selectbox("Axis Label Weight", ["normal", "bold", "heavy"], index=1)

st.subheader("Bar Chart")

def plot_grouped_bar_chart(df, cohort1, cohort2, color1, color2, orientation, font_size, font_family, bar_width, gridlines, grayscale, x_label, y_label, show_values, axis_label_weight):
    outcomes = df["Outcome"].tolist()
    cohort1_vals = df[cohort1].tolist()
    cohort2_vals = df[cohort2].tolist()
    n = len(outcomes)
    ind = np.arange(n)
    width = bar_width / 2

    fig, ax = plt.subplots(figsize=(max(6, 1.5 * n), 5))
    colors = ["#888888", "#BBBBBB"] if grayscale else [color1, color2]

    if orientation == "Vertical":
        bars1 = ax.bar(ind - width/2, cohort1_vals, width, label=cohort1, color=colors[0], edgecolor="#444")
        bars2 = ax.bar(ind + width/2, cohort2_vals, width, label=cohort2, color=colors[1], edgecolor="#444")
        ax.set_xticks(ind)
        ax.set_xticklabels(outcomes, fontsize=font_size, fontname=font_family, rotation=20, ha='right')
        ax.set_xlabel(x_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
        ax.set_ylabel(y_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
        if show_values:
            for rect in bars1:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., height, f'{height:.2f}', ha='center', va='bottom', fontsize=font_size)
            for rect in bars2:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., height, f'{height:.2f}', ha='center', va='bottom', fontsize=font_size)
        ax.legend(fontsize=font_size)
        ax.grid(gridlines, axis='y', linestyle='--', alpha=0.4)
    else:
        bars1 = ax.barh(ind - width/2, cohort1_vals, width, label=cohort1, color=colors[0], edgecolor="#444")
        bars2 = ax.barh(ind + width/2, cohort2_vals, width, label=cohort2, color=colors[1], edgecolor="#444")
        ax.set_yticks(ind)
        ax.set_yticklabels(outcomes, fontsize=font_size, fontname=font_family)
        ax.set_ylabel(x_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
        ax.set_xlabel(y_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
        if show_values:
            for rect in bars1:
                width_val = rect.get_width()
                ax.text(width_val, rect.get_y() + rect.get_height()/2., f'{width_val:.2f}', va='center', ha='left', fontsize=font_size)
            for rect in bars2:
                width_val = rect.get_width()
                ax.text(width_val, rect.get_y() + rect.get_height()/2., f'{width_val:.2f}', va='center', ha='left', fontsize=font_size)
        ax.legend(fontsize=font_size)
        ax.grid(gridlines, axis='x', linestyle='--', alpha=0.4)

    plt.tight_layout()
    plt.box(False)
    ax.spines[['top', 'right']].set_visible(False)
    return fig

fig = plot_grouped_bar_chart(
    df,
    cohort1=cohort1_name,
    cohort2=cohort2_name,
    color1=cohort1_color,
    color2=cohort2_color,
    orientation=orientation,
    font_size=font_size,
    font_family=font_family,
    bar_width=bar_width,
    gridlines=gridlines,
    grayscale=grayscale,
    x_label=x_label,
    y_label=y_label,
    show_values=show_values,
    axis_label_weight=axis_label_weight
)

st.pyplot(fig)

buf = BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
st.download_button(
    "📥 Download Chart as PNG",
    data=buf.getvalue(),
    file_name="TriNetX_2Cohort_Bargraph.png",
    mime="image/png"
)
