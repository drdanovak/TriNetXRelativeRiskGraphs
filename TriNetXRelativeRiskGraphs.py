import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="TriNetX RR Bargraph Generator", layout="centered")

def get_default_colors(n):
    palette = [
        "#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6",
        "#e67e22", "#1abc9c", "#34495e", "#95a5a6", "#fd79a8"
    ]
    return [palette[i % len(palette)] for i in range(n)]

st.title("TriNetX Relative Risk Bargraph Generator")
st.markdown("""
Add group headers by changing row type in the sidebar.  
Group headers will appear as bold text separators in your bar graph!
""")

def initialize_data():
    df = pd.DataFrame({
        'Row Type': ['Data', 'Data'],
        'Label': ['Cohort A', 'Cohort B'],
        'Relative Risk': [1.25, 0.97],
        'Bar Color': get_default_colors(2)
    })
    return df

if "data" not in st.session_state:
    st.session_state.data = initialize_data()
data = st.session_state.data.copy()

# --- Ensure all required columns exist and are the right length ---
required_cols = ["Row Type", "Label", "Relative Risk", "Bar Color"]
for col in required_cols:
    if col not in data.columns:
        if col == "Row Type":
            data[col] = ["Data"] * len(data)
        elif col == "Label":
            data[col] = [f"Cohort {i+1}" for i in range(len(data))]
        elif col == "Relative Risk":
            data[col] = [1.0] * len(data)
        elif col == "Bar Color":
            data[col] = get_default_colors(len(data))
    # If column exists but length is wrong, pad/truncate
    elif len(data[col]) != len(data):
        if col == "Row Type":
            data[col] = list(data[col]) + ["Data"] * (len(data) - len(data[col]))
            data[col] = data[col][:len(data)]
        elif col == "Label":
            data[col] = list(data[col]) + [f"Cohort {i+1}" for i in range(len(data) - len(data[col]))]
            data[col] = data[col][:len(data)]
        elif col == "Relative Risk":
            data[col] = list(data[col]) + [1.0] * (len(data) - len(data[col]))
            data[col] = data[col][:len(data)]
        elif col == "Bar Color":
            data[col] = list(data[col]) + get_default_colors(len(data) - len(data[col]))
            data[col] = data[col][:len(data)]

# --- Sidebar to set Row Type and Bar Color for each row ---
st.sidebar.header("Customize Table Rows")
for i in range(len(data)):
    row_type = data.at[i, "Row Type"] if "Row Type" in data.columns else "Data"
    index_for_box = 0 if row_type == "Data" else 1
    row_type = st.sidebar.selectbox(
        f"Row {i+1} Type",
        options=["Data", "Header"],
        index=index_for_box,
        key=f"rowtype_{i}"
    )
    data.at[i, "Row Type"] = row_type
    if row_type == "Data":
        color = data.at[i, "Bar Color"]
        if not isinstance(color, str) or not color.startswith("#"):
            color = get_default_colors(len(data))[i]
        data.at[i, "Bar Color"] = st.sidebar.color_picker(
            f"Color for {data.at[i, 'Label'] or f'Row {i+1}'}",
            value=color,
            key=f"color_{i}"
        )
    else:
        data.at[i, "Bar Color"] = "#FFFFFF"  # Not used

# Main editor for Label and RR
table_no_color = data[["Row Type", "Label", "Relative Risk"]]
table_no_color = st.data_editor(
    table_no_color,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Row Type": st.column_config.SelectboxColumn("Row Type", options=["Data", "Header"]),
        "Label": st.column_config.TextColumn("Label"),
        "Relative Risk": st.column_config.NumberColumn("Relative Risk", min_value=0.01, step=0.01),
    },
    key="table_main"
)
data["Label"] = table_no_color["Label"]
data["Relative Risk"] = table_no_color["Relative Risk"]
data["Row Type"] = table_no_color["Row Type"]

# Reapply safe default color to any new/changed rows
default_colors = get_default_colors(len(data))
for i in range(len(data)):
    if data.at[i, "Row Type"] == "Data":
        color = data.at[i, "Bar Color"]
        if not isinstance(color, str) or not color.startswith("#"):
            data.at[i, "Bar Color"] = default_colors[i]

st.session_state.data = data

# Appearance options
st.sidebar.header("🛠️ Appearance")
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

st.subheader("Step 2: View & Download Your Bargraph")

def plot_grouped_bargraph(df, orientation, font_size, font_family, bar_width, gridlines, grayscale, x_label, y_label, show_values, axis_label_weight):
    import numpy as np
    fig, ax = plt.subplots(figsize=(9, 5.5))
    y_pos = 0
    yticks = []
    ylabels = []
    colors = []
    bar_positions = []
    bar_values = []
    group_labels = []
    group_positions = []

    for i, row in df.iterrows():
        if row["Row Type"] == "Header":
            # Track this y-position for header label
            group_labels.append((row["Label"], y_pos))
        else:
            bar_positions.append(y_pos)
            ylabels.append(row["Label"])
            bar_values.append(row["Relative Risk"])
            if grayscale:
                colors.append("#888888")
            else:
                colors.append(row["Bar Color"])
            y_pos += 1
        y_pos += 0.15 if row["Row Type"] == "Header" else 0

    if orientation == "Horizontal":
        ax.barh(bar_positions, bar_values, color=colors, edgecolor="#444444", height=bar_width)
        ax.set_yticks(bar_positions)
        ax.set_yticklabels(ylabels, fontsize=font_size, fontname=font_family)
        ax.set_xlabel(y_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
        ax.set_ylabel(x_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
        # Show values
        if show_values:
            for y, v in zip(bar_positions, bar_values):
                ax.text(v, y, f" {v:.2f}", va='center', ha='left', fontsize=font_size, fontname=font_family)
        # Group headers as bold labels
        for text, pos in group_labels:
            ax.text(ax.get_xlim()[0], pos-0.1, text, va='center', ha='left', fontsize=font_size+2, fontweight='bold', fontname=font_family, color='#333333', backgroundcolor="#F2F2F2")
    else:
        ax.bar(bar_positions, bar_values, color=colors, edgecolor="#444444", width=bar_width)
        ax.set_xticks(bar_positions)
        ax.set_xticklabels(ylabels, fontsize=font_size, fontname=font_family, rotation=20, ha='right')
        ax.set_ylabel(y_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
        ax.set_xlabel(x_label, fontsize=font_size + 2, fontweight=axis_label_weight, fontname=font_family)
        # Show values
        if show_values:
            for x, v in zip(bar_positions, bar_values):
                ax.text(x, v, f"{v:.2f}", ha='center', va='bottom', fontsize=font_size, fontname=font_family)
        # Group headers as bold labels
        for text, pos in group_labels:
            ax.text(pos-0.1, ax.get_ylim()[1], text, va='bottom', ha='center', fontsize=font_size+2, fontweight='bold', fontname=font_family, color='#333333', backgroundcolor="#F2F2F2", rotation=0, clip_on=False)

    ax.grid(gridlines, axis='y' if orientation == "Vertical" else 'x', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.box(False)
    ax.spines[['top', 'right']].set_visible(False)
    return fig

fig = plot_grouped_bargraph(
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
    file_name="TriNetX_RR_Bargraph.png",
    mime="image/png"
)
