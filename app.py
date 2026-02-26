import streamlit as st
import google.generativeai as genai
import json, os, time, pandas as pd
from datetime import datetime, timedelta

# --- 1. CẤU HÌNH GIAO DIỆN TINH GỌN ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide")

st.markdown("""
<style>
    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display:none !important;}
    .stApp { background-color: #C5D3E8; } 
    
    .sticky-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-size: 30px; font-weight: 900; padding: 10px 0; z-index: 1000;
        border-bottom: 2px solid #004F98; text-transform: uppercase;
    }
    .sticky-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-weight: bold; padding: 10px 0; z-index: 1000;
        border-top: 1px solid #004F98;
    }
    
    .main-content { margin-top: 90px; margin-bottom: 80px; padding: 0 20px; }
    
    .card { 
        background-color: white; border-radius: 15px; padding: 20px; 
        border-top: 8px solid #004F98; box-shadow: 0 8px 20px rgba(0,0,0,0.1); 
        margin-bottom: 15px; 
    }

    /* TIÊU ĐỀ NHỎ GỌN TRÊN 1 DÒNG */
    .small-inline-title {
        color: #004F98 !important;
        font-size: 16px !important;
        font-weight: bold !important;
        margin-bottom: 5px;
        display: block;
        white-space: nowrap;
    }
    
    /* Tối ưu các ô nhập liệu */
    .stTextInput>div>div>input { padding: 5px 10px !important; }
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

# TỰ HỦY SAU 48 GIỜ
now = datetime.now()
rank_live = [r for r in rank_live if (now - datetime.fromisoformat(r['start_ts'])).total_seconds() < 172800]
save_db("RANK", rank_live)

# --- HIỂN THỊ CỐ ĐỊNH ---
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

role = st.query_params.get("role", "student")
ma_de = st.query_params.get("de", "")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ (TIÊU ĐỀ 1 DÒNG)
# ==========================================
if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium") # Tăng độ rộng cột phải hơn nữa
    
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        st.markdown('<span class="small-inline-title">🔑 BẢO MẬT</span>', unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Mật mã...", key="admin_pwd", label_visibility="collapsed")
        
        st.markdown('<span class="small-inline-title" style="margin-top:15px;">🤖 CẤU HÌNH AI</span>', unsafe_allow_html=True)
        api = st.text_input("", value=config.get("api_key", ""), type="password", placeholder="API Key...", key="admin_api", label_visibility="collapsed")
        if st.button("LƯU", use_container_width=True):
            save_db("CFG", {"api_key": api})
            st.toast("Đã lưu API!")
            
        if pwd == "thai2026":
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📁 FILE MẪU</span>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"Câu hỏi": ["10+5=?", "H.Tam giác cạnh 3,4,5. CV?"], "Đáp án": ["15", "12"]})
            st.download_button("📥 TẢI CSV MẪU", df_m.to_csv(index=False).encode('utf-8-sig'), "mau.csv", "text/csv", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 BẢNG QUẢN LÝ NỘI DUNG ĐỀ BÀI")
            
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                danh_sach = ["-- Tạo mới --"] + list(library.keys())
                de_chon = st.selectbox("Thư viện cũ:", options=danh_sach)
            with d_col2:
                up_f = st.file_uploader("Upload CSV:", type=["csv"])
            
            data_load = library.get(de_chon, [])
            if up_f:
                df_u = pd.read_csv(up_f)
                data_load = [{"q": r[0], "a": str(r[1])} for r in df_u.values]

            st.divider()
            m_de = st.text_input("Mã đề hiện tại:", value=de_chon if de_chon != "-- Tạo mới --" else "")
            
            # --- COPY LINK ---
            base_url = "https://toan-lop-3-thay-thai.streamlit.app" 
            full_link = f"{base_url}/?de={m_de}" if m_de else base_url
            c_l1, c_l2 = st.columns([5, 1])
            c_l1.code(full_link, language=None)
            if c_l2.button("📋 COPY", use_container_width=True):
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
                if st.form_submit_button("🚀 LƯU ĐỀ VÀO THƯ VIỆN", use_container_width=True):
                    library[m_de] = new_qs
                    save_db("LIB", library)
                    st.success("Đã lưu!")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
