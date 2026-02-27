import streamlit as st
import json, os, pandas as pd
import io, re, random
from datetime import datetime, timedelta

# --- 1. CẤU HÌNH GIAO DIỆN ---
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
    .mini-quiz-box {{ background-color: #1A2238; color: #FFD700; padding: 5px 20px; border-radius: 20px; display: inline-block; font-size: 12px; font-weight: bold; border: 1px solid #FFD700; }}
    .invite-text {{ color: #004F98; font-weight: 900; font-size: 18px; text-align: center; margin-bottom: 10px; text-transform: uppercase; }}
    .center-wrapper-top {{ display: flex; flex-direction: column; align-items: center; width: 100%; margin-top: -180px; position: relative; z-index: 100; }}
    .fixed-footer {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: #C5D3E8; color: #004F98; text-align: center; padding: 10px 0; font-weight: bold; font-size: 14px; z-index: 1001; border-top: 1px solid rgba(0,79,152,0.1); }}
    
    /* KHUNG KẾT QUẢ DỜI LÊN 4CM */
    .result-card {{ margin-top: -150px !important; text-align: center; border-top: 8px solid #FFD700 !important; }}
    .rank-text {{ font-size: 22px; font-weight: 900; color: #d32f2f; margin-top: 10px; }}
</style>
<div class="sticky-header">
    <div class="main-title">{display_title}</div>
    <div class="sub-title">{display_subtitle}</div>
</div>
<div class="fixed-footer">DESIGN BY TRAN HOANG THAI</div>
""", unsafe_allow_html=True)

# --- 2. BỘ MÁY BIẾN ĐỔI ĐỀ BÀI (DYNAMICS ENGINE) ---
LIST_TEN = ["An", "Bình", "Chi", "Dũng", "Yến", "Lan", "Nam", "Mai", "Cúc", "Tùng", "Linh", "Hùng", "Bắc"]

def bien_doi_cau_hoi(q_text, a_text):
    def thay_so(match):
        so_cu = int(match.group())
        return str(max(1, so_cu + random.randint(-3, 3)))
    cau_moi = re.sub(r'\b\d+\b', thay_so, q_text)
    for ten in LIST_TEN:
        if ten in cau_moi:
            cau_moi = cau_moi.replace(ten, random.choice([t for t in LIST_TEN if t != ten]))
    
    # TÍNH TOÁN ĐÁP ÁN MỚI CHÍNH XÁC
    da_moi = a_text
    try:
        clean_q = cau_moi.replace('x', '*').replace(':', '/')
        nums = re.findall(r'\d+', clean_q)
        if len(nums) >= 2:
            if '+' in q_text: da_moi = str(int(nums[0]) + int(nums[1]))
            elif '-' in q_text: da_moi = str(int(nums[0]) - int(nums[1]))
            elif 'x' in q_text or '*' in q_text: da_moi = str(int(nums[0]) * int(nums[1]))
            elif ':' in q_text or '/' in q_text: da_moi = str(int(int(nums[0]) / int(nums[1])))
    except: da_moi = a_text
    return {"q": cau_moi, "a": da_moi}

# --- 3. QUẢN LÝ DỮ LIỆU ---
DB_PATH, RES_PATH, PROF_PATH = "quiz_lib.json", "student_results.json", "student_profiles.json"

def load_data(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_data(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def cleanup_48h(results):
    now = datetime.now()
    upd = False; new_res = {}
    for de, l in results.items():
        filtered = [r for r in l if now - datetime.strptime(r.get('full_time', '2000-01-01 00:00:00'), "%Y-%m-%d %H:%M:%S") < timedelta(hours=48)]
        if len(filtered) != len(l): upd = True
        new_res[de] = filtered
    if upd: save_data(RES_PATH, new_res)
    return new_res

library = load_data(DB_PATH)
profiles = load_data(PROFILE_PATH)
results_all = cleanup_48h(load_data(RES_PATH))

# Khởi tạo session
for key, val in [('is_accepted', False), ('is_submitted', False), ('cau_hoi_hien_tai', []), ('ver_key', 0), ('data_step3', []), ('student_name', ""), ('current_rank', 0)]:
    if key not in st.session_state: st.session_state[key] = val

st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    # Phần quản trị giữ nguyên
    st.info("Chào Thầy Thái! Mời thầy nhập đề bài.")
    pwd = st.text_input("Mật mã", type="password")
    if pwd == "thai2026":
        m_de = st.text_input("Mã đề bài:").strip()
        if m_de:
            st.code(f"https://toan-thay-thai-spgcbe5cuemztnk5wuadum.streamlit.app/?de={m_de}")
else:
    if ma_de_url in library:
        st.markdown(f'<div class="move-up-container"><div class="mini-quiz-box">ĐANG LÀM ĐỀ: {ma_de_url}</div><hr class="ultra-tight-hr"></div>', unsafe_allow_html=True)

        if not st.session_state.is_accepted:
            st.markdown('<div class="center-wrapper-top"><p class="invite-text">MỜI CÁC EM NHẬP HỌ TÊN ĐỂ LÀM BÀI</p>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                name_in = st.text_input("", key="st_name_step", label_visibility="collapsed", autocomplete="off").strip()
                if st.button("ĐỒNG Ý", use_container_width=True, type="primary"):
                    if name_in:
                        s_key = f"{name_in}_{ma_de_url}"
                        if profiles.get(s_key, {}).get("attempts", 0) >= 20: st.error("Em đã làm 20 lần!")
                        else:
                            st.session_state.student_name = name_in
                            st.session_state.is_accepted = True
                            st.session_state.cau_hoi_hien_tai = [bien_doi_cau_hoi(i['q'], i['a']) for i in library[ma_de_url]]
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.is_accepted and not st.session_state.is_submitted:
            current_name = st.session_state.student_name
            st.success(f"Chào {current_name}!")
            answers = {}
            for idx, item in enumerate(st.session_state.cau_hoi_hien_tai, 1):
                st.markdown(f'<div class="card"><b>Câu {idx}:</b> {item["q"]}</div>', unsafe_allow_html=True)
                answers[f"Câu {idx}"] = st.text_input(f"Nhập đáp án {idx}:", key=f"ans_{idx}", label_visibility="collapsed", autocomplete="off")
            
            if st.button("📝 NỘP BÀI", use_container_width=True, type="primary"):
                correct = 0
                for idx, it in enumerate(st.session_state.cau_hoi_hien_tai, 1):
                    u_ans = str(answers.get(f"Câu {idx}", "")).strip()
                    if u_ans == str(it["a"]): correct += 1
                
                score = round((correct / len(st.session_state.cau_hoi_hien_tai)) * 10, 1)
                f_now = datetime.now()
                res_all = load_data(RES_PATH)
                if ma_de_url not in res_all: res_all[ma_de_url] = []
                res_all[ma_de_url].append({"full_time": f_now.strftime("%Y-%m-%d %H:%M:%S"), "time": f_now.strftime("%H:%M:%S"), "student": current_name, "score": score})
                save_data(RES_PATH, res_all)
                
                df_t = pd.DataFrame(res_all[ma_de_url]).sort_values(by=['score', 'time'], ascending=[False, True]).reset_index(drop=True)
                st.session_state.current_rank = df_t[df_t['student'] == current_name].index[0] + 1
                
                s_key = f"{current_name}_{ma_de_url}"
                profile = profiles.get(s_key, {"attempts": 0, "top10_count": 0})
                profile["attempts"] += 1
                if st.session_state.current_rank <= 10: profile["top10_count"] += 1
                profiles[s_key] = profile; save_data(PROF_PATH, profiles)
                
                st.session_state.final_score = score; st.session_state.is_submitted = True; st.balloons(); st.rerun()

        if st.session_state.is_submitted:
            # KHUNG KẾT QUẢ DỜI LÊN 4CM
            st.markdown(f"""<div class="card result-card">
                <h2 style="color:#004F98;">KẾT QUẢ: {st.session_state.final_score}/10</h2>
                <div class="rank-text">BẠN ĐANG ĐỨNG THỨ HẠNG SỐ: {st.session_state.current_rank}</div>
            </div>""", unsafe_allow_html=True)

            # BẢNG LIVE DƯỚI CÙNG
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🟢 CÁC BẠN ĐANG LIVE VÀ VỪA NỘP BÀI")
            res_data = cleanup_48h(load_data(RES_PATH)).get(ma_de_url, [])
            if res_data:
                df = pd.DataFrame(res_data).sort_values(by=['score', 'time'], ascending=[False, True]).reset_index(drop=True)
                df.index += 1
                df['Hạng'] = df.index
                df['Huy hiệu'] = df['Hạng'].apply(lambda x: "💎 KIM CƯƠNG" if x==1 else ("🥇 VÀNG" if x==2 else ("🥈 BẠC" if x==3 else ("🥉 ĐỒNG" if x<=10 else ""))))
                st.table(df.head(100)[['Hạng', 'Huy hiệu', 'student', 'score', 'time']].rename(columns={'student':'Học sinh', 'score':'Điểm', 'time':'Giờ nộp'}))
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Làm bài tiếp"):
                st.session_state.is_submitted = False
                st.session_state.cau_hoi_hien_tai = [bien_doi_cau_hoi(i['q'], i['a']) for i in library[ma_de_url]]
                st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
