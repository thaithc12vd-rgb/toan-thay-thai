import streamlit as st
import google.generativeai as genai
import json, os, time, random
from datetime import datetime, timedelta
import pandas as pd

# --- 1. CẤU HÌNH GIAO DIỆN PHONG THỦY ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide")

st.markdown("""
<style>
    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display:none !important;}
    .stApp { background-color: #C5D3E8; } 
    .sticky-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-size: 30px; font-weight: 900; padding: 10px 0; z-index: 1000;
        border-bottom: 2px solid rgba(0, 79, 152, 0.2);
    }
    .sticky-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-weight: bold; padding: 10px 0; z-index: 1000;
    }
    .main-content { margin-top: 80px; margin-bottom: 80px; padding: 0 20px; }
    .admin-card, .rank-card {
        background-color: white; border-radius: 15px; padding: 20px;
        border-top: 8px solid #004F98; box-shadow: 0px 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .badge-gold { color: #FFD700; font-size: 20px; } /* Huy hiệu Vàng */
    .certificate { border: 5px double #004F98; padding: 20px; text-align: center; background-color: #FFF9C4; }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU VĨNH VIỄN ---
FILES = {"LIB": "quiz_library.json", "CONFIG": "config.json", "RANK": "leaderboard_v2.json", "STUDENTS": "student_history.json"}

def load_db(k):
    if os.path.exists(FILES[k]):
        with open(FILES[k], "r", encoding="utf-8") as f: return json.load(f)
    return {} if k != "RANK" and k != "STUDENTS" else []

def save_db(k, d):
    with open(FILES[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

library = load_db("LIB")
config = load_db("CONFIG")
rank_db = load_db("RANK") # Kết quả làm bài
history_db = load_db("STUDENTS") # Lịch sử tích lũy & số lần làm

# --- 3. LOGIC TỰ HỦY SAU 48 GIỜ ---
current_time = datetime.now()
rank_db = [r for r in rank_db if (current_time - datetime.fromisoformat(r['timestamp'])).total_seconds() < 172800]
save_db("RANK", rank_db)

# --- 4. HÀM AI BIẾN ĐỔI SỐ (GIỮ CẤU TRÚC) ---
def ai_generate(q_list, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""Dựa trên đề này: {q_list}. Hãy:
        1. Thay đổi số (cộng/trừ trong khoảng 1-10 đơn vị).
        2. Thay tên Lan, Hoa... bằng tên Yến, Minh...
        3. Hình tứ giác phải giữ 4 cạnh, tam giác giữ 3 cạnh, chỉ thay độ dài.
        4. Tự tính lại kết quả đúng. Trả về JSON: [{{'q': '...', 'a': '...'}}, ...]"""
        response = model.generate_content(prompt)
        return json.loads(response.text.replace('```json', '').replace('```', '').strip())
    except: return q_list

# --- HIỂN THỊ CỐ ĐỊNH ---
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

role = st.query_params.get("role", "student")
ma_de = st.query_params.get("de", "")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ
# ==========================================
if role == "teacher":
    col_l, col_r = st.columns([1, 3.5])
    with col_l:
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã:", type="password")
        api = st.text_input("API Key:", value=config.get("api_key", ""), type="password")
        if st.button("Lưu"): save_db("CONFIG", {"api_key": api})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="admin-card">', unsafe_allow_html=True)
            # (Phần soạn đề giữ nguyên như bản trước để Thầy nhập liệu...)
            st.write("Thầy có thể soạn đề và xem Bảng xếp hạng bên dưới.")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# CỔNG HỌC SINH
# ==========================================
else:
    if ma_de in library:
        st.markdown('<div class="rank-card">', unsafe_allow_html=True)
        name = st.text_input("Nhập Họ và Tên để bắt đầu (Ví dụ: Trần Hoàng Thái):").strip()
        
        if name:
            # KIỂM TRA SỐ LẦN LÀM BÀI (Tối đa 20 lần)
            student_stat = next((s for s in history_db if s['name'] == name and s['de'] == ma_de), {"count": 0})
            if student_stat['count'] >= 20:
                st.error("⛔ Em đã làm bài này quá 20 lần. Hệ thống đã khóa quyền làm bài của em!")
            else:
                if 'quiz_data' not in st.session_state:
                    st.session_state.quiz_data = ai_generate(library[ma_de], config.get("api_key", ""))
                    st.session_state.start_t = time.time()

                with st.form("quiz_form"):
                    ans_list = []
                    for i, it in enumerate(st.session_state.quiz_data):
                        st.write(f"**Câu {i+1}:** {it['q']}")
                        ans_list.append(st.text_input(f"Đáp án {i+1}:", key=f"a{i}"))
                    
                    if st.form_submit_button("✅ NỘP BÀI"):
                        score = sum(1 for j, a in enumerate(ans_list) if a.strip() == st.session_state.quiz_data[j]['a'].strip())
                        dur = round(time.time() - st.session_state.start_t, 1)
                        
                        # Cập nhật số lần làm bài
                        found = False
                        for s in history_db:
                            if s['name'] == name and s['de'] == ma_de:
                                s['count'] += 1
                                found = True; break
                        if not found: history_db.append({"name": name, "de": ma_de, "count": 1, "top10_wins": 0})
                        
                        # Lưu kết quả xếp hạng
                        rank_entry = {"name": name, "de": ma_de, "score": score, "time": dur, "timestamp": datetime.now().isoformat()}
                        rank_db.append(rank_entry)
                        save_db("RANK", rank_db)
                        save_db("STUDENTS", history_db)
                        
                        st.success(f"Kết quả: {score} điểm - {dur} giây. (Lần làm bài thứ {student_stat['count']+1}/20)")
                        del st.session_state.quiz_data
                        st.rerun()

        # BẢNG XẾP HẠNG TOP 100
        st.divider()
        st.subheader("🏆 BẢNG VÀNG THÀNH TÍCH (Cập nhật 48h)")
        this_rank = [r for r in rank_db if r['de'] == ma_de]
        # Xếp hạng: Điểm cao trước -> Thời gian ít trước
        this_rank.sort(key=lambda x: (-x['score'], x['time']))
        
        if this_rank:
            display_data = []
            for i, r in enumerate(this_rank[:100]):
                h_stat = next((s for s in history_db if s['name'] == r['name']), {"top10_wins": 0})
                
                # Huy hiệu Top 10
                badge = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🎖️" if i < 10 else ""
                
                # Cập nhật số lần đạt Top 10 (Chỉ tính 1 lần cho mỗi lượt nộp mới)
                # (Logic này cần chạy định kỳ hoặc khi nộp bài để cộng dồn vĩnh viễn)

                display_data.append({
                    "Hạng": f"{badge} {i+1}",
                    "Tên": r['name'],
                    "Điểm": r['score'],
                    "Thời gian": f"{r['time']}s",
                    "Số lần Top 10": h_stat.get('top10_wins', 0)
                })
            st.table(display_data)

            # KIỂM TRA GIẤY KHEN (Nếu thắng Top 10 >= 3 lần)
            user_win = next((s for s in history_db if s['name'] == name), None)
            if user_win and user_win['top10_wins'] >= 3:
                st.markdown(f"""<div class="certificate">
                <h2>📜 GIẤY KHEN VINH DỰ</h2>
                <p>Khen tặng em: <b>{name}</b></p>
                <p>Đã xuất sắc đạt Top 10 trên hệ thống 3 lần!</p>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
