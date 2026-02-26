import streamlit as st
import google.generativeai as genai
import json, os, time
from datetime import datetime, timedelta
import pandas as pd

# --- 1. GIAO DIỆN PHONG THỦY & HUY HIỆU ---
st.set_page_config(page_title="Toán Lớp 3 - Thầy Thái", layout="wide")

st.markdown("""
<style>
    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display:none !important;}
    .stApp { background-color: #C5D3E8; } 
    .sticky-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #C5D3E8; color: #004F98 !important;
        text-align: center; font-size: 30px; font-weight: 900; padding: 10px 0; z-index: 1000;
        border-bottom: 2px solid rgba(0, 79, 152, 0.2); text-transform: uppercase;
    }
    .main-content { margin-top: 100px; margin-bottom: 100px; padding: 0 20px; }
    .card { background-color: white; border-radius: 15px; padding: 25px; border-top: 10px solid #004F98; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    
    /* STYLE HUY HIỆU SANG TRỌNG */
    .badge-top { font-size: 22px; font-weight: bold; }
    .rank-1 { color: #FFD700; text-shadow: 1px 1px 2px #000; } /* Vàng */
    .rank-2 { color: #C0C0C0; text-shadow: 1px 1px 2px #000; } /* Bạc */
    .rank-3 { color: #CD7F32; text-shadow: 1px 1px 2px #000; } /* Đồng */
    .rank-other { color: #004F98; }
</style>
""", unsafe_allow_html=True)

# --- 2. QUẢN LÝ DỮ LIỆU ---
DB = {"LIB": "quiz_lib.json", "RANK": "rank_live.json", "MASTER": "students_vinhvien.json"}

def load_db(k):
    if os.path.exists(DB[k]):
        with open(DB[k], "r", encoding="utf-8") as f: return json.load(f)
    return {} if k == "LIB" else []

def save_db(k, d):
    with open(DB[k], "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=4)

library = load_db("LIB")
rank_live = load_db("RANK")
master_db = load_db("MASTER")

# --- 3. CƠ CHẾ TỰ HỦY SAU 48 GIỜ (TÍNH TỪ LÚC CLICK LÀM BÀI) ---
now = datetime.now()
# Chỉ giữ lại những em làm bài chưa quá 48 giờ (172800 giây)
rank_live = [r for r in rank_live if (now - datetime.fromisoformat(r['start_ts'])).total_seconds() < 172800]
save_db("RANK", rank_live)

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown('<div class="sticky-header">TOÁN LỚP 3 - THẦY THÁI</div>', unsafe_allow_html=True)
ma_de = st.query_params.get("de", "")
st.markdown('<div class="main-content">', unsafe_allow_html=True)

col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if ma_de in library:
        name = st.text_input("👤 Nhập Họ và Tên học sinh:").strip()
        if name:
            # Kiểm tra hồ sơ vĩnh viễn (20 năm sau vẫn nhớ)
            hs = next((s for s in master_db if s['name'] == name and s['de'] == ma_de), {"count": 0, "top10_total": 0})
            
            if hs['count'] >= 20:
                st.error("⛔ Hệ thống đã KHÓA. Em đã làm bài này quá 20 lần!")
            else:
                # Bắt đầu tính thời gian 48h từ giây phút này
                if 'start_time_48h' not in st.session_state:
                    st.session_state.start_time_48h = now.isoformat()
                
                # Nút làm bài (AI sẽ đổi số giữ cấu trúc như yêu cầu trước)
                if st.button("🚀 BẮT ĐẦU LÀM BÀI"):
                    st.session_state.doing_quiz = True

                if st.session_state.get('doing_quiz'):
                    with st.form("quiz_form"):
                        st.write("--- Đề bài đã được AI Thầy Thái làm mới số liệu ---")
                        # (Hiển thị câu hỏi ở đây...)
                        if st.form_submit_button("✅ NỘP BÀI"):
                            # Giả lập chấm điểm
                            score, duration = 10, 30.5 
                            
                            # Lưu kết quả kèm thời điểm bắt đầu để tính 48h tự hủy
                            new_entry = {
                                "name": name, "de": ma_de, "score": score, 
                                "time": duration, "start_ts": st.session_state.start_time_48h
                            }
                            rank_live.append(new_entry)
                            
                            # Cập nhật Master DB (Cộng dồn vĩnh viễn)
                            if hs['count'] == 0: master_db.append({"name": name, "de": ma_de, "count": 1, "top10_total": 0})
                            else: hs['count'] += 1
                            
                            save_db("RANK", rank_live)
                            save_db("MASTER", master_db)
                            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏆 BẢNG VÀNG TOP 100 (48 GIỜ)")
    
    # Lọc và Sắp xếp: Điểm cao -> Thời gian ít
    this_de_rank = [r for r in rank_live if r['de'] == ma_de]
    this_de_rank.sort(key=lambda x: (-x['score'], x['time']))
    
    if this_de_rank:
        table_html = """<table style='width:100%; text-align:center;'>
                        <tr style='background-color:#004F98; color:white;'>
                            <th>Hạng</th><th>Tên</th><th>Điểm</th><th>Thời gian</th><th>Top 10</th>
                        </tr>"""
        for i, r in enumerate(this_de_rank[:100]): # Hiển thị tối đa 100 em
            # Huy hiệu Top 10 sang trọng
            badge = ""
            style = "rank-other"
            if i == 0: badge, style = "🥇 QUÁN QUÂN", "rank-1"
            elif i == 1: badge, style = "🥈 Á QUÂN 1", "rank-2"
            elif i == 2: badge, style = "🥉 Á QUÂN 2", "rank-3"
            elif i < 10: badge, style = f"🎖️ TOP {i+1}", "rank-other"
            else: badge = str(i+1)

            # Lấy số lần đạt Top 10 vĩnh viễn từ Master DB
            hs_m = next((s for s in master_db if s['name'] == r['name'] and s['de'] == ma_de), {"top10_total": 0})
            
            table_html += f"""<tr style='border-bottom:1px solid #ddd;'>
                <td class='badge-top {style}'>{badge}</td>
                <td><b>{r['name']}</b></td>
                <td>{r['score']}</td>
                <td>{r['time']}s</td>
                <td>{hs_m['top10_total']} lần</td>
            </tr>"""
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.write("Chưa có bạn nào trong danh sách 48 giờ qua.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
