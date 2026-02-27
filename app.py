import streamlit as st
import json, os, pandas as pd
import io

# --- 1. CẤU HÌNH GIAO DIỆN & XỬ LÝ LINK ---
st.set_page_config(page_title="Toan Lop 3 - Thay Thai", layout="wide")

# Đọc tham số từ link ngay khi trang tải
query_params = st.query_params
ma_de_url = query_params.get("de", "")
role = query_params.get("role", "student")

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
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU ---
DB_PATH = "quiz_lib.json"
def load_db():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}
def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

library = load_db()

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
        pwd = st.text_input("Mật mã quản trị", type="password", key="pwd_f")
        if pwd == "thai2026":
            st.success("Đã xác thực")
            up_f = st.file_uploader("📤 Tải đề từ CSV", type=["csv"], key=f"up_{st.session_state.ver_key}")
            if up_f:
                df = pd.read_csv(up_f, header=None).dropna(how='all')
                newList = []
                for _, r in df.iterrows():
                    if any(x in str(r[0]).lower() for x in ["stt", "câu"]): continue
                    newList.append({"q": f"{str(r[1])}: {str(r[2])}" if pd.notnull(r[1]) else str(r[2]), "a": str(r[3]) if len(r)>3 else ""})
                if newList:
                    st.session_state.data_step3 = newList
                    st.session_state.ver_key += 1
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            list_de = list(library.keys())
            de_chon = st.selectbox("📂 Lấy dữ liệu từ đề cũ:", options=["-- Tạo mới --"] + list_de, key="sel_de")
            if de_chon != "-- Tạo mới --" and st.session_state.get('last_de') != de_chon:
                st.session_state.data_step3 = library.get(de_chon, [])
                st.session_state.last_de = de_chon
                st.session_state.ver_key += 1
                st.rerun()

            st.divider()
            # BƯỚC 1 & 2: NHẬP MÃ ĐỀ VÀ HIỆN LINK
            m_de = st.text_input("👉 Bước 1: Nhập Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "").strip()
            
            if m_de:
                st.markdown("**👉 Bước 2: Bôi đen dòng dưới đây để Copy gửi cho học sinh:**")
                # Lấy domain tự động để tránh lỗi Not Found
                final_link = f"https://toan-lop-3-thay-thai.streamlit.app/?de={m_de}"
                st.text_input("Link bài tập:", value=final_link, key="link_out", label_visibility="collapsed")
                st.caption("Nháy đúp vào ô trên để chọn toàn bộ link.")

            st.divider()
            # NÚT LƯU NẰM TRÊN BƯỚC 3
            if st.button("🚀 LƯU ĐỀ VÀO KHO & XUẤT BẢN", use_container_width=True, type="primary"):
                if m_de:
                    final_qs = []
                    num_qs = len(st.session_state.data_step3) if st.session_state.data_step3 else 5
                    for i in range(1, num_qs + 1):
                        q = st.session_state.get(f"q_{st.session_state.ver_key}_{i}", "")
                        a = st.session_state.get(f"a_{st.session_state.ver_key}_{i}", "")
                        final_qs.append({"q": q, "a": a})
                    library[m_de] = final_qs
                    save_db(library)
                    st.success(f"Đã lưu đề {m_de} thành công!")
                    st.rerun()

            st.markdown("**👉 Bước 3: Soạn thảo nội dung:**")
            count_data = len(st.session_state.data_step3) if st.session_state.data_step3 else 5
            num_q = st.number_input("Số câu hiển thị:", 1, 100, value=count_data, key=f"num_{st.session_state.ver_key}")

            for i in range(1, num_q + 1):
                vq = st.session_state.data_step3[i-1]["q"] if i <= len(st.session_state.data_step3) else ""
                va = st.session_state.data_step3[i-1]["a"] if i <= len(st.session_state.data_step3) else ""
                st.markdown(f"**Câu {i}**")
                st.text_input(f"Nội dung {i}", value=vq, key=f"q_{st.session_state.ver_key}_{i}", label_visibility="collapsed")
                st.text_input(f"Đáp án", value=va, key=f"a_{st.session_state.ver_key}_{i}")
                st.markdown("---")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # HIỂN THỊ CHO HỌC SINH
    if ma_de_url and ma_de_url in library:
        st.markdown(f'<div class="card"><h3>✍️ ĐANG LÀM ĐỀ: {ma_de_url}</h3></div>', unsafe_allow_html=True)
        for idx, item in enumerate(library[ma_de_url], 1):
            st.markdown(f'<div class="card"><b>Câu {idx}:</b> {item["q"]}</div>', unsafe_allow_html=True)
            st.text_input("Câu trả lời của em:", key=f"ans_{idx}")
    else:
        st.info("Chào mừng các em! Vui lòng dùng đúng link Thầy gửi.")
st.markdown('</div>', unsafe_allow_html=True)
