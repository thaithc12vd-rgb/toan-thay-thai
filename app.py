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

    /* NỀN XÁM XANH MỆNH THỦY */
    .stApp { background-color: #C5D3E8; } 

    /* HEADER CỐ ĐỊNH */
    .sticky-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-size: clamp(20px, 5vw, 40px) !important;
        font-weight: 900 !important; padding: 10px 0; z-index: 1000;
        border-bottom: 2px solid rgba(0, 79, 152, 0.2); text-transform: uppercase;
    }

    /* FOOTER CỐ ĐỊNH */
    .sticky-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-weight: bold; padding: 12px 0;
        font-size: 15px; z-index: 1000; border-top: 2px solid rgba(0, 79, 152, 0.2);
    }

    /* VÙNG NỘI DUNG CHÍNH */
    .main-content { margin-top: 100px; margin-bottom: 100px; padding: 0 20px; }

    /* KHUNG TRẮNG PHÂN KHU */
    .admin-card {
        background-color: white; border-radius: 20px; padding: 25px;
        border-top: 10px solid #004F98; box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.05);
        height: 100%;
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

# HIỂN THỊ HEADER/FOOTER
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

params = st.query_params
role = params.get("role", "student")
ma_de_tu_link = params.get("de", "")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ (CHIA CỘT TRÁI - PHẢI)
# ==========================================
if role == "teacher":
    col_left, col_right = st.columns([1, 3], gap="large")

    # --- CỘT BÊN TRÁI: MẬT KHẨU & API ---
    with col_left:
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.subheader("🔑 BẢO MẬT")
        pwd = st.text_input("Mật mã quản trị:", type="password")
        st.divider()
        st.subheader("🤖 CẤU HÌNH AI")
        api_key = st.text_input("Gemini API Key:", value=config.get("api_key", ""), type="password")
        if st.button("LƯU CẤU HÌNH"):
            save_db("CONFIG", {"api_key": api_key})
            st.success("Đã lưu API Key!")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- CỘT BÊN PHẢI: NHẬP LIỆU ĐỀ BÀI ---
    with col_right:
        if pwd == "thai2026":
            st.markdown('<div class="admin-card">', unsafe_allow_html=True)
            st.subheader("📝 BẢNG NHẬP LIỆU CÂU HỎI")
            
            # Chọn đề cũ
            danh_sach_de = ["-- Tạo đề mới --"] + list(library.keys())
            de_chon = st.selectbox("Chọn đề từ thư viện để lấy dữ liệu:", options=danh_sach_de)
            data_to_edit = library.get(de_chon, []) if de_chon != "-- Tạo đề mới --" else []
            
            st.divider()
            
            c_mde, c_num = st.columns([3, 1])
            with c_mde:
                ma_de_moi = st.text_input("Mã đề (Ví dụ: BAI_01):", value=de_chon if de_chon != "-- Tạo đề mới --" else "")
            with c_num:
                num_q = st.number_input("Số câu:", min_value=1, max_value=20, value=len(data_to_edit) if data_to_edit else 5)

            with st.form("admin_form"):
                new_quizzes = []
                col1, col2 = st.columns(2)
                for i in range(1, num_q + 1):
                    v_q = data_to_edit[i-1]["q"] if i <= len(data_to_edit) else ""
                    v_a = data_to_edit[i-1]["a"] if i <= len(data_to_edit) else ""
                    with (col1 if i <= (num_q+1)//2 else col2):
                        q_val = st.text_input(f"Câu hỏi {i}:", value=v_q, key=f"q{i}")
                        a_val = st.text_input(f"Đáp án {i}:", value=v_a, key=f"a{i}")
                        new_quizzes.append({"q": q_val, "a": a_val})
                
                if st.form_submit_button("🚀 LƯU ĐỀ VÀO THƯ VIỆN"):
                    if ma_de_moi:
                        library[ma_de_moi] = new_quizzes
                        save_db("LIB", library)
                        st.success(f"Đã lưu thành công đề: {ma_de_moi}")
                        st.balloons()
                    else: st.error("Thầy chưa nhập mã đề!")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Vui lòng nhập đúng mật mã ở bên trái để mở Bảng nhập liệu.")

# ==========================================
# CỔNG HỌC SINH (Giữ nguyên)
# ==========================================
else:
    if not ma_de_tu_link:
        st.info("Chào các em! Hãy bấm vào link bài tập Thầy Thái gửi để bắt đầu làm nhé.")
    elif ma_de_tu_link not in library:
        st.error(f"Lỗi: Không tìm thấy đề {ma_de_tu_link}")
    else:
        # (AI xử lý và hiển thị đề cho học sinh...)
        if 'active_quiz' not in st.session_state or st.session_state.get('current_de') != ma_de_tu_link:
            try:
                genai.configure(api_key=config.get("api_key", ""))
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Thay đổi số và tên người nhưng giữ nguyên cấu trúc toán: {library[ma_de_tu_link]}. Trả về JSON: [{{'q': '...', 'a': '...'}}, ...]"
                response = model.generate_content(prompt)
                st.session_state.active_quiz = json.loads(response.text.replace('```json', '').replace('```', '').strip())
                st.session_state.current_de = ma_de_tu_link
            except: st.session_state.active_quiz = library[ma_de_tu_link]

        with st.form("student_form"):
            st.markdown(f"### ✍️ ĐỀ BÀI: {ma_de_tu_link}")
            for idx, item in enumerate(st.session_state.active_quiz):
                st.write(f"**Câu {idx+1}:** {item['q']}")
                st.text_input(f"Đáp án {idx+1}:", key=f"user_a{idx}")
            st.form_submit_button("✅ NỘP BÀI")

st.markdown('</div>', unsafe_allow_html=True)
