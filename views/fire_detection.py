import streamlit as st
import pandas as pd
import altair as alt


# ------------------------------
# Sidebar: AI Model Configuration
# ------------------------------
st.sidebar.header("AI Model Configuration")

model = st.sidebar.selectbox(
    "Select Model",
    ["Model A (Default)", "Model B", "Model C"],
)

threshold = st.sidebar.text_input("Threshold", "0.85")
min_area = st.sidebar.text_input("Minimum Area (pixels)", "50")
frame_history = st.sidebar.text_input("Frame History", "10")

apply_btn = st.sidebar.button("Apply Configuration")

if apply_btn:
    st.sidebar.success(f"Configuration applied for {model}")

# ------------------------------
# Sidebar: Feedback
# ------------------------------
st.sidebar.markdown("---")
st.sidebar.header("AI Model Feedback")
feedback = st.sidebar.text_area("Provide feedback on model performance...")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Feedback submitted. Thank you!")

# ------------------------------
# Main Content
# ------------------------------
st.title("🔥 Advanced Fire Detection Analysis")

# === Section 1: Predictive Analytics ===
st.subheader("📊 Predictive Analytics")
st.markdown("**Fire Risk Prediction (Next 24h)**")

# Metrik ringkasan
col1, col2 = st.columns([1, 3])
with col1:
    st.metric(label="Fire Risk Level", value="High", delta="↑ 15%")

with col2:
    # Grafik prediksi dummy 24 jam
    hours = list(range(0, 25, 4))
    values = [40, 60, 55, 70, 80, 60, 75]
    df_pred = pd.DataFrame({"Hour": hours, "Risk": values})
    chart = (
        alt.Chart(df_pred)
        .mark_area(line={"color": "#d43811"})
        .encode(
            x=alt.X("Hour", title="Next 24h"),
            y=alt.Y("Risk", title="Risk Level (%)", scale=alt.Scale(domain=[0, 100])),
        )
        .properties(height=180)
    )
    st.altair_chart(chart, use_container_width=True)

# === Section 2: Anomaly Detection ===
st.subheader("🚨 Anomaly Detection")

anomaly_data = pd.DataFrame(
    {
        "Timestamp": [
            "2024-03-15 14:30",
            "2024-03-15 14:45",
            "2024-03-15 15:00",
            "2024-03-15 15:15",
            "2024-03-15 15:30",
        ],
        "Location": ["Section A", "Section B", "Section C", "Section D", "Section E"],
        "Severity": ["High", "Medium", "Low", "Medium", "High"],
    }
)

# Pewarnaan otomatis berdasarkan severity
def color_severity(val):
    color_map = {"High": "#ff4b4b", "Medium": "#e6a700", "Low": "#00b050"}
    color = color_map.get(val, "#ffffff")
    return f"background-color: {color}20; color: {color}; font-weight: bold; text-align:center;"

styled_anomaly = anomaly_data.style.applymap(
    color_severity, subset=["Severity"]
)

st.dataframe(styled_anomaly, use_container_width=True, height=220)

# === Section 3: AI-Detected Events History ===
st.subheader("📜 AI-Detected Events History")

history_data = pd.DataFrame(
    {
        "Timestamp": [
            "2024-03-14 10:00",
            "2024-03-14 12:00",
            "2024-03-14 14:00",
            "2024-03-14 16:00",
            "2024-03-14 18:00",
        ],
        "Location": ["Section A", "Section B", "Section C", "Section D", "Section E"],
        "Event Type": ["Fire", "Smoke", "Heat Anomaly", "Fire", "Smoke"],
        "Confidence": ["95%", "80%", "70%", "90%", "85%"],
    }
)

st.dataframe(history_data, use_container_width=True, height=250)

# Footer
st.markdown("---")
st.caption("© 2025 Hanwha Thermal AI Dashboard – Powered by Streamlit")
