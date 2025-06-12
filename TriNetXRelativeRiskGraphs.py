import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import io

st.set_page_config(page_title="Relative Risk Bargraph Generator", layout="centered")
st.title("TriNetX Relative Risk Bargraph Generator")

# --- Default Data ---
default_data = pd.DataFrame({
    "Cohort Name": ["##Statins", "Atorvastatin", "Rosuvastatin", "##Non-statins", "No Statin"],
    "Relative Risk": [None, 1.2, 1.5, None, 1.0]
})

# --- Editable Table ---
st.subheader("Enter Cohort Names and Relative Risk Values")
st.caption('Tip: Any row with "##Heading" in Cohort Name creates a group heading in the chart.')
data = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    key="rr_table"
)
data = data.dropna(subset=["Cohort Name"])
data["Cohort Name"] = data["Cohort Name"].astype(str).str.strip()

# --- Sidebar Customization ---
st.sidebar.header("Chart Options")
orientation = st.sidebar.radio("Orientation", ["Horizontal", "Vertical"], index=0)
custom_xlabel = st.sidebar.text_input(
    "X Axis Title", "Relative Risk" if orientation == "Horizontal" else "Cohort"
)
custom_ylabel = st.sidebar.text_input(
    "Y Axis Title", "Cohort" if orientation == "Horizontal" else "Relative Risk"
)
font_family = st.sidebar.selectbox(
    "Font Family", ["DejaVu Sans", "Arial", "Times New Roman", "Calibri"]
)
font_size = st.sidebar.slider("Font Size", 10, 24, 14)
bar_color = st.sidebar.color_picker("Bar Color", "#1976D2")
bg_color = st.sidebar.color_picker("Background Color", "#FFFFFF")
axis_color = st.sidebar.color_picker("Axis/Label Color", "#333333")
label_pos = st.sidebar.selectbox("Label Position", ["Outside", "Inside"], index=0)
spacing = st.sidebar.slider("Bar/Label Spacing", 0, 40, 10)
gridlines = st.sidebar.checkbox("Show Grid Lines", value=True)
grayscale = st.sidebar.checkbox("Grayscale (Black & White)", value=False)

# --- Apply Grayscale if checked ---
if grayscale:
    plt.style.use("grayscale")
    bar_color = "#888888"
    bg_color = "#FFFFFF"
    axis_color = "#111111"
else:
    plt.style.use("default")
    matplotlib.rcParams.update({'axes.prop_cycle': matplotlib.cycler('color', [bar_color])})

# --- Parse Table for Plotting ---
plot_labels = []
plot_values = []
group_boundaries = []
group_labels = []

current_group = ""
bar_positions = []  # Track position for each actual bar (excluding group headings)
for i, row in data.iterrows():
    name = row["Cohort Name"]
    if name.startswith("##"):
        current_group = name.replace("##", "").strip()
        group_boundaries.append(len(plot_labels))  # Group headings are *between* bars
        group_labels.append(current_group)
    elif pd.notnull(row["Relative Risk"]):
        plot_labels.append(name)
        plot_values.append(float(row["Relative Risk"]))
        bar_positions.append(i)

num_bars = len(plot_labels)
# Dynamically scale figure height to avoid crowding
fig_height = max(4, num_bars * 0.65) if orientation == "Horizontal" else 5

fig, ax = plt.subplots(figsize=(7, fig_height))
plt.rcParams.update({'font.size': font_size, 'font.family': font_family})
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

indices = np.arange(num_bars)
bar_kwargs = {'color': bar_color, 'edgecolor': axis_color}

