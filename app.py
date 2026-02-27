import streamlit as st
import json
import os
import pandas as pd
import io
import re
import random
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
    .move-up-container {{ position: relative; top: -130px; text-align: center; z-index: 99; margin-bottom: -120px; }}
    .mini-quiz-box {{ background-color: #1A2238; color: #FFD700; padding: 5px 20px; border-radius: 20px; display: inline-block; font-size: 12px; font-weight: bold; border: 1px solid #FFD700; }}
    .center-wrapper-top {{ display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: -180px; position: relative; z-index: 100; }}
    .result-card {{ margin-top: -150px !important; text-align: center; border-top: 8px solid #FFD700 !important; }}
    .rank-text {{ font-size: 22px; font-weight: 900; color: #d32f2f; margin-top: 10px; }}
    .fixed-footer {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: #C5D3E8; color: #004F98; text-align: center; padding: 10px 0; font-weight: bold; font-size: 14px; z-index: 1001; border-top: 1px solid rgba(0,79,152,0.1); }}
    
    .stButton>button {{ width: 100%; border-radius: 10px; }}
    .live-btn button {{ background-color: #d32f2f !important; color: white !important; font-weight: bold !important; }}
    .hide-btn button {{ background-color: #6c757d !important; color: white !important; }}
</style>
<div class="sticky-header">
    <div class="main-title">{display_title}</div>
    <div class="sub-title">{display_subtitle}</div>
</div>
<div class="fixed-footer">DESIGN BY TRAN HOANG THAI</div>
""", unsafe_allow_html=True)

# --- 2. BỘ MÁY BIẾN ĐỔI ĐỀ BÀI (VÁ LỖI CHẤM ĐIỂM TUYỆT ĐỐI) ---
TEN_DS = ["An", "Bình", "Chi", "Dũng", "Yến", "Lan", "Nam", "Mai", "Cúc", "Tùng", "Linh", "Hùng", "Bắc"]

def bien_doi_cau_hoi(q_text, a_text):
    def thay_so(match):
        num = int(match.group())
        return str(max(1, num + random.randint(-3, 3)))
    
    q_moi = re.sub(r'\b\d+\b', thay_so, q_text)
    for t in TEN_DS:
        if t in q_moi: q_moi = q_moi.replace(t, random.choice([x for x in TEN_DS if x != t]))
    
    a_moi = a_text
    try:
        clean_q = q_moi.replace('x', '*').replace(':', '/')
        nums = [int(s) for s in re.findall(r'\d+', clean_q)]
        if len(nums) >= 2:
            if '+' in q_text: a_moi = str(nums[0] + nums[1])
            elif '-' in q_text: a_moi = str(nums[0] - nums[1])
            elif 'x' in q_text or '*' in q_text: a_moi = str(nums[0] * nums[1])
            elif ':' in q_text or '/' in q_text: a_moi = str(int(nums[0] / nums[1]))
    except: pass
    return {"q": q_moi, "a": a_moi}

# --- 3. QUẢN LÝ DỮ LIỆU ---
FILE_DB, FILE_RES, FILE_PROF = "quiz_lib.json", "student_results.json", "student_profiles.json"

def doc_file(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def ghi_file(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def quet_don_48h(results):
    hien_tai = datetime.now()
    thay_doi = False; kq_moi = {}
    for de, ds in results.items():
        loc = [r for r in ds if hien_tai - datetime.strptime(r.get('full_time', '2000-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S") < timedelta(hours=48)]
        if len(loc) != len(ds): thay_doi = True
        kq_moi[de] = loc
    if thay_doi: ghi_file(FILE_RES, kq_moi)
    return kq_moi

library = doc_file(FILE_DB)
profiles = doc_file(FILE_PROF)

for k, v in [('is_accepted', False), ('is_submitted', False), ('cau_hoi_hien_tai', []), ('ver_key', 0), ('data_step3', []), ('student_name', ""), ('current_rank', 0), ('final_score', 0), ('view_live', False), ('start_time', 0)]:
    if k not in st.session_state: st.session_state[k] = v

st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    col_l, col_r = st.columns([1, 4], gap="medium")
    with col_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã quản trị", type="password", key="p_admin")
        if pwd == "thai2026":
            up_f = st.file_uploader("📤 Tải CSV", type=["csv"], key=f"up_{st.session_state.ver_key}")
            if up_f:
                df = pd.read_csv(io.BytesIO(up_f.getvalue()), header=None, encoding='utf-8-sig', encoding_errors='replace').dropna(how='all')
                st.session_state.data_step3 = [{"q": f"{str(r[1])}: {str(r[2])}" if pd.notnull(r[1]) else str(r[2]), "a": str(r[3]) if len(r)>3 else ""} for _, r in df.iterrows() if not any(x in str(r[0]).lower() for x in ["stt", "câu"])]
                st.session_state.ver_key += 1; st.rerun()
            
            st.markdown('<div class="live-btn">', unsafe_allow_html=True)
            if st.button("🔴 HIỆN LIVE"): st.session_state.view_live = True
            st.markdown('</div><div class="hide-btn">', unsafe_allow_html=True)
            if st.button("⚪ ẨN LIVE"): st.session_state.view_live = False
            st.markdown('</div>', unsafe_allow_html=True)
            
            m_de_cnt = st.text_input("Mã đề đếm tổng:", key="cnt_de").strip()
            if m_de_cnt:
                total_em = sum(1 for k in profiles.keys() if m_de_cnt in k)
                st.info(f"Tổng số các em: {total_em}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_r:
        if pwd == "thai2026":
            if st.session_state.view_live:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                m_de_live = st.text_input("Mã đề Live:", key="live_de").strip()
                if m_de_live:
                    dt_live = doc_file(FILE_RES).get(m_de_live, [])
                    if dt_live:
                        df_l = pd.DataFrame(dt_live).sort_values(by=['score', 'duration'], ascending=[False, True]).reset_index(drop=True)
                        df_l.index += 1
                        st.table(df_l.head(100).rename(columns={'student':'Học sinh','score':'Điểm','time':'Thời gian làm'}))
                st.markdown('</div>', unsafe_allow_html=True)
            # (Phần soạn thảo giữ nguyên cấu trúc thầy yêu cầu)
            st.info("Thầy quản lý đề tại đây.")
else:
    # --- GIAO DIỆN HỌC SINH ---
    if ma_de_url in library:
        st.markdown(f'<div class="move-up-container"><div class="mini-quiz-box">ĐANG LÀM ĐỀ: {ma_de_url}</div></div>', unsafe_allow_html=True)
        if not st.session_state.is_accepted:
            st.markdown('<div class="center-wrapper-top"><p class="invite-text">MỜI CÁC EM NHẬP HỌ TÊN ĐỂ LÀM BÀI</p>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                name_in = st.text_input("", key="st_name_step", label_visibility="collapsed", autocomplete="off").strip()
                if st.button("ĐỒNG Ý", use_container_width=True, type="primary"):
                    if name_in:
                        sk = f"{name_in}_{ma_de_url}"
                        if doc_file(FILE_PROF).get(sk, {}).get("attempts", 0) >= 20: st.error("Hết lượt!")
                        else:
                            st.session_state.student_name = name_in; st.session_state.is_accepted = True
                            st.session_state.start_time = time.time() # Bắt đầu tính giờ
                            st.session_state.cau_hoi_hien_tai = [bien_doi_cau_hoi(i['q'], i['a']) for i in library[ma_de_url]]
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.is_accepted and not st.session_state.is_submitted:
            ans_dict = {}
            for idx, item in enumerate(st.session_state.cau_hoi_hien_tai, 1):
                st.markdown(f'<div class="card"><b>Câu {idx}:</b> {item["q"]}</div>', unsafe_allow_html=True)
                ans_dict[f"Câu {idx}"] = st.text_input(f"A_{idx}", key=f"ans_{idx}", label_visibility="collapsed", autocomplete="off")
            
            if st.button("📝 NỘP BÀI", use_container_width=True, type="primary"):
                # CHẤM ĐIỂM CHUẨN XÁC
                dung = sum(1 for idx, it in enumerate(st.session_state.cau_hoi_hien_tai, 1) if str(ans_dict.get(f"Câu {idx}", "")).strip() == str(it["a"]))
                diem = int((dung / len(st.session_state.cau_hoi_hien_tai)) * 10) # Lấy số nguyên
                
                # Tính phút và giây làm bài
                duration_sec = int(time.time() - st.session_state.start_time)
                phut, giay = divmod(duration_sec, 60)
                tg_lam = f"{phut} phút {giay} giây"
                
                t_now = datetime.now()
                r_all = doc_file(FILE_RES)
                if ma_de_url not in r_all: r_all[ma_de_url] = []
                r_all[ma_de_url].append({
                    "full_time": t_now.strftime("%Y-%m-%d %H:%M:%S"),
                    "time": tg_lam, # Lưu phút giây làm bài
                    "duration": duration_sec, # Để sắp xếp hạng
                    "student": st.session_state.student_name, 
                    "score": diem # Lưu điểm số nguyên
                })
                ghi_file(FILE_RES, r_all)
                
                dt = pd.DataFrame(r_all[ma_de_url]).sort_values(by=['score', 'duration'], ascending=[False, True]).reset_index(drop=True)
                st.session_state.current_rank = dt[dt['student'] == st.session_state.student_name].index[0] + 1
                sk = f"{st.session_state.student_name}_{ma_de_url}"
                pall = doc_file(FILE_PROF); prof = pall.get(sk, {"attempts": 0, "top10_count": 0})
                prof["attempts"] += 1
                if st.session_state.current_rank <= 10: prof["top10_count"] += 1
                pall[sk] = prof; ghi_file(FILE_PROF, pall)
                
                st.session_state.final_score = diem; st.session_state.is_submitted = True; st.balloons(); st.rerun()

        if st.session_state.is_submitted:
            st.markdown(f'<div class="card result-card"><h2>KẾT QUẢ: {st.session_state.final_score} ĐIỂM</h2><div class="rank-text">BẠN ĐANG ĐỨNG THỨ HẠNG SỐ: {st.session_state.current_rank}</div></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            all_data = doc_file(FILE_RES).get(ma_de_url, [])
            st.markdown(f"### 📊 TỔNG SỐ BẠN ĐÃ THAM GIA: {len(all_data)}")
            if all_data:
                ds_h = quet_don_48h({ma_de_url: all_data})[ma_de_url]
                df = pd.DataFrame(ds_h).sort_values(by=['score', 'duration'], ascending=[False, True]).reset_index(drop=True)
                df.index += 1; df['Hạng'] = df.index
                df['Top 10'] = df['Hạng'].apply(lambda x: "💎 Kim Cương" if x==1 else ("🥇 Vàng" if x==2 else ("🥈 Bạc" if x==3 else ("🥉 Đồng" if x<=10 else ""))))
                df['Số lần đạt Top 10'] = df['student'].apply(lambda x: doc_file(FILE_PROF).get(f"{x}_{ma_de_url}", {}).get("top10_count", 0))
                # HIỂN THỊ CỘT ĐIỂM SỐ NGUYÊN VÀ THỜI GIAN PHÚT GIÂY
                st.table(df.head(100)[['Hạng', 'Top 10', 'student', 'score', 'time', 'Số lần đạt Top 10']].rename(columns={'student':'Học sinh', 'score':'Điểm', 'time':'Thời gian làm'}))
            if st.button("Làm bài tiếp"):
                st.session_state.is_submitted = False; st.session_state.cau_hoi_hien_tai = [bien_doi_cau_hoi(i['q'], i['a']) for i in library[ma_de_url]]; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
