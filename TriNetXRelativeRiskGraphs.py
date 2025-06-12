import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from io import BytesIO

st.set_page_config(page_title="TriNetX RR Bargraph Generator", layout="centered")

st.title("TriNetX Relative Risk Bargraph Generator")
st.markdown("""
This app helps you create publication-quality bargraphs of Relative Risks for your TriNetX cohorts.  
Enter your cohort names and RR values below, customize the look, and download as PNG!
""")

# --- Table Input Section ---
st.subheader("Step 1: Enter Cohort Data")

def initialize_data():
    return pd.DataFrame({
        'Cohort Name': ['Cohort A', 'Cohort B'],
        'Relative Risk': [1.25, 0.97]
    })

data = st.session_state.get("data", initialize_data())
edited_data = st.data_editor(
    data,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Cohort Name": st.column_config.TextColumn("Cohort Name"),
        "Relative Risk": st.column_config.NumberColumn("Relative Risk", min_value=0.01, step=0.01),
    },
    key="rr_table"
)
st.session_state.data = edited_data

# --- Chart Options ---
st.subheader("Step 2: Customize Chart Appearance")
with st.expander("🛠️ Appearance Options", expanded=True):

    col1, col2 = st.columns(2)
    with col1:
        orientation = st.radio("Bar Orientation", ["Horizontal", "Vertical"], index=0)
        font_size = st.slider("Font Size", 8, 28, 14)
        font_family = st.selectbox("Font Family", ["DejaVu Sans", "Arial", "Helvetica", "Times New Roman", "Courier New"])
        bar_width = st.slider("Bar/Value Spacing", 0.2, 0.9, 0.6)
        gridlines = st.checkbox("Show gridlines", value=True)
        grayscale = st.checkbox("Grayscale", value=False)
    with col2:
        color = st.color_picker("Bar Color", "#3498db")
        edge_color = st.color_picker("Bar Edge Color", "#333333")
        x_label = st.text_input("X-axis Label", "Cohort")
        y_label = st.text_input("Y-axis Label", "Relative Risk")
        show_values = st.checkbox("Show values on bars", value=True)
        axis_label_weight = st.selectbox("Axis Label Weight", ["normal", "bold", "heavy"], index=1)

# --- Draw Chart ---
st.subheader("Step 3: View & Download Your Bargraph")

def plot_bargraph(df, orientation, font_size, font_family, bar_width, color, edge_color, gridlines, grayscale,
                  x_label, y_label, show_values, axis_label_weight):
    fig, ax = plt.subplots(figsize=(8, 4.8))

    cohort_names = df['Cohort Name']
    rr_values = df['Relative Risk']
    indices = range(len(df))

    # Bar settings
    plot_color = "#888888" if grayscale else color
    edge_col = "#444444" if grayscale else edge_color

    if orientation == "Horizontal":
        bars = ax.barh(indices, rr_values, color=plot_color, edgecolor=edge_col, height=bar_width)
        ax.set_yticks(indices)
        ax.set_yticklabels(cohort_names, fontsize=font_size, fontname=font_family)
        ax.set_xlabel(y_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
        ax.set_ylabel(x_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
        if show_values:
            for i, v in enumerate(rr_values):
                ax.text(v, i, f" {v:.2f}", va='center', ha='left', fontsize=font_size, fontname=font_family)
    else:
        bars = ax.bar(indices, rr_values, color=plot_color, edgecolor=edge_col, width=bar_width)
        ax.set_xticks(indices)
        ax.set_xticklabels(cohort_names, fontsize=font_size, fontname=font_family, rotation=20, ha='right')
        ax.set_ylabel(y_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
        ax.set_xlabel(x_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
        if show_values:
            for i, v in enumerate(rr_values):
                ax.text(i, v, f"{v:.2f}", ha='center', va='bottom', fontsize=font_size, fontname=font_family)

    # Gridlines
    ax.grid(gridlines, axis='y' if orientation == "Vertical" else 'x', linestyle='--', alpha=0.4)

    # Tight layout, clean up
    plt.tight_layout()
    plt.box(False)
    ax.spines[['top', 'right']].set_visible(False)
    return fig

fig = plot_bargraph(
    edited_data,
    orientation=orientation,
    font_size=font_size,
    font_family=font_family,
    bar_width=bar_width,
    color=color,
    edge_color=edge_color,
    gridlines=gridlines,
    grayscale=grayscale,
    x_label=x_label,
    y_label=y_label,
    show_values=show_values,
    axis_label_weight=axis_label_weight,
)

st.pyplot(fig)

# --- Download as PNG ---
buf = BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
st.download_button(
    "📥 Download Chart as PNG",
    data=buf.getvalue(),
    file_name="TriNetX_RR_Bargraph.png",
    mime="image/png"
)
