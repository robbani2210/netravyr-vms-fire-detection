import streamlit as st
import pandas as pd
import altair as alt
import base64
import numpy as np
from datetime import datetime, timedelta

# ================================
# PAGE CONFIG
# ================================
st.title("Thermal Flame Detection")

# ================================
# FUNGSI UNTUK VIDEO TANPA KONTROL
# ================================
def autoplay_video(video_path):
    """Menampilkan video tanpa kontrol, autoplay, loop, dan mute"""
    try:
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
        video_base64 = base64.b64encode(video_bytes).decode()
        
        video_html = f"""
        <div style="border: 2px solid #ff4b4b; border-radius: 10px; overflow: hidden;">
            <video width="100%" autoplay loop muted playsinline style="display: block;">
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        """
        st.markdown(video_html, unsafe_allow_html=True)
        return True
    except Exception as e:
        st.error(f"Error loading video: {e}")
        return False

# ================================
# SESSION STATE UNTUK INTERAKTIVITAS
# ================================
if 'selected_event' not in st.session_state:
    st.session_state.selected_event = None

if 'show_event_detail' not in st.session_state:
    st.session_state.show_event_detail = False

# ================================
# TABS
# ================================
tabs = st.tabs([
    "🧭 AI Model Overview",
    "📊 Detection Analytics", 
    "⚙️ Model Parameters",
    "📝 System Notes"
])

# ================================
# DATA SAMPLE UNTUK OBJECT DETECTION MODEL
# ================================
# Generate lebih banyak data untuk scatter chart yang lebih informatif
np.random.seed(42)
timestamps = pd.date_range(start='2023-10-26 08:00:00', end='2023-10-26 18:00:00', freq='10min')

# Generate data deteksi api dengan variasi confidence dan bounding box
detection_data = []
for i, ts in enumerate(timestamps[:50]):  # Ambil 50 data point
    confidence = np.random.uniform(0.6, 0.98)
    
    # Generate bounding box coordinates yang realistis
    x = np.random.randint(50, 700)
    y = np.random.randint(50, 500)
    width = np.random.randint(30, 100)
    height = np.random.randint(30, 100)
    bbox = f"[x:{x}, y:{y}, w:{width}, h:{height}]"
    
    # Kategori berdasarkan confidence
    if confidence >= 0.9:
        event_type = "High Confidence Flame"
        color = "#00b050"
    elif confidence >= 0.7:
        event_type = "Medium Confidence Flame" 
        color = "#e6a700"
    else:
        event_type = "Low Confidence Flame"
        color = "#ff4b4b"
    
    detection_data.append({
        "TIMESTAMP": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "EVENT_TYPE": event_type,
        "MODEL_USED": "YOLOv8-Flame",
        "CONFIDENCE": confidence,
        "BOUNDING_BOX": bbox,
        "BBOX_WIDTH": width,
        "BBOX_HEIGHT": height,
        "BBOX_AREA": width * height,
        "COLOR": color,
        "CLASS": "Flame"
    })

event_history = pd.DataFrame(detection_data)

# ================================
# FUNGSI UNTUK STYLING
# ================================
def style_event_type(val):
    if "High Confidence" in val:
        return "color: #00b050; font-weight: bold;"
    elif "Medium Confidence" in val:
        return "color: #e6a700; font-weight: bold;"
    elif "Low Confidence" in val:
        return "color: #ff4b4b; font-weight: bold;"
    return ""

def style_confidence(val):
    if val is None:
        return ""
    elif val >= 0.9:
        return "color: #00b050; font-weight: bold;"
    elif val >= 0.7:
        return "color: #e6a700; font-weight: bold;"
    else:
        return "color: #ff4b4b; font-weight: bold;"

def color_severity(val):
    color_map = {"High": "#ff4b4b", "Medium": "#e6a700", "Low": "#00b050"}
    color = color_map.get(val, "#ffffff")
    return f"background-color: {color}20; color: {color}; font-weight: bold; text-align:center;"

