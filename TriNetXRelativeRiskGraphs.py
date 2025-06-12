import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io

st.set_page_config(page_title="Relative Risk Bargraph Generator", layout="centered")
st.title("TriNetX Relative Risk Bargraph Generator")

# --- Default Data ---
default_data = pd.DataFrame({
    "Cohort Name": ["Cohort 1", "Cohort 2"],
    "Relative Risk": [1.0, 2.0]
})

# --- Editable Table ---
st.subheader("Enter Cohort Names and Relative Risk Values")
data = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    key="rr_table"
)
data = data.dropna()
data["Relative Risk"] = pd.to_numeric(data["Relative Risk"], errors="coerce")

# --- Customization Options ---
st.sidebar.header("Chart Options")
orientation = st.sidebar.radio("Orientation", ["Vertical", "Horizontal"], index=0)
grayscale = st.sidebar.checkbox("Grayscale (Black & White)", value=False)
font_family = st.sidebar.selectbox("Font Family", ["DejaVu Sans", "Arial", "Times New Roman", "Calibri"])
font_size = st.sidebar.slider("Font Size", 10, 24, 14)
bar_color = st.sidebar.color_picker("Bar Color", "#1976D2")
bg_color = st.sidebar.color_picker("Background Color", "#FFFFFF")
axis_color = st.sidebar.color_picker("Axis/Label Color", "#333333")
label_pos = st.sidebar.selectbox("Label Position", ["Outside", "Inside"], index=0)

# --- Matplotlib Styles ---
if grayscale:
    plt.style.use("grayscale")
    bar_color = "#888888"
    bg_color = "#FFFFFF"
    axis_color = "#111111"
else:
    matplotlib.rcParams.update({'axes.prop_cycle': matplotlib.cycler('color', [bar_color])})

# --- Plotting ---
fig, ax = plt.subplots(figsize=(6, 4))
plt.rcParams.update({'font.size': font_size, 'font.family': font_family})
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

names = data["Cohort Name"].tolist()
values = data["Relative Risk"].tolist()

if orientation == "Vertical":
    bars = ax.bar(names, values, color=bar_color, edgecolor=axis_color)
    ax.set_ylabel("Relative Risk", color=axis_color)
    ax.set_xlabel("Cohort", color=axis_color)
    ax.set_xticklabels(names, color=axis_color, rotation=0)
    ax.set_yticklabels(ax.get_yticks(), color=axis_color)
    # Labels
    for bar in bars:
        value = bar.get_height()
        if label_pos == "Inside":
            ax.text(bar.get_x() + bar.get_width() / 2, value / 2, f"{value:.2f}", ha='center', va='center', color='white' if not grayscale else 'black', fontweight="bold")
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}", ha='center', va='bottom', color=axis_color, fontweight="bold")
else:
    bars = ax.barh(names, values, color=bar_color, edgecolor=axis_color)
    ax.set_xlabel("Relative Risk", color=axis_color)
    ax.set_ylabel("Cohort", color=axis_color)
    ax.set_yticklabels(names, color=axis_color)
    ax.set_xticklabels(ax.get_xticks(), color=axis_color)
    # Labels
    for bar in bars:
        value = bar.get_width()
        if label_pos == "Inside":
            ax.text(value / 2, bar.get_y() + bar.get_height() / 2, f"{value:.2f}", va='center', ha='center', color='white' if not grayscale else 'black', fontweight="bold")
        else:
            ax.text(value, bar.get_y() + bar.get_height() / 2, f"{value:.2f}", va='center', ha='left', color=axis_color, fontweight="bold")

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
