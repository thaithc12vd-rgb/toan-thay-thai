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
PROFILE_PATH = "student_profiles.json"

def load_data(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

def save_data(path, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

# HÀM TỰ HỦY KẾT QUẢ SAU 48 GIỜ
def cleanup_results(results_all):
    now = datetime.now()
    updated = False
    new_results = {}
    for de, list_res in results_all.items():
        filtered_list = []
        for res in list_res:
            res_time = datetime.strptime(res['full_time'], "%Y-%m-%d %H:%M:%S")
            if now - res_time < timedelta(hours=48):
                filtered_list.append(res)
            else:
                updated = True
        new_results[de] = filtered_list
    if updated:
        save_data(RESULT_PATH, new_results)
    return new_results

library = load_data(DB_PATH)
profiles = load_data(PROFILE_PATH)
results_all = cleanup_results(load_data(RESULT_PATH))

if 'is_accepted' not in st.session_state: st.session_state.is_accepted = False
if 'is_submitted' not in st.session_state: st.session_state.is_submitted = False

st.markdown('<div class="main-content">', unsafe_allow_html=True)

if role == "teacher":
    st.info("Chế độ quản trị: Nhập liệu đề gốc tại đây.")
else:
    if ma_de_url in library:
        st.markdown(f'<div class="move-up-container"><div class="mini-quiz-box">ĐANG LÀM ĐỀ: {ma_de_url}</div></div>', unsafe_allow_html=True)

        if not st.session_state.is_accepted:
            st.markdown('<div class="center-wrapper-top"><p class="invite-text">MỜI CÁC EM NHẬP HỌ TÊN ĐỂ LÀM BÀI</p>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                name_in = st.text_input("", key="st_name_step", label_visibility="collapsed", autocomplete="off").strip()
                if st.button("ĐỒNG Ý", use_container_width=True, type="primary"):
                    if name_in:
                        student_key = f"{name_in}_{ma_de_url}"
                        profile = profiles.get(student_key, {"attempts": 0, "top10_count": 0})
                        if profile["attempts"] >= 20:
                            st.error("Em đã làm 20 lần rồi, hệ thống đã khóa!")
                        else:
                            st.session_state.student_name = name_in
                            st.session_state.is_accepted = True
                            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.is_accepted and not st.session_state.is_submitted:
            current_name = st.session_state.student_name
            st.success(f"Chào {current_name}! Em có 48 giờ để giữ hạng trên bảng vàng.")
            quiz_data = library[ma_de_url]
            answers = {}
            for idx, item in enumerate(quiz_data, 1):
                st.markdown(f'<div class="card"><b>Câu {idx}:</b> {item["q"]}</div>', unsafe_allow_html=True)
                answers[f"Câu {idx}"] = st.text_input(f"Trả lời:", key=f"ans_{idx}", label_visibility="collapsed", autocomplete="off")
            
            if st.button("📝 NỘP BÀI", use_container_width=True, type="primary"):
                correct = sum(1 for idx, it in enumerate(quiz_data, 1) if str(answers.get(f"Câu {idx}", "")).strip().lower() == str(it["a"]).strip().lower())
                score = round((correct / len(quiz_data)) * 10, 1)
                full_now = datetime.now()
                
                # Lưu kết quả kèm mốc thời gian đầy đủ để tính 48h
                res_all = load_data(RESULT_PATH)
                if ma_de_url not in res_all: res_all[ma_de_url] = []
                res_all[ma_de_url].append({
                    "full_time": full_now.strftime("%Y-%m-%d %H:%M:%S"),
                    "time": full_now.strftime("%H:%M:%S"),
                    "student": current_name,
                    "score": score
                })
                save_data(RESULT_PATH, res_all)
                
                # Tính hạng và cộng dồn Top 10
                df_temp = pd.DataFrame(res_all[ma_de_url]).sort_values(by=['score', 'time'], ascending=[False, True]).reset_index(drop=True)
                rank = df_temp[df_temp['student'] == current_name].index[0] + 1
                
                student_key = f"{current_name}_{ma_de_url}"
                profile = profiles.get(student_key, {"attempts": 0, "top10_count": 0})
                profile["attempts"] += 1
                if rank <= 10: profile["top10_count"] += 1
                profiles[student_key] = profile
                save_data(PROFILE_PATH, profiles)
                
                st.session_state.final_score = score
                st.session_state.is_submitted = True; st.rerun()

        if st.session_state.is_submitted:
            st.markdown(f'<div class="card" style="text-align:center;"><h2>KẾT QUẢ: {st.session_state.final_score}/10</h2><p>Hạng của em sẽ tự hủy sau 48 giờ!</p></div>', unsafe_allow_html=True)

            # BẢNG VÀNG LIVE 100 EM VỚI HUY HIỆU SANG TRỌNG
            st.markdown('<div class="card">', unsafe_allow_html=True)
            res_data = results_all.get(ma_de_url, [])
            if res_data:
                df = pd.DataFrame(res_data).sort_values(by=['score', 'time'], ascending=[False, True]).reset_index(drop=True)
                df.index += 1
                
                def get_medal(rank):
                    if rank == 1: return "💎 KIM CƯƠNG"
                    if rank == 2: return "🥇 VÀNG"
                    if rank == 3: return "🥈 BẠC"
                    if 4 <= rank <= 10: return "🥉 ĐỒNG"
                    return ""

                df['Huy hiệu'] = [get_medal(i) for i in df.index]
                df['Hạng'] = df.index
                df['Lần đạt Top 10'] = df['student'].apply(lambda x: profiles.get(f"{x}_{ma_de_url}", {}).get("top10_count", 0))
                
                st.markdown(f"### 👑 BẢNG VÀNG LIVE (Cập nhật liên tục)")
                st.table(df.head(100)[['Hạng', 'Huy hiệu', 'student', 'score', 'time', 'Lần đạt Top 10']].rename(columns={'student':'Học sinh', 'score':'Điểm', 'time':'Giờ nộp'}))
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Làm bài tiếp"):
                st.session_state.is_accepted = False; st.session_state.is_submitted = False; st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
