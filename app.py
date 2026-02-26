import streamlit as st
import google.generativeai as genai
import json
import os
import time
import pandas as pd

# --- 1. CẤU HÌNH GIAO DIỆN PHONG THỦY ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide", page_icon="🎓")

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
        text-align: center; font-weight: bold; padding: 12px 0; z-index: 1000;
        border-top: 2px solid rgba(0, 79, 152, 0.2);
    }
    .main-content { margin-top: 100px; margin-bottom: 100px; padding: 0 20px; }
    .admin-card, .rank-card {
        background-color: white; border-radius: 15px; padding: 20px;
        border-top: 8px solid #004F98; box-shadow: 0px 10px 20px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU (THÊM FILE LƯU ĐIỂM) ---
FILES = {"LIB": "quiz_library.json", "CONFIG": "config.json", "RANK": "leaderboard.json"}

def load_db(k):
    if os.path.exists(FILES[k]):
        with open(FILES[k], "r", encoding="utf-8") as f: return json.load(f)
    return {} if k != "RANK" else []

def save_db(k, d):
    with open(FILES[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

library = load_db("LIB")
config = load_db("CONFIG")
rank_data = load_db("RANK")

# --- HIỂN THỊ CỐ ĐỊNH ---
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

# LẤY THAM SỐ URL
role = st.query_params.get("role", "student")
ma_de_tu_link = st.query_params.get("de", "")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ (CHIA CỘT TRÁI - PHẢI FULL)
# ==========================================
if role == "teacher":
    col_l, col_r = st.columns([1, 3.5], gap="large")
    
    with col_l:
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.subheader("🔑 BẢO MẬT")
        pwd = st.text_input("Mật mã:", type="password")
        st.divider()
        api_key = st.text_input("Gemini API:", value=config.get("api_key", ""), type="password")
        if st.button("LƯU API"):
            save_db("CONFIG", {"api_key": api_key})
            st.success("Đã lưu!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="admin-card">', unsafe_allow_html=True)
            st.subheader("📝 SOẠN ĐỀ & QUẢN LÝ")
            
            # Chọn đề cũ
            danh_sach = ["-- Tạo mới --"] + list(library.keys())
            de_chon = st.selectbox("Lấy dữ liệu từ thư viện:", options=danh_sach)
            
            # Link copy tự động
            m_de = st.text_input("Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "")
            base_url = "https://toan-lop-3-thay-thai.streamlit.app" # SỬA LINK THẬT TẠI ĐÂY
            full_link = f"{base_url}/?de={m_de}" if m_de else base_url
            
            l_c1, l_c2 = st.columns([5, 1])
            l_c1.code(full_link, language=None)
            if l_c2.button("📋 COPY"):
                st.write(f'<script>navigator.clipboard.writeText("{full_link}")</script>', unsafe_allow_html=True)
                st.toast("Đã sao chép!")

            # Bảng nhập liệu
            num_q = st.number_input("Số câu:", 1, 30, value=len(library.get(de_chon, [])) if de_chon != "-- Tạo mới --" else 5)
            with st.form("admin_form"):
                new_qs = []
                c1, c2 = st.columns(2)
                data_old = library.get(de_chon, [])
                for i in range(1, num_q + 1):
                    vq = data_old[i-1]["q"] if i <= len(data_old) else ""
                    va = data_old[i-1]["a"] if i <= len(data_old) else ""
                    with (c1 if i <= (num_q+1)//2 else c2):
                        q = st.text_input(f"Câu {i}:", value=vq, key=f"q{i}")
                        a = st.text_input(f"Đáp án {i}:", value=va, key=f"a{i}")
                        new_qs.append({"q": q, "a": a})
                if st.form_submit_button("🚀 LƯU ĐỀ"):
                    library[m_de] = new_qs
                    save_db("LIB", library)
                    st.success("Đã lưu vào thư viện!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# CỔNG HỌC SINH (BỔ SUNG XẾP HẠNG)
# ==========================================
else:
    if ma_de_tu_link in library:
        st.markdown(f'<div class="admin-card"><h3>✍️ BÀI TẬP: {ma_de_tu_link}</h3>', unsafe_allow_html=True)
        ten_hs = st.text_input("Nhập họ và tên của em:", placeholder="Ví dụ: Nguyễn Văn A")
        
        if ten_hs:
            # AI Biến đổi đề bài (giả lập để code chạy nhanh)
            quiz = library[ma_de_tu_link]
            if 'start_time' not in st.session_state: st.session_state.start_time = time.time()
            
            with st.form("quiz_form"):
                answers = []
                for idx, item in enumerate(quiz):
                    st.write(f"**Câu {idx+1}:** {item['q']}")
                    answers.append(st.text_input(f"Trả lời {idx+1}:", key=f"ans{idx}"))
                
                if st.form_submit_button("✅ NỘP BÀI"):
                    score = sum(1 for i, a in enumerate(answers) if a.strip() == quiz[i]['a'].strip())
                    duration = round(time.time() - st.session_state.start_time, 1)
                    
                    # Lưu vào bảng xếp hạng
                    new_rank = {"Tên": ten_hs, "Đề": ma_de_tu_link, "Điểm": f"{score}/{len(quiz)}", "Thời gian (giây)": duration}
                    rank_data.append(new_rank)
                    save_db("RANK", rank_data)
                    
                    st.success(f"Chúc mừng {ten_hs}! Em đúng {score} câu. Thời gian: {duration} giây.")
                    st.balloons()

        # HIỂN THỊ BẢNG XẾP HẠNG THỜI GIAN THỰC
        st.divider()
        st.subheader("🏆 BẢNG VÀNG THÀNH TÍCH")
        if rank_data:
            df_rank = pd.DataFrame(rank_data)
            # Chỉ hiện kết quả của mã đề này
            df_this_de = df_rank[df_rank["Đề"] == ma_de_tu_link].sort_values(by=["Điểm", "Thời gian (giây)"], ascending=[False, True])
            st.table(df_this_de[["Tên", "Điểm", "Thời gian (giây)"]].head(10))
            st.write(f"📊 Tổng số người đã làm đề này: {len(df_this_de)}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Chào mừng các em! Hãy chọn bài tập Thầy Thái gửi để bắt đầu nhé.")

st.markdown('</div>', unsafe_allow_html=True)
