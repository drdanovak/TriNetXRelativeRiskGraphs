import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="TriNetX Grouped Bargraph Generator", layout="centered")

# Helper: return a color for each cohort, consistent across groups
def get_palette():
    return [
        "#8e44ad",  # purple
        "#27ae60",  # green
        "#e74c3c",  # red
        "#2980b9",  # blue
        "#f1c40f",  # yellow
        "#d35400",  # orange
        "#16a085",  # teal
        "#2c3e50",  # dark blue
        "#fd79a8",  # pink
        "#636e72",  # gray
        "#b2bec3",  # light gray
        "#00b894",  # light green
    ]

def get_cohort_colors(cohort_names):
    palette = get_palette()
    unique_cohorts = []
    cohort_color_map = {}
    for name in cohort_names:
        if pd.isna(name) or name.strip() == "":
            continue
        if name not in cohort_color_map:
            color = palette[len(unique_cohorts) % len(palette)]
            cohort_color_map[name] = color
            unique_cohorts.append(name)
    return cohort_color_map

st.title("TriNetX Grouped Bargraph Generator")
st.markdown("""
- **Add unlimited disease groups** by adding "Header" rows.
- **Add any number of cohorts under each group** as "Data" rows.
- **Cohort colors are consistent across all groups**.
""")

def initialize_data():
    df = pd.DataFrame({
        "Type": ["Header", "Data", "Data", "Header", "Data", "Data"],
        "Group Label": ["Anemia", "", "", "Cancer", "", ""],
        "Cohort Label": ["", "Cohort 1", "Cohort 2", "", "Cohort 1", "Cohort 2"],
        "Relative Risk": [None, 1.1, 1.3, None, 0.9, 1.4]
    })
    return df

if "data" not in st.session_state:
    st.session_state.data = initialize_data()
data = st.session_state.data.copy()

# Always ensure columns exist
needed = ["Type", "Group Label", "Cohort Label", "Relative Risk"]
for col in needed:
    if col not in data.columns:
        if col == "Type":
            data[col] = ["Data"] * len(data)
        elif col == "Group Label":
            data[col] = ["" for _ in range(len(data))]
        elif col == "Cohort Label":
            data[col] = [f"Cohort {i+1}" for i in range(len(data))]
        elif col == "Relative Risk":
            data[col] = [None] * len(data)
    elif len(data[col]) != len(data):
        if col == "Group Label":
            data[col] = (list(data[col]) + [""] * len(data))[:len(data)]
        elif col == "Cohort Label":
            data[col] = (list(data[col]) + [f"Cohort {i+1}" for i in range(len(data))])[:len(data)]
        elif col == "Relative Risk":
            data[col] = (list(data[col]) + [None] * len(data))[:len(data)]
        elif col == "Type":
            data[col] = (list(data[col]) + ["Data"]*len(data))[:len(data)]

# Table editing
table_for_edit = data[["Type", "Group Label", "Cohort Label", "Relative Risk"]]
table_for_edit = st.data_editor(
    table_for_edit,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Type": st.column_config.SelectboxColumn("Type", options=["Data", "Header"]),
        "Group Label": st.column_config.TextColumn("Disease/Group (for headers)"),
        "Cohort Label": st.column_config.TextColumn("Cohort Name"),
        "Relative Risk": st.column_config.NumberColumn("Relative Risk", min_value=0.01, step=0.01, required=False),
    },
    key="data_table"
)
data["Type"] = table_for_edit["Type"]
data["Group Label"] = table_for_edit["Group Label"]
data["Cohort Label"] = table_for_edit["Cohort Label"]
data["Relative Risk"] = table_for_edit["Relative Risk"]

st.session_state.data = data

# Determine all unique, non-empty cohort names
cohort_names = [name for i, name in enumerate(data["Cohort Label"]) if data.at[i, "Type"] == "Data" and pd.notna(name) and name.strip() != ""]
cohort_color_map = get_cohort_colors(cohort_names)

