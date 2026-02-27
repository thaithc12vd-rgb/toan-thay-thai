import streamlit as st
import json
import os
import pandas as pd
import io
import re
import random
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
    .live-btn button {{ background-color: #d32f2f !important; color: white !important; font-weight: bold !important; border-radius: 10px; }}
</style>
<div class="sticky-header">
    <div class="main-title">{"HỆ THỐNG QUẢN LÝ" if role=="teacher" else "TOÁN LỚP 3 - THẦY THÁI"}</div>
    <div class="sub-title">{"Chúc thầy vượt qua mọi thử thách" if role=="teacher" else "Chúc các em làm bài tốt"}</div>
</div>
<div class="fixed-footer">DESIGN BY TRAN HOANG THAI</div>
""", unsafe_allow_html=True)

# --- 2. BỘ MÁY BIẾN ĐỔI ĐỀ BÀI (VÁ LỖI CHẤM ĐIỂM CHUẨN) ---
TEN_DANH_SACH = ["An", "Bình", "Chi", "Dũng", "Yến", "Lan", "Nam", "Mai", "Cúc", "Tùng", "Linh", "Hùng", "Bắc"]

def bien_doi_cau_hoi(q_text, a_text):
    def thay_so_ngau_nhien(match):
        num = int(match.group())
        return str(max(1, num + random.randint(-2, 2)))
    
    cau_moi = re.sub(r'\b\d+\b', thay_so_ngau_nhien, q_text)
    for t in TEN_DANH_SACH:
        if t in cau_moi:
            cau_moi = cau_moi.replace(t, random.choice([x for x in TEN_DANH_SACH if x != t]))
    
    # Tính toán lại đáp án mới tự động theo đề đã đổi số
    da_moi = a_text
    try:
        if str(a_text).isdigit():
            clean_q = cau_moi.replace('x', '*').replace(':', '/')
            nums = [int(s) for s in re.findall(r'\d+', clean_q)]
            if len(nums) >= 2:
                s1, s2 = nums[0], nums[1]
                if '+' in q_text: da_moi = str(s1 + s2)
                elif '-' in q_text: da_moi = str(s1 - s2)
                elif 'x' in q_text or '*' in q_text: da_moi = str(s1 * s2)
                elif ':' in q_text or '/' in q_text: da_moi = str(int(s1 / s2))
    except: pass
    return {"q": cau_moi, "a": da_moi}

# --- 3. QUẢN LÝ DỮ LIỆU ---
FILE_DB, FILE_RES, FILE_PROF = "quiz_lib.json", "student_results.json", "student_profiles.json"

def load_data(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_data(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

library = load_data(FILE_DB)
profiles = load_data(FILE_PROF)
results_all = load_data(FILE_RES)

# Khởi tạo session
for k, v in [('is_accepted', False), ('is_submitted', False), ('cau_hoi_hien_tai', []), ('ver_key', 0), ('data_step3', []), ('student_name', ""), ('current_rank', 0), ('final_score', 0), ('view_live', False)]:
    if k not in st.session_state: st.session_state[k] = v

st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    # --- GIAO DIỆN QUẢN TRỊ ---
    col_l, col_r = st.columns([1, 1], gap="medium")
    
    with col_l:
        st.markdown('<div class="card live-btn">', unsafe_allow_html=True)
        if st.button("🔴 NHẤN VÀO ĐÂY ĐỂ XEM LIVE", use_container_width=True):
            st.session_state.view_live = not st.session_state.view_live
        
        m_de_live = st.text_input("Nhập Mã đề để xem Live:", key="live_de_input").strip()
        
        if st.session_state.view_live and m_de_live:
            st.markdown(f"### 🏆 TOP 100 ĐANG LIVE: {m_de_live}")
            data_all = load_data(FILE_RES).get(m_de_live, [])
            if data_all:
                df_live = pd.DataFrame(data_all).sort_values(by=['score', 'time'], ascending=[False, True]).reset_index(drop=True)
                df_live.index += 1; df_live['Hạng'] = df_live.index
                st.table(df_live.head(100)[['Hạng', 'student', 'score', 'time']].rename(columns={'student':'Học sinh','score':'Điểm','time':'Giờ nộp'}))
            else: st.write("Chưa có dữ liệu học sinh.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        pwd = st.text_input("Mật mã quản trị", type="password", key="p_admin")
        if pwd == "thai2026":
            st.success("Đã xác nhận")
            # Phần quản lý đề gốc... (giữ nguyên logic soạn thảo của thầy)
            m_de = st.text_input("Mã đề để soạn/lưu:", key="m_de_admin").strip()
            if m_de: st.code(f"https://toan-thay-thai-spgcbe5cuemztnk5wuadum.streamlit.app/?de={m_de}")
        st.markdown('</div>', unsafe_allow_html=True)

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
                        if profiles.get(sk, {}).get("attempts", 0) >= 20: st.error("Đã làm quá 20 lần!")
                        else:
                            st.session_state.student_name = name_in; st.session_state.is_accepted = True
                            st.session_state.cau_hoi_hien_tai = [bien_doi_cau_hoi(i['q'], i['a']) for i in library[ma_de_url]]
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.is_accepted and not st.session_state.is_submitted:
            ans_dict = {}
            for idx, item in enumerate(st.session_state.cau_hoi_hien_tai, 1):
                st.markdown(f'<div class="card"><b>Câu {idx}:</b> {item["q"]}</div>', unsafe_allow_html=True)
                ans_dict[f"Câu {idx}"] = st.text_input(f"A_{idx}", key=f"ans_{idx}", label_visibility="collapsed", autocomplete="off")
            
            if st.button("📝 NỘP BÀI", use_container_width=True, type="primary"):
                dung = sum(1 for idx, it in enumerate(st.session_state.cau_hoi_hien_tai, 1) if str(ans_dict.get(f"Câu {idx}", "")).strip() == str(it["a"]))
                diem = round((dung / len(st.session_state.cau_hoi_hien_tai)) * 10, 1); t = datetime.now()
                
                # Lưu kết quả vĩnh viễn (Không bao giờ xóa)
                r_all = load_data(FILE_RES)
                if ma_de_url not in r_all: r_all[ma_de_url] = []
                r_all[ma_de_url].append({"full_time": t.strftime("%Y-%m-%d %H:%M:%S"), "time": t.strftime("%H:%M:%S"), "student": st.session_state.student_name, "score": diem})
                save_data(FILE_RES, r_all)
                
                # Xếp hạng và Profile vĩnh viễn
                df_t = pd.DataFrame(r_all[ma_de_url]).sort_values(by=['score', 'time'], ascending=[False, True]).reset_index(drop=True)
                st.session_state.current_rank = df_t[df_t['student'] == st.session_state.student_name].index[0] + 1
                sk = f"{st.session_state.student_name}_{ma_de_url}"
                prof = profiles.get(sk, {"attempts": 0, "top10_count": 0})
                prof["attempts"] += 1
                if st.session_state.current_rank <= 10: prof["top10_count"] += 1
                profiles[sk] = prof; save_data(FILE_PROF, profiles)
                
                st.session_state.final_score = diem; st.session_state.is_submitted = True; st.balloons(); st.rerun()

        if st.session_state.is_submitted:
            st.markdown(f'<div class="card result-card"><h2>KẾT QUẢ: {st.session_state.final_score}/10</h2><div class="rank-text">BẠN ĐANG ĐỨNG THỨ HẠNG SỐ: {st.session_state.current_rank}</div></div>', unsafe_allow_html=True)
            
            # BẢNG VÀNG LIVE CỦA HỌC SINH
            st.markdown('<div class="card">', unsafe_allow_html=True)
            data_live = load_data(FILE_RES).get(ma_de_url, [])
            st.markdown(f"### 📊 TỔNG SỐ BẠN ĐÃ LÀM BÀI NÀY: {len(data_live)}")
            if data_live:
                df = pd.DataFrame(data_live).sort_values(by=['score', 'time'], ascending=[False, True]).reset_index(drop=True)
                df.index += 1; df['Hạng'] = df.index
                df['Top 10'] = df['Hạng'].apply(lambda x: "💎 Kim Cương" if x==1 else ("🥇 Vàng" if x==2 else ("🥈 Bạc" if x==3 else ("🥉 Đồng" if x<=10 else ""))))
                df['Số lần đạt Top 10'] = df['student'].apply(lambda x: profiles.get(f"{x}_{ma_de_url}", {}).get("top10_count", 0))
                
                st.table(df.head(100)[['Hạng', 'Top 10', 'student', 'score', 'time', 'Số lần đạt Top 10']].rename(columns={'student':'Học sinh','score':'Điểm','time':'Giờ nộp'}))
            
            if st.button("Làm bài tiếp"):
                st.session_state.is_submitted = False; st.session_state.cau_hoi_hien_tai = [bien_doi_cau_hoi(i['q'], i['a']) for i in library[ma_de_url]]; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
