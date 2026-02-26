import streamlit as st
import google.generativeai as genai
import json
import os
import time

# --- 1. CẤU HÌNH GIAO DIỆN & KHÓA HỆ THỐNG TRIỆT ĐỂ ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide", page_icon="🎓")

# MÃ CSS & JAVASCRIPT TỔNG LỰC ĐỂ DIỆT NÚT MANAGE APP
hide_st_style = """
<style>
    /* Ẩn hoàn toàn các thành phần mặc định của Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Truy quét và ẩn tất cả các loại nút Deploy/Manage app */
    .stDeployButton {display:none !important;}
    button[data-testid="stDeployButton"] {display:none !important;}
    div[data-testid="stToolbar"] {display:none !important;}
    div[data-testid="stDecoration"] {display:none !important;}
    #stDecoration {display:none !important;}
    
    /* Ẩn thanh trạng thái góc trên */
    div[data-testid="stStatusWidget"] {display:none !important;}
    
    /* PHONG THỦY MỆNH THỦY */
    .stApp { background-color: #C5D3E8; } 
    
    .main-header { 
        color: #004F98 !important; 
        text-align: center; 
        font-size: clamp(30px, 5vw, 50px) !important; 
        font-weight: 900 !important;
        margin-top: -85px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    
    .footer-design {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #C5D3E8;
        color: #004F98 !important;
        text-align: center;
        font-weight: bold;
        padding: 15px 0;
        font-size: 16px;
        z-index: 9999;
        border-top: 1px solid rgba(0, 79, 152, 0.1);
    }
    
    /* KHUNG FORM */
    div[data-testid="stForm"] {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        border-top: 10px solid #004F98;
        box-shadow: 0px 15px 35px rgba(0, 79, 152, 0.15);
        margin-bottom: 100px;
    }
</style>

<script>
    // Xóa sổ nút Manage App ngay khi nó vừa xuất hiện trong DOM
    const hideManageApp = () => {
        const buttons = window.parent.document.getElementsByTagName('button');
        for (let btn of buttons) {
            if (btn.innerText.includes('Manage app') || btn.getAttribute('data-testid') === 'stDeployButton') {
                btn.style.display = 'none';
                btn.style.visibility = 'hidden';
            }
        }
        const toolbar = window.parent.document.querySelector('div[data-testid="stToolbar"]');
        if (toolbar) toolbar.style.display = 'none';
    };
    
    // Chạy liên tục để quét
    setInterval(hideManageApp, 100);
</script>
"""

st.markdown(hide_st_style, unsafe_allow_html=True)

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

# --- 3. HÀM AI BIẾN ĐỔI ---
def ai_transform(q_list, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        n = len(q_list)
        prompt = f"Thay đổi số và tên người trong {n} bài toán này: {q_list}. Giữ nguyên dạng toán. Trả về JSON: [{{'q': '...', 'a': '...'}}, ...]"
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except: return q_list

# --- 4. HIỂN THỊ TIÊU ĐỀ ---
st.markdown('<h1 class="main-header">TOÁN LỚP 3 - THẦY THÁI</h1>', unsafe_allow_html=True)

role = st.query_params.get("role", "student")

# CỔNG QUẢN TRỊ
if role == "teacher":
    st.sidebar.header("🔑 QUẢN TRỊ")
    if st.sidebar.text_input("Mật mã:", type="password") == "thai2026":
        key = st.sidebar.text_input("Gemini API Key:", value=config.get("api_key", ""), type="password")
        if st.sidebar.button("Lưu cấu hình"): save_db("CONFIG", {"api_key": key})
        
        num_q = st.number_input("Lựa chọn số câu:", min_value=1, max_value=20, value=len(library) if library else 5)
        st.subheader(f"📝 SOẠN {num_q} CÂU HỎI GỐC")
        with st.form("admin_form"):
            new_quizzes = []
            col1, col2 = st.columns(2)
            for i in range(1, num_q + 1):
                with (col1 if i <= (num_q + 1) // 2 else col2):
                    q = st.text_input(f"Câu hỏi {i}:", key=f"q{i}")
                    a = st.text_input(f"Đáp án {i}:", key=f"a{i}")
                    new_quizzes.append({"q": q, "a": a})
            if st.form_submit_button(f"🚀 CẬP NHẬT {num_q} CÂU NÀY"):
                save_db("LIB", new_quizzes)
                st.success("Đã cập nhật!")

# CỔNG HỌC SINH
else:
    if not library: 
        st.info("Chào các em! Thầy Thái đang chuẩn bị bài tập nhé!")
    else:
        if 'student_quiz' not in st.session_state:
            with st.spinner("AI đang tạo đề bài mới cho em..."):
                st.session_state.student_quiz = ai_transform(library, config.get("api_key", ""))
                st.session_state.start_time = time.time()

        with st.form("student_form"):
            st.markdown(f"<h3 style='color:#004F98; text-align:center;'>✍️ THỬ THÁCH {len(st.session_state.student_quiz)} CÂU TOÁN</h3>", unsafe_allow_html=True)
            user_answers = []
            for idx, item in enumerate(st.session_state.student_quiz):
                st.write(f"**Câu {idx+1}:** {item['q']}")
                ans = st.text_input(f"Đáp án câu {idx+1}:", key=f"user_a{idx}")
                user_answers.append(ans)
            if st.form_submit_button("✅ NỘP BÀI"):
                correct = 0
                for i, item in enumerate(st.session_state.student_quiz):
                    if user_answers[i].strip() == str(item['a']).strip(): correct += 1
                st.success(f"Kết quả: {correct}/{len(st.session_state.student_quiz)} câu đúng!")
                if correct == len(st.session_state.student_quiz): st.balloons()
                del st.session_state.student_quiz

# CHỮ KÝ PHONG THỦY - LUÔN HIỂN THỊ CHÍNH GIỮA
st.markdown('<div class="footer-design">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)
