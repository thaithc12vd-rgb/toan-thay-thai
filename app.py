import streamlit as st
import google.generativeai as genai
import json, os, time, pandas as pd
from datetime import datetime
import io

# --- 1. CẤU HÌNH GIAO DIỆN (BẢO TOÀN) ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide")

st.markdown("""
<style>
    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display:none !important;}
    .stApp { background-color: #C5D3E8; } 
    .sticky-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; padding: 10px 0; z-index: 1000;
        border-bottom: 2px solid #004F98; text-transform: uppercase;
    }
    .main-title { font-size: 30px; font-weight: 900; margin: 0; }
    .sub-title { font-size: 11px; font-weight: bold; margin: 0; color: #004F98; opacity: 0.9; }
    .main-content { margin-top: 110px; margin-bottom: 100px; padding: 0 20px; }
    .card { background-color: white; border-radius: 15px; padding: 20px; border-top: 8px solid #004F98; box-shadow: 0 8px 20px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .small-inline-title { color: #004F98 !important; font-size: 16px !important; font-weight: bold !important; margin-bottom: 5px; display: block; }
    .link-box { background-color: #f1f3f4; border: 2px dashed #004F98; padding: 12px; border-radius: 8px; color: #d32f2f; font-family: monospace; font-size: 15px; word-break: break-all; margin: 10px 0; font-weight: bold; text-align: center; }
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

ma_de_url = st.query_params.get("de", "")
role = st.query_params.get("role", "student")

# --- HEADER THEO VAI TRÒ ---
if role == "teacher":
    header_title, header_sub = "CHÀO MỪNG THẦY ĐẾN VỚI APP TOÁN LỚP 3", "Chúc thầy luôn vượt qua thử thách"
else:
    header_title, header_sub = "TOÁN LỚP 3 - THẦY THÁI", "Chúc các em làm bài tốt"

st.markdown(f'<div class="sticky-header"><div class="main-title">{header_title}</div><div class="sub-title">{header_sub}</div></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ
# ==========================================
if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="small-inline-title">🔑 BẢO MẬT</span>', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã", type="password", key="admin_pwd", label_visibility="collapsed")
        
        st.markdown('<span class="small-inline-title" style="margin-top:15px;">🤖 CẤU HÌNH AI</span>', unsafe_allow_html=True)
        api = st.text_input("API Key", value=config.get("api_key", ""), type="password", key="admin_api", label_visibility="collapsed")
        if st.button("LƯU CẤU HÌNH", use_container_width=True):
            save_db("CFG", {"api_key": api}); st.toast("Đã lưu!")
            
        if pwd == "thai2026":
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📁 FILE MẪU</span>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"Câu": ["1"], "Yêu cầu": ["Tính"], "Nội dung câu hỏi": ["1+1=?"], "Đáp án": ["2"]})
            st.download_button("📥 TẢI CSV MẪU", df_m.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'), "mau_de.csv", "text/csv", use_container_width=True)
            
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📤 UPLOAD ĐỀ</span>', unsafe_allow_html=True)
            up_f = st.file_uploader("", type=["csv"], label_visibility="collapsed", key="file_up")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 QUẢN LÝ NỘI DUNG ĐỀ BÀI")
            de_chon = st.selectbox("Lấy dữ liệu từ đề cũ:", options=["-- Tạo mới --"] + list(library.keys()))
            data_load = library.get(de_chon, [])
            
            # --- KHẮC PHỤC LỖI MẤT CÂU 1-5 ---
            if st.session_state.get('file_up'):
                raw_bytes = st.session_state.file_up.getvalue()
                # Tự nhận diện mã hóa
                for enc in ['utf-8-sig', 'latin-1']:
                    try:
                        df_u = pd.read_csv(io.BytesIO(raw_bytes), encoding=enc)
                        # Ép kiểu dữ liệu về chuỗi và lấy toàn bộ dòng (không bỏ sót dòng nào)
                        data_load = [{"q": f"{str(r.iloc[1])}: {str(r.iloc[2])}", "a": str(r.iloc[3])} for _, r in df_u.iterrows()]
                        break
                    except: continue

            st.divider()
            m_de = st.text_input("👉 Bước 1: Nhập Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "")
            
            if m_de:
                st.markdown(f"**👉 Bước 2: Copy link bài tập cho học sinh:**")
                # Lấy domain động
                domain = "https://toan-lop-3-thay-thai.streamlit.app"
                link_hs = f"{domain}/?de={m_de}"
                st.markdown(f'<div class="link-box" id="link_text">{link_hs}</div>', unsafe_allow_html=True)
                
                # JAVASCRIPT COPY MẠNH HƠN
                js_copy = f"""
                <script>
                function copyNow() {{
                    var text = window.location.origin + window.location.pathname + "?de={m_de}";
                    var dummy = document.createElement("textarea");
                    document.body.appendChild(dummy);
                    dummy.value = text;
                    dummy.select();
                    document.execCommand("copy");
                    document.body.removeChild(dummy);
                    alert("✅ Đã copy thành công link bài tập!");
                }}
                </script>
                <button onclick="copyNow()" style="width:100%; padding:15px; background-color:#004F98; color:white; border-radius:12px; border:none; font-weight:bold; cursor:pointer; font-size:18px;">
                📋 NHẤN VÀO ĐÂY ĐỂ COPY LINK (GỬI ZALO)
                </button>
                """
                st.markdown(js_copy, unsafe_allow_html=True)

            st.divider()
            st.markdown("**👉 Bước 3: Soạn câu hỏi:**")
            num_q = st.number_input("Số câu:", 1, 1000, len(data_load) if data_load else 5)
            with st.form("admin_form"):
                new_qs = []
                for i in range(1, num_q + 1):
                    vq = data_load[i-1]["q"] if i <= len(data_load) else ""
                    va = data_load[i-1]["a"] if i <= len(data_load) else ""
                    st.markdown(f"**Câu {i}**")
                    q_in = st.text_input(f"Nội dung câu {i}:", value=vq, key=f"q{i}", label_visibility="collapsed")
                    a_in = st.text_input(f"Đáp án {i}:", value=va, key=f"a{i}")
                    new_qs.append({"q": q_in, "a": a_in})
                if st.form_submit_button("🚀 LƯU ĐỀ & XUẤT BẢN", use_container_width=True):
                    library[m_de] = new_qs; save_db("LIB", library); st.success("Đã lưu!"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- CỔNG HỌC SINH (BẢO TOÀN) ---
    if ma_de_url in library:
        st.markdown(f'<div class="card"><h3>✍️ BÀI TẬP: {ma_de_url}</h3></div>', unsafe_allow_html=True)
    else:
        st.info("Chào mừng các em! Hãy sử dụng link Thầy Thái gửi để làm bài.")
st.markdown('</div>', unsafe_allow_html=True)
