import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import io

def wrap_labels(labels, width):
    """Wrap long labels for better display."""
    new_labels = []
    for label in labels:
        if len(label) > width:
            words = label.split()
            new_label = ''
            line = ''
            for word in words:
                if len(line) + len(word) + 1 <= width:
                    line += (word + ' ')
                else:
                    new_label += line.rstrip() + '\n'
                    line = word + ' '
            new_label += line.rstrip()
            new_labels.append(new_label)
        else:
            new_labels.append(label)
    return new_labels

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
base_font_size = st.sidebar.slider("Font Size", 10, 24, 14)
bar_color = st.sidebar.color_picker("Bar Color", "#1976D2")
bg_color = st.sidebar.color_picker("Background Color", "#FFFFFF")
axis_color = st.sidebar.color_picker("Axis/Label Color", "#333333")
label_pos = st.sidebar.selectbox("Label Position", ["Outside", "Inside"], index=0)
spacing = st.sidebar.slider("Bar/Label Spacing", 0, 40, 10)
gridlines = st.sidebar.checkbox("Show Grid Lines", value=True)
grayscale = st.sidebar.checkbox("Grayscale (Black & White)", value=False)
show_group_shading = st.sidebar.checkbox("Shade Groups", value=True)
show_reference_line = st.sidebar.checkbox("Reference Line (RR=1)", value=True)

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
label_locs = []  # Index in table (for group headers)

for i, row in data.iterrows():
    name = row["Cohort Name"]
    if name.startswith("##"):
        group_name = name.replace("##", "").strip()
        group_boundaries.append(len(plot_labels))
        group_labels.append(group_name)
        label_locs.append(i)
    elif pd.notnull(row["Relative Risk"]):
        plot_labels.append(name)
        plot_values.append(float(row["Relative Risk"]))

num_bars = len(plot_labels)
# --- Adjust font size if many bars
font_size = base_font_size
if num_bars > 18:
    font_size = max(8, base_font_size - (num_bars - 18) // 2)

# --- Figure size based on content ---
max_label_len = max([len(lbl) for lbl in plot_labels]) if plot_labels else 10
if orientation == "Horizontal":
    fig_height = max(4, num_bars * 0.7)
    fig_width = min(12, 4 + max_label_len * 0.17)
else:
    fig_height = 5 + max_label_len * 0.08
    fig_width = max(7, num_bars * 0.55)
fig, ax = plt.subplots(figsize=(fig_width, fig_height))
plt.rcParams.update({'font.size': font_size, 'font.family': font_family})
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

indices = np.arange(num_bars)
bar_kwargs = {'color': bar_color, 'edgecolor': axis_color}

# --- Draw shaded groups ---
group_indices = [0] + group_boundaries + [num_bars]
if show_group_shading:
    for i, (start, end) in enumerate(zip(group_indices, group_indices[1:])):
        if i % 2 == 1:
            if orientation == "Horizontal":
                ax.axhspan(start-0.5, end-0.5, color='#f0f0f0', zorder=0)
            else:
                ax.axvspan(start-0.5, end-0.5, color='#f0f0f0', zorder=0)

# --- Draw bars and handle labels ---
if orientation == "Horizontal":
    bars = ax.barh(indices, plot_values, **bar_kwargs)
    y_labels_wrapped = wrap_labels(plot_labels, 20)
    ax.set_yticks(indices)
    ax.set_yticklabels(y_labels_wrapped, color=axis_color, fontsize=font_size)
    ax.set_xlabel(custom_xlabel, color=axis_color)
    ax.set_ylabel(custom_ylabel, color=axis_color)
    ax.set_xticklabels(ax.get_xticks(), color=axis_color)
    # If many bars, skip every other label
    if num_bars > 18:
        for idx, label in enumerate(ax.get_yticklabels()):
            if idx % 2 != 0:
                label.set_visible(False)
    # Value Labels
    for i, bar in enumerate(bars):
        value = bar.get_width()
        if label_pos == "Inside" and value > 0.15*max(plot_values):
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
    x_labels_wrapped = wrap_labels(plot_labels, 12)
    ax.set_xticks(indices)
    # If many bars, rotate and skip every other label
    if num_bars > 12:
        rotation_angle = 60
    else:
        rotation_angle = 35
    ax.set_xticklabels(x_labels_wrapped, color=axis_color, rotation=rotation_angle, ha='right', fontsize=font_size)
    if num_bars > 18:
        for idx, label in enumerate(ax.get_xticklabels()):
            if idx % 2 != 0:
                label.set_visible(False)
    ax.set_ylabel(custom_ylabel, color=axis_color)
    ax.set_xlabel(custom_xlabel, color=axis_color)
    ax.set_yticklabels(ax.get_yticks(), color=axis_color)
    # Value Labels
    for i, bar in enumerate(bars):
        value = bar.get_height()
        if label_pos == "Inside" and value > 0.15*max(plot_values):
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

plt.subplots_adjust(left=0.25 if orientation=="Horizontal" else 0.14,
                    right=0.98, top=0.90, bottom=0.27 if orientation=="Vertical" else 0.10)

plt.tight_layout()

# --- Group Headings / Separators ---
for idx, group_start in enumerate(group_boundaries):
    if 0 < group_start <= num_bars:
        if orientation == "Horizontal":
            ax.axhline(group_start - 0.5, color=axis_color, linewidth=1, linestyle='--', zorder=5)
            ax.text(
                ax.get_xlim()[0], group_start - 0.5, group_labels[idx],
                va='bottom', ha='left',
                color=axis_color, fontweight="bold",
                fontsize=font_size + 1,
                bbox=dict(facecolor=bg_color, edgecolor='none', boxstyle='round,pad=0.3')
            )
        else:
            ax.axvline(group_start - 0.5, color=axis_color, linewidth=1, linestyle='--', zorder=5)
            ax.text(
                group_start - 0.5, ax.get_ylim()[1], group_labels[idx],
                va='bottom', ha='center',
                color=axis_color, fontweight="bold",
                fontsize=font_size + 1,
                bbox=dict(facecolor=bg_color, edgecolor='none', boxstyle='round,pad=0.3')
            )

# --- Reference line ---
if show_reference_line:
    if orientation == "Horizontal":
        ax.axvline(1, color='red', linestyle=':', linewidth=1)
    else:
        ax.axhline(1, color='red', linestyle=':', linewidth=1)

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
- **Dynamic Sizing:** Figure size and font auto-adjust to content.
- **Custom Axis Titles:** Set X and Y axis labels in the sidebar.
- **Label Rotation/Skipping:** Rotates and/or skips tick labels for crowded plots.
- **Label Wrapping:** Long cohort names wrap for readability.
- **Bar/Value Spacing:** Use the slider to set space between bars and value labels.
- **Grouping Tools:** Enter `##Heading Name` in Cohort Name to create group headers/separators in your chart, with optional group shading.
- **Reference Line:** Optional red dashed line at RR=1.
- **Grid Lines:** Toggle gridlines on/off.
- **Font, Color, Grayscale, Download:** Customize everything; export as PNG.
- **Orientation:** Horizontal or vertical bar charts (horizontal is default).
- **Dynamic Rows:** Add or remove rows in the table for unlimited cohorts.
    """)
