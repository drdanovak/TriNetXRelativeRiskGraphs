import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="TriNetX RR Bargraph Generator", layout="centered")

st.title("TriNetX Relative Risk Bargraph Generator")
st.markdown("""
This app helps you create publication-quality bargraphs of Relative Risks for your TriNetX cohorts.  
Enter your cohort names and RR values below, customize the look, and download as PNG!
""")

def get_default_colors(n):
    palette = [
        "#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6",
        "#e67e22", "#1abc9c", "#34495e", "#95a5a6", "#fd79a8"
    ]
    return [palette[i % len(palette)] for i in range(n)]

# --- Table Input Section ---
st.subheader("Step 1: Enter Cohort Data")

def initialize_data():
    df = pd.DataFrame({
        'Cohort Name': ['Cohort A', 'Cohort B'],
        'Relative Risk': [1.25, 0.97],
    })
    df['Bar Color'] = get_default_colors(len(df))
    return df

# Get previous data or initialize
data = st.session_state.get("data", initialize_data())

# Always ensure "Bar Color" column exists and is sized correctly
if "Bar Color" not in data.columns or len(data["Bar Color"]) != len(data):
    base_colors = get_default_colors(len(data))
    if "Bar Color" in data.columns:
        old_colors = list(data["Bar Color"]) + base_colors
        data["Bar Color"] = old_colors[:len(data)]
    else:
        data["Bar Color"] = base_colors

# Color pickers in sidebar for each row
st.sidebar.header("Bar Colors")
edited_data = data.copy()
for i in range(len(edited_data)):
    color_key = f"bar_color_{i}"
    current_color = edited_data.at[i, "Bar Color"]
    if not isinstance(current_color, str) or not current_color.startswith("#"):
        current_color = get_default_colors(len(edited_data))[i]
    edited_data.at[i, "Bar Color"] = st.sidebar.color_picker(
        f"Color for {edited_data.at[i, 'Cohort Name'] or f'Cohort {i+1}'}",
        value=current_color,
        key=color_key
    )

# Main data editor for names and RR only
table_no_color = edited_data.drop(columns=["Bar Color"])
table_no_color = st.data_editor(
    table_no_color,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Cohort Name": st.column_config.TextColumn("Cohort Name"),
        "Relative Risk": st.column_config.NumberColumn("Relative Risk", min_value=0.01, step=0.01),
    },
    key="rr_table"
)

# Restore Bar Color after data editor changes
edited_data["Cohort Name"] = table_no_color["Cohort Name"]
edited_data["Relative Risk"] = table_no_color["Relative Risk"]

# Fill in any missing/invalid bar colors with defaults, row by row
default_colors = get_default_colors(len(edited_data))
for i in range(len(edited_data)):
    color = edited_data.at[i, "Bar Color"]
    if not isinstance(color, str) or not color.startswith("#"):
        edited_data.at[i, "Bar Color"] = default_colors[i]

# Save in session state
st.session_state.data = edited_data

# --- Chart Options in Sidebar ---
st.sidebar.header("🛠️ Customize Appearance")
orientation = st.sidebar.radio("Bar Orientation", ["Horizontal", "Vertical"], index=0)
font_size = st.sidebar.slider("Font Size", 8, 28, 14)
font_family = st.sidebar.selectbox("Font Family", ["DejaVu Sans", "Arial", "Helvetica", "Times New Roman", "Courier New"])
bar_width = st.sidebar.slider("Bar/Value Spacing", 0.2, 0.9, 0.6)
gridlines = st.sidebar.checkbox("Show gridlines", value=True)
grayscale = st.sidebar.checkbox("Grayscale", value=False)
x_label = st.sidebar.text_input("X-axis Label", "Cohort")
y_label = st.sidebar.text_input("Y-axis Label", "Relative Risk")
show_values = st.sidebar.checkbox("Show values on bars", value=True)
axis_label_weight = st.sidebar.selectbox("Axis Label Weight", ["normal", "bold", "heavy"], index=1)
pair_bars = st.sidebar.checkbox("Group bars into pairs (side-by-side)?", value=False)

# --- Draw Chart ---
st.subheader("Step 2: View & Download Your Bargraph")

