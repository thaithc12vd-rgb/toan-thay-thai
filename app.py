import streamlit as st
import json, os, pandas as pd
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
role = st.query_params.get("role", "student")

# --- HEADER (BẢO TOÀN) ---
if role == "teacher":
    h_title, h_sub = "CHÀO MỪNG THẦY ĐẾN VỚI APP TOÁN LỚP 3", "Chúc thầy luôn vượt qua thử thách"
else:
    h_title, h_sub = "TOÁN LỚP 3 - THẦY THÁI", "Chúc các em làm bài tốt"

st.markdown(f'<div class="sticky-header"><div class="main-title">{h_title}</div><div class="sub-title">{h_sub}</div></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="small-inline-title">🔑 BẢO MẬT</span>', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã", type="password", key="admin_pwd", label_visibility="collapsed")
        
        if pwd == "thai2026":
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">🤖 CẤU HÌNH AI</span>', unsafe_allow_html=True)
            api = st.text_input("Gemini API Key", value=config.get("api_key", ""), type="password", key="admin_api", label_visibility="collapsed")
            if st.button("LƯU API"):
                config["api_key"] = api
                save_db("CFG", config)
                st.toast("Đã lưu API!")

            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📁 FILE MẪU</span>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"Câu": [1], "Yêu cầu": ["Tính"], "Nội dung": ["10+20=?"], "Đáp án": ["30"]})
            csv_m = df_m.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 TẢI CSV MẪU", csv_m.encode('utf-8-sig'), "mau_chuan.csv", "text/csv", use_container_width=True)
            
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📤 UPLOAD ĐỀ</span>', unsafe_allow_html=True)
            up_f = st.file_uploader("", type=["csv"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 QUẢN LÝ NỘI DUNG ĐỀ BÀI")
            de_chon = st.selectbox("Lấy dữ liệu từ đề cũ:", options=["-- Tạo mới --"] + list(library.keys()))
            
            # Khởi tạo danh sách câu hỏi trong session_state
            if 'temp_qs' not in st.session_state or de_chon != "-- Tạo mới --":
                st.session_state.temp_qs = library.get(de_chon, [])

            # --- XỬ LÝ UPLOAD: LẤY TOÀN BỘ DỮ LIỆU ---
            if up_f is not None:
                raw = up_f.getvalue()
                for enc in ['utf-8-sig', 'windows-1258', 'utf-8', 'latin-1', 'cp1252']:
                    try:
                        # Đọc file không header để lấy sạch dòng đầu
                        df_u = pd.read_csv(io.BytesIO(raw), encoding=enc, header=None)
                        df_u = df_u.dropna(how='all') # Bỏ dòng trắng hoàn toàn
                        
                        newList = []
                        for idx, r in df_u.iterrows():
                            # Nếu dòng chứa tiêu đề 'STT' hoặc 'Câu' thì bỏ, nếu không thì lấy hết
                            val0 = str(r[0]).lower()
                            if "stt" in val0 or "câu" in val0 or "cau" in val0:
                                continue
                            
                            # Lấy dữ liệu: Cột 1 (Yêu cầu) + Cột 2 (Nội dung) -> Cột 3 (Đáp án)
                            q_text = f"{str(r[1])}: {str(r[2])}" if pd.notnull(r[1]) and r[1] != "" else str(r[2])
                            a_text = str(r[3]) if len(r) > 3 else ""
                            newList.append({"q": q_text, "a": a_text})
                        
                        if newList:
                            st.session_state.temp_qs = newList
                            st.success(f"✅ Đã nhận {len(newList)} câu hỏi từ file!")
                            break
                    except: continue

            st.divider()
            m_de = st.text_input("👉 Bước 1: Nhập Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "")
            
            if m_de:
                st.markdown(f"**👉 Bước 2: Copy link cho học sinh:**")
                link_hs = f"https://toan-lop-3-thay-thai.streamlit.app/?de={m_de}"
                st.markdown(f'<div class="link-box">{link_hs}</div>', unsafe_allow_html=True)
                
                # NÚT COPY MẠNH MẼ
                if st.button("📋 NHẤN ĐỂ COPY LINK"):
                    st.write(f'<script>navigator.clipboard.writeText("{link_hs}"); alert("Đã copy thành công!");</script>', unsafe_allow_html=True)

            st.divider()
            st.markdown("**👉 Bước 3: Soạn câu hỏi (Kiểm tra từ Câu 1):**")
            # Tự động đếm số câu
            total = len(st.session_state.temp_qs) if st.session_state.temp_qs else 5
            num_q = st.number_input("Số câu hiện có:", 1, 1000, value=total)

            with st.form("admin_form"):
                new_qs = []
                for i in range(1, num_q + 1):
                    vq = st.session_state.temp_qs[i-1]["q"] if i <= len(st.session_state.temp_qs) else ""
                    va = st.session_state.temp_qs[i-1]["a"] if i <= len(st.session_state.temp_qs) else ""
                    st.markdown(f"**Câu {i}**")
                    q_in = st.text_input(f"Câu hỏi {i}", value=vq, key=f"q{i}", label_visibility="collapsed")
                    a_in = st.text_input(f"Đáp án {i}", value=va, key=f"a{i}")
                    new_qs.append({"q": q_in, "a": a_in})
                if st.form_submit_button("🚀 LƯU ĐỀ & XUẤT BẢN", use_container_width=True):
                    library[m_de] = new_qs; save_db("LIB", library); st.success("Đã lưu!"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
else:
    if ma_de_url in library:
        st.markdown(f'<div class="card"><h3>✍️ BÀI TẬP: {ma_de_url}</h3></div>', unsafe_allow_html=True)
    else: st.info("Chào mừng các em! Hãy sử dụng link Thầy gửi.")
st.markdown('</div>', unsafe_allow_html=True)
