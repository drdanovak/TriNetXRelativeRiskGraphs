import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="TriNetX Grouped Bargraph Generator", layout="centered")

def get_default_colors(n):
    palette = [
        "#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6",
        "#e67e22", "#1abc9c", "#34495e", "#95a5a6", "#fd79a8"
    ]
    return [palette[i % len(palette)] for i in range(n)]

st.title("TriNetX Grouped Bargraph Generator")
st.markdown("""
- Use "Header" rows to create group titles (e.g., "Anemia", "Cancer").
- Use "Data" rows to add cohort bars under each header.
- You can add/remove/reorder rows as you like!
""")

# Initialize data
def initialize_data():
    df = pd.DataFrame({
        "Type": ["Header", "Data", "Data", "Header", "Data", "Data"],
        "Label": ["Anemia", "Cohort 1", "Cohort 2", "Cancer", "Cohort 1", "Cohort 2"],
        "Relative Risk": [None, 1.1, 1.3, None, 0.9, 1.4],
        "Bar Color": ["#FFFFFF", "#3498db", "#e74c3c", "#FFFFFF", "#2ecc71", "#f1c40f"]
    })
    return df

if "data" not in st.session_state:
    st.session_state.data = initialize_data()
data = st.session_state.data.copy()

# Always ensure correct columns and lengths
needed = ["Type", "Label", "Relative Risk", "Bar Color"]
for col in needed:
    if col not in data.columns:
        if col == "Type":
            data[col] = ["Data"] * len(data)
        elif col == "Label":
            data[col] = [f"Row {i+1}" for i in range(len(data))]
        elif col == "Relative Risk":
            data[col] = [None] * len(data)
        elif col == "Bar Color":
            data[col] = get_default_colors(len(data))
    elif len(data[col]) != len(data):
        if col == "Bar Color":
            data[col] = (list(data[col]) + get_default_colors(len(data)))[:len(data)]
        elif col == "Relative Risk":
            data[col] = (list(data[col]) + [None]*len(data))[:len(data)]
        elif col == "Label":
            data[col] = (list(data[col]) + [f"Row {i+1}" for i in range(len(data))])[:len(data)]
        elif col == "Type":
            data[col] = (list(data[col]) + ["Data"]*len(data))[:len(data)]

# Sidebar: set Type and Color for each row
st.sidebar.header("Rows: Header or Data")
for i in range(len(data)):
    # Row type
    type_default = 0 if data.at[i, "Type"] == "Data" else 1
    rowtype = st.sidebar.selectbox(
        f"Row {i+1} Type",
        options=["Data", "Header"],
        index=type_default,
        key=f"type_{i}"
    )
    data.at[i, "Type"] = rowtype
    # Color
    if rowtype == "Data":
        color = data.at[i, "Bar Color"]
        if not isinstance(color, str) or not color.startswith("#"):
            color = get_default_colors(len(data))[i]
        data.at[i, "Bar Color"] = st.sidebar.color_picker(
            f"Bar Color for {data.at[i, 'Label'] or f'Row {i+1}'}",
            value=color,
            key=f"color_{i}"
        )
    else:
        data.at[i, "Bar Color"] = "#FFFFFF"

# Main table editing for Type, Label, and Relative Risk
table_for_edit = data[["Type", "Label", "Relative Risk"]]
table_for_edit = st.data_editor(
    table_for_edit,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Type": st.column_config.SelectboxColumn("Type", options=["Data", "Header"]),
        "Label": st.column_config.TextColumn("Label"),
        "Relative Risk": st.column_config.NumberColumn("Relative Risk", min_value=0.01, step=0.01, required=False),
    },
    key="data_table"
)
data["Type"] = table_for_edit["Type"]
data["Label"] = table_for_edit["Label"]
data["Relative Risk"] = table_for_edit["Relative Risk"]

# Clean up colors if new/removed rows
default_colors = get_default_colors(len(data))
for i in range(len(data)):
    if data.at[i, "Type"] == "Data":
        color = data.at[i, "Bar Color"]
        if not isinstance(color, str) or not color.startswith("#"):
            data.at[i, "Bar Color"] = default_colors[i]
    else:
        data.at[i, "Bar Color"] = "#FFFFFF"

st.session_state.data = data

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

# Plotting
st.subheader("Step 2: Bar Graph with Group Headings")

def plot_with_headings(df, orientation, font_size, font_family, bar_width, gridlines, grayscale, x_label, y_label, show_values, axis_label_weight):
    import numpy as np
    fig, ax = plt.subplots(figsize=(10, 6))
    pos = 0
    bar_positions = []
    bar_labels = []
    bar_values = []
    bar_colors = []
    header_positions = []
    header_labels = []
    tick_positions = []
    for i, row in df.iterrows():
        if row["Type"] == "Header":
            header_positions.append(pos)
            header_labels.append(row["Label"])
        elif row["Type"] == "Data" and pd.notnull(row["Relative Risk"]):
            bar_positions.append(pos)
            bar_labels.append(row["Label"])
            bar_values.append(row["Relative Risk"])
            bar_colors.append("#888888" if grayscale else row["Bar Color"])
            tick_positions.append(pos)
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

fig = plot_with_headings(
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
