import streamlit as st
import google.generativeai as genai
import json
import os
import time
import pandas as pd

# --- 1. CẤU HÌNH GIAO DIỆN & GHIM TIÊU ĐỀ/CHÂN TRANG ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide", page_icon="🎓")

st.markdown("""
<style>
    /* ẨN CÁC THÀNH PHẦN HỆ THỐNG */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none !important;}

    /* NỀN XÁM XANH PHONG THỦY */
    .stApp { background-color: #C5D3E8; } 

    /* GHIM TIÊU ĐỀ CỐ ĐỊNH PHÍA TRÊN */
    .sticky-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #C5D3E8;
        color: #004F98 !important;
        text-align: center;
        font-size: clamp(25px, 5vw, 45px) !important;
        font-weight: 900 !important;
        padding: 10px 0;
        z-index: 1000;
        border-bottom: 2px solid rgba(0, 79, 152, 0.2);
        text-transform: uppercase;
    }

    /* GHIM CHỮ DESIGN CỐ ĐỊNH PHÍA DƯỚI */
    .sticky-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #C5D3E8;
        color: #004F98 !important;
        text-align: center;
        font-weight: bold;
        padding: 15px 0;
        font-size: 16px;
        z-index: 1000;
        border-top: 2px solid rgba(0, 79, 152, 0.2);
        letter-spacing: 2px;
    }

    /* ĐẨY NỘI DUNG FORM RA KHỎI VÙNG BỊ GHIM */
    .main-content {
        margin-top: 100px;
        margin-bottom: 100px;
    }

    div[data-testid="stForm"] {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        border-top: 10px solid #004F98;
        box-shadow: 0px 15px 35px rgba(0, 79, 152, 0.15);
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

# --- HIỂN THỊ CÁC THÀNH PHẦN CỐ ĐỊNH (HEADER & FOOTER) ---
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

# BẮT ĐẦU VÙNG NỘI DUNG CHÍNH (Có lề để không bị đè)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# --- 3. HÀM AI ---
def ai_transform(q_list, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Thay đổi số và tên nhưng giữ nguyên dạng toán: {q_list}. Trả về JSON: [{{'q': '...', 'a': '...'}}, ...]"
        response = model.generate_content(prompt)
        return json.loads(response.text.replace('```json', '').replace('```', '').strip())
    except: return q_list

params = st.query_params
role = params.get("role", "student")
ma_de_tu_link = params.get("de", "")

# ==========================================
# CỔNG QUẢN TRỊ (THẦY THÁI)
# ==========================================
if role == "teacher":
    st.sidebar.header("🔑 QUẢN TRỊ")
    if st.sidebar.text_input("Mật mã:", type="password") == "thai2026":
        key = st.sidebar.text_input("API Key:", value=config.get("api_key", ""), type="password")
        if st.sidebar.button("Lưu API Key"): save_db("CONFIG", {"api_key": key})
        
        st.subheader("📁 QUẢN LÝ KHO ĐỀ")
        # Chức năng chọn đề cũ để sửa
        danh_sach_de = ["-- Chọn đề --"] + list(library.keys())
        de_duoc_chon = st.selectbox("🎯 Chọn đề từ thư viện để hiện lên ô nhập:", options=danh_sach_de)
        
        data_to_edit = library.get(de_duoc_chon, []) if de_duoc_chon != "-- Chọn đề --" else []
        
        ma_de_moi = st.text_input("Mã đề:", value=de_duoc_chon if de_duoc_chon != "-- Chọn đề --" else "")
        num_q = st.number_input("Số câu:", min_value=1, max_value=20, value=len(data_to_edit) if data_to_edit else 5)
        
        with st.form("admin_form"):
            new_quizzes = []
            c1, c2 = st.columns(2)
            for i in range(1, num_q + 1):
                val_q = data_to_edit[i-1]["q"] if i <= len(data_to_edit) else ""
                val_a = data_to_edit[i-1]["a"] if i <= len(data_to_edit) else ""
                with (c1 if i <= (num_q+1)//2 else c2):
                    q = st.text_input(f"Câu {i}:", value=val_q, key=f"q{i}")
                    a = st.text_input(f"Đáp án {i}:", value=val_a, key=f"a{i}")
                    new_quizzes.append({"q": q, "a": a})
            if st.form_submit_button("🚀 LƯU VÀO THƯ VIỆN"):
                if ma_de_moi:
                    library[ma_de_moi] = new_quizzes
                    save_db("LIB", library)
                    st.success(f"Đã lưu đề '{ma_de_moi}'!")
                else: st.error("Thiếu mã đề!")

# ==========================================
# CỔNG HỌC SINH
# ==========================================
else:
    if not ma_de_tu_link:
        st.info("Chào các em! Hãy bấm vào link bài tập Thầy gửi nhé.")
    elif ma_de_tu_link not in library:
        st.error(f"Lỗi: Không tìm thấy đề {ma_de_tu_link}")
    else:
        if 'active_quiz' not in st.session_state or st.session_state.get('current_de') != ma_de_tu_link:
            st.session_state.active_quiz = ai_transform(library[ma_de_tu_link], config.get("api_key", ""))
            st.session_state.current_de = ma_de_tu_link
        
        with st.form("student_form"):
            st.markdown(f"### ✍️ ĐỀ BÀI: {ma_de_tu_link}")
            for idx, item in enumerate(st.session_state.active_quiz):
                st.write(f"**Câu {idx+1}:** {item['q']}")
                st.text_input(f"Đáp án {idx+1}:", key=f"user_a{idx}")
            st.form_submit_button("✅ NỘP BÀI")

st.markdown('</div>', unsafe_allow_html=True) # Kết thúc main-content