# Sidebar: Show color assignments for each cohort (user cannot edit directly for consistency)
st.sidebar.header("Cohort Color Key")
for cohort, color in cohort_color_map.items():
    st.sidebar.markdown(f'<div style="display:inline-block;width:20px;height:20px;background:{color};margin-right:8px;border-radius:4px"></div> {cohort}', unsafe_allow_html=True)

# Sidebar - appearance
st.sidebar.header("Appearance")
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

st.subheader("Step 2: Bar Graph with Disease Groupings and Cohort Colors")

def plot_with_headings_and_cohort_colors(
    df, orientation, font_size, font_family, bar_width, gridlines, grayscale, x_label, y_label, show_values, axis_label_weight, cohort_color_map
):
    import numpy as np
    fig, ax = plt.subplots(figsize=(10, 6))
    pos = 0
    bar_positions = []
    bar_labels = []
    bar_values = []
    bar_colors = []
    header_positions = []
    header_labels = []

    # For each row: if Header, insert; if Data, plot
    for i, row in df.iterrows():
        if row["Type"] == "Header":
            header_positions.append(pos)
            header_labels.append(row["Group Label"])
        elif row["Type"] == "Data" and pd.notnull(row["Relative Risk"]) and pd.notna(row["Cohort Label"]) and row["Cohort Label"].strip() != "":
            bar_positions.append(pos)
            bar_labels.append(row["Cohort Label"])
            bar_values.append(row["Relative Risk"])
            cohort = row["Cohort Label"]
            if grayscale:
                bar_colors.append("#888888")
            else:
                bar_colors.append(cohort_color_map.get(cohort, "#222222"))
            pos += 1
        pos += 0.25 if row["Type"] == "Header" else 0

    if orientation == "Horizontal":
        ax.barh(bar_positions, bar_values, color=bar_colors, edgecolor="#444444", height=bar_width)
        ax.set_yticks(bar_positions)
        ax.set_yticklabels(bar_labels, fontsize=font_size, fontname=font_family)
        ax.set_xlabel(y_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
        ax.set_ylabel(x_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
        if show_values:
            for y, v in zip(bar_positions, bar_values):
                ax.text(v, y, f" {v:.2f}", va='center', ha='left', fontsize=font_size, fontname=font_family)
        for head, ypos in zip(header_labels, header_positions):
            ax.axhline(y=ypos-0.13, color="#BBBBBB", linewidth=1)
            ax.text(ax.get_xlim()[0], ypos-0.18, head, va='center', ha='left', fontsize=font_size+3, fontweight='bold', fontname=font_family, color='#333333', backgroundcolor="#F5F5F5")
    else:
        ax.bar(bar_positions, bar_values, color=bar_colors, edgecolor="#444444", width=bar_width)
        ax.set_xticks(bar_positions)
        ax.set_xticklabels(bar_labels, fontsize=font_size, fontname=font_family, rotation=20, ha='right')
        ax.set_ylabel(y_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
        ax.set_xlabel(x_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
        if show_values:
            for x, v in zip(bar_positions, bar_values):
                ax.text(x, v, f"{v:.2f}", ha='center', va='bottom', fontsize=font_size, fontname=font_family)
        for head, xpos in zip(header_labels, header_positions):
            ax.axvline(x=xpos-0.13, color="#BBBBBB", linewidth=1)
            ax.text(xpos-0.18, ax.get_ylim()[1], head, va='bottom', ha='center', fontsize=font_size+3, fontweight='bold', fontname=font_family, color='#333333', backgroundcolor="#F5F5F5", rotation=0, clip_on=False)

    ax.grid(gridlines, axis='y' if orientation == "Vertical" else 'x', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.box(False)
    ax.spines[['top', 'right']].set_visible(False)
    return fig

fig = plot_with_headings_and_cohort_colors(
    data,
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
    cohort_color_map=cohort_color_map,
)

st.pyplot(fig)

buf = BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
st.download_button(
    "📥 Download Chart as PNG",
    data=buf.getvalue(),
    file_name="TriNetX_Grouped_Bargraph.png",
    mime="image/png"
)
