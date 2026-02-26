import streamlit as st
import google.generativeai as genai
import json
import os
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
        border-bottom: 2px solid rgba(0, 79, 152, 0.2);
    }
    .sticky-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-weight: bold; padding: 12px 0; z-index: 1000;
        border-top: 2px solid rgba(0, 79, 152, 0.2);
    }
    .main-content { margin-top: 80px; margin-bottom: 80px; }
    .admin-card {
        background-color: white; border-radius: 15px; padding: 20px;
        border-top: 8px solid #004F98; box-shadow: 0px 10px 20px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. XỬ LÝ DỮ LIỆU ---
DB_FILE = "quiz_library.json"
CF_FILE = "config.json"

def load_data(f):
    if os.path.exists(f):
        with open(f, "r", encoding="utf-8") as file: return json.load(file)
    return {}

def save_data(f, d):
    with open(f, "w", encoding="utf-8") as file: json.dump(d, file, ensure_ascii=False, indent=4)

library = load_data(DB_FILE)
config = load_data(CF_FILE)

# HEADER & FOOTER
st.markdown('<div class="sticky-header">HỆ THỐNG QUẢN TRỊ - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

# ĐIỀU HƯỚNG
role = st.query_params.get("role", "student")
ma_de_link = st.query_params.get("de", "")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    # CHIA CỘT TRÁI (1) - PHẢI (3)
    col_left, col_right = st.columns([1, 3.5], gap="medium")

    # --- BÊN TRÁI: BẢO MẬT & TIỆN ÍCH ---
    with col_left:
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.subheader("🔑 XÁC THỰC")
        pwd = st.text_input("Mật mã:", type="password")
        
        st.divider()
        st.subheader("🤖 CẤU HÌNH AI")
        api_val = st.text_input("Gemini API:", value=config.get("api_key", ""), type="password")
        if st.button("LƯU API"):
            save_data(CF_FILE, {"api_key": api_val})
            st.success("Đã lưu!")

        if pwd == "thai2026":
            st.divider()
            st.subheader("📂 FILE MẪU")
            df_template = pd.DataFrame({"Câu hỏi": ["2 + 3 = ?", "5 x 4 = ?"], "Đáp án": ["5", "20"]})
            st.download_button("Tải File Excel Mẫu", df_template.to_csv(index=False).encode('utf-8-sig'), "mau_de_bai.csv", "text/csv")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- BÊN PHẢI: NHẬP LIỆU FULL ---
    with col_right:
        if pwd == "thai2026":
            st.markdown('<div class="admin-card">', unsafe_allow_html=True)
            st.subheader("📝 SOẠN THẢO NỘI DUNG")
            
            # Chọn đề cũ (Sửa lỗi không thấy đề mới)
            danh_sach = ["-- Tạo mới --"] + list(library.keys())
            de_chon = st.selectbox("Lấy dữ liệu từ thư viện:", options=danh_sach)
            
            # Tải file hàng loạt
            up_file = st.file_uploader("Hoặc Upload file đề bài (CSV):", type=["csv"])
            data_load = library.get(de_chon, [])
            if up_file:
                df_up = pd.read_csv(up_file)
                data_load = [{"q": r[0], "a": r[1]} for r in df_up.values]

            st.divider()
            
            col_m, col_n = st.columns([2, 1])
            with col_m: m_de = st.text_input("Mã đề hiện tại:", value=de_chon if de_chon != "-- Tạo mới --" else "")
            with col_n: n_q = st.number_input("Số câu:", 1, 30, len(data_load) if data_load else 5)

            with st.form("form_nhap"):
                new_qs = []
                c1, c2 = st.columns(2)
                for i in range(1, n_q + 1):
                    vq = data_load[i-1]["q"] if i <= len(data_load) else ""
                    va = data_load[i-1]["a"] if i <= len(data_load) else ""
                    with (c1 if i <= (n_q+1)//2 else c2):
                        q = st.text_input(f"Câu {i}:", value=vq, key=f"q{i}")
                        a = st.text_input(f"Đáp án {i}:", value=va, key=f"a{i}")
                        new_qs.append({"q": q, "a": a})
                
                if st.form_submit_button("💾 LƯU VÀO THƯ VIỆN"):
                    if m_de:
                        library[m_de] = new_qs
                        save_data(DB_FILE, library)
                        st.success(f"Đã lưu đề {m_de}!")
                        st.rerun() # Refresh để cập nhật danh sách chọn
                    else: st.error("Thiếu mã đề!")
            
            if m_de in library:
                st.info(f"🔗 Link cho học sinh: `https://share.streamlit.io/vunghia/toan3/main?de={m_de}`")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Nhập mật mã bên trái để mở bảng nhập liệu.")

# CỔNG HỌC SINH (GIỮ NGUYÊN)
else:
    if ma_de_link in library:
        st.markdown(f"### 📝 BÀI TẬP: {ma_de_link}")
        # AI Logic hiển thị ở đây...
        st.write("Hệ thống AI đang tạo đề bài cho em...")
    else:
        st.info("Chào mừng các em đến với lớp Toán Thầy Thái!")

st.markdown('</div>', unsafe_allow_html=True)
