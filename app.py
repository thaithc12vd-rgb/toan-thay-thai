import streamlit as st
import google.generativeai as genai
import json
import os
import time
import pandas as pd
import io

# --- 1. CẤU HÌNH GIAO DIỆN & DIỆT NÚT MANAGE APP ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide", page_icon="🎓")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    .stApp { background-color: #C5D3E8; } 
    .main-header { 
        color: #004F98 !important; text-align: center; font-weight: 900 !important;
        margin-top: -85px; margin-bottom: 10px; text-transform: uppercase;
    }
    .footer-design {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-weight: bold; padding: 15px 0; font-size: 16px; z-index: 999;
    }
    div[data-testid="stForm"] {
        background-color: white; border-radius: 20px; padding: 30px;
        border-top: 10px solid #004F98; box-shadow: 0px 15px 35px rgba(0, 79, 152, 0.15);
        margin-bottom: 100px;
    }
    .link-display-box {
        background-color: #ffffff; border: 2px solid #004F98; padding: 10px;
        border-radius: 8px; color: #d32f2f; font-family: monospace; word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU ---
FILES = {"LIB": "quiz_library.json", "CONFIG": "config.json"}
def load_db(k):
    if os.path.exists(FILES[k]):
        with open(FILES[k], "r", encoding="utf-8") as f: return json.load(f)
    return {}
def save_db(k, d):
    with open(FILES[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

config = load_db("CONFIG")
library = load_db("LIB")

# --- 3. HÀM AI ---
def ai_transform(q_list, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Thay đổi số và tên người nhưng giữ nguyên dạng toán: {q_list}. Trả về JSON: [{{'q': '...', 'a': '...'}}, ...]"
        response = model.generate_content(prompt)
        return json.loads(response.text.replace('```json', '').replace('```', '').strip())
    except: return q_list

# --- 4. HIỂN THỊ TIÊU ĐỀ ---
st.markdown('<h1 class="main-header">TOÁN LỚP 3 - THẦY THÁI</h1>', unsafe_allow_html=True)

params = st.query_params
role = params.get("role", "student")
ma_de_tu_link = params.get("de", "")

# ==========================================
# CỔNG QUẢN TRỊ (THẦY THÁI)
# ==========================================
if role == "teacher":
    st.sidebar.header("🔑 QUẢN TRỊ")
    if st.sidebar.text_input("Mật mã:", type="password") == "thai2026":
        key = st.sidebar.text_input("Gemini API Key:", value=config.get("api_key", ""), type="password")
        if st.sidebar.button("Lưu API Key"): save_db("CONFIG", {"api_key": key})
        
        st.subheader("📁 QUẢN LÝ KHO ĐỀ")
        
        # --- A. TẢI FILE MẪU & UP FILE ---
        col_file1, col_file2 = st.columns(2)
        with col_file1:
            df_mau = pd.DataFrame([{"Câu hỏi": "Ví dụ: 15 + 10 = ?", "Đáp án": "25"}])
            csv = df_mau.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải file mẫu (CSV)", data=csv, file_name="mau_de_toan.csv", mime="text/csv")
        
        with col_file2:
            uploaded_file = st.file_uploader("📤 Up file đề đã soạn", type=["csv"])
        
        # --- B. LỰA CHỌN ĐỀ ĐÃ LƯU ---
        danh_sach_de = ["-- Chọn đề để sửa --"] + list(library.keys())
        de_duoc_chon = st.selectbox("🎯 Xem/Sửa đề trong thư viện:", options=danh_sach_de)
        
        # Đổ dữ liệu vào các ô nhập
        data_to_edit = []
        if uploaded_file:
            df_up = pd.read_csv(uploaded_file)
            data_to_edit = [{"q": row["Câu hỏi"], "a": str(row["Đáp án"])} for _, row in df_up.iterrows()]
            st.success("Đã tải dữ liệu từ file!")
        elif de_duoc_chon != "-- Chọn đề để sửa --":
            data_to_edit = library[de_duoc_chon]
        
        st.divider()
        
        # --- C. NHẬP MÃ ĐỀ & TẠO LINK ---
        ma_de_moi = st.text_input("1. Nhập mã đề mới (hoặc tên đề đang sửa):", value=de_duoc_chon if de_duoc_chon != "-- Chọn đề để sửa --" else "")
        current_url = "https://toan-lop-3-thay-thai.streamlit.app" # SỬA ĐÚNG LINK APP CỦA THẦY
        st.write("🔗 **Link gửi học sinh:**")
        st.markdown(f'<div class="link-display-box">{current_url}/?de={ma_de_moi}</div>', unsafe_allow_html=True)

        num_q = st.number_input("2. Số lượng câu hỏi:", min_value=1, max_value=20, value=len(data_to_edit) if data_to_edit else 5)
        
        with st.form("admin_form"):
            new_quizzes = []
            c1, c2 = st.columns(2)
            for i in range(1, num_q + 1):
                # Lấy giá trị mặc định nếu đang ở chế độ sửa hoặc up file
                default_q = data_to_edit[i-1]["q"] if i <= len(data_to_edit) else ""
                default_a = data_to_edit[i-1]["a"] if i <= len(data_to_edit) else ""
                
                with (c1 if i <= (num_q+1)//2 else c2):
                    q = st.text_input(f"Câu {i}:", value=default_q, key=f"q{i}")
                    a = st.text_input(f"Đáp án {i}:", value=default_a, key=f"a{i}")
                    new_quizzes.append({"q": q, "a": a})
            
            if st.form_submit_button("🚀 LƯU VÀO THƯ VIỆN"):
                if ma_de_moi:
                    library[ma_de_moi] = new_quizzes
                    save_db("LIB", library)
                    st.success(f"Đã lưu đề '{ma_de_moi}'!")
                    st.rerun()
                else: st.error("Vui lòng nhập mã đề!")

# ==========================================
# CỔNG HỌC SINH (Giữ nguyên như cũ)
# ==========================================
else:
    if not ma_de_tu_link:
        st.info("Chào các em! Hãy bấm vào link bài tập Thầy Thái gửi nhé.")
    elif ma_de_tu_link not in library:
        st.error(f"Không tìm thấy bài tập: {ma_de_tu_link}")
    else:
        if 'active_quiz' not in st.session_state or st.session_state.get('current_de') != ma_de_tu_link:
            st.session_state.active_quiz = ai_transform(library[ma_de_tu_link], config.get("api_key", ""))
            st.session_state.current_de = ma_de_tu_link
            st.session_state.start_time = time.time()

        with st.form("student_form"):
            st.markdown(f"<h3 style='color:#004F98; text-align:center;'>✍️ ĐỀ BÀI: {ma_de_tu_link}</h3>", unsafe_allow_html=True)
            for idx, item in enumerate(st.session_state.active_quiz):
                st.write(f"**Câu {idx+1}:** {item['q']}")
                st.text_input(f"Đáp án {idx+1}:", key=f"user_a{idx}")
            if st.form_submit_button("✅ NỘP BÀI"):
                st.balloons()

st.markdown('<div class="footer-design">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)
