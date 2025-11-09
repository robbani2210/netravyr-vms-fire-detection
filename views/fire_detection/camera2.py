import streamlit as st
import pandas as pd
import altair as alt
import base64
import numpy as np
from datetime import datetime, timedelta
import os
import base64

# ================================
# PAGE CONFIG
# ================================
st.title("Thermal Flame Detection")

# ================================
# FUNGSI UNTUK MEMOTONG VIDEO YANG LEBIH BAIK
# ================================
def cut_video_by_duration(input_video_path, duration_seconds, output_video_path):
    """Memotong video berdasarkan durasi yang ditentukan dengan codec yang kompatibel"""
    try:
        import cv2
        import os
        
        # Baca video input
        cap = cv2.VideoCapture(input_video_path)
        
        if not cap.isOpened():
            st.error(f"❌ Cannot open video: {input_video_path}")
            return False
        
        # Dapatkan properti video
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        original_duration = total_frames / fps if fps > 0 else 0
        
        st.info(f"📹 Original video: {original_duration:.1f}s, {fps:.1f} FPS, {total_frames} frames")
        
        # Jika FPS = 0, gunakan nilai default
        if fps == 0:
            fps = 30
            st.warning("⚠️ FPS not detected, using default 30 FPS")
        
        # Hitung frame yang dibutuhkan untuk durasi yang diminta
        target_frames = int(duration_seconds * fps)
        
        # Jika durasi yang diminta lebih panjang dari video asli, gunakan video asli
        if duration_seconds > original_duration:
            st.warning(f"⚠️ Requested duration ({duration_seconds}s) is longer than original video ({original_duration:.1f}s). Using original video.")
            cap.release()
            import shutil
            shutil.copy2(input_video_path, output_video_path)
            return True
        
        # Setup video writer - gunakan codec H.264 yang lebih kompatibel
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Jika width/height tidak terdeteksi, gunakan nilai dari frame pertama
        if width == 0 or height == 0:
            ret, frame = cap.read()
            if ret:
                height, width = frame.shape[:2]
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset ke frame 0
            else:
                width, height = 640, 480
                st.warning("⚠️ Video dimensions not detected, using default 640x480")
        
        st.info(f"🎬 Output video: {width}x{height}, {fps} FPS, {target_frames} frames")
        
        # Buat VideoWriter
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            st.error("❌ Cannot create output video writer, trying alternative codec...")
            # Coba codec alternatif
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
            if not out.isOpened():
                st.error("❌ Failed to create video writer with any codec")
                cap.release()
                return False
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Baca dan tulis frame sesuai durasi
        frames_written = 0
        for frame_idx in range(target_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            # Pastikan frame tidak kosong
            if frame is not None and frame.size > 0:
                out.write(frame)
                frames_written += 1
            
            # Update progress setiap 10 frame
            if frame_idx % 10 == 0:
                progress = (frame_idx + 1) / target_frames
                progress_bar.progress(progress)
                status_text.text(f"🔄 Cutting video: {frames_written}/{target_frames} frames")
        
        # Release resources
        cap.release()
        out.release()
        progress_bar.empty()
        status_text.empty()
        
        # Cek jika video berhasil dibuat
        if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
            actual_duration = frames_written / fps
            output_size = os.path.getsize(output_video_path) / (1024*1024)
            st.success(f"✅ Video cut successfully: {actual_duration:.1f}s ({frames_written} frames, {output_size:.2f} MB)")
            return True
        else:
            st.error("❌ Output video file is empty or not created")
            return False
        
    except Exception as e:
        st.error(f"❌ Error cutting video: {str(e)}")
        return False

def get_detection_video(duration_seconds):
    """
    Fungsi untuk mendapatkan video deteksi AI yang sudah dipotong sesuai durasi
    """
    import os
    import tempfile
    
    # Path video hasil deteksi AI (yang sudah ada bounding box)
    AI_DETECTION_VIDEO = r"C:\Users\ROBBANI\Downloads\netraMVA\Camera Hanwha\Dashboard\Design_2\Demo\1-1.mp4"
    
    # Cek jika video hasil deteksi AI ada
    if not os.path.exists(AI_DETECTION_VIDEO):
        st.error(f"❌ AI detection video not found: {AI_DETECTION_VIDEO}")
        st.info("💡 Please make sure the file '1-1.mp4' exists in the Demo folder")
        return None
    
    # Test baca video asli dulu
    st.info("🔍 Testing original video...")
    import cv2
    test_cap = cv2.VideoCapture(AI_DETECTION_VIDEO)
    if test_cap.isOpened():
        ret, test_frame = test_cap.read()
        if ret and test_frame is not None:
            st.success(f"✅ Original video OK: {test_frame.shape[1]}x{test_frame.shape[0]}")
        else:
            st.error("❌ Cannot read frames from original video")
        test_cap.release()
    else:
        st.error("❌ Cannot open original video file")
    
    # Buat file output sementara
    temp_dir = tempfile.gettempdir()
    output_filename = f"detection_{duration_seconds}s.mp4"
    output_path = os.path.join(temp_dir, output_filename)
    
    # Hapus file lama jika ada
    if os.path.exists(output_path):
        os.remove(output_path)
    
    # Potong video sesuai durasi
    st.info(f"✂️ Cutting AI detection video to {duration_seconds} seconds...")
    success = cut_video_by_duration(AI_DETECTION_VIDEO, duration_seconds, output_path)
    
    if success and os.path.exists(output_path):
        return output_path
    else:
        st.error("❌ Failed to cut video, using original video")
        return AI_DETECTION_VIDEO

# ================================
# FUNGSI UNTUK VIDEO DENGAN KONTROL (FIXED)
# ================================
def display_video_with_controls(video_path):
    """Menampilkan video dengan kontrol play/pause"""
    try:
        if not video_path or not os.path.exists(video_path):
            st.error(f"❌ Video file not found: {video_path}")
            return False
            
        # Cek ukuran file
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            st.error("❌ Video file is empty (0 bytes)")
            return False
        
        # Test video dengan OpenCV dulu
        import cv2
        test_cap = cv2.VideoCapture(video_path)
        if test_cap.isOpened():
            ret, frame = test_cap.read()
            test_cap.release()
        else:
            st.error("❌ Video test failed - cannot open file")
                    
        # Baca video sebagai bytes
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
        
        # Tampilkan video dengan kontrol menggunakan st.video
        st.video(video_bytes, format="video/mp4")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error loading video: {e}")
        return False

# ================================
# FUNGSI ALTERNATIF JIKA MASIH GAGAL
# ================================
def simple_video_cutter(input_path, duration_seconds):
    """Alternatif sederhana untuk memotong video"""
    try:
        import subprocess
        import tempfile
        import os
        
        # Gunakan ffmpeg jika tersedia (lebih reliable)
        output_path = os.path.join(tempfile.gettempdir(), f"cut_{duration_seconds}s.mp4")
        
        # Perintah ffmpeg untuk memotong video
        cmd = [
            'ffmpeg', '-i', input_path,
            '-t', str(duration_seconds),
            '-c', 'copy',  # Copy tanpa re-encode
            '-y',  # Overwrite output file
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            st.success("✅ Video cut successfully with ffmpeg")
            return output_path
        else:
            st.error(f"❌ FFmpeg failed: {result.stderr}")
            return None
            
    except Exception as e:
        st.error(f"❌ Alternative method failed: {e}")
        return None

# ================================
# FUNGSI UNTUK VIDEO INPUT TANPA KONTROL (AUTOPLAY)
# ================================
def autoplay_video(video_path):
    """Menampilkan video tanpa kontrol, autoplay, loop, dan mute untuk video input"""
    try:
        if not video_path or not os.path.exists(video_path):
            st.error(f"❌ Video file not found: {video_path}")
            return False
            
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
        st.error(f"❌ Error loading video: {e}")
        return False

# ================================
# SESSION STATE UNTUK INTERAKTIVITAS
# ================================
if 'selected_event' not in st.session_state:
    st.session_state.selected_event = None

if 'show_event_detail' not in st.session_state:
    st.session_state.show_event_detail = False

if 'run_detection' not in st.session_state:
    st.session_state.run_detection = False

if 'detection_video_path' not in st.session_state:
    st.session_state.detection_video_path = None

if 'current_duration' not in st.session_state:
    st.session_state.current_duration = 10

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
import pandas as pd
import numpy as np

np.random.seed(42)
timestamps = pd.date_range(start='2023-10-26 08:00:00', end='2023-10-26 18:00:00', freq='10min')

detection_data = []
for i, ts in enumerate(timestamps[:50]):
    confidence = np.random.uniform(0.6, 0.98)
    
    x = np.random.randint(50, 700)
    y = np.random.randint(50, 500)
    width = np.random.randint(30, 100)
    height = np.random.randint(30, 100)
    bbox = f"[x:{x}, y:{y}, w:{width}, h:{height}]"
    
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
        'avg_bbox_area': avg_bbox_area
    }

# ================================
# 🧭 TAB 1: AI MODEL OVERVIEW
# ================================
with tabs[0]:
    # Jika ada detail event yang diklik
    if st.session_state.show_event_detail and st.session_state.selected_event is not None:
        event = event_history.iloc[st.session_state.selected_event]
        
        st.subheader(f"🖼️ Detection Detail - {event['TIMESTAMP']}")
        
        col1, col2 = st.columns([1.2, 1.5])

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

    # ================================
    # MODE OVERVIEW
    # ================================
    else:
        col_video1, col_video2 = st.columns(2)
        
        # Kolom kiri: kamera input
        with col_video1:
            st.markdown("#### 📹 Camera Input Stream")
            INPUT_VIDEO_PATH = r"C:\Users\ROBBANI\Downloads\netraMVA\Camera Hanwha\Dashboard\Design_2\Demo\1-1 real.mp4"
            
            if os.path.exists(INPUT_VIDEO_PATH):
                video_loaded = autoplay_video(INPUT_VIDEO_PATH)
                if not video_loaded:
                    st.error("❌ Failed to load input video")
            else:
                st.error(f"❌ Input video not found: {INPUT_VIDEO_PATH}")

            # Kontrol Deteksi
            st.markdown("")
            duration_seconds = st.slider(
                "⏱️ Video Duration (seconds)",
                min_value=1,
                max_value=60,
                value=st.session_state.current_duration,
                help="Select duration to from AI detection video",
                label_visibility="visible"
            )
            
            st.session_state.current_duration = duration_seconds

            # Tombol kontrol
            col_clear, col_run = st.columns(2)

            with col_clear:
                if st.button("🗑️ Clear", type="secondary", use_container_width=True):
                    st.session_state.detection_video_path = None
                    st.session_state.run_detection = False
                    st.rerun()

            with col_run:
                if st.button("🎬 Run Detection", type="primary", use_container_width=True):
                    st.session_state.run_detection = True
                    with st.spinner(f"✂️ Cutting AI detection video to {duration_seconds} seconds..."):
                        # Coba metode ffmpeg dulu jika ada
                        ffmpeg_path = simple_video_cutter(
                            r"C:\Users\ROBBANI\Downloads\netraMVA\Camera Hanwha\Dashboard\Design_2\Demo\1-1.mp4",
                            duration_seconds
                        )
                        if ffmpeg_path:
                            st.session_state.detection_video_path = ffmpeg_path
                        else:
                            st.session_state.detection_video_path = get_detection_video(duration_seconds)
                    st.rerun()

        # Kolom kanan: hasil AI detection
        with col_video2:
            st.markdown("#### 🤖 AI Detection Result")
            
            if st.session_state.run_detection and st.session_state.detection_video_path:
                ai_video_path = st.session_state.detection_video_path
                
                if os.path.exists(ai_video_path):
                    file_size = os.path.getsize(ai_video_path) / (1024*1024)
                    
                    # Tampilkan video
                    video_success = display_video_with_controls(ai_video_path)
                    
                    if not video_success:
                        st.error("❌ Failed to display video")
                        
                else:
                    st.error(f"❌ video file not found")
                    
            elif st.session_state.run_detection and not st.session_state.detection_video_path:
                st.error("❌ No video path available")
                
            else:
                # Tampilan awal
                st.markdown(f"""
                <div style="text-align: center; padding: 140px; border: 2px dashed #ccc; border-radius: 10px; background: #f9f9f9;">
                    <h3 style="color: #666;">🚀 Ready to Run Display Detection</h3>
                    <p>Set duration and click "Run Detection"</p>
                </div>
                """, unsafe_allow_html=True)

        # Metrik tambahan
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