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

# --- Helper to create color pickers for each row ---
def get_default_colors(n):
    palette = [
        "#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22", "#1abc9c", "#34495e", "#95a5a6", "#fd79a8"
    ]
    return [palette[i % len(palette)] for i in range(n)]

# --- Table Input Section ---
st.subheader("Step 1: Enter Cohort Data")

def initialize_data():
    return pd.DataFrame({
        'Cohort Name': ['Cohort A', 'Cohort B'],
        'Relative Risk': [1.25, 0.97],
        'Bar Color': get_default_colors(2),
    })

data = st.session_state.get("data", initialize_data())
# Use the color pickers in the sidebar for a better UI:
edited_data = data.copy()
n_rows = len(data)

# Display the table with color pickers for each bar in the sidebar
st.sidebar.header("Bar Colors")
for i in range(n_rows):
    edited_data.at[i, "Bar Color"] = st.sidebar.color_picker(
        f"Color for {data.at[i, 'Cohort Name']}",
        value=data.at[i, "Bar Color"] if pd.notnull(data.at[i, "Bar Color"]) else get_default_colors(n_rows)[i],
        key=f"bar_color_{i}"
    )

# Now allow main data editing without Bar Color in the main table
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
# Restore Bar Color column
edited_data["Cohort Name"] = table_no_color["Cohort Name"]
edited_data["Relative Risk"] = table_no_color["Relative Risk"]
# Keep it sorted/indexed as entered
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
    fig, ax = plt.subplots(figsize=(8, 4.8))

    cohort_names = df['Cohort Name']
    rr_values = df['Relative Risk']
    bar_colors = ["#888888"] * len(df) if grayscale else df["Bar Color"].tolist()
    indices = range(len(df))

    if pair_bars and len(df) >= 2:
        # Group in pairs (stacked groups of 2)
        groups = [f"Group {i//2 + 1}" for i in range(len(df))]
        unique_groups = []
        xticks = []
        xticklabels = []
        group_labels = []
        group_values = []
        group_colors = []

        for i in range(0, len(df), 2):
            unique_groups.append(i//2)
            group_labels.append([
                cohort_names.iloc[i],
                cohort_names.iloc[i+1] if i+1 < len(df) else ""
            ])
            group_values.append([
                rr_values.iloc[i],
                rr_values.iloc[i+1] if i+1 < len(df) else None
            ])
            group_colors.append([
                bar_colors[i],
                bar_colors[i+1] if i+1 < len(df) else "#888888" if grayscale else get_default_colors(1)[0]
            ])
            xticks.append(i//2)
            label = ""
            if group_labels[-1][1]:
                label = f"{group_labels[-1][0]} vs\n{group_labels[-1][1]}"
            else:
                label = group_labels[-1][0]
            xticklabels.append(label)

        import numpy as np
        bar_width_actual = bar_width/2 if orientation == "Vertical" else bar_width

        if orientation == "Horizontal":
            for idx, vals in enumerate(group_values):
                pos = xticks[idx]
                y1 = pos - 0.15
                y2 = pos + 0.15
                if vals[0] is not None:
                    ax.barh(y1, vals[0], color=group_colors[idx][0], height=bar_width_actual, edgecolor="#444444")
                    if show_values:
                        ax.text(vals[0], y1, f" {vals[0]:.2f}", va='center', ha='left', fontsize=font_size, fontname=font_family)
                if vals[1] is not None:
                    ax.barh(y2, vals[1], color=group_colors[idx][1], height=bar_width_actual, edgecolor="#444444")
                    if show_values:
                        ax.text(vals[1], y2, f" {vals[1]:.2f}", va='center', ha='left', fontsize=font_size, fontname=font_family)
            ax.set_yticks(xticks)
            ax.set_yticklabels(xticklabels, fontsize=font_size, fontname=font_family)
            ax.set_xlabel(y_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
            ax.set_ylabel(x_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
        else:
            for idx, vals in enumerate(group_values):
                pos = xticks[idx]
                x1 = pos - 0.15
                x2 = pos + 0.15
                if vals[0] is not None:
                    ax.bar(x1, vals[0], color=group_colors[idx][0], width=bar_width_actual, edgecolor="#444444")
                    if show_values:
                        ax.text(x1, vals[0], f"{vals[0]:.2f}", ha='center', va='bottom', fontsize=font_size, fontname=font_family)
                if vals[1] is not None:
                    ax.bar(x2, vals[1], color=group_colors[idx][1], width=bar_width_actual, edgecolor="#444444")
                    if show_values:
                        ax.text(x2, vals[1], f"{vals[1]:.2f}", ha='center', va='bottom', fontsize=font_size, fontname=font_family)
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticklabels, fontsize=font_size, fontname=font_family)
            ax.set_ylabel(y_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
            ax.set_xlabel(x_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
    else:
        if orientation == "Horizontal":
            bars = ax.barh(indices, rr_values, color=bar_colors, edgecolor="#444444", height=bar_width)
            ax.set_yticks(indices)
            ax.set_yticklabels(cohort_names, fontsize=font_size, fontname=font_family)
            ax.set_xlabel(y_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
            ax.set_ylabel(x_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
            if show_values:
                for i, v in enumerate(rr_values):
                    ax.text(v, i, f" {v:.2f}", va='center', ha='left', fontsize=font_size, fontname=font_family)
        else:
            bars = ax.bar(indices, rr_values, color=bar_colors, edgecolor="#444444", width=bar_width)
            ax.set_xticks(indices)
            ax.set_xticklabels(cohort_names, fontsize=font_size, fontname=font_family, rotation=20, ha='right')
            ax.set_ylabel(y_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
            ax.set_xlabel(x_label, fontsize=font_size+2, fontweight=axis_label_weight, fontname=font_family)
            if show_values:
                for i, v in enumerate(rr_values):
                    ax.text(i, v, f"{v:.2f}", ha='center', va='bottom', fontsize=font_size, fontname=font_family)

    # Gridlines
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
