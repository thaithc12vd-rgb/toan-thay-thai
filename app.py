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
        with open(DB[k], "r", encoding="utf-8") as f: return json.load(f)
    return {}
def save_db(k, d):
    with open(DB[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

library = load_db("LIB")
config = load_db("CFG")
ma_de_url = st.query_params.get("de", "")
role = st.query_params.get("role", "student")

# --- HEADER THEO VAI TRÒ (BẢO TOÀN) ---
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
            df_m = pd.DataFrame({"Câu": [1], "Yêu cầu": ["Tính"], "Nội dung câu hỏi": ["10 + 5 = ?"], "Đáp án": ["15"]})
            # Xuất file mẫu dùng chuẩn UTF-8-SIG để máy Thầy mở lên không bị lỗi font
            csv_m = df_m.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 TẢI CSV MẪU", csv_m.encode('utf-8-sig'), "mau_chuan.csv", "text/csv", use_container_width=True)
            
            st.markdown('<span class="small-inline-title" style="margin-top:15px;">📤 UPLOAD ĐỀ</span>', unsafe_allow_html=True)
            up_f = st.file_uploader("", type=["csv"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📝 QUẢN LÝ ĐỀ BÀI")
            de_chon = st.selectbox("Lấy dữ liệu từ đề cũ:", options=["-- Tạo mới --"] + list(library.keys()))
            data_load = library.get(de_chon, [])

            # --- XỬ LÝ UPLOAD THÔNG MINH (CHẤP NHẬN MỌI CHUẨN MÁY TÍNH) ---
            if up_f is not None:
                raw_bytes = up_f.getvalue()
                # Danh sách các bảng mã phổ biến nhất (UTF-8, ANSI Việt Nam, Windows)
                for encoding_type in ['utf-8-sig', 'utf-16', 'windows-1258', 'cp1252', 'utf-8']:
                    try:
                        df_u = pd.read_csv(io.BytesIO(raw_bytes), encoding=encoding_type)
                        df_u = df_u.dropna(how='all') # Xóa dòng trống
                        
                        temp_data = []
                        for _, r in df_u.iterrows():
                            # Lấy chính xác dữ liệu từ các cột
                            q_text = f"{str(r.iloc[1])}: {str(r.iloc[2])}"
                            a_text = str(r.iloc[3])
                            temp_data.append({"q": q_text, "a": a_text})
                        
                        data_load = temp_data
                        st.success(f"✅ Tải thành công {len(data_load)} câu với bảng mã: {encoding_type}")
                        break # Nếu đọc thành công thì dừng thử các bảng mã khác
                    except:
                        continue

            st.divider()
            m_de = st.text_input("👉 Bước 1: Nhập Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "")
            
            if m_de:
                st.markdown(f"**👉 Bước 2: Copy link cho học sinh:**")
                link_hs = f"https://toan-lop-3-thay-thai.streamlit.app/?de={m_de}"
                st.markdown(f'<div class="link-box">{link_hs}</div>', unsafe_allow_html=True)
                
                # NÚT COPY CƯỠNG ÉP (CHẠY TRÊN MỌI TRÌNH DUYỆT)
                js_code = f"""
                <script>
                function forceCopy() {{
                    const el = document.createElement('textarea');
                    el.value = '{link_hs}';
                    document.body.appendChild(el);
                    el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    alert("✅ Đã copy link thành công!");
                }}
                </script>
                <button onclick="forceCopy()" style="width:100%; padding:15px; background-color:#004F98; color:white; border-radius:12px; border:none; font-weight:bold; cursor:pointer; font-size:18px;">
                📋 NHẤN VÀO ĐÂY ĐỂ COPY LINK (KHÔNG CẦN PHÍM TẮT)
                </button>
                """
                st.markdown(js_code, unsafe_allow_html=True)

            st.divider()
            st.markdown("**👉 Bước 3: Soạn câu hỏi (Kiểm tra từ câu 1 bên dưới):**")
            num_q = st.number_input("Số câu hiển thị:", 1, 1000, len(data_load) if data_load else 5)
            with st.form("admin_form"):
                new_qs = []
                for i in range(1, num_q + 1):
                    # Đảm bảo hiển thị từ câu 1 (index 0)
                    vq = data_load[i-1]["q"] if i <= len(data_load) else ""
                    va = data_load[i-1]["a"] if i <= len(data_load) else ""
                    st.markdown(f"**Câu {i}**")
                    q_in = st.text_input(f"Nội dung {i}", value=vq, key=f"q{i}", label_visibility="collapsed")
                    a_in = st.text_input(f"Đáp án {i}", value=va, key=f"a{i}", placeholder="Đáp án...")
                    new_qs.append({"q": q_in, "a": a_in})
                if st.form_submit_button("🚀 LƯU ĐỀ & XUẤT BẢN", use_container_width=True):
                    library[m_de] = new_qs; save_db("LIB", library); st.success("Đã lưu!"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- PHẦN HỌC SINH (BẢO TOÀN) ---
    if ma_de_url in library:
        st.markdown(f'<div class="card"><h3>✍️ BÀI TẬP: {ma_de_url}</h3></div>', unsafe_allow_html=True)
    else: st.info("Chào mừng các em! Hãy sử dụng link Thầy gửi.")
st.markdown('</div>', unsafe_allow_html=True)
