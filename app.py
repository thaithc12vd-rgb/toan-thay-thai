import streamlit as st
import google.generativeai as genai
import json, os, time, pandas as pd
from datetime import datetime

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
    
    /* STYLE CHO DÒNG LINK VÀ NÚT COPY */
    .link-box {
        background-color: #f8f9fa;
        border: 1px dashed #004F98;
        padding: 10px;
        border-radius: 5px;
        color: #d32f2f;
        font-family: monospace;
        font-size: 14px;
        word-break: break-all;
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

library = load_db("LIB")
rank_live = load_db("RANK")
master_db = load_db("MASTER")
config = load_db("CFG")

# TỰ HỦY SAU 48 GIỜ
now = datetime.now()
rank_live = [r for r in rank_live if (now - datetime.fromisoformat(r['start_ts'])).total_seconds() < 172800]
save_db("RANK", rank_live)

# --- HIỂN THỊ HEADER/FOOTER ---
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

ma_de = st.query_params.get("de", "")
role = st.query_params.get("role", "teacher" if not ma_de else "student") # Tự động vào vai teacher nếu không có mã đề

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ
# ==========================================
if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="small-inline-title">🔑 BẢO MẬT</span>', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã", type="password", placeholder="Mật mã...", key="admin_pwd", label_visibility="collapsed")
        
        st.markdown('<span class="small-inline-title" style="margin-top:15px;">🤖 CẤU HÌNH AI</span>', unsafe_allow_html=True)
        api = st.text_input("API Key", value=config.get("api_key", ""), type="password", placeholder="API Key...", key="admin_api", label_visibility="collapsed")
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
            st.subheader("📝 QUẢN LÝ NỘI DUNG ĐỀ BÀI")
            
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                danh_sach = ["-- Tạo mới --"] + list(library.keys())
                de_chon = st.selectbox("Thư viện cũ:", options=danh_sach)
            with d_col2:
                up_f = st.file_uploader("Upload CSV (Tải đề hàng loạt):", type=["csv"])
            
            data_load = library.get(de_chon, [])
            if up_f:
                df_u = pd.read_csv(up_f)
                data_load = [{"q": r[0], "a": str(r[1])} for r in df_u.values]

            st.divider()
            m_de = st.text_input("Bước 1: Nhập Mã đề tại đây (Ví dụ: BAI_01):", value=de_chon if de_chon != "-- Tạo mới --" else "")
            
            # --- HIỂN THỊ LINK VÀ NÚT COPY (LUÔN XUẤT HIỆN KHI CÓ MÃ ĐỀ) ---
            if m_de:
                # Tự động nhận diện URL web
                full_url = f"https://toan-lop-3-thay-thai.streamlit.app/?de={m_de}" # Link ví dụ
                
                st.markdown(f"**Bước 2: Copy link gửi cho học sinh:**")
                st.markdown(f'<div class="link-box">{full_url}</div>', unsafe_allow_html=True)
                
                js_code = f"""
                <script>
                function copyLink() {{
                    var url = window.location.origin + window.location.pathname + "?de={m_de}";
                    var dummy = document.createElement("textarea");
                    document.body.appendChild(dummy);
                    dummy.value = url;
                    dummy.select();
                    document.execCommand("copy");
                    document.body.removeChild(dummy);
                    alert("Đã copy thành công link bài: " + url);
                }}
                </script>
                <button onclick="copyLink()" style="width:100%; padding:12px; margin-top:10px; background-color:#004F98; color:white; border-radius:10px; border:none; font-weight:bold; cursor:pointer; font-size:16px;">
                📋 NHẤN VÀO ĐÂY ĐỂ COPY LINK (DÙNG CHO ZALO/FACEBOOK)
                </button>
                """
                st.markdown(js_code, unsafe_allow_html=True)

            st.divider()
            st.markdown("**Bước 3: Soạn câu hỏi và đáp án:**")
            num_q = st.number_input("Số lượng câu:", 1, 30, len(data_load) if data_load else 5)
            
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
                if st.form_submit_button("🚀 LƯU VÀO THƯ VIỆN & XUẤT BẢN", use_container_width=True):
                    library[m_de] = new_qs
                    save_db("LIB", library)
                    st.success(f"Đã lưu thành công đề: {m_de}")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Vui lòng nhập mật mã bên trái để mở bảng quản lý.")

# ==========================================
# CỔNG HỌC SINH
# ==========================================
else:
    if ma_de in library:
        st.markdown(f'<div class="card"><h3>✍️ BÀI TẬP: {ma_de}</h3></div>', unsafe_allow_html=True)
    else:
        st.info("Chào mừng các em! Hãy chọn bài tập Thầy Thái gửi để bắt đầu.")

st.markdown('</div>', unsafe_allow_html=True)
