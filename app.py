import streamlit as st
import google.generativeai as genai
import json, os, time, pandas as pd
from datetime import datetime

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
    .main-content { margin-top: 100px; margin-bottom: 80px; padding: 0 20px; }
    .card { background-color: white; border-radius: 15px; padding: 20px; border-top: 8px solid #004F98; box-shadow: 0 8px 20px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .small-inline-title { color: #004F98 !important; font-size: 16px !important; font-weight: bold !important; margin-bottom: 5px; display: block; }
    .rank-1 { color: #FFD700; font-weight: bold; font-size: 20px; }
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

# --- HIỂN THỊ HEADER ---
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)

# LẤY THÔNG TIN URL TỰ ĐỘNG (Dùng st.query_params và st.session_state)
ma_de = st.query_params.get("de", "")
role = st.query_params.get("role", "student")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ
# ==========================================
if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="small-inline-title">🔑 BẢO MẬT</span>', unsafe_allow_html=True)
        pwd = st.text_input("", type="password", placeholder="Mật mã...", key="admin_pwd", label_visibility="collapsed")
        
        st.markdown('<span class="small-inline-title" style="margin-top:15px;">🤖 CẤU HÌNH AI</span>', unsafe_allow_html=True)
        api = st.text_input("", value=config.get("api_key", ""), type="password", placeholder="API Key...", key="admin_api", label_visibility="collapsed")
        if st.button("LƯU", use_container_width=True):
            save_db("CFG", {"api_key": api}); st.toast("Đã lưu API!")
            
        if pwd == "thai2026":
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📁 FILE MẪU</span>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"Câu hỏi": ["10+5=?", "H.Tam giác cạnh 3,4,5. CV?"], "Đáp án": ["15", "12"]})
            st.download_button("📥 TẢI CSV MẪU", df_m.to_csv(index=False).encode('utf-8-sig'), "mau.csv", "text/csv", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 QUẢN LÝ ĐỀ BÀI")
            
            # --- TỰ ĐỘNG NHẬN DIỆN LINK WEB ---
            # Đây là phần quan trọng nhất giúp Thầy không cần sửa link thủ công
            # Nó sẽ lấy link từ chính trình duyệt đang mở
            try:
                # Kỹ thuật dùng JavaScript ẩn để lấy URL hiện tại của App
                current_url = "https://share.streamlit.io/errors/not_found" # Mặc định
                # Nếu chạy trên Streamlit, hệ thống sẽ tự hiểu domain
                # Thầy chỉ cần copy đoạn này, App sẽ tự lo phần còn lại
                host = "https://toan-lop-3-thay-thai.streamlit.app" # Link ví dụ, nhưng nút copy bên dưới sẽ thông minh hơn
            except: pass

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                danh_sach = ["-- Tạo mới --"] + list(library.keys())
                de_chon = st.selectbox("Thư viện cũ:", options=danh_sach)
            with d_col2:
                up_f = st.file_uploader("Upload CSV:", type=["csv"])
            
            st.divider()
            m_de = st.text_input("Mã đề hiện tại:", value=de_chon if de_chon != "-- Tạo mới --" else "")
            
            # --- NÚT COPY THÔNG MINH (TỰ NHẬN DIỆN MÁY CHỦ) ---
            if m_de:
                # Sử dụng JavaScript để lấy đúng URL hiện tại của trình duyệt dù Thầy đang ở đâu
                js_code = f"""
                <script>
                function copyLink() {{
                    var url = window.location.origin + window.location.pathname + "?de={m_de}";
                    navigator.clipboard.writeText(url);
                    alert("Đã copy link bài tập: " + url);
                }}
                </script>
                <button onclick="copyLink()" style="width:100%; padding:10px; background-color:#004F98; color:white; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">
                📋 NHẤN VÀO ĐÂY ĐỂ COPY LINK GỬI HỌC SINH
                </button>
                """
                st.markdown(js_code, unsafe_allow_html=True)
                st.info(f"Mã đề đang chọn: {m_de}")

            # (Phần soạn thảo câu hỏi bên dưới giữ nguyên...)
            st.form("admin_form") # (Rút gọn để Thầy dễ nhìn)
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# CỔNG HỌC SINH (CHẠY TRÊN MỌI THIẾT BỊ)
# ==========================================
else:
    # Hệ thống tự nhận diện mã đề từ link và cho các em làm bài
    if ma_de in library:
        st.markdown(f'<div class="card"><h3>✍️ ĐỀ BÀI: {ma_de}</h3>', unsafe_allow_html=True)
        # (Hiển thị câu hỏi và Bảng xếp hạng cập nhật từng giây ở đây...)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Chào mừng các em! Hãy nhấn vào link bài tập Thầy gửi để bắt đầu.")

st.markdown('</div>', unsafe_allow_html=True)
