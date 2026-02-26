import streamlit as st
import google.generativeai as genai
import json
import os
import time

# --- 1. CẤU HÌNH GIAO DIỆN & MÀU PHONG THỦY ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide")

st.markdown("""
<style>
    /* Nền xám xanh nhẹ nhàng */
    .stApp { background-color: #C5D3E8; } 

    /* TIÊU ĐỀ CHÍNH - MÀU PHONG THỦY */
    .main-header { 
        color: #004F98 !important; 
        text-align: center; 
        font-size: 50px !important; 
        font-weight: 900 !important;
        margin-bottom: 20px;
    }

    /* DÒNG CHỮ DESIGN - CANH GIỮA & PHONG THỦY */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: #004F98 !important;
        text-align: center;
        font-weight: bold;
        padding: 15px;
        font-size: 16px;
        letter-spacing: 2px;
        z-index: 100;
    }

    /* Khung làm bài trắng tinh khôi */
    div[data-testid="stForm"] {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        border-top: 10px solid #004F98;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
    }
    
    /* Bảng vàng sang trọng */
    .stTable { background-color: white; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM XỬ LÝ DỮ LIỆU ---
FILES = {"LIB": "quiz_library.json", "ANNUAL": "annual_data.json", "CONFIG": "config.json"}
def load_db(k):
    if os.path.exists(FILES[k]):
        with open(FILES[k], "r", encoding="utf-8") as f: return json.load(f)
    return {} if k != "ANNUAL" else []
def save_db(k, d):
    with open(FILES[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

config = load_db("CONFIG")
library = load_db("LIB")

# --- 3. HÀM AI TỰ ĐỔI SỐ (GIỮ NGUYÊN CẤU TRÚC) ---
def ai_transform(q_list, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Dựa trên 10 bài toán này: {q_list}. Hãy thay đổi con số và tên người nhưng giữ nguyên dạng toán. Trả về đúng định dạng JSON danh sách 10 câu: [{{'q': '...', 'a': '...'}}, ...]"
        response = model.generate_content(prompt)
        # Làm sạch chuỗi JSON từ AI
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
    st.sidebar.header("🔑 QUẢN TRỊ")
    if st.sidebar.text_input("Mật khẩu:", type="password") == "thai2026":
        key = st.sidebar.text_input("Dán Gemini API Key:", value=config.get("api_key", ""), type="password")
        if st.sidebar.button("Lưu cấu hình"): save_db("CONFIG", {"api_key": key})
        
        st.subheader("📝 NHẬP 10 CÂU HỎI MẪU")
        with st.form("admin_form"):
            new_quizzes = []
            cols = st.columns(2)
            for i in range(1, 11):
                with cols[0 if i <= 5 else 1]:
                    q = st.text_input(f"Câu hỏi {i}:", key=f"q{i}")
                    a = st.text_input(f"Đáp án {i}:", key=f"a{i}")
                    new_quizzes.append({"q": q, "a": a})
            
            if st.form_submit_button("🚀 GIAO 10 CÂU NÀY"):
                save_db("LIB", new_quizzes)
                st.success("Đã lưu 10 câu hỏi gốc thành công!")

# ==========================================
# CỔNG HỌC SINH
# ==========================================
else:
    if not library: st.info("Chờ Thầy Thái giao đề nhé!")
    else:
        if 'student_quiz' not in st.session_state:
            with st.spinner("AI đang tạo đề bài mới với các con số khác cho em..."):
                st.session_state.student_quiz = ai_transform(library, config.get("api_key", ""))
                st.session_state.start_time = time.time()

        with st.form("student_form"):
            user_answers = []
            for idx, item in enumerate(st.session_state.student_quiz):
                st.write(f"**Câu {idx+1}:** {item['q']}")
                ans = st.text_input(f"Trả lời câu {idx+1}:", key=f"user_a{idx}")
                user_answers.append(ans)
            
            if st.form_submit_button("✅ NỘP BÀI"):
                correct = 0
                for i, item in enumerate(st.session_state.student_quiz):
                    if user_answers[i].strip() == str(item['a']).strip(): correct += 1
                
                duration = round(time.time() - st.session_state.start_time, 1)
                st.success(f"Kết quả: {correct}/10 câu đúng! Thời gian: {duration} giây.")
                if correct == 10: st.balloons()
                del st.session_state.student_quiz # Đổi số cho lần sau

# --- CHỮ KÝ PHONG THỦY ---
st.markdown('<div class="footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)
