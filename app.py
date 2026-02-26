import streamlit as st
import google.generativeai as genai
import json, os, time, pandas as pd
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN PHONG THỦY (KHÔNG ĐỔI) ---
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
    .main-content { margin-top: 100px; margin-bottom: 100px; padding: 0 20px; }
    .card { background-color: white; border-radius: 15px; padding: 20px; border-top: 8px solid #004F98; box-shadow: 0 8px 20px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .small-inline-title { color: #004F98 !important; font-size: 16px !important; font-weight: bold !important; margin-bottom: 5px; display: block; white-space: nowrap; }
    
    /* DÒNG LINK HIỂN THỊ ĐÃ KHÔI PHỤC */
    .link-box { 
        background-color: #f1f3f4; 
        border: 2px dashed #004F98; 
        padding: 12px; 
        border-radius: 8px; 
        color: #d32f2f; 
        font-family: 'Courier New', monospace; 
        font-size: 15px; 
        word-break: break-all; 
        margin: 10px 0;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU ---
DB = {"LIB": "quiz_lib.json", "RANK": "rank_live.json", "MASTER": "students_history.json", "CFG": "config.json"}
def load_db(k):
    if os.path.exists(DB[k]):
        with open(DB[k], "r", encoding="utf-8") as f: return json.load(f)
    return {} if k in ["LIB", "CFG"] else []
def save_db(k, d):
    with open(DB[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

library, rank_live, master_db, config = load_db("LIB"), load_db("RANK"), load_db("MASTER"), load_db("CFG")

# --- HIỂN THỊ HEADER/FOOTER ---
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

# LẤY MÃ ĐỀ TỪ URL
ma_de_url = st.query_params.get("de", "")
role = st.query_params.get("role", "teacher" if not ma_de_url else "student")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ (PHẢI HIỆN ĐỦ LINK VÀ NHẬP LIỆU)
# ==========================================
if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="small-inline-title">🔑 BẢO MẬT</span>', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã", type="password", placeholder="Mật mã...", key="admin_pwd", label_visibility="collapsed")
        st.markdown('<span class="small-inline-title" style="margin-top:15px;">🤖 CẤU HÌNH AI</span>', unsafe_allow_html=True)
        api = st.text_input("API Key", value=config.get("api_key", ""), type="password", placeholder="API Key...", key="admin_api", label_visibility="collapsed")
        if st.button("LƯU API", use_container_width=True): save_db("CFG", {"api_key": api}); st.toast("Đã lưu!")
        if pwd == "thai2026":
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📁 FILE MẪU</span>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"Câu hỏi": ["10+5=?", "12+8=?"], "Đáp án": ["15", "20"]})
            st.download_button("📥 TẢI CSV MẪU", df_m.to_csv(index=False).encode('utf-8-sig'), "mau.csv", "text/csv", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 BẢNG QUẢN LÝ ĐỀ BÀI")
            
            d_col1, d_col2 = st.columns([3, 1])
            with d_col1: 
                de_chon = st.selectbox("Lấy dữ liệu từ đề cũ:", options=["-- Tạo mới --"] + list(library.keys()))
            with d_col2:
                st.markdown('<p style="font-size:11px; margin-bottom:0;">Upload (CSV):</p>', unsafe_allow_html=True)
                up_f = st.file_uploader("", type=["csv"], label_visibility="collapsed")
            
            data_load = library.get(de_chon, [])
            if up_f:
                df_u = pd.read_csv(up_f)
                data_load = [{"q": r[0], "a": str(r[1])} for r in df_u.values]

            st.divider()
            m_de = st.text_input("Bước 1: Nhập Mã đề bài muốn tạo (Ví dụ: BAI_01):", value=de_chon if de_chon != "-- Tạo mới --" else "")
            
            # --- ĐOẠN KHỐI LINK VÀ COPY (ĐÃ KHÔI PHỤC VÀ KIỂM TRA) ---
            if m_de:
                st.markdown(f"**Bước 2: Đường link gửi cho học sinh làm bài:**")
                # Hiển thị link trực quan
                link_full = f"https://toan-lop-3-thay-thai.streamlit.app/?de={m_de}"
                st.markdown(f'<div class="link-box">{link_full}</div>', unsafe_allow_html=True)
                
                # Nút nhấn Copy vạn năng
                js_copy = f"""
                <script>
                function copyLinkHS() {{
                    var url = window.location.origin + window.location.pathname + "?de={m_de}";
                    var el = document.createElement('textarea');
                    el.value = url;
                    document.body.appendChild(el);
                    el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    alert("✅ Đã copy link thành công: " + url);
                }}
                </script>
                <button onclick="copyLinkHS()" style="width:100%; padding:15px; background-color:#004F98; color:white; border-radius:12px; border:none; font-weight:bold; cursor:pointer; font-size:18px;">
                📋 NHẤN VÀO ĐÂY ĐỂ COPY LINK (GỬI QUA ZALO)
                </button>
                """
                st.markdown(js_copy, unsafe_allow_html=True)

            st.divider()
            st.markdown("**Bước 3: Soạn thảo câu hỏi và đáp án:**")
            num_q = st.number_input("Số câu hỏi hiển thị trong đề:", 1, 30, len(data_load) if data_load else 5)
            
            with st.form("admin_form"):
                new_qs = []
                c1, c2 = st.columns(2)
                for i in range(1, num_q + 1):
                    vq = data_load[i-1]["q"] if i <= len(data_load) else ""
                    va = data_load[i-1]["a"] if i <= len(data_load) else ""
                    with (c1 if i <= (num_q+1)//2 else c2):
                        q_in = st.text_input(f"Câu hỏi {i}:", value=vq, key=f"q{i}")
                        a_in = st.text_input(f"Đáp án {i}:", value=va, key=f"a{i}")
                        new_qs.append({"q": q_in, "a": a_in})
                if st.form_submit_button("🚀 LƯU ĐỀ VÀO THƯ VIỆN & XUẤT BẢN", use_container_width=True):
                    library[m_de] = new_qs; save_db("LIB", library); st.success(f"Đã lưu thành công đề: {m_de}"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Vui lòng nhập đúng mật mã bên trái để mở bảng quản trị.")

# ==========================================
# CỔNG HỌC SINH (KHÔNG THAY ĐỔI)
# ==========================================
else:
    if ma_de_url in library:
        st.markdown(f'<div class="card"><h3>✍️ BÀI TẬP: {ma_de_url}</h3></div>', unsafe_allow_html=True)
    else:
        st.info("Chào mừng các em! Hãy sử dụng link bài tập Thầy gửi để bắt đầu.")

st.markdown('</div>', unsafe_allow_html=True)
