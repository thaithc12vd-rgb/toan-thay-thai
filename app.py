import streamlit as st
import google.generativeai as genai
import json
import os
import time

# --- 1. CẤU HÌNH PHONG THỦY (MỆNH THỦY) ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #C5D3E8; } /* Nền xám xanh */
    .main-header { color: #004F98; text-align: center; font-size: 40px; font-weight: 900; }
    .footer { position: fixed; bottom: 10px; width: 100%; text-align: center; color: #004F98; font-weight: bold; letter-spacing: 1px; }
    div[data-testid="stForm"] { background-color: white; border-radius: 15px; padding: 25px; border-top: 10px solid #004F98; box-shadow: 0px 10px 20px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU ---
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
def ai_generate_new_quiz(original_q, original_a, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Dựa trên bài toán: '{original_q}' với đáp án '{original_a}'. Hãy thay đổi các con số và tên riêng nhưng GIỮ NGUYÊN cấu trúc và dạng toán. Nếu là hình học, chỉ đổi số đo, giữ nguyên số cạnh. Trả về đúng định dạng: Câu hỏi: [nội dung] | Đáp án: [số]"
        response = model.generate_content(prompt)
        return response.text.strip()
    except: return f"Câu hỏi: {original_q} | Đáp án: {original_a}"

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown('<h1 class="main-header">TOÁN LỚP 3 - THẦY THÁI</h1>', unsafe_allow_html=True)

role = st.query_params.get("role", "student")
if role == "teacher":
    st.sidebar.header("🔑 QUẢN TRỊ")
    if st.sidebar.text_input("Mật khẩu:", type="password") == "thai2026":
        key = st.sidebar.text_input("Dán Gemini API Key vào đây:", value=config.get("api_key", ""), type="password")
        if st.sidebar.button("Lưu cấu hình"): save_db("CONFIG", {"api_key": key})
        st.subheader("📝 Giao đề bài mẫu")
        txt = st.text_area("Nội dung bài toán mẫu:")
        ans = st.text_input("Đáp án đúng (số):")
        if st.button("LƯU ĐỀ"):
            library["current"] = {"q": txt, "a": ans}
            save_db("LIB", library)
            st.success("Đã lưu đề gốc thành công!")
else:
    if not library: st.info("Chờ Thầy Thái giao bài nhé!")
    else:
        if 'active_q' not in st.session_state:
            res = ai_generate_new_quiz(library["current"]["q"], library["current"]["a"], config.get("api_key", ""))
            parts = res.split(" | ")
            st.session_state.active_q = parts[0].replace("Câu hỏi: ", "")
            st.session_state.active_a = parts[1].replace("Đáp án: ", "")
            st.session_state.start_time = time.time()

        with st.form("quiz"):
            st.write(f"### ✍️ {st.session_state.active_q}")
            u_ans = st.text_input("Kết quả của em:")
            if st.form_submit_button("NỘP BÀI"):
                if u_ans.strip() == st.session_state.active_a.strip():
                    st.balloons()
                    st.success(f"Chính xác! Thời gian: {round(time.time()-st.session_state.start_time, 1)} giây.")
                else: st.error(f"Sai rồi! Đáp án đúng là {st.session_state.active_a}")
                del st.session_state.active_q # Để lần sau nhấn làm bài sẽ đổi số mới

st.markdown('<div class="footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)