def color_priority(val):
    color_map = {"High": "#ff4b4b", "Medium": "#e6a700", "Low": "#00b050"}
    color = color_map.get(val, "#666666")
    return f"color: {color}; font-weight: bold;"

# ================================
# FUNGSI UNTUK DETECTION STATISTICS
# ================================
def get_detection_stats(df):
    """Generate detection statistics untuk dashboard"""
    total_detections = len(df)
    high_confidence = len(df[df['CONFIDENCE'] >= 0.9])
    medium_confidence = len(df[(df['CONFIDENCE'] >= 0.7) & (df['CONFIDENCE'] < 0.9)])
    low_confidence = len(df[df['CONFIDENCE'] < 0.7])
    
    avg_confidence = df['CONFIDENCE'].mean()
    avg_bbox_area = df['BBOX_AREA'].mean()
    
    return {
        'total_detections': total_detections,
        'avg_confidence': avg_confidence,
        'high_confidence': high_confidence,
        'medium_confidence': medium_confidence,
        'low_confidence': low_confidence,
        'avg_bbox_area': avg_bbox_area,
        'high_confidence_rate': high_confidence / total_detections if total_detections > 0 else 0
    }

# ================================
# FUNGSI UNTUK MENGAMBIL GAMBAR LOKAL
# ================================
def get_local_detection_image(second_index):
    """
    Fungsi untuk mendapatkan path gambar lokal berdasarkan index detik
    Sesuaikan dengan struktur folder dan penamaan file Anda
    """
    import os
    import glob
    
    # Definisikan path folder gambar lokal Anda
    # Ganti dengan path folder Anda yang sebenarnya
    IMAGE_FOLDER = r"C:\Users\ROBBANI\Downloads\netraMVA\Camera Hanwha\Dashboard\Design_2\Demo\1-1 frames"
    
    # Beberapa contoh pattern penamaan file yang mungkin:
    patterns = [
        f"detection_{second_index + 1}.jpg",
        f"detection_{second_index + 1}.png", 
        f"frame_{second_index + 1}.jpg",
        f"frame_{second_index + 1}.png",
        f"output_{second_index + 1}.jpg",
        f"output_{second_index + 1}.png",
        f"image_{second_index + 1}.jpg",
        f"image_{second_index + 1}.png",
    ]
    
    # Cari file yang sesuai dengan pattern
    for pattern in patterns:
        file_path = os.path.join(IMAGE_FOLDER, pattern)
        if os.path.exists(file_path):
            return file_path
    
    # Jika tidak ditemukan, coba cari file dengan ekstensi umum
    all_images = glob.glob(os.path.join(IMAGE_FOLDER, "*.jpg")) + \
                 glob.glob(os.path.join(IMAGE_FOLDER, "*.png")) + \
                 glob.glob(os.path.join(IMAGE_FOLDER, "*.jpeg"))
    
    # Urutkan file dan ambil berdasarkan index (jika file terurut)
    if all_images and second_index < len(all_images):
        sorted_images = sorted(all_images)
        return sorted_images[second_index]
    
    # Fallback ke GIF jika tidak ada gambar lokal
    return "https://media.giphy.com/media/l0HlGSD6Q0eKzowb6/giphy.gif"

