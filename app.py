import streamlit as st
import json, os, pandas as pd
import io

# --- 1. CẤU HÌNH GIAO DIỆN (BẢO TOÀN NGUYÊN TRẠNG) ---
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
DB = {"LIB": "quiz_lib.json", "CFG": "config.json"}
def load_db(k):
    if os.path.exists(DB[k]):
        try:
            with open(DB[k], "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def save_db(k, d):
    with open(DB[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

library = load_db("LIB")
config = load_db("CFG")
ma_de_url = st.query_params.get("de", "")
role = st.query_params.get("role", "teacher" if "role" in st.query_params and st.query_params["role"]=="teacher" else "student")

# --- HEADER (BẢO TOÀN) ---
header_title = "CHÀO MỪNG THẦY ĐẾN VỚI APP TOÁN LỚP 3" if role == "teacher" else "TOÁN LỚP 3 - THẦY THÁI"
header_sub = "Chúc thầy luôn vượt qua thử thách" if role == "teacher" else "Chúc các em làm bài tốt"

st.markdown(f'<div class="sticky-header"><div class="main-title">{header_title}</div><div class="sub-title">{header_sub}</div></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="small-inline-title">🔑 BẢO MẬT</span>', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã", type="password", key="admin_pwd", label_visibility="collapsed")
        
        if pwd == "thai2026":
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📁 FILE MẪU</span>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"STT": ["1"], "YeuCau": ["Tính"], "NoiDung": ["10+20=?"], "DapAn": ["30"]})
            csv_m = df_m.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 TẢI CSV MẪU", csv_m.encode('utf-8-sig'), "mau.csv", "text/csv", use_container_width=True)
            
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📤 UPLOAD ĐỀ</span>', unsafe_allow_html=True)
            up_f = st.file_uploader("", type=["csv", "txt"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 QUẢN LÝ NỘI DUNG ĐỀ BÀI")
            de_chon = st.selectbox("Lấy dữ liệu từ đề cũ:", options=["-- Tạo mới --"] + list(library.keys()))
            
            # Khởi tạo data_load từ thư viện hoặc để trống
            if 'temp_data' not in st.session_state:
                st.session_state.temp_data = library.get(de_chon, [])

            # --- DÒ CÂU HỎI TỰ ĐỘNG KHI UPLOAD ---
            if up_f is not None:
                raw_bytes = up_f.getvalue()
                for enc in ['utf-8-sig', 'utf-8', 'windows-1258', 'latin-1']:
                    try:
                        df_u = pd.read_csv(io.BytesIO(raw_bytes), encoding=enc, header=None)
                        df_u = df_u.dropna(how='all')
                        # Kiểm tra xem dòng 0 có phải là tiêu đề không, nếu phải thì bắt đầu từ dòng 1
                        start_idx = 1 if any(x in str(df_u.iloc[0, 1]) for x in ["Yêu cầu", "YeuCau", "STT"]) else 0
                        
                        st.session_state.temp_data = []
                        for i in range(start_idx, len(df_u)):
                            row = df_u.iloc[i]
                            q = f"{str(row[1])}: {str(row[2])}" if pd.notnull(row[1]) else str(row[2])
                            a = str(row[3]) if len(row) > 3 and pd.notnull(row[3]) else ""
                            st.session_state.temp_data.append({"q": q, "a": a})
                        
                        st.success(f"✅ Hệ thống đã dò thấy {len(st.session_state.temp_data)} câu hỏi!")
                        break
                    except: continue

            st.divider()
            m_de = st.text_input("👉 Bước 1: Nhập Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "")
            
            if m_de:
                st.markdown(f"**👉 Bước 2: Copy link cho học sinh:**")
                link_hs = f"https://toan-lop-3-thay-thai.streamlit.app/?de={m_de}"
                st.markdown(f'<div class="link-box" id="link_val">{link_hs}</div>', unsafe_allow_html=True)
                # Nút Copy mạnh hơn
                if st.button("📋 CLICK ĐỂ COPY LINK", use_container_width=True):
                    st.write(f'<script>navigator.clipboard.writeText("{link_hs}"); alert("Đã copy!");</script>', unsafe_allow_html=True)

            st.divider()
            st.markdown("**👉 Bước 3: Soạn câu hỏi (Tự động điền số câu từ file):**")
            
            # --- TỰ ĐỘNG ĐIỀN SỐ CÂU ---
            count_q = len(st.session_state.temp_data) if st.session_state.temp_data else 5
            num_q = st.number_input("Số lượng câu hiện có:", 1, 1000, value=count_q)

            with st.form("admin_form"):
                new_qs = []
                for i in range(1, num_q + 1):
                    # Hiển thị dữ liệu từ câu 1 (index 0)
                    vq = st.session_state.temp_data[i-1]["q"] if i <= len(st.session_state.temp_data) else ""
                    va = st.session_state.temp_data[i-1]["a"] if i <= len(st.session_state.temp_data) else ""
                    st.markdown(f"**Câu {i}**")
                    q_in = st.text_input(f"Nội dung {i}", value=vq, key=f"q{i}", label_visibility="collapsed")
                    a_in = st.text_input(f"Đáp án {i}", value=va, key=f"a{i}")
                    new_qs.append({"q": q_in, "a": a_in})
                if st.form_submit_button("🚀 LƯU ĐỀ & XUẤT BẢN", use_container_width=True):
                    library[m_de] = new_qs; save_db("LIB", library); st.success("Đã lưu!"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- PHẦN HỌC SINH ---
    if ma_de_url in library:
        st.markdown(f'<div class="card"><h3>✍️ BÀI TẬP: {ma_de_url}</h3></div>', unsafe_allow_html=True)
    else: st.info("Chào mừng các em! Hãy sử dụng link Thầy Thái gửi.")
st.markdown('</div>', unsafe_allow_html=True)