def plot_bargraph(
    df, orientation, font_size, font_family, bar_width, gridlines,
    grayscale, x_label, y_label, show_values, axis_label_weight, pair_bars
):
    import numpy as np
    fig, ax = plt.subplots(figsize=(8, 4.8))

    cohort_names = df['Cohort Name']
    rr_values = df['Relative Risk']
    bar_colors = ["#888888"] * len(df) if grayscale else df["Bar Color"].tolist()
    indices = np.arange(len(df))

    if pair_bars and len(df) >= 2:
        # Group in pairs (side-by-side)
        xticks = []
        xticklabels = []
        for i in range(0, len(df), 2):
            label = cohort_names.iloc[i]
            if i + 1 < len(df):
                label += f" vs\n{cohort_names.iloc[i + 1]}"
            xticks.append(i // 2)
            xticklabels.append(label)
        width = bar_width / 2
        offset = 0.18
        if orientation == "Horizontal":
            for idx, i in enumerate(range(0, len(df), 2)):
                y1 = idx - offset
                y2 = idx + offset
                if i < len(df):
                    ax.barh(y1, rr_values.iloc[i], color=bar_colors[i], height=width, edgecolor="#444444")
                    if show_values:
                        ax.text(rr_values.iloc[i], y1, f" {rr_values.iloc[i]:.2f}", va='center', ha='left', fontsize=font_size, fontname=font_family)
                if i + 1 < len(df):
                    ax.barh(y2, rr_values.iloc[i + 1], color=bar_colors[i + 1], height=width, edgecolor="#444444")
                    if show_values:
                        ax.text(rr_values.iloc[i + 1], y2, f" {rr_values.iloc[i + 1]:.2f}", va='center', ha='left', fontsize=font_size, fontname=font_family)
            ax.set_yticks(range(len(xticks)))
            ax.set_yticklabels(xticklabels, fontsize=font_size, fontname=font_family)
            ax.set_xlabel(y_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
            ax.set_ylabel(x_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
        else:
            for idx, i in enumerate(range(0, len(df), 2)):
                x1 = idx - offset
                x2 = idx + offset
                if i < len(df):
                    ax.bar(x1, rr_values.iloc[i], color=bar_colors[i], width=width, edgecolor="#444444")
                    if show_values:
                        ax.text(x1, rr_values.iloc[i], f"{rr_values.iloc[i]:.2f}", ha='center', va='bottom', fontsize=font_size, fontname=font_family)
                if i + 1 < len(df):
                    ax.bar(x2, rr_values.iloc[i + 1], color=bar_colors[i + 1], width=width, edgecolor="#444444")
                    if show_values:
                        ax.text(x2, rr_values.iloc[i + 1], f"{rr_values.iloc[i + 1]:.2f}", ha='center', va='bottom', fontsize=font_size, fontname=font_family)
            ax.set_xticks(range(len(xticks)))
            ax.set_xticklabels(xticklabels, fontsize=font_size, fontname=font_family)
            ax.set_ylabel(y_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
            ax.set_xlabel(x_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
    else:
        if orientation == "Horizontal":
            bars = ax.barh(indices, rr_values, color=bar_colors, edgecolor="#444444", height=bar_width)
            ax.set_yticks(indices)
            ax.set_yticklabels(cohort_names, fontsize=font_size, fontname=font_family)
            ax.set_xlabel(y_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
            ax.set_ylabel(x_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
            if show_values:
                for i, v in enumerate(rr_values):
                    ax.text(v, i, f" {v:.2f}", va='center', ha='left', fontsize=font_size, fontname=font_family)
        else:
            bars = ax.bar(indices, rr_values, color=bar_colors, edgecolor="#444444", width=bar_width)
            ax.set_xticks(indices)
            ax.set_xticklabels(cohort_names, fontsize=font_size, fontname=font_family, rotation=20, ha='right')
            ax.set_ylabel(y_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
            ax.set_xlabel(x_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
            if show_values:
                for i, v in enumerate(rr_values):
                    ax.text(i, v, f"{v:.2f}", ha='center', va='bottom', fontsize=font_size, fontname=font_family)

    ax.grid(gridlines, axis='y' if orientation == "Vertical" else 'x', linestyle='--', alpha=0.4)
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
    gridlines=gridlines,
    grayscale=grayscale,
    x_label=x_label,
    y_label=y_label,
    show_values=show_values,
    axis_label_weight=axis_label_weight,
    pair_bars=pair_bars,
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
