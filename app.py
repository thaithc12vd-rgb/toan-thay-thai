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
ma_de_url = st.query_params.get("de", "").strip() 
role = st.query_params.get("role", "student")

if 'data_step3' not in st.session_state:
    st.session_state.data_step3 = []
if 'ver_key' not in st.session_state:
    st.session_state.ver_key = 0

st.markdown(f'<div class="sticky-header"><div class="main-title">TOÁN LỚP 3 - THẦY THÁI</div><div class="sub-title">Hệ thống quản lý chuyên nghiệp</div></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="small-inline-title">🔑 BẢO MẬT</span>', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã", type="password", key="pwd_safe_v15", label_visibility="collapsed")
        
        if pwd == "thai2026":
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📁 FILE MẪU</span>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"STT": [1], "Yêu cầu": ["Tính"], "Nội dung": ["10+20=?"], "Đáp án": ["30"]})
            st.download_button("📥 TẢI CSV MẪU", df_m.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'), "mau.csv", "text/csv", use_container_width=True)
            
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📤 UPLOAD ĐỀ</span>', unsafe_allow_html=True)
            up_f = st.file_uploader("", type=["csv"], label_visibility="collapsed", key="file_up_v15")
            
            if up_f is not None:
                raw = up_f.getvalue()
                for enc in ['utf-8-sig', 'windows-1258', 'utf-8']:
                    try:
                        df_u = pd.read_csv(io.BytesIO(raw), encoding=enc, header=None)
                        df_u = df_u.dropna(how='all')
                        newList = []
                        for idx, r in df_u.iterrows():
                            if any(x in str(r[0]).lower() for x in ["stt", "câu", "cau"]): continue
                            q_v = f"{str(r[1])}: {str(r[2])}" if pd.notnull(r[1]) else str(r[2])
                            newList.append({"q": q_v, "a": str(r[3]) if len(r) > 3 else ""})
                        if newList:
                            st.session_state.data_step3 = newList
                            st.session_state.ver_key += 1
                        break
                    except: continue
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 QUẢN LÝ NỘI DUNG")
            list_de = list(library.keys())
            de_chon = st.selectbox("Lấy dữ liệu từ đề cũ:", options=["-- Tạo mới --"] + list_de)
            
            if de_chon != "-- Tạo mới --" and not st.session_state.data_step3:
                st.session_state.data_step3 = library.get(de_chon, [])
                st.session_state.ver_key += 1

            st.divider()
            m_de_input = st.text_input("👉 Bước 1: Nhập Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "").strip()

            if m_de_input:
                st.markdown(f"**👉 Bước 2: Copy link cho học sinh:**")
                # ĐỊA CHỈ GỐC CỐ ĐỊNH - KHÔNG DÙNG DẤU CÁCH
                base_url = "https://toan-lop-3-thay-thai.streamlit.app/"
                clean_url = f"{base_url}?de={m_de_input}"
                st.markdown(f'<div class="link-box">{clean_url}</div>', unsafe_allow_html=True)
                
                # JAVASCRIPT COPY SIÊU SẠCH - FIX BAD REQUEST
                js_clean = f"""
                <script>
                function copySafe() {{
                    var link = "{base_url}" + "?de=" + encodeURIComponent("{m_de_input}");
                    var el = document.createElement('textarea');
                    el.value = link;
                    document.body.appendChild(el);
                    el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    alert("✅ Đã copy link chuẩn! Thầy hãy dán qua trình duyệt khác.");
                }}
                </script>
                <button onclick="copySafe()" style="width:100%; padding:15px; background-color:#004F98; color:white; border-radius:12px; border:none; font-weight:bold; cursor:pointer;">📋 NHẤN ĐỂ COPY LINK</button>
                """
                st.markdown(js_clean, unsafe_allow_html=True)

            st.divider()
            # NÚT LƯU NẰM TRÊN DÒNG BƯỚC 3
            if st.button("🚀 NHẤN VÀO ĐÂY ĐỂ LƯU ĐỀ VÀ XUẤT BẢN", use_container_width=True, type="primary"):
                if m_de_input:
                    final_qs = []
                    num_qs = len(st.session_state.data_step3) if st.session_state.data_step3 else 5
                    for i in range(1, num_qs + 1):
                        q_val = st.session_state.get(f"q_{st.session_state.ver_key}_{i}", "")
                        a_val = st.session_state.get(f"a_{st.session_state.ver_key}_{i}", "")
                        final_qs.append({"q": q_val, "a": a_val})
                    library[m_de_input] = final_qs
                    save_db("LIB", library)
                    st.session_state.data_step3 = []
                    st.success("Đã lưu thành công!")
                    st.rerun()

            st.markdown("**👉 Bước 3: Soạn thảo và Lưu bài:**")
            total_qs = len(st.session_state.data_step3) if st.session_state.data_step3 else 5
            num_q = st.number_input("Số câu hiện có:", 1, 1000, value=total_qs, key=f"num_{st.session_state.ver_key}")

            for i in range(1, num_q + 1):
                vq = st.session_state.data_step3[i-1]["q"] if i <= len(st.session_state.data_step3) else ""
                va = st.session_state.data_step3[i-1]["a"] if i <= len(st.session_state.data_step3) else ""
                st.markdown(f"**Câu {i}**")
                st.text_input(f"Q_{i}", value=vq, key=f"q_{st.session_state.ver_key}_{i}", label_visibility="collapsed")
                st.text_input(f"Đáp án", value=va, key=f"a_{st.session_state.ver_key}_{i}")
                st.markdown("---")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    if ma_de_url in library:
        st.markdown(f'<div class="card"><h3>✍️ BÀI TẬP: {ma_de_url}</h3></div>', unsafe_allow_html=True)
    else: st.info("Chào mừng các em!")
st.markdown('</div>', unsafe_allow_html=True)
