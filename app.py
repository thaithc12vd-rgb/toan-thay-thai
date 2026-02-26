import streamlit as st
import google.generativeai as genai
import json
import os
import time

# --- 1. CẤU HÌNH GIAO DIỆN & PHONG THỦY TUYỆT ĐỐI ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide", page_icon="🎓")

st.markdown("""
<style>
    /* ẨN CHỮ MANAGE APP VÀ MENU HỆ THỐNG */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    .reportview-container .main footer {visibility: hidden;}

    /* NỀN XÁM XANH MỆNH THỦY */
    .stApp { background-color: #C5D3E8; } 

    /* TIÊU ĐỀ CHÍNH - XANH ĐẠI DƯƠNG */
    .main-header { 
        color: #004F98 !important; 
        text-align: center; 
        font-size: 50px !important; 
        font-weight: 900 !important;
        margin-top: -30px;
        margin-bottom: 10px;
    }

    /* CHỮ DESIGN - CANH GIỮA & PHONG THỦY (HIỆN CHO TẤT CẢ) */
    .footer-design {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(197, 211, 232, 0.9); /* Tiệp màu nền */
        color: #004F98 !important;
        text-align: center;
        font-weight: bold;
        padding: 10px;
        font-size: 16px;
        letter-spacing: 2px;
        z-index: 999;
    }

    /* KHUNG LÀM BÀI TRẮNG SẠCH SẼ */
    div[data-testid="stForm"] {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        border-top: 10px solid #004F98;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 60px; /* Tránh đè lên footer */
    }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU ---
FILES = {"LIB": "quiz_library.json", "CONFIG": "config.json"}
def load_db(k):
    if os.path.exists(FILES[k]):
        with open(FILES[k], "r", encoding="utf-8") as f: return json.load(f)
    return {} if k == "CONFIG" else []
def save_db(k, d):
    with open(FILES[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

config = load_db("CONFIG")
library = load_db("LIB")

# --- 3. HÀM AI BIẾN ĐỔI 10 CÂU (GIỮ CẤU TRÚC) ---
def ai_transform(q_list, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Dựa trên 10 bài toán này: {q_list}. Hãy thay đổi con số và tên người nhưng giữ nguyên dạng toán. Trả về đúng định dạng JSON danh sách 10 câu: [{{'q': '...', 'a': '...'}}, ...]"
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except: return q_list

# --- 4. HIỂN THỊ TIÊU ĐỀ ---
st.markdown('<h1 class="main-header">TOÁN LỚP 3 - THẦY THÁI</h1>', unsafe_allow_html=True)

role = st.query_params.get("role", "student")

# ==========================================
# CỔNG QUẢN TRỊ (THẦY THÁI)
# ==========================================
if role == "teacher":
    st.sidebar.header("🔑 QUẢN TRỊ VIÊN")
    if st.sidebar.text_input("Nhập mật mã:", type="password") == "thai2026":
        key = st.sidebar.text_input("Dán Gemini API Key:", value=config.get("api_key", ""), type="password")
        if st.sidebar.button("Lưu cấu hình"): save_db("CONFIG", {"api_key": key})
        
        st.subheader("📝 SOẠN 10 CÂU HỎI GỐC")
        with st.form("admin_form"):
            new_quizzes = []
            col_a, col_b = st.columns(2)
            for i in range(1, 11):
                with (col_a if i <= 5 else col_b):
                    q = st.text_input(f"Câu hỏi {i}:", key=f"q{i}")
                    a = st.text_input(f"Đáp án {i}:", key=f"a{i}")
                    new_quizzes.append({"q": q, "a": a})
            
            if st.form_submit_button("🚀 CẬP NHẬT 10 CÂU NÀY"):
                save_db("LIB", new_quizzes)
                st.success("Đã cập nhật thư viện đề gốc!")

# ==========================================
# CỔNG HỌC SINH
# ==========================================
else:
    if not library: 
        st.info("Chào các em! Thầy Thái đang chuẩn bị bài tập, các em quay lại sau nhé!")
    else:
        if 'student_quiz' not in st.session_state:
            with st.spinner("Đang kết nối AI để tạo đề bài mới cho em..."):
                st.session_state.student_quiz = ai_transform(library, config.get("api_key", ""))
                st.session_state.start_time = time.time()

        with st.form("student_form"):
            st.markdown("<h3 style='color:#004F98;'>✍️ BÀI TẬP THỬ THÁCH</h3>", unsafe_allow_html=True)
            user_answers = []
            for idx, item in enumerate(st.session_state.student_quiz):
                st.write(f"**Câu {idx+1}:** {item['q']}")
                ans = st.text_input(f"Kết quả câu {idx+1}:", key=f"user_a{idx}")
                user_answers.append(ans)
            
            if st.form_submit_button("✅ NỘP BÀI CHO THẦY"):
                correct = 0
                for i, item in enumerate(st.session_state.student_quiz):
                    if user_answers[i].strip() == str(item['a']).strip(): correct += 1
                
                duration = round(time.time() - st.session_state.start_time, 1)
                st.success(f"Kết quả: {correct}/10 câu đúng! Thời gian: {duration} giây.")
                if correct == 10: st.balloons()
                # Tự động xóa bài cũ để lần sau làm sẽ là số mới
                del st.session_state.student_quiz

# --- DÒNG CHỮ THƯƠNG HIỆU - LUÔN HIỂN THỊ ---
st.markdown('<div class="footer-design">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)
