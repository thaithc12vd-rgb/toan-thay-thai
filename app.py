import streamlit as st
import google.generativeai as genai
import json
import os
import time

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
        color: #004F98 !important; 
        text-align: center; 
        font-size: clamp(30px, 5vw, 50px) !important; 
        font-weight: 900 !important;
        margin-top: -85px;
        margin-bottom: 10px;
    }
    .footer-design {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-weight: bold; padding: 15px 0;
        font-size: 16px; z-index: 999;
    }
    div[data-testid="stForm"] {
        background-color: white; border-radius: 20px; padding: 30px;
        border-top: 10px solid #004F98; box-shadow: 0px 15px 35px rgba(0, 79, 152, 0.15);
        margin-bottom: 100px;
    }
    .link-display-box {
        background-color: #ffffff;
        border: 2px solid #004F98;
        padding: 10px;
        border-radius: 8px;
        color: #d32f2f;
        font-family: monospace;
        font-size: 14px;
        margin-top: 5px;
        word-break: break-all;
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

# --- 3. HÀM AI BIẾN ĐỔI ---
def ai_transform(q_list, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Thay đổi số và tên người nhưng giữ nguyên dạng toán: {q_list}. Trả về JSON: [{{'q': '...', 'a': '...'}}, ...]"
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except: return q_list

# --- 4. HIỂN THỊ TIÊU ĐỀ ---
st.markdown('<h1 class="main-header">TOÁN LỚP 3 - THẦY THÁI</h1>', unsafe_allow_html=True)

# LẤY THÔNG TIN TỪ URL HIỆN TẠI ĐỂ TỰ ĐỘNG TẠO LINK ĐÚNG
# Kỹ thuật dùng st.query_params để đọc tham số
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
        if st.sidebar.button("Lưu cấu hình"): save_db("CONFIG", {"api_key": key})
        
        st.subheader("📝 SOẠN ĐỀ VÀ TẠO LINK")
        
        # Ô NHẬP MÃ ĐỀ TỰ DO
        ma_de_moi = st.text_input("1. Nhập mã đề Thầy muốn (Ví dụ: BAI_01):", value="")
        
        # TỰ ĐỘNG LẤY DOMAIN CỦA APP ĐỂ TẠO LINK (Fix lỗi Not Found)
        # Nếu đang chạy trên máy tính (localhost), nó sẽ lấy localhost. 
        # Nếu chạy trên web, nó sẽ lấy đúng tên miền .streamlit.app
        try:
            # Lấy URL gốc từ trang web đang mở
            current_url = "https://toan-lop-3-thay-thai.streamlit.app" # Thầy hãy sửa dòng này duy nhất 1 lần cho đúng link app của Thầy
            if ma_de_moi:
                full_link = f"{current_url}/?de={ma_de_moi}"
            else:
                full_link = current_url
        except:
            full_link = "Vui lòng nhập mã đề để tạo link"

        st.write("🔗 **Link gửi học sinh (Hãy bôi đen và Copy dòng này):**")
        st.markdown(f'<div class="link-display-box">{full_link}</div>', unsafe_allow_html=True)
        
        num_q = st.number_input("2. Số lượng câu hỏi:", min_value=1, max_value=20, value=5)
        
        with st.form("admin_form"):
            new_quizzes = []
            c1, c2 = st.columns(2)
            for i in range(1, num_q + 1):
                with (c1 if i <= (num_q+1)//2 else c2):
                    q = st.text_input(f"Câu hỏi {i}:", key=f"q{i}")
                    a = st.text_input(f"Đáp án {i}:", key=f"a{i}")
                    new_quizzes.append({"q": q, "a": a})
            
            if st.form_submit_button("🚀 LƯU ĐỀ VÀO THƯ VIỆN"):
                if ma_de_moi:
                    library[ma_de_moi] = new_quizzes
                    save_db("LIB", library)
                    st.success(f"Đã lưu thành công đề: {ma_de_moi}")
                else:
                    st.warning("Thầy hãy nhập tên đề ở mục 1 trước khi Lưu nhé!")

# ==========================================
# CỔNG HỌC SINH
# ==========================================
else:
    if not ma_de_tu_link:
        st.info("Chào các em! Hãy bấm vào link bài tập Thầy Thái gửi trong Zalo nhé.")
    elif ma_de_tu_link not in library:
        st.error(f"Không tìm thấy bài tập mã: {ma_de_tu_link}. Em kiểm tra lại link Thầy gửi nhé!")
    else:
        if 'active_quiz' not in st.session_state or st.session_state.get('current_de') != ma_de_tu_link:
            with st.spinner("Đang chuẩn bị đề bài riêng cho em..."):
                st.session_state.active_quiz = ai_transform(library[ma_de_tu_link], config.get("api_key", ""))
                st.session_state.current_de = ma_de_tu_link
                st.session_state.start_time = time.time()

        with st.form("student_form"):
            st.markdown(f"<h3 style='color:#004F98; text-align:center;'>✍️ ĐỀ BÀI: {ma_de_tu_link}</h3>", unsafe_allow_html=True)
            user_answers = []
            for idx, item in enumerate(st.session_state.active_quiz):
                st.write(f"**Câu {idx+1}:** {item['q']}")
                ans = st.text_input(f"Đáp án {idx+1}:", key=f"user_a{idx}")
                user_answers.append(ans)
            
            if st.form_submit_button("✅ NỘP BÀI"):
                correct = 0
                for i, item in enumerate(st.session_state.active_quiz):
                    if user_answers[i].strip() == str(item['a']).strip(): correct += 1
                st.success(f"Kết quả: {correct}/{len(st.session_state.active_quiz)} câu đúng!")
                if correct == len(st.session_state.active_quiz): st.balloons()
                del st.session_state.active_quiz

st.markdown('<div class="footer-design">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)
