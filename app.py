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
    /* ẨN THÀNH PHẦN HỆ THỐNG */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none !important;}

    /* PHONG THỦY MỆNH THỦY */
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

    /* NỘI DUNG CHÍNH */
    .main-content { margin-top: 100px; margin-bottom: 100px; }

    /* KHUNG FORM SOẠN THẢO */
    div[data-testid="stForm"] {
        background-color: white; border-radius: 20px; padding: 30px;
        border-top: 10px solid #004F98; box-shadow: 0px 15px 35px rgba(0, 79, 152, 0.15);
    }

    /* NÚT ĐIỀU KHIỂN GỌN GÀNG GÓC PHẢI */
    .btn-container {
        display: flex;
        justify-content: flex-end;
        margin-top: -20px;
        margin-bottom: 10px;
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

# XỬ LÝ ĐIỀU HƯỚNG
params = st.query_params
role = params.get("role", "student")
ma_de_tu_link = params.get("de", "")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ (NÚT LỆNH GÓC PHẢI)
# ==========================================
if role == "teacher":
    # Trạng thái đóng mở
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = "expanded"

    # NÚT ĐIỀU KHIỂN CHỈ HIỂN THỊ DẤU (Góc trên bên phải)
    col_main, col_btn = st.columns([10, 1])
    with col_btn:
        icon = "❮" if st.session_state.sidebar_state == "expanded" else "❯"
        if st.button(icon, help="Đóng/Mở bảng cài đặt"):
            st.session_state.sidebar_state = "collapsed" if st.session_state.sidebar_state == "expanded" else "expanded"
            st.rerun()

    # Sidebar chứa API và Mật khẩu
    with st.sidebar:
        st.markdown("<h3 style='color:#004F98;'>CÀI ĐẶT</h3>", unsafe_allow_html=True)
        pwd = st.text_input("Mật mã:", type="password")
        if pwd == "thai2026":
            st.success("Đúng!")
            api_key = st.text_input("Gemini API Key:", value=config.get("api_key", ""), type="password")
            if st.button("Lưu"):
                save_db("CONFIG", {"api_key": api_key})
                st.toast("Đã lưu!")
            st.divider()
            danh_sach_de = ["-- Chọn đề cũ --"] + list(library.keys())
            de_chon = st.selectbox("Lấy dữ liệu đề cũ:", options=danh_sach_de)
        else:
            st.warning("Nhập mã để mở cấu hình.")

    # BẢNG NHẬP DỮ LIỆU (HIỂN THỊ CHÍNH GIỮA)
    if pwd == "thai2026":
        data_to_edit = library.get(de_chon, []) if de_chon != "-- Chọn đề cũ --" else []
        
        st.subheader("📝 BẢNG NHẬP DỮ LIỆU CÂU HỎI")
        
        c_mde, c_num = st.columns([3, 1])
        with c_mde:
            ma_de_moi = st.text_input("Mã đề (Ví dụ: BAI_01):", value=de_chon if de_chon != "-- Chọn đề cũ --" else "")
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
            
            if st.form_submit_button("🚀 LƯU VÀO THƯ VIỆN"):
                if ma_de_moi:
                    library[ma_de_moi] = new_quizzes
                    save_db("LIB", library)
                    st.success(f"Đã lưu thành công đề: {ma_de_moi}")
                    st.rerun()
                else: st.error("Chưa có mã đề!")

# ==========================================
# CỔNG HỌC SINH (Giữ nguyên)
# ==========================================
else:
    # (Phần xử lý đề cho học sinh)
    if not ma_de_tu_link:
        st.info("Chào các em! Hãy bấm vào link bài tập Thầy Thái gửi để bắt đầu nhé.")
    elif ma_de_tu_link not in library:
        st.error(f"Không tìm thấy mã đề: {ma_de_tu_link}")
    else:
        if 'active_quiz' not in st.session_state or st.session_state.get('current_de') != ma_de_tu_link:
            genai.configure(api_key=config.get("api_key", ""))
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Thay đổi số và tên người nhưng giữ nguyên cấu trúc toán: {library[ma_de_tu_link]}. Trả về JSON: [{{'q': '...', 'a': '...'}}, ...]"
            try:
                response = model.generate_content(prompt)
                st.session_state.active_quiz = json.loads(response.text.replace('```json', '').replace('```', '').strip())
                st.session_state.current_de = ma_de_tu_link
                st.session_state.start_time = time.time()
            except:
                st.session_state.active_quiz = library[ma_de_tu_link]

        with st.form("student_form"):
            st.markdown(f"### ✍️ ĐỀ BÀI: {ma_de_tu_link}")
            for idx, item in enumerate(st.session_state.active_quiz):
                st.write(f"**Câu {idx+1}:** {item['q']}")
                st.text_input(f"Đáp án {idx+1}:", key=f"user_a{idx}")
            st.form_submit_button("✅ NỘP BÀI")

st.markdown('</div>', unsafe_allow_html=True)
