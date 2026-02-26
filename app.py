import streamlit as st
import google.generativeai as genai
import json
import os
import time
import pandas as pd

# --- 1. CẤU HÌNH GIAO DIỆN & GHIM CỐ ĐỊNH ---
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
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-size: clamp(20px, 5vw, 40px) !important;
        font-weight: 900 !important; padding: 10px 0; z-index: 1000;
        border-bottom: 2px solid rgba(0, 79, 152, 0.2); text-transform: uppercase;
    }

    /* GHIM CHỮ DESIGN CỐ ĐỊNH PHÍA DƯỚI */
    .sticky-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-weight: bold; padding: 12px 0;
        font-size: 15px; z-index: 1000; border-top: 2px solid rgba(0, 79, 152, 0.2);
    }

    /* VÙNG NỘI DUNG CHÍNH */
    .main-content { margin-top: 80px; margin-bottom: 80px; }

    div[data-testid="stForm"] {
        background-color: white; border-radius: 20px; padding: 30px;
        border-top: 10px solid #004F98; box-shadow: 0px 15px 35px rgba(0, 79, 152, 0.15);
    }

    /* TÙY CHỈNH SIDEBAR (TAB QUẢN TRỊ) */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-right: 3px solid #004F98;
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

# HIỂN THỊ HEADER/FOOTER CỐ ĐỊNH
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

# --- 3. HÀM AI ---
def ai_transform(q_list, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Thay đổi số và tên người nhưng giữ nguyên cấu trúc toán: {q_list}. Trả về JSON: [{{'q': '...', 'a': '...'}}, ...]"
        response = model.generate_content(prompt)
        return json.loads(response.text.replace('```json', '').replace('```', '').strip())
    except: return q_list

# --- XỬ LÝ ĐIỀU HƯỚNG ---
params = st.query_params
role = params.get("role", "student")
ma_de_tu_link = params.get("de", "")

# VÙNG NỘI DUNG CHÍNH
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ (CÓ NÚT THU NHỎ/MỞ RỘNG)
# ==========================================
if role == "teacher":
    # Streamlit có sẵn nút ">" và "<" ở góc trên thanh Sidebar
    with st.sidebar:
        st.markdown("<h2 style='color:#004F98;'>⚙️ HỆ THỐNG</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Nhập mật mã quản trị:", type="password")
        
        if pwd == "thai2026":
            st.success("Đã xác thực!")
            api_key = st.text_input("Gemini API Key:", value=config.get("api_key", ""), type="password")
            if st.button("Lưu cấu hình"):
                save_db("CONFIG", {"api_key": api_key})
                st.toast("Đã lưu API Key!")
            
            st.divider()
            st.write("📂 **KHO DỮ LIỆU**")
            danh_sach_de = ["-- Chọn đề --"] + list(library.keys())
            de_chon = st.selectbox("Lấy dữ liệu từ đề cũ:", options=danh_sach_de)
        else:
            st.warning("Vui lòng nhập đúng mật mã để mở API & Kho đề.")

    # PHẦN SOẠN THẢO CHÍNH (Hiện ở giữa màn hình)
    if pwd == "thai2026":
        data_to_edit = library.get(de_chon, []) if de_chon != "-- Chọn đề --" else []
        
        col_title1, col_title2 = st.columns([2, 1])
        with col_title1:
            ma_de_moi = st.text_input("📝 Đặt mã đề (Ví dụ: TUAN_1):", value=de_chon if de_chon != "-- Chọn đề --" else "")
        with col_title2:
            num_q = st.number_input("🔢 Số lượng câu:", min_value=1, max_value=20, value=len(data_to_edit) if data_to_edit else 5)

        with st.form("admin_form"):
            new_quizzes = []
            c1, c2 = st.columns(2)
            for i in range(1, num_q + 1):
                val_q = data_to_edit[i-1]["q"] if i <= len(data_to_edit) else ""
                val_a = data_to_edit[i-1]["a"] if i <= len(data_to_edit) else ""
                with (c1 if i <= (num_q+1)//2 else c2):
                    q_input = st.text_input(f"Câu {i}:", value=val_q, key=f"q{i}")
                    a_input = st.text_input(f"Đáp án {i}:", value=val_a, key=f"a{i}")
                    new_quizzes.append({"q": q_input, "a": a_input})
            
            if st.form_submit_button("🚀 LƯU VÀO THƯ VIỆN & CẬP NHẬT LINK"):
                if ma_de_moi:
                    library[ma_de_moi] = new_quizzes
                    save_db("LIB", library)
                    st.success(f"Đã lưu thành công đề '{ma_de_moi}'!")
                else: st.error("Thầy chưa nhập mã đề!")

# ==========================================
# CỔNG HỌC SINH (Giữ nguyên)
# ==========================================
else:
    if not ma_de_tu_link:
        st.info("Chào các em! Hãy bấm vào link bài tập Thầy Thái gửi để bắt đầu nhé.")
    elif ma_de_tu_link not in library:
        st.error(f"Không tìm thấy mã đề: {ma_de_tu_link}")
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

st.markdown('</div>', unsafe_allow_html=True)