if orientation == "Horizontal":
    bars = ax.barh(indices, plot_values, **bar_kwargs)
    ax.set_yticks(indices)
    ax.set_yticklabels(plot_labels, color=axis_color, fontsize=font_size)
    ax.set_xlabel(custom_xlabel, color=axis_color)
    ax.set_ylabel(custom_ylabel, color=axis_color)
    ax.set_xticklabels(ax.get_xticks(), color=axis_color)
    # Value Labels
    for i, bar in enumerate(bars):
        value = bar.get_width()
        if label_pos == "Inside":
            ax.text(
                value / 2, bar.get_y() + bar.get_height() / 2, f"{value:.2f}",
                va='center', ha='center',
                color='white' if not grayscale else 'black', fontweight="bold"
            )
        else:
            ax.text(
                value + spacing / 100, bar.get_y() + bar.get_height() / 2, f"{value:.2f}",
                va='center', ha='left',
                color=axis_color, fontweight="bold"
            )
    ax.invert_yaxis()
else:
    bars = ax.bar(indices, plot_values, **bar_kwargs)
    ax.set_xticks(indices)
    # Use sharp rotation to prevent overlap
    ax.set_xticklabels(plot_labels, color=axis_color, rotation=45, ha='right', fontsize=font_size)
    ax.set_ylabel(custom_ylabel, color=axis_color)
    ax.set_xlabel(custom_xlabel, color=axis_color)
    ax.set_yticklabels(ax.get_yticks(), color=axis_color)
    # Value Labels
    for i, bar in enumerate(bars):
        value = bar.get_height()
        if label_pos == "Inside":
            ax.text(
                bar.get_x() + bar.get_width() / 2, value / 2, f"{value:.2f}",
                ha='center', va='center',
                color='white' if not grayscale else 'black', fontweight="bold"
            )
        else:
            ax.text(
                bar.get_x() + bar.get_width() / 2, value + spacing / 100, f"{value:.2f}",
                ha='center', va='bottom',
                color=axis_color, fontweight="bold"
            )

plt.tight_layout()  # Prevents label overlap in tight plots

# --- Group Headings / Separators ---
for idx, group_start in enumerate(group_boundaries):
    if 0 < group_start <= num_bars:
        if orientation == "Horizontal":
            ax.axhline(group_start - 0.5, color=axis_color, linewidth=1, linestyle='--')
            ax.text(
                ax.get_xlim()[0], group_start - 0.5, group_labels[idx],
                va='bottom', ha='left',
                color=axis_color, fontweight="bold",
                fontsize=font_size + 1,
                bbox=dict(facecolor=bg_color, edgecolor='none', boxstyle='round,pad=0.3')
            )
        else:
            ax.axvline(group_start - 0.5, color=axis_color, linewidth=1, linestyle='--')
            ax.text(
                group_start - 0.5, ax.get_ylim()[1], group_labels[idx],
                va='bottom', ha='center',
                color=axis_color, fontweight="bold",
                fontsize=font_size + 1,
                bbox=dict(facecolor=bg_color, edgecolor='none', boxstyle='round,pad=0.3')
            )

# --- Gridlines ---
if gridlines:
    if orientation == "Horizontal":
        ax.xaxis.grid(True, linestyle='--', alpha=0.5)
    else:
        ax.yaxis.grid(True, linestyle='--', alpha=0.5)
else:
    ax.grid(False)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color(axis_color)
ax.spines['left'].set_color(axis_color)
ax.tick_params(axis='x', colors=axis_color)
ax.tick_params(axis='y', colors=axis_color)

st.pyplot(fig)

# --- Download PNG ---
buf = io.BytesIO()
fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
st.download_button(
    label="Download Chart as PNG",
    data=buf.getvalue(),
    file_name="relative_risk_bargraph.png",
    mime="image/png"
)

# --- Features Recap ---
with st.expander("Available Features & Options"):
    st.markdown("""
- **Custom Axis Titles:** Set X and Y axis labels in the sidebar.
- **Bar/Value Spacing:** Use the slider to set space between bars and value labels.
- **Grouping Tools:** Enter `##Heading Name` in Cohort Name to create group headers/separators in your chart.
- **Grid Lines:** Toggle gridlines on/off for a cleaner or more analytic look.
- **Font, Color, Grayscale, Download:** Customize everything; export as PNG.
- **Orientation:** Horizontal or vertical bar charts (horizontal is default).
- **Dynamic Rows:** Add or remove rows in the table for unlimited cohorts.
    """)
