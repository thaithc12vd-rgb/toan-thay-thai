import streamlit as st
import json
import os
import time

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #C5D3E8; }
    .main-header { color: #004F98; text-align: center; font-size: 35px; font-weight: 900; }
    div[data-testid="stForm"] { background-color: white; border-radius: 15px; padding: 20px; border-top: 8px solid #004F98; }
</style>
""", unsafe_allow_html=True)

# --- HÀM XỬ LÝ DỮ LIỆU VĨNH CỬU ---
FILES = {
    "LIB": "quiz_library.json",   # Thư viện đề bài
    "HIS": "user_history.json",   # Lượt làm (20 lần/em)
    "ANNUAL": "annual_top10.json" # Bảng vàng cả năm
}

def load_db(key):
    file = FILES[key]
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f: return json.load(f)
    return {} if key != "ANNUAL" else []

def save_db(key, data):
    with open(FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Khởi tạo dữ liệu
library = load_db("LIB")
history = load_db("HIS")
annual = load_db("ANNUAL")

# --- PHÂN QUYỀN ---
is_teacher = st.query_params.get("role") == "teacher"

# --- GIAO DIỆN ---
if is_teacher:
    st.markdown("<h2 style='text-align: center;'>👨‍🏫 CỔNG GIAO ĐỀ VĨNH CỬU</h2>", unsafe_allow_html=True)
    pass_input = st.sidebar.text_input("Mật khẩu quản trị:", type="password")
    if pass_input == "thai2026":
        with st.form("add_quiz"):
            q_id = st.text_input("Mã đề mới (Ví dụ: DE_01):")
            q_json = st.text_area("Nội dung câu hỏi (JSON):")
            if st.form_submit_button("LƯU ĐỀ VÀO THƯ VIỆN"):
                library[q_id] = json.loads(q_json)
                save_db("LIB", library)
                st.success(f"Đã lưu thành công đề {q_id}!")
else:
    st.markdown('<h1 class="main-header">TOÁN LỚP 3 - THẦY THÁI</h1>', unsafe_allow_html=True)
    
    if not library:
        st.info("Thầy Thái đang soạn đề, các em quay lại sau nhé!")
    else:
        q_selected = st.selectbox("🎯 CHỌN BÀI TOÁN:", list(library.keys()))
        tab1, tab2 = st.tabs(["✍️ LÀM BÀI", "🏆 BẢNG VÀNG CẢ NĂM"])
        
        with tab1:
            name = st.text_input("Họ và tên của em:")
            if name:
                key = f"{name}_{q_selected}"
                attempts = history.get(key, 0)
                if attempts >= 20:
                    st.error("Em đã hết 20 lượt làm bài này!")
                else:
                    st.warning(f"Lượt làm: {attempts}/20")
                    with st.form("do_quiz"):
                        # Logic hiển thị đề...
                        if st.form_submit_button("NỘP BÀI"):
                            history[key] = attempts + 1
                            save_db("HIS", history)
                            st.balloons()