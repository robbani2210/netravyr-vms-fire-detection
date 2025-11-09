import streamlit as st

# === Styling dasar (tanpa ubah posisi tombol lewat CSS) ===
st.markdown("""
    <style>
    body {
        background-color: #1b100c;
        color: #f3f3f3;
        font-family: 'Space Grotesk', sans-serif;
    }

    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }

    .subtext {
        color: #aaa;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    h2, h3 {
        color: #ffffff;
        margin-top: 1rem;
    }

    .stButton button {
        background-color: #d43811 !important;
        color: white !important;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        transition: 0.2s;
        font-size: 1rem;
    }

    .stButton button:hover {
        background-color: #b82f0f !important;
        transform: scale(1.03);
    }

    div[role='radiogroup'] {
        justify-content: center;
        gap: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# === Header ===
st.markdown("<h1>Reports</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>Generate and view reports related to thermal data, fire incidents, and system performance.</p>", unsafe_allow_html=True)

# === Report Type ===
st.markdown("<h3>Report Type</h3>", unsafe_allow_html=True)
report_type = st.radio(
    "",
    ["Thermal Data", "Fire Incidents", "System Performance"],
    horizontal=True,
    index=0,
    label_visibility="collapsed"
)

# === Report Parameters ===
st.markdown("<h3>Report Parameters</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    time_range = st.selectbox("Time Range", ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"])
with col2:
    camera = st.selectbox("Camera", ["All Cameras", "Camera #1 - Sector A", "Camera #2 - Sector B", "Camera #3 - Sector C"])

format_choice = st.selectbox("Format", ["PDF", "CSV", "XLSX"])

# === Scheduling Section ===
st.markdown("<h3>Scheduling</h3>", unsafe_allow_html=True)
schedule = st.checkbox("Schedule Report")
if schedule:
    frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
else:
    frequency = None

# === Tombol rata kanan dengan layout kolom ===
col_spacer, col_button = st.columns([5, 1])
with col_button:
    generate = st.button("Generate Report")

# === Logika tombol ===
if generate:
    st.success(
        f"✅ Report generated successfully!\n\n"
        f"**Type:** {report_type}\n"
        f"**Camera:** {camera}\n"
        f"**Range:** {time_range}\n"
        f"**Format:** {format_choice}\n"
        f"**Schedule:** {'Yes ('+frequency+')' if schedule else 'No'}"
    )