# ================================
# 🧭 TAB 1: AI MODEL OVERVIEW
# ================================
with tabs[0]:
    # Jika ada detail event yang diklik
    if st.session_state.show_event_detail and st.session_state.selected_event is not None:
        event = event_history.iloc[st.session_state.selected_event]
        
        st.subheader(f"🖼️ Detection Detail - {event['TIMESTAMP']}")
        
        col1, col2 = st.columns([1.2, 1.5])

        # Kolom kiri: bounding box simulasi
        with col1:
            bbox_info = event['BOUNDING_BOX']
            st.markdown(f"""
            <div style="border: 2px solid #ff4b4b; border-radius: 10px; padding: 20px; text-align: center; background: #f8f9fa;">
                <div style="width: 100%; height: 300px; background: linear-gradient(45deg, #2c3e50, #34495e); 
                            border-radius: 8px; position: relative; display: flex; align-items: center; justify-content: center;">
                    <div style="border: 3px solid {event['COLOR']}; position: absolute; 
                                width: {min(event['BBOX_WIDTH']*0.8, 150)}px; 
                                height: {min(event['BBOX_HEIGHT']*0.8, 120)}px; 
                                top: 40%; left: 30%; background: rgba(255, 75, 75, 0.1);">
                        <span style="position: absolute; top: -25px; left: 0; background: {event['COLOR']}; color: white; 
                                    padding: 2px 8px; font-size: 12px; border-radius: 4px;">
                            Flame: {event['CONFIDENCE']:.1%}
                        </span>
                    </div>
                    <span style="color: white; font-weight: bold;">BOUNDING BOX: {bbox_info}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"🔥 {event['EVENT_TYPE']} - Area: {event['BBOX_AREA']} pixels²")

        # Kolom kanan: informasi deteksi
        with col2:
            st.markdown("### 📌 Detection Information")
            st.write(f"**Timestamp:** {event['TIMESTAMP']}")
            st.write(f"**Event Type:** {event['EVENT_TYPE']}")
            st.write(f"**Model Used:** {event['MODEL_USED']}")
            st.write(f"**Confidence Score:** {event['CONFIDENCE']:.2%}")
            st.write(f"**Bounding Box:** {event['BOUNDING_BOX']}")
            st.write(f"**BBox Area:** {event['BBOX_AREA']} pixels²")
            st.write(f"**Class:** {event['CLASS']}")
            
            st.markdown("---")
            st.markdown("### 📊 Detection Metrics")
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            col_p1.metric("Confidence", f"{event['CONFIDENCE']*100:.1f}%")
            col_p2.metric("BBox Width", f"{event['BBOX_WIDTH']}px")
            col_p3.metric("BBox Height", f"{event['BBOX_HEIGHT']}px")
            col_p4.metric("BBox Area", f"{event['BBOX_AREA']}px²")
            
            if st.button("← Back to Overview"):
                st.session_state.show_event_detail = False
                st.session_state.selected_event = None
                st.rerun()

    # ================================
    # MODE OVERVIEW
    # ================================
    else:
        col_video1, col_video2 = st.columns(2)
        
        # Kolom kiri: kamera input
        with col_video1:
            st.markdown("#### 📹 Camera Input Stream")
            VIDEO_PATH = r"C:\Users\ROBBANI\Downloads\netraMVA\Camera Hanwha\Dashboard\Design_2\Demo\1-1 real.mp4"
            
            video_loaded = autoplay_video(VIDEO_PATH)
            if not video_loaded:
                fallback_gif = "https://media.giphy.com/media/l0HlGSD6Q0eKzowb6/giphy.gif"
                st.image(fallback_gif, caption="Camera Input Stream", use_container_width=True)

            # --- Kontrol Deteksi (slider + tombol) ---
            st.markdown("")
            duration_seconds = st.slider(
                "⏱️ Duration (seconds)",
                min_value=1,
                max_value=60,
                value=10,
                help="Select how many seconds of detection output to display",
                label_visibility="visible"
            )

            # TOMBOL DITUKAR POSISI DAN STRETCH SAMA LEBAR
            col_clear, col_run = st.columns(2)  # Ditukar urutannya

            with col_clear:
                if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                    st.session_state.detection_images = []
                    st.session_state.current_card_index = 0
                    st.session_state.run_detection = False
                    st.session_state.current_second = 0
                    st.rerun()

            with col_run:
                if st.button("🎬 Run Detection", type="primary", use_container_width=True):
                    st.session_state.run_detection = True
                    st.session_state.current_second = 0
                    st.session_state.detection_images = []
                    st.session_state.current_card_index = 0
                    st.rerun()

        # Kolom kanan: hasil AI detection
        with col_video2:
            st.markdown("#### 🤖 AI Model Detection Output")

            if 'run_detection' not in st.session_state:
                st.session_state.run_detection = False
            if 'current_second' not in st.session_state:
                st.session_state.current_second = 0
            if 'detection_images' not in st.session_state:
                st.session_state.detection_images = []
            if 'current_card_index' not in st.session_state:
                st.session_state.current_card_index = 0

            # Jalankan simulasi deteksi
            if st.session_state.run_detection:
                progress_bar = st.progress(st.session_state.current_second / duration_seconds)
                st.info(f"🔄 Generating detection output: {st.session_state.current_second + 1}/{duration_seconds} seconds")

                if len(st.session_state.detection_images) <= st.session_state.current_second:
                    # GUNAKAN GAMBAR LOKAL DARI FOLDER
                    local_image_path = get_local_detection_image(st.session_state.current_second)
                    
                    st.session_state.detection_images.append({
                        'image': local_image_path,
                        'second': st.session_state.current_second + 1,
                        'timestamp': f"Second {st.session_state.current_second + 1}"
                    })

                if st.session_state.current_second < duration_seconds - 1:
                    st.session_state.current_second += 1
                    st.rerun()
                else:
                    st.session_state.run_detection = False

            # --- Tampilkan hasil deteksi ---
            if st.session_state.detection_images:
                current_data = st.session_state.detection_images[st.session_state.current_card_index]

                # Tampilkan gambar lokal
                try:
                    st.image(
                        current_data['image'],
                        use_container_width=True,
                        caption=f"Detection Output - {current_data['timestamp']}"
                    )
                except Exception as e:
                    st.error(f"Error loading image: {e}")
                    # Fallback ke GIF jika gambar lokal tidak tersedia
                    st.image(
                        "https://media.giphy.com/media/l0HlGSD6Q0eKzowb6/giphy.gif",
                        use_container_width=True,
                        caption=f"Detection Output - {current_data['timestamp']} (Fallback)"
                    )

                st.markdown("""
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # --- Navigasi Card yang Lebih Rapi ---
                total_cards = len(st.session_state.detection_images)
                current_card = st.session_state.current_card_index + 1
                
                # Layout navigasi yang lebih proporsional
                col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns([1, 1, 2, 1, 1])
                
                with col_nav1:
                    if st.button("⏮️", help="First card", use_container_width=True):
                        st.session_state.current_card_index = 0
                        st.rerun()
                
                with col_nav2:
                    if st.button("◀️", help="Previous card", use_container_width=True) and st.session_state.current_card_index > 0:
                        st.session_state.current_card_index -= 1
                        st.rerun()
                
                with col_nav3:
                    # Center indicator dengan styling yang lebih baik
                    st.markdown(f"""
                    <div style="text-align: center; padding: 5px; background: #f0f2f6; border-radius: 8px;">
                        <strong>Card {current_card} of {total_cards}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    # Progress bar yang lebih kecil
                    st.progress(current_card / total_cards)
                
                with col_nav4:
                    if st.button("▶️", help="Next card", use_container_width=True) and st.session_state.current_card_index < total_cards - 1:
                        st.session_state.current_card_index += 1
                        st.rerun()
                
                with col_nav5:
                    if st.button("⏭️", help="Last card", use_container_width=True):
                        st.session_state.current_card_index = total_cards - 1
                        st.rerun()

            else:
                st.markdown("""
                <div style="text-align: center; padding: 160px; border: 2px dashed #ccc; border-radius: 10px; background: #f9f9f9;">
                    <h3 style="color: #666;">🚀 Ready to Display Detection Output</h3>
                    <p>Set the duration and click "Run Detection" to generate detection cards</p>
                </div>
                """, unsafe_allow_html=True)

        # ================================
        # METRIK TAMBAHAN DI BAWAHNYA
        # ================================
        st.markdown("---")
        stats = get_detection_stats(event_history)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Detections", stats['total_detections'])
            st.metric("Average Confidence", f"{stats['avg_confidence']:.1%}")
        with col2:
            st.metric("High Confidence", stats['high_confidence'])
            st.metric("Medium Confidence", stats['medium_confidence'])
        with col3:
            st.metric("Low Confidence", stats['low_confidence'])
            st.metric("Avg BBox Area", f"{stats['avg_bbox_area']:.0f} px²")


# ================================
# 📊 TAB 2: DETECTION ANALYTICS
# ================================
with tabs[1]:
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Confidence Distribution Over Time")
        
        # Scatter plot confidence vs time dengan size seragam
        scatter_timeline = alt.Chart(event_history).mark_circle(size=60).encode(  # Size seragam 60
            x=alt.X('TIMESTAMP:T', title='Time', axis=alt.Axis(format='%H:%M')),
            y=alt.Y('CONFIDENCE:Q', title='Confidence Score', scale=alt.Scale(domain=[0.5, 1.0])),
            color=alt.Color('EVENT_TYPE:N', 
                           scale=alt.Scale(
                               domain=['High Confidence Flame', 'Medium Confidence Flame', 'Low Confidence Flame'],
                               range=['#00b050', '#e6a700', '#ff4b4b']
                           )),
            tooltip=['TIMESTAMP', 'EVENT_TYPE', 'CONFIDENCE', 'BOUNDING_BOX']
        ).properties(
            height=400,
            title="Flame Detection Confidence Over Time"
        )
        
        # Tambahkan threshold lines
        threshold_line_90 = alt.Chart(pd.DataFrame({'y': [0.9]})).mark_rule(
            color='#00b050', strokeDash=[5, 5], strokeWidth=2
        ).encode(y='y:Q')
        
        threshold_line_70 = alt.Chart(pd.DataFrame({'y': [0.7]})).mark_rule(
            color='#e6a700', strokeDash=[5, 5], strokeWidth=2
        ).encode(y='y:Q')
        
        final_chart = scatter_timeline + threshold_line_90 + threshold_line_70
        st.altair_chart(final_chart, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Detection Summary")
        
        stats = get_detection_stats(event_history)
        
        st.metric("Total Flame Detections", stats['total_detections'])
        st.metric("High Confidence", stats['high_confidence'])
        st.metric("Medium Confidence", stats['medium_confidence'])
        st.metric("Low Confidence", stats['low_confidence'])
    
    st.markdown("---")
    st.subheader("📋 Recent Flame Detections")
    
    # Display events dengan informasi lengkap
    display_df = event_history.tail(10).copy()
    display_df = display_df[['TIMESTAMP', 'EVENT_TYPE', 'CONFIDENCE', 'BOUNDING_BOX', 'BBOX_AREA']]
    display_df['CONFIDENCE'] = display_df['CONFIDENCE'].apply(lambda x: f"{x:.1%}")
    display_df.index = range(1, len(display_df) + 1)
    display_df.index.name = "No"
    
    styled_df = display_df.style.applymap(style_event_type, subset=["EVENT_TYPE"])
    st.dataframe(styled_df, use_container_width=True, height=300)

# ================================
# ⚙️ TAB 3: MODEL PARAMETERS
# ================================
with tabs[2]:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🛠️ Flame Detection Model Configuration")
        
        model = st.selectbox(
            "Select Detection Model", 
            ["YOLOv8-Flame", "RetinaNet-Fire", "YOLOv8-Smoke", "ThermalVision-Pro"],
            help="Choose the object detection model for flame detection"
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.65, 
            step=0.05,
            help="Minimum confidence score for flame detection"
        )
        
        iou_threshold = st.slider(
            "IoU Threshold", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.65, 
            step=0.05,
            help="Intersection over Union threshold for NMS"
        )

        Overlap_Threshold = st.slider(
            "Overlap Threshold", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.65, 
            step=0.05,
            help="Intersection over Union threshold for NMS"
        )

    with col2:
        st.subheader("🎯 Bounding Box Parameters")
        
        min_box_size = st.slider(
            "Minimum Box Size (pixels)",
            min_value=10,
            max_value=100,
            value=25,
            help="Minimum bounding box size to consider as valid detection"
        )
        
        max_box_size = st.slider(
            "Maximum Box Size (pixels)", 
            min_value=100,
            max_value=500,
            value=300,
            help="Maximum bounding box size to consider as valid detection"
        )
        
        aspect_ratio_min = st.number_input(
            "Min Aspect Ratio",
            min_value=0.1,
            max_value=2.0,
            value=0.5,
            step=0.1,
            help="Minimum aspect ratio for valid detections"
        )
        
        aspect_ratio_max = st.number_input(
            "Max Aspect Ratio", 
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.1,
            help="Maximum aspect ratio for valid detections"
        )
    
    st.markdown("---")
    
    st.subheader("🔧 Processing Settings")
    
    processing_mode = st.radio(
        "Inference Mode",
        ["Real-time (Fast)", "Balanced", "High Accuracy"],
        index=0,
        help="Trade-off between speed and accuracy"
    )
    
    alert_confidence = st.slider(
        "Alert Confidence Threshold", 
        min_value=0.5, 
        max_value=0.95, 
        value=0.8,
        help="Minimum confidence to trigger fire alerts"
    )
    
    col_apply, col_reset, _ = st.columns([1, 1, 4])
    
    with col_apply:
        if st.button("💾 Apply Configuration", use_container_width=True):
            st.success(f"✅ {model} configuration applied successfully!")
    
    with col_reset:
        if st.button("🔄 Reset to Default", use_container_width=True):
            st.warning("Model configuration reset to default values")

# ================================
# 📝 TAB 4: SYSTEM NOTES
# ================================
with tabs[3]:
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### ✍️ Add Detection Observation")
        
        note_title = st.text_input("Observation Title", placeholder="Enter observation title...")
        
        note_category = st.selectbox(
            "Observation Category",
            ["Model Performance", "False Positive", "Confidence Pattern", 
             "Bounding Box Issue", "Environmental Factor", "Calibration"],
            key="flame_notes_category"
        )
        
        note_content = st.text_area(
            "Observation Details",
            placeholder="Describe flame detection patterns, confidence issues, or bounding box behavior...",
            height=150,
            key="flame_notes_content"
        )
        
        col_save, col_clear = st.columns(2)
        with col_save:
            if st.button("💾 Save Observation", use_container_width=True, key="save_flame_note"):
                if note_title.strip() and note_content.strip():
                    st.success("✅ Flame detection observation saved!")
                else:
                    st.warning("⚠️ Please fill in both title and content")
        
        with col_clear:
            if st.button("🗑️ Clear Form", use_container_width=True, key="clear_flame_form"):
                st.rerun()
    
    with col2:
        st.markdown("#### 📋 Recent Observations")
        
        recent_notes = pd.DataFrame({
            "Title": [
                "High confidence detections during daylight",
                "False positives with reflective surfaces", 
                "Bounding box size consistent across detections",
                "Confidence drop in smoky conditions",
                "Improved detection with model retraining"
            ],
            "Date": [
                "2023-10-26", "2023-10-25", "2023-10-24",
                "2023-10-23", "2023-10-22"
            ],
            "Category": ["Performance", "False Positive", "BBox Analysis", 
                        "Environment", "Model Update"],
        })
        
        recent_notes.index = range(1, len(recent_notes) + 1)
        recent_notes.index.name = "No"
        
        st.table(recent_notes)