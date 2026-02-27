import streamlit as st
import json, os, pandas as pd
import io
from datetime import datetime

# --- 1. CẤU HÌNH GIAO DIỆN & XỬ LÝ LINK ---
st.set_page_config(page_title="Toan Lop 3 - Thay Thai", layout="wide")

query_params = st.query_params
ma_de_url = query_params.get("de", "")
role = query_params.get("role", "student")

if role == "teacher":
    display_title = "HỆ THỐNG QUẢN LÝ CÂU HỎI YOUTUBE"
    display_subtitle = "Chúc thầy vượt qua mọi thử thách"
else:
    display_title = "TOÁN LỚP 3 - THẦY THÁI"
    display_subtitle = "Chúc các em làm bài tốt"

st.markdown(f"""
<style>
    #MainMenu, footer, header, .stDeployButton {{visibility: hidden; display:none !important;}}
    .stApp {{ background-color: #C5D3E8; }} 
    .sticky-header {{
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; padding: 10px 0; z-index: 1000;
        border-bottom: 2px solid #004F98; text-transform: uppercase;
    }}
    .main-title {{ font-size: 30px; font-weight: 900; margin: 0; }}
    .sub-title {{ font-size: 11px; font-weight: bold; margin: 0; color: #004F98; opacity: 0.9; }}
    
    /* ĐIỀU CHỈNH KHOẢNG CÁCH NỘI DUNG CHÍNH */
    .main-content {{ margin-top: 100px; margin-bottom: 80px; padding: 0 20px; }}
    
    .card {{ background-color: white; border-radius: 15px; padding: 20px; border-top: 8px solid #004F98; box-shadow: 0 8px 20px rgba(0,0,0,0.1); margin-bottom: 15px; }}
    
    /* KHỐI DI CHUYỂN SÁT LÊN TRÊN (~2CM) */
    .move-up-container {{
        position: relative;
        top: -65px; /* ÉP CẢ CỤM DỜI LÊN CAO SÁT CHỮ KÝ */
        text-align: center;
        z-index: 99;
    }}
    
    .mini-quiz-box {{
        background-color: #1A2238; 
        color: #FFD700; 
        padding: 5px 20px; 
        border-radius: 20px; 
        display: inline-block; 
        font-size: 12px; 
        font-weight: bold;
        border: 1px solid #FFD700;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }}

    .fixed-footer {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98;
        text-align: center; padding: 10px 0; font-weight: bold;
        font-size: 14px; z-index: 1001; border-top: 1px solid rgba(0,79,152,0.1);
    }}
    
    .ultra-tight-hr {{ 
        margin: 0 auto 15px auto !important; 
        border: 0; 
        border-top: 1px solid rgba(0,0,0,0.1); 
        width: 100%;
    }}
</style>
<div class="sticky-header">
    <div class="main-title">{display_title}</div>
    <div class="sub-title">{display_subtitle}</div>
</div>
<div class="fixed-footer">DESIGN BY TRAN HOANG THAI</div>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU ---
DB_PATH = "quiz_lib.json"
RESULT_PATH = "student_results.json"

def load_db(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {}
    return {}

def save_db(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f: 
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Lỗi lưu file: {e}")

library = load_db(DB_PATH)

if 'data_step3' not in st.session_state:
    st.session_state.data_step3 = []
if 'ver_key' not in st.session_state:
    st.session_state.ver_key = 0

st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã quản trị", type="password", key="pwd_f")
        if pwd == "thai2026":
            st.success("Đã xác nhận")
            up_f = st.file_uploader("📤 Tải đề từ CSV", type=["csv"], key=f"up_{st.session_state.ver_key}")
            if up_f:
                try:
                    df = pd.read_csv(up_f, header=None, encoding='utf-8-sig', encoding_errors='replace').dropna(how='all')
                    newList = []
                    for _, r in df.iterrows():
                        if any(x in str(r[0]).lower() for x in ["stt", "câu"]): continue
                        q_text = f"{str(r[1])}: {str(r[2])}" if pd.notnull(r[1]) else str(r[2])
                        newList.append({"q": q_text, "a": str(r[3]) if len(r)>3 else ""})
                    if newList:
                        st.session_state.data_step3 = newList
                        st.session_state.ver_key += 1
                        st.rerun()
                except Exception as e:
                    st.error(f"Lỗi đọc dữ liệu: {e}")
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
            m_de = st.text_input("👉 Bước 1: Nhập Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "").strip()
            
            if m_de:
                st.markdown("**👉 Bước 2: Bôi đen dòng dưới đây để Copy:**")
                base_url = "https://toan-thay-thai-spgcbe5cuemztnk5wuadum.streamlit.app/"
                final_link = f"{base_url}?de={m_de}"
                st.text_input("Link bài tập:", value=final_link, key="link_out", label_visibility="collapsed")

            st.divider()
            if st.button("🚀 LƯU ĐỀ VÀO KHO & XUẤT BẢN", use_container_width=True, type="primary"):
                if m_de:
                    final_qs = []
                    num_qs = len(st.session_state.data_step3) if st.session_state.data_step3 else 5
                    for i in range(1, num_qs + 1):
                        q_val = st.session_state.get(f"q_{st.session_state.ver_key}_{i}", "")
                        a_val = st.session_state.get(f"a_{st.session_state.ver_key}_{i}", "")
                        final_qs.append({"q": q_val, "a": a_val})
                    library[m_de] = final_qs
                    save_db(DB_PATH, library)
                    st.success(f"Đã lưu thành công đề: {m_de}")
                    st.rerun()

            st.markdown("**👉 Bước 3: Soạn thảo nội dung:**")
            count_data = len(st.session_state.data_step3) if st.session_state.data_step3 else 5
            num_q = st.number_input("Số câu hiện có:", 1, 100, value=count_data, key=f"num_{st.session_state.ver_key}")
            for i in range(1, num_q + 1):
                vq = st.session_state.data_step3[i-1]["q"] if i <= len(st.session_state.data_step3) else ""
                va = st.session_state.data_step3[i-1]["a"] if i <= len(st.session_state.data_step3) else ""
                st.markdown(f"**Câu {i}**")
                st.text_input(f"Nội dung {i}", value=vq, key=f"q_{st.session_state.ver_key}_{i}", label_visibility="collapsed")
                st.text_input(f"Đáp án", value=va, key=f"a_{st.session_state.ver_key}_{i}")
                st.markdown("---")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- GIAO DIỆN HỌC SINH ---
    if ma_de_url and ma_de_url in library:
        # CỤM KHỐI DỜI LÊN SÁT CHỮ KÝ
        st.markdown(f'''
            <div class="move-up-container">
                <div class="mini-quiz-box">ĐANG LÀM ĐỀ: {ma_de_url}</div>
                <hr class="ultra-tight-hr">
            </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="card" style="margin-top:-50px;">', unsafe_allow_html=True)
        student_name = st.text_input("Bước 1: Nhập tên của em để hiện đề bài:", key="student_name").strip()
        st.markdown('</div>', unsafe_allow_html=True)
        
        if student_name:
            st.success(f"Chào {student_name}! Mời em bắt đầu làm bài.")
            answers = {}
            quiz_data = library[ma_de_url]
            for idx, item in enumerate(quiz_data, 1):
                st.markdown(f'<div class="card"><b>Câu {idx}:</b> {item["q"]}</div>', unsafe_allow_html=True)
                answers[f"Câu {idx}"] = st.text_input(f"Trả lời câu {idx}:", key=f"ans_{idx}", label_visibility="collapsed")
            
            if st.button("📝 NỘP BÀI", use_container_width=True, type="primary"):
                correct_count = 0
                for idx, item in enumerate(quiz_data, 1):
                    user_ans = str(answers.get(f"Câu {idx}", "")).strip().lower()
                    real_ans = str(item["a"]).strip().lower()
                    if user_ans == real_ans: correct_count += 1
                
                score = round((correct_count / len(quiz_data)) * 10, 1)
                results = load_db(RESULT_PATH)
                submission = {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "student": student_name,
                    "quiz": ma_de_url,
                    "score": score
                }
                if ma_de_url not in results: results[ma_de_url] = []
                results[ma_de_url].append(submission)
                save_db(RESULT_PATH, results)
                
                st.balloons()
                st.markdown(f"""<div class="card" style="text-align:center; border-top:8px solid #FFD700;">
                    <h2 style="color:#004F98;">KẾT QUẢ CỦA {student_name.upper()}</h2>
                    <h1 style="font-size:60px; color:#d32f2f;">{score} / 10</h1>
                    <p>Em làm đúng {correct_count}/{len(quiz_data)} câu</p>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🟢 DANH SÁCH CÁC BẠN ĐÃ HOÀN THÀNH")
            all_res = load_db(RESULT_PATH).get(ma_de_url, [])
            if all_res:
                df_res = pd.DataFrame(all_res).sort_index(ascending=
