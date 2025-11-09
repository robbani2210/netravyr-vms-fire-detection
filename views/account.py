import streamlit as st

st.title("System Configuration")

st.write("Configure camera connections and essential system parameters.")

st.markdown("---")

# === Camera Configuration ===
st.subheader("📷 Camera Configuration")

# Camera 1
st.markdown("**🔴 Camera 1**")
col1, col2 = st.columns(2)
with col1:
    cam1_ip = st.text_input("IP Address", "192.168.1.101", key="cam1_ip")
with col2:
    cam1_port = st.text_input("Port", "8080", key="cam1_port")

# Camera 2  
st.markdown("**🟢 Camera 2**")
col1, col2 = st.columns(2)
with col1:
    cam2_ip = st.text_input("IP Address", "192.168.1.102", key="cam2_ip")
with col2:
    cam2_port = st.text_input("Port", "8080", key="cam2_port")

# Camera 3
st.markdown("**🔵 Camera 3**")
col1, col2 = st.columns(2)
with col1:
    cam3_ip = st.text_input("IP Address", "192.168.1.103", key="cam3_ip")
with col2:
    cam3_port = st.text_input("Port", "8080", key="cam3_port")

st.markdown("---")

# === System Parameters ===
st.subheader("🌡️ Data Settings")

# Format suhu dropdown
temp_unit = st.selectbox(
    "Temperature Unit",
    ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"],
    index=0
)

refresh_rate = st.selectbox(
    "Data Refresh Rate",
    ["1 second", "3 seconds", "5 seconds", "10 seconds", "30 seconds"],
    index=2
)

st.markdown("---")

# === Notification Settings ===
st.subheader("🔔 Alert Settings")

col1, col2 = st.columns(2)

with col1:
    admin_email = st.text_input("Admin Email", "admin01@company.com")
    admin_email_ = st.text_input("Admin Email", "admin02@company.com")
    
with col2:
    email_alerts = st.checkbox("Email Alerts", value=True)
    sound_alerts = st.checkbox("Sound Alerts", value=True)
    push_notifications = st.checkbox("Push Notifications", value=False)

st.markdown("---")


col1, col2, col3, col4 = st.columns([2, 1, 1, 1])  # Tambah kolom untuk spacing

with col4:  # Kolom paling kanan
    save_settings = st.button(
        "Save Configuration", 
        type="primary", 
        use_container_width=True
    )

# === CSS Styling untuk tombol ===
st.markdown(
    """
    <style>
    /* Styling untuk tombol Save */
    div.stButton > button:first-child {
        background-color: #d43811 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        border: none !important;
        transition: 0.2s !important;
        width: 100% !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #b82f0f !important;
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# === Feedback ===
if save_settings:
    st.success("✅ Configuration saved successfully!")