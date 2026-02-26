import streamlit as st
import google.generativeai as genai
import json
import os
import time
import pandas as pd

# --- 1. CẤU HÌNH GIAO DIỆN & KHÓA HỆ THỐNG ---
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
    .main-content { margin-top: 100px; margin-bottom: 100px; }

    div[data-testid="stForm"] {
        background-color: white; border-radius: 20px; padding: 30px;
        border-top: 10px solid #004F98; box-shadow: 0px 15px 35px rgba(0, 79, 152, 0.15);
    }

    /* NÚT ĐÓNG MỞ QUẢN TRỊ TÙY CHỈNH */
    .stButton > button {
        background-color: #004F98 !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
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

# --- XỬ LÝ ĐIỀU HƯỚNG ---
params = st.query_params
role = params.get("role", "student")
ma_de_tu_link = params.get("de", "")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ (NÚT ĐÓNG MỞ LUÔN HIỂN THỊ)
# ==========================================
if role == "teacher":
    # Sử dụng State để nhớ trạng thái đóng/mở
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = "expanded"

    # Nút bấm thủ công để đổi trạng thái
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        label = "◀ THU NHỎ QUẢN TRỊ" if st.session_state.sidebar_state == "expanded" else "▶ MỞ RỘNG QUẢN TRỊ"
        if st.button(label):
            st.session_state.sidebar_state = "collapsed" if st.session_state.sidebar_state == "expanded" else "expanded"
            st.rerun()

    # Áp dụng trạng thái cho Sidebar (Hệ thống Streamlit sẽ tự đóng mở)
    # Lưu ý: Thầy cũng có thể dùng nút < > mặc định ở góc trái
    with st.sidebar:
        st.markdown("<h3 style='color:#004F98;'>⚙️ CÀI ĐẶT BẢO MẬT</h3>", unsafe_allow_html=True)
        pwd = st.text_input("Nhập mật mã:", type="password")
        
        if pwd == "thai2026":
            st.success("Xác nhận thành công!")
            api_key = st.text_input("Gemini API Key:", value=config.get("api_key", ""), type="password")
            if st.button("LƯU CẤU HÌNH"):
                save_db("CONFIG", {"api_key": api_key})
                st.toast("Đã lưu!")
            st.divider()
            danh_sach_de = ["-- Chọn đề cũ --"] + list(library.keys())
            de_chon = st.selectbox("Lấy dữ liệu từ thư viện:", options=danh_sach_de)
        else:
            st.info("Nhập mật mã để mở Kho đề và API.")

    # VÙNG SOẠN THẢO
    if pwd == "thai2026":
        data_to_edit = library.get(de_chon, []) if de_chon != "-- Chọn đề cũ --" else []
        ma_de_moi = st.text_input("📝 Mã đề:", value=de_chon if de_chon != "-- Chọn đề cũ --" else "")
        num_q = st.number_input("🔢 Số câu:", min_value=1, max_value=20, value=len(data_to_edit) if data_to_edit else 5)

        with st.form("admin_form"):
            new_quizzes = []
            c1, c2 = st.columns(2)
            for i in range(1, num_q + 1):
                v_q = data_to_edit[i-1]["q"] if i <= len(data_to_edit) else ""
                v_a = data_to_edit[i-1]["a"] if i <= len(data_to_edit) else ""
                with (c1 if i <= (num_q+1)//2 else c2):
                    q_in = st.text_input(f"Câu {i}:", value=v_q, key=f"q{i}")
                    a_in = st.text_input(f"Đáp án {i}:", value=v_a, key=f"a{i}")
                    new_quizzes.append({"q": q_in, "a": a_in})
            
            if st.form_submit_button("🚀 LƯU VÀO THƯ VIỆN"):
                if ma_de_moi:
                    library[ma_de_moi] = new_quizzes
                    save_db("LIB", library)
                    st.success("Đã lưu!")
                else: st.error("Chưa có mã đề!")

# ==========================================
# CỔNG HỌC SINH
# ==========================================
else:
    # (Giữ nguyên phần hiển thị đề cho học sinh như bản trước)
    pass

st.markdown('</div>', unsafe_allow_html=True)
