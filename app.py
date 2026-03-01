import streamlit as st
import json
import os
import pandas as pd
import io
import time
from datetime import datetime, timedelta

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Toan Lop 3 - Thay Thai", layout="wide")

# Khởi tạo các file dữ liệu nếu chưa tồn tại để tránh lỗi "trống trơn"
FILE_DB, FILE_RES, FILE_PROF = "quiz_lib.json", "student_results.json", "student_profiles.json"
for f_path in [FILE_DB, FILE_RES, FILE_PROF]:
    if not os.path.exists(f_path):
        with open(f_path, "w", encoding="utf-8") as f:
            json.dump({}, f)

def doc_file(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                return json.loads(content) if content else {}
    except: return {}
    return {}

def ghi_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Load dữ liệu ngay từ đầu
library = doc_file(FILE_DB)
profiles = doc_file(FILE_PROF)

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
    .move-up-container {{ position: relative; top: -130px; text-align: center; z-index: 99; margin-bottom: -120px; }}
    .mini-quiz-box {{ background-color: #1A2238; color: #FFD700; padding: 5px 20px; border-radius: 20px; display: inline-block; font-size: 12px; font-weight: bold; border: 1px solid #FFD700; }}
    .invite-text {{ color: #004F98; font-weight: 900; font-size: 18px; text-align: center; margin-bottom: 10px; text-transform: uppercase; }}
    .center-wrapper-top {{ display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: -180px; position: relative; z-index: 100; }}
    .fixed-footer {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: #C5D3E8; color: #004F98; text-align: center; padding: 10px 0; font-weight: bold; font-size: 14px; z-index: 1001; border-top: 1px solid rgba(0,79,152,0.1); }}
    .result-card {{ margin-top: -150px !important; text-align: center; border-top: 8px solid #FFD700 !important; }}
    .rank-text {{ font-size: 22px; font-weight: 900; color: #d32f2f; margin-top: 10px; }}
    .certificate-box {{
        border: 10px double #004F98; padding: 30px; background-color: #fff;
        text-align: center; font-family: 'Times New Roman', serif; margin: 20px 0;
    }}
    .cert-title {{ font-size: 30px; font-weight: bold; color: #d32f2f; }}
    .cert-medal {{ font-size: 60px; margin: 10px 0; }}
    .cert-name {{ font-size: 40px; font-weight: bold; color: #004F98; border-bottom: 2px solid #EEE; display: inline-block; padding: 0 30px; }}
</style>
<div class="sticky-header">
    <div class="main-title">{display_title}</div>
    <div class="sub-title">{display_subtitle}</div>
</div>
<div class="fixed-footer">DESIGN BY TRAN HOANG THAI</div>
""", unsafe_allow_html=True)

for k, v in [('is_accepted', False), ('is_submitted', False), ('ver_key', 0), ('data_step3', []), ('student_name', ""), ('current_rank', 0), ('final_score', 0), ('start_time', 0)]:
    if k not in st.session_state: st.session_state[k] = v

st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã quản trị", type="password", key="p_admin")
        if pwd == "thai2026":
            template_df = pd.DataFrame({"Câu": [f"Câu {i}" for i in range(1, 11)], "Nội dung câu hỏi": [""]*10, "Đáp án": [""]*10})
            towrap = io.BytesIO()
            template_df.to_csv(towrap, index=False, encoding='utf-8-sig')
            st.download_button(label="📥 TẢI FILE MẪU", data=towrap.getvalue(), file_name="mau_10_cau.csv", mime="text/csv")
            
            up_f = st.file_uploader("📤 TẢI CSV", type=["csv"], key=f"up_{st.session_state.ver_key}")
            if up_f:
                df = pd.read_csv(io.BytesIO(up_f.getvalue()), encoding='utf-8-sig').dropna(how='all')
                st.session_state.data_step3 = [{"q": str(r.iloc[1]), "a": str(r.iloc[2])} for _, r in df.iterrows()]
                st.session_state.ver_key += 1; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if pwd == "thai2026":
            st.markdown('<div class="card">', unsafe_allow_html=True)
            list_de = list(library.keys())
            de_chon = st.selectbox("📂 Chọn đề cũ:", options=["-- Tạo mới --"] + list_de)
            
            if de_chon != "-- Tạo mới --" and st.session_state.get('last_de') != de_chon:
                st.session_state.data_step3 = library.get(de_chon, [])
                st.session_state.last_de = de_chon
                st.session_state.ver_key += 1; st.rerun()

            m_de = st.text_input("👉 Mã đề bài:", value=de_chon if de_chon != "-- Tạo mới --" else "").strip()
            if m_de:
                full_link = f"https://toan-thay-thai-spgcbe5cuemztnk5wuadum.streamlit.app/?de={m_de}"
                st.success(f"Link học sinh: {full_link}")
                st.code(full_link)

            if st.button("🚀 LƯU ĐỀ VÀO KHO"):
                if m_de:
                    new_qs = [{"q": st.session_state.get(f"q_{st.session_state.ver_key}_{i}", ""), "a": st.session_state.get(f"a_{st.session_state.ver_key}_{i}", "")} for i in range(1, 11)]
                    library[m_de] = new_qs
                    ghi_file(FILE_DB, library)
                    st.success(f"Đã lưu mã đề {m_de} vào file hệ thống!")
                    time.sleep(1); st.rerun()
            
            for i in range(1, 11):
                vq = st.session_state.data_step3[i-1]["q"] if i <= len(st.session_state.data_step3) else ""
                va = st.session_state.data_step3[i-1]["a"] if i <= len(st.session_state.data_step3) else ""
                st.text_input(f"Câu hỏi {i}", value=vq, key=f"q_{st.session_state.ver_key}_{i}")
                st.text_input(f"Đáp án {i}", value=va, key=f"a_{st.session_state.ver_key}_{i}")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- GIAO DIỆN HỌC SINH ---
    if ma_de_url in library:
        st.markdown(f'<div class="move-up-container"><div class="mini-quiz-box">ĐANG LÀM ĐỀ: {ma_de_url}</div></div>', unsafe_allow_html=True)
        if not st.session_state.is_accepted:
            st.markdown('<div class="center-wrapper-top"><p class="invite-text">MỜI CÁC EM NHẬP HỌ TÊN ĐỂ LÀM BÀI</p>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                name_in = st.text_input("", key="st_name_step", label_visibility="collapsed").strip()
                if st.button("ĐỒNG Ý", use_container_width=True, type="primary"):
                    if name_in:
                        sk = f"{name_in}_{ma_de_url}"
                        cur_prof = doc_file(FILE_PROF)
                        prof = cur_prof.get(sk, {"attempts": 0, "top10_count": 0})
                        
                        if prof["attempts"] >= 20:
                            st.error("Bạn đã hết 20 lượt làm đề này!")
                        else:
                            prof["attempts"] += 1
                            cur_prof[sk] = prof
                            ghi_file(FILE_PROF, cur_prof)
                            st.session_state.student_name = name_in
                            st.session_state.is_accepted = True
                            st.session_state.start_time = time.time(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.is_accepted and not st.session_state.is_submitted:
            ans_dict = {}
            for idx, item in enumerate(library[ma_de_url], 1):
                if item["q"]:
                    st.markdown(f'<div class="card"><b>Câu {idx}:</b> {item["q"]}</div>', unsafe_allow_html=True)
                    ans_dict[f"q{idx}"] = st.text_input(f"Kết quả {idx}", key=f"ans_{idx}", label_visibility="collapsed")
            
            if st.button("📝 NỘP BÀI", use_container_width=True, type="primary"):
                dung = 0
                q_list = [x for x in library[ma_de_url] if x["q"]]
                for idx, it in enumerate(q_list, 1):
                    if str(ans_dict.get(f"q{idx}", "")).strip().lower() == str(it["a"]).strip().lower():
                        dung += 1
                diem = int((dung / len(q_list)) * 10) if q_list else 0
                dur_sec = int(time.time() - st.session_state.start_time)
                
                r_all = doc_file(FILE_RES)
                if ma_de_url not in r_all: r_all[ma_de_url] = []
                r_all[ma_de_url].append({"full_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "time": f"{dur_sec//60}p {dur_sec%60}s", "duration": dur_sec, "student": st.session_state.student_name, "score": diem})
                ghi_file(FILE_RES, r_all)
                
                dt = pd.DataFrame(r_all[ma_de_url]).sort_values(by=['score', 'duration'], ascending=[False, True]).reset_index(drop=True)
                st.session_state.current_rank = dt[dt['student'] == st.session_state.student_name].index[0] + 1
                
                if st.session_state.current_rank <= 10:
                    cur_prof = doc_file(FILE_PROF)
                    sk = f"{st.session_state.student_name}_{ma_de_url}"
                    cur_prof[sk]["top10_count"] = cur_prof[sk].get("top10_count", 0) + 1
                    ghi_file(FILE_PROF, cur_prof)
                
                st.session_state.final_score = diem; st.session_state.is_submitted = True; st.balloons(); st.rerun()

        if st.session_state.is_submitted:
            st.markdown(f'<div class="card result-card"><h2>KẾT QUẢ: {st.session_state.final_score} ĐIỂM</h2><div class="rank-text">HẠNG: {st.session_state.current_rank}</div></div>', unsafe_allow_html=True)
            if st.session_state.current_rank <= 10:
                medal = "💎" if st.session_state.current_rank == 1 else ("🥇" if st.session_state.current_rank == 2 else ("🥈" if st.session_state.current_rank == 3 else "🥉"))
                cert_html = f'<div class="certificate-box"><div class="cert-title">GIẤY KHEN</div><div class="cert-medal">{medal}</div><div class="cert-name">{st.session_state.student_name.upper()}</div><p>Hạng {st.session_state.current_rank} mã đề {ma_de_url}</p></div>'
                st.markdown(cert_html, unsafe_allow_html=True)
                st.download_button("📥 TẢI GIẤY KHEN", data=cert_html, file_name=f"giaykhen.html", mime="text/html")
            if st.button("Làm bài tiếp"):
                st.session_state.is_accepted = False; st.session_state.is_submitted = False; st.rerun()
    else:
        st.warning("Mã đề không tồn tại hoặc đã bị xóa. Vui lòng kiểm tra lại link.")
