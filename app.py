import streamlit as st
import json
import os
import pandas as pd
import io
import time
from datetime import datetime, timedelta

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Toan Lop 3 - Thay Thai", layout="wide")

try:
    query_params = st.query_params
    ma_de_url = query_params.get("de", "")
    role = query_params.get("role", "student")
except:
    ma_de_url = ""
    role = "student"

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
    .fixed-footer {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: #C5D3E8; color: #004F98; text-align: center; padding: 10px 0; font-weight: bold; font-size: 14px; z-index: 1001; border-top: 1px solid rgba(0,79,152,0.1); }}
    
    /* STYLE GIẤY KHEN */
    .certificate-box {{
        border: 10px double #FFD700; padding: 30px; background: #fff;
        text-align: center; position: relative; margin-top: 20px;
        background-image: url('https://www.transparenttextures.com/patterns/paper.png');
    }}
    .cert-title {{ font-size: 28px; font-weight: 900; color: #d32f2f; text-transform: uppercase; }}
    .cert-name {{ font-size: 35px; font-weight: bold; color: #004F98; margin: 15px 0; border-bottom: 2px solid #EEE; display: inline-block; padding: 0 20px; }}
    .cert-badge {{ font-size: 50px; margin: 10px 0; }}

    .stButton>button {{ width: 100%; border-radius: 10px; }}
    .live-btn button {{ background-color: #d32f2f !important; color: white !important; font-weight: bold !important; }}
    .download-btn button {{ background-color: #28a745 !important; color: white !important; font-weight: bold !important; }}
</style>
<div class="sticky-header">
    <div class="main-title">{display_title}</div>
    <div class="sub-title">{display_subtitle}</div>
</div>
<div class="fixed-footer">DESIGN BY TRAN HOANG THAI</div>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU ---
FILE_DB, FILE_RES, FILE_PROF = "quiz_lib.json", "student_results.json", "student_profiles.json"

def doc_file(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def ghi_file(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

library = doc_file(FILE_DB)
profiles = doc_file(FILE_PROF)

if 'ver_key' not in st.session_state: st.session_state.ver_key = 0
if 'data_step3' not in st.session_state: st.session_state.data_step3 = []
if 'is_accepted' not in st.session_state: st.session_state.is_accepted = False
if 'is_submitted' not in st.session_state: st.session_state.is_submitted = False
if 'view_live' not in st.session_state: st.session_state.view_live = False

st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã quản trị", type="password", key="p_admin")
        if pwd == "thai2026":
            # Tải mẫu 10 câu
            template_df = pd.DataFrame({"Câu": [f"Câu {i}" for i in range(1, 11)], "Nội dung câu hỏi": [f"Câu hỏi {i}" for i in range(1, 11)], "Đáp án": [""]*10})
            towrap = io.BytesIO()
            template_df.to_csv(towrap, index=False, encoding='utf-8-sig')
            st.download_button(label="📥 TẢI FILE MẪU (10 CÂU)", data=towrap.getvalue(), file_name="mau_10_cau.csv", mime="text/csv")
            
            up_f = st.file_uploader("📤 TẢI CSV", type=["csv"], key=f"up_{st.session_state.ver_key}")
            if up_f:
                df = pd.read_csv(io.BytesIO(up_f.getvalue()), encoding='utf-8-sig').dropna(how='all')
                st.session_state.data_step3 = [{"q": str(r.iloc[1]), "a": str(r.iloc[2])} for _, r in df.iterrows()]
                st.session_state.ver_key += 1; st.rerun()

            if st.button("🔴 HIỆN LIVE"): st.session_state.view_live = True
            if st.button("⚪ ẨN LIVE"): st.session_state.view_live = False
            
            m_de_cnt = st.text_input("Mã đề đếm tổng:", key="cnt_de").strip()
            if m_de_cnt:
                total_em = sum(1 for k in profiles.keys() if m_de_cnt in k)
                st.info(f"Tổng số các em: {total_em}")
            
            # --- NÚT QUẢN LÝ ĐỀ ---
            if st.button("📂 QUẢN LÝ ĐỀ TRONG KHO"):
                st.session_state.show_storage = True
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            # Giao diện kho đề
            if st.session_state.get('show_storage'):
                st.markdown('<div class="card"><h3>📦 KHO ĐỀ ĐÃ LƯU</h3>', unsafe_allow_html=True)
                for d_key in list(library.keys()):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"🔹 **Mã đề:** {d_key} ({len(library[d_key])} câu)")
                    if c2.button("Xóa", key=f"del_{d_key}"):
                        del library[d_key]; ghi_file(FILE_DB, library); st.rerun()
                if st.button("Đóng kho đề"): st.session_state.show_storage = False; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.view_live:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                m_de_live = st.text_input("Nhập Mã đề Live:", key="live_de").strip()
                if m_de_live:
                    dt_live = doc_file(FILE_RES).get(m_de_live, [])
                    if dt_live:
                        df_l = pd.DataFrame(dt_live).sort_values(by=['score', 'duration'], ascending=[False, True]).reset_index(drop=True)
                        df_l.index += 1
                        st.table(df_l.head(100).rename(columns={'student':'Học sinh','score':'Điểm','time':'Thời gian làm'}))
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            de_chon = st.selectbox("📂 Chọn đề cũ:", options=["-- Tạo mới --"] + list(library.keys()))
            if de_chon != "-- Tạo mới --" and st.session_state.get('last_de') != de_chon:
                st.session_state.data_step3 = library.get(de_chon, [])
                st.session_state.last_de = de_chon; st.session_state.ver_key += 1; st.rerun()
            
            m_de = st.text_input("👉 Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "").strip()
            # TỰ SINH LINK KHI CÓ MÃ ĐỀ
            if m_de:
                st.info(f"🔗 Link học sinh: https://toan-thay-thai-spgcbe5cuemztnk5wuadum.streamlit.app/?de={m_de}")
            
            if st.button("🚀 LƯU ĐỀ VÀO KHO"):
                if m_de:
                    library[m_de] = [{"q": st.session_state.get(f"q_{st.session_state.ver_key}_{i}", ""), "a": st.session_state.get(f"a_{st.session_state.ver_key}_{i}", "")} for i in range(1, 11)]
                    ghi_file(FILE_DB, library); st.success("Đã lưu!"); st.rerun()

            for i in range(1, 11):
                vq = st.session_state.data_step3[i-1]["q"] if i <= len(st.session_state.data_step3) else ""
                va = st.session_state.data_step3[i-1]["a"] if i <= len(st.session_state.data_step3) else ""
                st.text_input(f"Câu hỏi {i}", value=vq, key=f"q_{st.session_state.ver_key}_{i}")
                st.text_input(f"Đáp án {i}", value=va, key=f"a_{st.session_state.ver_key}_{i}")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- GIAO DIỆN HỌC SINH ---
    if ma_de_url in library:
        if not st.session_state.is_accepted:
            st.markdown('<div class="card"><h3>HỌ TÊN ĐỂ LÀM BÀI</h3>', unsafe_allow_html=True)
            name_in = st.text_input("Nhập tên em:").strip()
            if st.button("BẮT ĐẦU"):
                if name_in:
                    st.session_state.student_name = name_in; st.session_state.is_accepted = True
                    st.session_state.start_time = time.time(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.is_accepted and not st.session_state.is_submitted:
            ans_dict = {}
            for idx, item in enumerate(library[ma_de_url], 1):
                st.markdown(f'<div class="card"><b>Câu {idx}:</b> {item["q"]}</div>', unsafe_allow_html=True)
                ans_dict[idx] = st.text_input(f"Kết quả {idx}", key=f"ans_{idx}")
            if st.button("📝 NỘP BÀI"):
                dung = sum(1 for i, it in enumerate(library[ma_de_url], 1) if str(ans_dict.get(i, "")).strip().lower() == str(it["a"]).strip().lower())
                diem = int((dung / len(library[ma_de_url])) * 10)
                dur = int(time.time() - st.session_state.start_time)
                r_all = doc_file(FILE_RES)
                if ma_de_url not in r_all: r_all[ma_de_url] = []
                r_all[ma_de_url].append({"student": st.session_state.student_name, "score": diem, "duration": dur, "time": f"{dur//60}p {dur%60}s", "full_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                ghi_file(FILE_RES, r_all)
                dt = pd.DataFrame(r_all[ma_de_url]).sort_values(by=['score', 'duration'], ascending=[False, True]).reset_index(drop=True)
                st.session_state.current_rank = dt[dt['student'] == st.session_state.student_name].index[0] + 1
                st.session_state.final_score = diem; st.session_state.is_submitted = True; st.balloons(); st.rerun()

        if st.session_state.is_submitted:
            # GIẤY KHEN VÀ NÚT TẢI VỀ
            if st.session_state.current_rank <= 10:
                rank = st.session_state.current_rank
                badge = "💎" if rank==1 else ("🥇" if rank==2 else ("🥈" if rank==3 else "🥉"))
                title = "KIM CƯƠNG" if rank==1 else ("VÀNG" if rank==2 else ("BẠC" if rank==3 else "ĐỒNG"))
                cert_html = f"""
                <div class="certificate-box">
                    <div class="cert-badge">{badge}</div>
                    <div class="cert-title">GIẤY KHEN VINH DANH</div>
                    <div class="cert-name">{st.session_state.student_name}</div>
                    <div class="cert-rank">Học sinh danh hiệu: {title}</div>
                    <p>Hạng: {rank} | Điểm: {st.session_state.final_score} | Đề: {ma_de_url}</p>
                </div>"""
                st.markdown(cert_html, unsafe_allow_html=True)
                # NÚT TẢI GIẤY KHEN (Dạng file văn bản lưu niệm)
                cert_text = f"CHÚC MỪNG {st.session_state.student_name.upper()}\nDanh hiệu: {title}\nHạng: {rank}\nĐiểm: {st.session_state.final_score}\nMã đề: {ma_de_url}\nDesign by Tran Hoang Thai"
                st.download_button(label="📥 TẢI GIẤY KHEN VỀ MÁY", data=cert_text, file_name=f"GiayKhen_{st.session_state.student_name}.txt", mime="text/plain")

            st.markdown(f'<div class="card"><h3>KẾT QUẢ: {st.session_state.final_score} ĐIỂM - HẠNG: {st.session_state.current_rank}</h3></div>', unsafe_allow_html=True)
            if st.button("Làm bài tiếp"): st.session_state.is_submitted = False; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
