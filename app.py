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
ma_de_url = st.query_params.get("de", "").strip() 
role = st.query_params.get("role", "student")

# --- KHỞI TẠO BỘ NHỚ (DÙNG ĐỂ BAY DỮ LIỆU VÀO BƯỚC 3) ---
if 'data_step3' not in st.session_state:
    st.session_state.data_step3 = []

# --- HEADER PHÂN QUYỀN ---
h_title = "CHÀO MỪNG THẦY ĐẾY VỚI APP TOÁN LỚP 3" if role == "teacher" else "TOÁN LỚP 3 - THẦY THÁI"
h_sub = "Chúc thầy luôn vượt qua thử thách" if role == "teacher" else "Chúc các em làm bài tốt"

st.markdown(f'<div class="sticky-header"><div class="main-title">{h_title}</div><div class="sub-title">{h_sub}</div></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="small-inline-title">🔑 BẢO MẬT</span>', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã", type="password", key="pwd_gv_final", label_visibility="collapsed")
        
        if pwd == "thai2026":
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📁 FILE MẪU</span>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"STT": [1], "Yêu cầu": ["Tính"], "Nội dung": ["10+20=?"], "Đáp án": ["30"]})
            csv_m = df_m.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 TẢI CSV MẪU", csv_m.encode('utf-8-sig'), "mau.csv", "text/csv", use_container_width=True)
            
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📤 UPLOAD ĐỀ</span>', unsafe_allow_html=True)
            up_f = st.file_uploader("", type=["csv"], label_visibility="collapsed", key="uploader_fix_v1")
            
            if up_f is not None:
                raw = up_f.getvalue()
                for enc in ['utf-8-sig', 'windows-1258', 'utf-8', 'latin-1']:
                    try:
                        df_u = pd.read_csv(io.BytesIO(raw), encoding=enc, header=None)
                        df_u = df_u.dropna(how='all')
                        newList = []
                        for idx, r in df_u.iterrows():
                            # Lọc dòng tiêu đề STT/Câu
                            if any(x in str(r[0]).lower() for x in ["stt", "câu", "cau"]): continue
                            q_v = f"{str(r[1])}: {str(r[2])}" if pd.notnull(r[1]) else str(r[2])
                            newList.append({"q": q_v, "a": str(r[3]) if len(r) > 3 else ""})
                        
                        if newList:
                            # ÉP BUỘC GHI ĐÈ DỮ LIỆU VÀO SESSION STATE
                            st.session_state.data_step3 = newList
                            # Xóa các key cũ để không bị ghi đè dữ liệu cũ vào ô soạn thảo
                            for key in list(st.session_state.keys()):
                                if key.startswith("q_in_") or key.startswith("a_in_"):
                                    del st.session_state[key]
                        break
                    except: continue
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 QUẢN LÝ ĐỀ BÀI")
            de_chon = st.selectbox("Lấy dữ liệu từ đề cũ:", options=["-- Tạo mới --"] + list(library.keys()))
            
            if de_chon != "-- Tạo mới --" and not st.session_state.data_step3:
                st.session_state.data_step3 = library.get(de_chon, [])

            st.divider()
            m_de = st.text_input("👉 Bước 1: Nhập Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "").strip()
            
            if m_de:
                st.markdown(f"**👉 Bước 2: Copy link cho học sinh:**")
                clean_url = f"https://toan-lop-3-thay-thai.streamlit.app/?de={m_de}"
                st.markdown(f'<div class="link-box">{clean_url}</div>', unsafe_allow_html=True)
                js_cp = f"""
                <script>
                function clickCopy() {{
                    var text = "{clean_url}";
                    var el = document.createElement('textarea'); el.value = text;
                    document.body.appendChild(el); el.select();
                    document.execCommand('copy'); document.body.removeChild(el);
                    alert("✅ Đã copy thành công!");
                }}
                </script>
                <button onclick="clickCopy()" style="width:100%; padding:15px; background-color:#004F98; color:white; border-radius:12px; border:none; font-weight:bold; cursor:pointer; font-size:18px;">
                📋 NHẤN ĐỂ COPY LINK
                </button>
                """
                st.markdown(js_cp, unsafe_allow_html=True)

            st.divider()
            
            # --- YÊU CẦU: NÚT LƯU LÊN PHÍA TRÊN DÒNG BƯỚC 3 ---
            if st.button("🚀 NHẤN VÀO ĐÂY ĐỂ LƯU ĐỀ VÀ XUẤT BẢN", use_container_width=True, type="primary"):
                if m_de:
                    final_qs = []
                    # Đếm số lượng câu hiện có trong giao diện
                    total_to_save = len(st.session_state.data_step3) if st.session_state.data_step3 else 5
                    for i in range(1, total_to_save + 1):
                        # Lấy dữ liệu trực tiếp từ các ô text_input đã nhập
                        q_val = st.session_state.get(f"q_in_{i}", "")
                        a_val = st.session_state.get(f"a_in_{i}", "")
                        final_qs.append({"q": q_val, "a": a_val})
                    
                    library[m_de] = final_qs
                    save_db("LIB", library)
                    st.session_state.data_step3 = []
                    st.success(f"Đã lưu thành công đề {m_de}!")
                    st.rerun()
                else:
                    st.error("Vui lòng nhập Mã đề!")

            st.markdown("**👉 Bước 3: Soạn thảo và Lưu bài (Dữ liệu tự động hiện bên dưới):**")
            
            total_qs = len(st.session_state.data_step3) if st.session_state.data_step3 else 5
            num_q = st.number_input("Số câu hiện có:", 1, 1000, value=total_qs)

            # Vòng lặp hiển thị từng câu (index 0 là Câu 1)
            for i in range(1, num_q + 1):
                vq = st.session_state.data_step3[i-1]["q"] if i <= len(st.session_state.data_step3) else ""
                va = st.session_state.data_step3[i-1]["a"] if i <= len(st.session_state.data_step3) else ""
                
                st.markdown(f"**Câu {i}**")
                # Hiển thị nội dung câu hỏi
                st.text_input(f"Nội dung câu {i}", value=vq, key=f"q_in_{i}", label_visibility="collapsed")
                # Hiển thị ô Đáp án ngay bên dưới
                st.text_input(f"Đáp án", value=va, key=f"a_in_{i}")
                st.markdown("---")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    if ma_de_url in library:
        st.markdown(f'<div class="card"><h3>✍️ BÀI TẬP: {ma_de_url}</h3></div>', unsafe_allow_html=True)
    else: st.info("Chào mừng các em!")
st.markdown('</div>', unsafe_allow_html=True)
