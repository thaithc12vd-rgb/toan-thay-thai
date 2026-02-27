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
    .main-content {{ margin-top: 100px; margin-bottom: 80px; padding: 0 20px; }}
    .card {{ background-color: white; border-radius: 15px; padding: 20px; border-top: 8px solid #004F98; box-shadow: 0 8px 20px rgba(0,0,0,0.1); margin-bottom: 15px; }}
    
    .move-up-container {{ position: relative; top: -130px; text-align: center; z-index: 99; margin-bottom: -120px; }}
    .mini-quiz-box {{ background-color: #1A2238; color: #FFD700; padding: 5px 20px; border-radius: 20px; display: inline-block; font-size: 12px; font-weight: bold; border: 1px solid #FFD700; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }}
    .invite-text {{ color: #004F98; font-weight: 900; font-size: 18px; text-align: center; margin-bottom: 10px; text-transform: uppercase; }}
    .center-wrapper-top {{ display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: -180px; position: relative; z-index: 100; }}
    .fixed-footer {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: #C5D3E8; color: #004F98; text-align: center; padding: 10px 0; font-weight: bold; font-size: 14px; z-index: 1001; border-top: 1px solid rgba(0,79,152,0.1); }}
    .ultra-tight-hr {{ margin: 5px auto !important; border: 0; border-top: 1px solid rgba(0,0,0,0.1); width: 100%; }}
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

if 'is_accepted' not in st.session_state: st.session_state.is_accepted = False
if 'is_submitted' not in st.session_state: st.session_state.is_submitted = False
if 'ver_key' not in st.session_state: st.session_state.ver_key = 0
if 'data_step3' not in st.session_state: st.session_state.data_step3 = []

st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    # (GIỮ NGUYÊN PHẦN QUẢN TRỊ CỦA THẦY)
    col_l, col_r = st.columns([1, 4], gap="medium")
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã", type="password")
        if pwd == "thai2026":
            up_f = st.file_uploader("📥 CSV", type=["csv"], key=f"up_{st.session_state.ver_key}")
            if up_f:
                df = pd.read_csv(io.BytesIO(up_f.getvalue()), header=None, encoding='utf-8-sig', encoding_errors='replace').dropna(how='all')
                st.session_state.data_step3 = [{"q": f"{r[1]}: {r[2]}" if pd.notnull(r[1]) else r[2], "a": str(r[3]) if len(r)>3 else ""} for _, r in df.iterrows() if "câu" not in str(r[0]).lower()]
                st.session_state.ver_key += 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            list_de = list(library.keys())
            de_chon = st.selectbox("📂 Đề cũ:", ["-- Tạo mới --"] + list_de)
            if de_chon != "-- Tạo mới --" and st.session_state.get('last_de') != de_chon:
                st.session_state.data_step3 = library.get(de_chon, [])
                st.session_state.last_de = de_chon
                st.session_state.ver_key += 1
                st.rerun()
            m_de = st.text_input("👉 Bước 1: Mã đề:", value=de_chon if de_chon != "-- Tạo mới --" else "").strip()
            if m_de:
                st.text_input("Link:", value=f"https://toan-thay-thai-spgcbe5cuemztnk5wuadum.streamlit.app/?de={m_de}")
            if st.button("🚀 LƯU ĐỀ"):
                library[m_de] = [{"q": st.session_state.get(f"q_{st.session_state.ver_key}_{i}", ""), "a": st.session_state.get(f"a_{st.session_state.ver_key}_{i}", "")} for i in range(1, len(st.session_state.data_step3)+1 or 6)]
                save_db(DB_PATH, library); st.rerun()
            num_q = st.number_input("Số câu:", 1, 100, value=len(st.session_state.data_step3) or 5, key=f"n_{st.session_state.ver_key}")
            for i in range(1, num_q + 1):
                vq = st.session_state.data_step3[i-1]["q"] if i <= len(st.session_state.data_step3) else ""
                va = st.session_state.data_step3[i-1]["a"] if i <= len(st.session_state.data_step3) else ""
                st.text_input(f"Q{i}", value=vq, key=f"q_{st.session_state.ver_key}_{i}")
                st.text_input(f"A{i}", value=va, key=f"a_{st.session_state.ver_key}_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- GIAO DIỆN HỌC SINH ---
    if ma_de_url and ma_de_url in library:
        st.markdown(f'<div class="move-up-container"><div class="mini-quiz-box">ĐANG LÀM ĐỀ: {ma_de_url}</div><hr class="ultra-tight-hr"></div>', unsafe_allow_html=True)

        if not st.session_state.is_accepted:
            st.markdown('<div class="center-wrapper-top"><p class="invite-text">MỜI CÁC EM NHẬP HỌ TÊN ĐỂ LÀM BÀI</p>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                name_in = st.text_input("", key="st_name_step", label_visibility="collapsed").strip()
                if st.button("ĐỒNG Ý", use_container_width=True, type="primary"):
                    if name_in: st.session_state.student_name = name_in; st.session_state.is_accepted = True; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # LOGIC: NẾU ĐÃ CHẤP NHẬN VÀ CHƯA NỘP -> HIỆN ĐỀ
        if st.session_state.is_accepted and not st.session_state.is_submitted:
            current_name = st.session_state.student_name
            st.success(f"Chào {current_name}! Mời em bắt đầu làm bài.")
            answers = {}
            quiz_data = library[ma_de_url]
            for idx, item in enumerate(quiz_data, 1):
                st.markdown(f'<div class="card"><b>Câu {idx}:</b> {item["q"]}</div>', unsafe_allow_html=True)
                answers[f"Câu {idx}"] = st.text_input(f"Trả lời câu {idx}:", key=f"ans_{idx}", label_visibility="collapsed")
            
            if st.button("📝 NỘP BÀI", use_container_width=True, type="primary"):
                correct = sum(1 for i, it in enumerate(quiz_data, 1) if str(answers.get(f"Câu {i}", "")).strip().lower() == str(it["a"]).strip().lower())
                score = round((correct / len(quiz_data)) * 10, 1)
                
                res_all = load_db(RESULT_PATH)
                if ma_de_url not in res_all: res_all[ma_de_url] = []
                res_all[ma_de_url].append({"time": datetime.now().strftime("%H:%M:%S"), "student": current_name, "score": score})
                save_db(RESULT_PATH, res_all)
                
                st.session_state.final_score = score
                st.session_state.correct_count = correct
                st.session_state.is_submitted = True
                st.balloons(); st.rerun()

        # LOGIC: NẾU ĐÃ NỘP -> CHỈ HIỆN KẾT QUẢ VÀ BẢNG LIVE
        if st.session_state.is_submitted:
            st.markdown(f"""<div class="card" style="text-align:center; border-top:8px solid #FFD700;">
                <h2 style="color:#004F98;">KẾT QUẢ CỦA {st.session_state.student_name.upper()}</h2>
                <h1 style="font-size:60px; color:#d32f2f;">{st.session_state.final_score} / 10</h1>
                <p>Em làm đúng {st.session_state.correct_count} câu. Đề bài đã được đóng lại.</p>
            </div>""", unsafe_allow_html=True)

            # --- BẢNG XẾP HẠNG LIVE 100 EM ---
            st.markdown('<div class="card">', unsafe_allow_html=True)
            res_data = load_db(RESULT_PATH).get(ma_de_url, [])
            if res_data:
                df = pd.DataFrame(res_data)
                # Tính số lần đạt Top 10 của mỗi bạn dựa trên tên
                top10_counts = df.groupby('student').apply(lambda x: sum(1 for _, r in x.iterrows() if r['score'] >= 9)).to_dict() # Giả định điểm >=9 là có triển vọng top 10
                
                # Sắp xếp theo Điểm giảm dần, sau đó đến Thời gian sớm dần
                df = df.sort_values(by=['score', 'time'], ascending=[False, True]).reset_index(drop=True)
                df.index += 1
                df = df.head(100) # Lấy 100 em
                
                df['Hạng'] = df.index
                df['Top 10'] = df['Hạng'].apply(lambda x: "🏆" if x <= 10 else "")
                df['Lần đạt Top 10'] = df['student'].map(top10_counts)
                
                st.markdown(f"### 🟢 BẢNG VÀNG LIVE (Tổng số: {len(res_data)} em)")
                st.table(df[['Hạng', 'Top 10', 'student', 'score', 'time', 'Lần đạt Top 10']].rename(columns={'student':'Học sinh', 'score':'Điểm', 'time':'Giờ nộp'}))
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Làm bài mới"): # Nút để reset nếu thầy muốn các em làm lại
                st.session_state.is_accepted = False; st.session_state.is_submitted = False; st.rerun()
    else:
        st.info("Chào mừng các em! Vui lòng dùng đúng link Thầy Thái gửi.")

st.markdown('</div>', unsafe_allow_html=True)
