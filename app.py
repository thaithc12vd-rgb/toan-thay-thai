import streamlit as st
import google.generativeai as genai
import json, os, time, pandas as pd
from datetime import datetime, timedelta

# --- 1. CẤU HÌNH GIAO DIỆN & STYLE HUY HIỆU ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide")

st.markdown("""
<style>
    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display:none !important;}
    .stApp { background-color: #C5D3E8; } 
    .sticky-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-size: 30px; font-weight: 900; padding: 10px 0; z-index: 1000;
        border-bottom: 2px solid rgba(0, 79, 152, 0.2); text-transform: uppercase;
    }
    .sticky-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-weight: bold; padding: 10px 0; z-index: 1000;
        border-top: 2px solid rgba(0, 79, 152, 0.2);
    }
    .main-content { margin-top: 100px; margin-bottom: 100px; padding: 0 20px; }
    .card { background-color: white; border-radius: 15px; padding: 25px; border-top: 10px solid #004F98; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px; }
    
    /* HUY HIỆU SANG TRỌNG */
    .rank-1 { color: #FFD700; font-weight: bold; font-size: 20px; }
    .rank-2 { color: #C0C0C0; font-weight: bold; font-size: 18px; }
    .rank-3 { color: #CD7F32; font-weight: bold; font-size: 18px; }
    .giay-khen { border: 8px double #FFD700; padding: 20px; text-align: center; background: #FFF9C4; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU VĨNH VIỄN ---
DB = {"LIB": "quiz_lib.json", "RANK": "rank_live.json", "MASTER": "students_history.json", "CFG": "config.json"}

def load_db(k):
    if os.path.exists(DB[k]):
        with open(DB[k], "r", encoding="utf-8") as f: return json.load(f)
    return {} if k in ["LIB", "CFG"] else []

def save_db(k, d):
    with open(DB[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

library = load_db("LIB")
rank_live = load_db("RANK")
master_db = load_db("MASTER")
config = load_db("CFG")

# TỰ HỦY SAU 48 GIỜ (Tính từ lúc bắt đầu làm bài)
now = datetime.now()
rank_live = [r for r in rank_live if (now - datetime.fromisoformat(r['start_ts'])).total_seconds() < 172800]
save_db("RANK", rank_live)

# --- 3. HÀM AI THAY SỐ GIỮ CẤU TRÚC ---
def ai_generate(q_list, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Thay đổi số (+/-10) và tên người trong các câu hỏi này: {q_list}. GIỮ NGUYÊN cấu trúc toán (tứ giác 4 cạnh, tam giác 3 cạnh). Tự tính đáp án mới. Trả về JSON: [{{'q': '...', 'a': '...'}}, ...]"
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
# CỔNG QUẢN TRỊ (2 CỘT FULL TÍNH NĂNG)
# ==========================================
if role == "teacher":
    col_l, col_r = st.columns([1, 3.5], gap="large")
    
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔑 BẢO MẬT")
        pwd = st.text_input("Mật mã:", type="password")
        api = st.text_input("API Key:", value=config.get("api_key", ""), type="password")
        if st.button("LƯU CẤU HÌNH"):
            save_db("CFG", {"api_key": api})
            st.success("Đã lưu!")
        if pwd == "thai2026":
            st.divider()
            st.subheader("📁 FILE MẪU")
            df_m = pd.DataFrame({"Câu hỏi": ["15 + 10 = ?", "Hình tam giác có 3 cạnh là 3,4,5. Chu vi?"], "Đáp án": ["25", "12"]})
            st.download_button("📥 Tải File Mẫu", df_m.to_csv(index=False).encode('utf-8-sig'), "mau.csv", "text/csv")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 BẢNG QUẢN LÝ ĐỀ BÀI")
            danh_sach = ["-- Tạo mới --"] + list(library.keys())
            de_chon = st.selectbox("Lấy dữ liệu từ đề cũ:", options=danh_sach)
            up_f = st.file_uploader("Hoặc Upload file Excel (CSV):", type=["csv"])
            
            data_load = library.get(de_chon, [])
            if up_f:
                df_u = pd.read_csv(up_f)
                data_load = [{"q": r[0], "a": str(r[1])} for r in df_u.values]

            st.divider()
            m_de = st.text_input("Mã đề (Ví dụ: BAI_01):", value=de_chon if de_chon != "-- Tạo mới --" else "")
            
            # --- COPY LINK ---
            base_url = "https://toan-lop-3-thay-thai.streamlit.app" # SỬA ĐÚNG LINK CỦA THẦY
            full_link = f"{base_url}/?de={m_de}" if m_de else base_url
            c_l1, c_l2 = st.columns([5, 1])
            c_l1.code(full_link, language=None)
            if c_l2.button("📋 COPY"):
                st.write(f'<script>navigator.clipboard.writeText("{full_link}")</script>', unsafe_allow_html=True)
                st.toast("Đã copy link!")

            num_q = st.number_input("Số câu:", 1, 30, len(data_load) if data_load else 5)
            with st.form("admin_form"):
                new_qs = []
                c1, c2 = st.columns(2)
                for i in range(1, num_q + 1):
                    vq = data_load[i-1]["q"] if i <= len(data_load) else ""
                    va = data_load[i-1]["a"] if i <= len(data_load) else ""
                    with (c1 if i <= (num_q+1)//2 else c2):
                        q = st.text_input(f"Câu {i}:", value=vq, key=f"q{i}")
                        a = st.text_input(f"Đáp án {i}:", value=va, key=f"a{i}")
                        new_qs.append({"q": q, "a": a})
                if st.form_submit_button("🚀 LƯU VÀO THƯ VIỆN"):
                    library[m_de] = new_qs
                    save_db("LIB", library)
                    st.success("Đã lưu!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# CỔNG HỌC SINH (HẾT HẠN 48H & KHÓA 20 LẦN)
# ==========================================
else:
    col_q, col_rank = st.columns([1.2, 1], gap="large")
    with col_q:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if ma_de in library:
            name = st.text_input("👤 Nhập Họ và Tên:").strip()
            if name:
                hs_m = next((s for s in master_db if s['name'] == name and s['de'] == ma_de), {"count": 0, "top10_total": 0})
                if hs_m['count'] >= 20:
                    st.error("⛔ Hệ thống đã KHÓA. Em đã làm bài này 20 lần!")
                else:
                    if 'quiz_data' not in st.session_state:
                        st.session_state.quiz_data = ai_generate(library[ma_de], config.get("api_key", ""))
                        st.session_state.start_48h = now.isoformat()
                        st.session_state.start_quiz = time.time()

                    with st.form("quiz_form"):
                        st.subheader(f"✍️ ĐỀ BÀI: {ma_de}")
                        ans_u = []
                        for i, it in enumerate(st.session_state.quiz_data):
                            st.write(f"**Câu {i+1}:** {it['q']}")
                            ans_u.append(st.text_input(f"Đáp án {i+1}:", key=f"ans_{i}"))
                        
                        if st.form_submit_button("✅ NỘP BÀI"):
                            score = sum(1 for j, a in enumerate(ans_u) if a.strip() == st.session_state.quiz_data[j]['a'].strip())
                            dur = round(time.time() - st.session_state.start_quiz, 1)
                            
                            # Cập nhật kết quả & Tăng số lần làm
                            rank_live.append({"name": name, "de": ma_de, "score": score, "time": dur, "start_ts": st.session_state.start_48h})
                            
                            # Logic Cộng dồn Top 10
                            this_rank = [r for r in rank_live if r['de'] == ma_de]
                            this_rank.sort(key=lambda x: (-x['score'], x['time']))
                            is_top10 = any(r['name'] == name for r in this_rank[:10])
                            
                            found = False
                            for s in master_db:
                                if s['name'] == name and s['de'] == ma_de:
                                    s['count'] += 1
                                    if is_top10: s['top10_total'] += 1
                                    found = True; break
                            if not found: master_db.append({"name": name, "de": ma_de, "count": 1, "top10_total": 1 if is_top10 else 0})
                            
                            save_db("RANK", rank_live)
                            save_db("MASTER", master_db)
                            st.success(f"Kết quả: {score} câu đúng - {dur} giây.")
                            del st.session_state.quiz_data
                            st.rerun()
            
            # GIẤY KHEN
            hs_now = next((s for s in master_db if s['name'] == name and s['de'] == ma_de), None)
            if hs_now and hs_now['top10_total'] >= 3:
                st.markdown(f'<div class="giay-khen">📜 GIẤY KHEN: {name} đã 3 lần đạt TOP 10!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_rank:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏆 BẢNG VÀNG TOP 100")
        r_list = [r for r in rank_live if r['de'] == ma_de]
        r_list.sort(key=lambda x: (-x['score'], x['time']))
        
        for i, r in enumerate(r_list[:100]):
            badge = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🎖️" if i < 10 else f"{i+1}"
            style = f"rank-{i+1}" if i < 3 else ""
            hs_info = next((s for s in master_db if s['name'] == r['name'] and s['de'] == ma_de), {"top10_total": 0})
            st.markdown(f"<div class='{style}'>{badge}. {r['name']} - {r['score']}đ - {r['time']}s (Top 10: {hs_info['top10_total']} lần)</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
