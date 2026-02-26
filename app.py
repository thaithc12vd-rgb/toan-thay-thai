import streamlit as st
import google.generativeai as genai
import json
import os
import time
import pandas as pd

# --- 1. CẤU HÌNH GIAO DIỆN PHONG THỦY & GHIM CỐ ĐỊNH ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide", page_icon="🎓")

st.markdown("""
<style>
    /* ẨN CÁC THÀNH PHẦN HỆ THỐNG */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display:none !important;}

    /* NỀN XÁM XANH MỆNH THỦY */
    .stApp { background-color: #C5D3E8; } 

    /* HEADER CỐ ĐỊNH */
    .sticky-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-size: clamp(20px, 5vw, 40px) !important;
        font-weight: 900 !important; padding: 10px 0; z-index: 1000;
        border-bottom: 2px solid rgba(0, 79, 152, 0.2); text-transform: uppercase;
    }

    /* FOOTER CỐ ĐỊNH */
    .sticky-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-weight: bold; padding: 12px 0;
        font-size: 15px; z-index: 1000; border-top: 2px solid rgba(0, 79, 152, 0.2);
    }

    /* VÙNG NỘI DUNG CHÍNH */
    .main-content { margin-top: 100px; margin-bottom: 100px; padding: 0 20px; }

    /* KHUNG TRẮNG PHÂN KHU */
    .admin-card {
        background-color: white; border-radius: 20px; padding: 25px;
        border-top: 10px solid #004F98; box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }

    /* HỘP HIỂN THỊ LINK */
    .link-container {
        display: flex; align-items: center; background-color: #f1f3f4;
        padding: 10px; border-radius: 8px; border: 1px solid #004F98;
        margin-top: 10px;
    }
    .url-text { color: #d32f2f; font-family: monospace; flex-grow: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU ---
FILES = {"LIB": "quiz_library.json", "CONFIG": "config.json"}
def load_db(k):
    if os.path.exists(FILES[k]):
        with open(FILES[k], "r", encoding="utf-8") as f: return json.load(f)
    return {}
def save_db(k, d):
    with open(FILES[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

config = load_db("CONFIG")
library = load_db("LIB")

# HIỂN THỊ HEADER/FOOTER
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
st.markdown('<div class="sticky-footer">DESIGNED BY TRẦN HOÀNG THÁI</div>', unsafe_allow_html=True)

# LẤY THAM SỐ TỪ URL
role = st.query_params.get("role", "student")
ma_de_tu_link = st.query_params.get("de", "")

st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ==========================================
# CỔNG QUẢN TRỊ (CHIA CỘT TRÁI - PHẢI)
# ==========================================
if role == "teacher":
    col_left, col_right = st.columns([1, 3.5], gap="large")

    with col_left:
        st.markdown('<div class="admin-card">', unsafe_allow_html=True)
        st.subheader("🔑 BẢO MẬT")
        pwd = st.text_input("Mật mã:", type="password")
        st.divider()
        st.subheader("🤖 CẤU HÌNH AI")
        api_key = st.text_input("Gemini API Key:", value=config.get("api_key", ""), type="password")
        if st.button("LƯU CẤU HÌNH"):
            save_db("CONFIG", {"api_key": api_key})
            st.success("Đã lưu API!")
        
        if pwd == "thai2026":
            st.divider()
            st.subheader("📁 FILE MẪU")
            df_mau = pd.DataFrame({"Câu hỏi": ["20 + 30 = ?", "Hình vuông cạnh 5cm. Chu vi?"], "Đáp án": ["50", "20"]})
            st.download_button("📥 Tải file mẫu (Excel/CSV)", df_mau.to_csv(index=False).encode('utf-8-sig'), "mau_de_bai.csv", "text/csv")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        if pwd == "thai2026":
            st.markdown('<div class="admin-card">', unsafe_allow_html=True)
            st.subheader("📝 BẢNG NHẬP LIỆU CÂU HỎI")
            
            # Chọn đề cũ
            danh_sach_de = ["-- Tạo đề mới --"] + list(library.keys())
            de_chon = st.selectbox("Chọn đề từ thư viện để lấy dữ liệu:", options=danh_sach_de)
            
            # Upload file hàng loạt
            up_file = st.file_uploader("📤 Hoặc tải lên file đề đã soạn (CSV):", type=["csv"])
            
            data_load = library.get(de_chon, [])
            if up_file:
                df_up = pd.read_csv(up_file)
                data_load = [{"q": r[0], "a": str(r[1])} for r in df_up.values]

            st.divider()
            
            c_mde, c_num = st.columns([3, 1])
            with c_mde:
                ma_de_moi = st.text_input("Mã đề (Ví dụ: BAI_01):", value=de_chon if de_chon != "-- Tạo đề mới --" else "")
            with c_num:
                num_q = st.number_input("Số câu:", min_value=1, max_value=30, value=len(data_load) if data_load else 5)

            # TẠO LINK VÀ NÚT COPY
            # Thầy lưu ý sửa dòng link này đúng link web của Thầy nhé
            base_url = "https://toan-lop-3-thay-thai.streamlit.app" 
            full_link = f"{base_url}/?de={ma_de_moi}" if ma_de_moi else base_url
            
            st.write("🔗 **Link bài tập gửi học sinh:**")
            l_col1, l_col2 = st.columns([5, 1])
            with l_col1:
                st.code(full_link, language=None)
            with l_col2:
                # Nút copy tích hợp sẵn của Streamlit qua st.code hoặc dùng mẹo nút bấm
                if st.button("📋 COPY"):
                    st.write(f'<script>navigator.clipboard.writeText("{full_link}")</script>', unsafe_allow_html=True)
                    st.toast("Đã sao chép link!")

            with st.form("admin_form"):
                new_quizzes = []
                col1, col2 = st.columns(2)
                for i in range(1, num_q + 1):
                    v_q = data_load[i-1]["q"] if i <= len(data_load) else ""
                    v_a = data_load[i-1]["a"] if i <= len(data_load) else ""
                    with (col1 if i <= (num_q+1)//2 else col2):
                        q_in = st.text_input(f"Câu hỏi {i}:", value=v_q, key=f"q{i}")
                        a_in = st.text_input(f"Đáp án {i}:", value=v_a, key=f"a{i}")
                        new_quizzes.append({"q": q_in, "a": a_in})
                
                if st.form_submit_button("🚀 LƯU ĐỀ VÀO THƯ VIỆN"):
                    if ma_de_moi:
                        library[ma_de_moi] = new_quizzes
                        save_db("LIB", library)
                        st.success(f"Đã lưu thành công đề: {ma_de_moi}")
                        st.rerun()
                    else: st.error("Thầy chưa nhập mã đề!")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Nhập đúng mật mã bên trái để mở bảng quản trị.")

else:
    # --- CỔNG HỌC SINH (Giữ nguyên logic AI) ---
    if ma_de_tu_link in library:
        st.write(f"### Đang chuẩn bị bài: {ma_de_tu_link}")
    else:
        st.info("Chào mừng các em đến với lớp học của Thầy Thái!")

st.markdown('</div>', unsafe_allow_html=True)
