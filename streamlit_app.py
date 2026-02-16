import streamlit as st
import pandas as pd
import os
from datetime import datetime

# הגדרות עמוד
st.set_page_config(page_title="המרחב המאורגן שלי", page_icon="✨", layout="wide")

# פונקציות שמירה וטעינה
DB_FILE = "tasks_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['due_date'] = pd.to_datetime(df['due_date']).dt.date
        return df.to_dict('records')
    return []

def save_data(tasks):
    df = pd.DataFrame(tasks)
    df.to_csv(DB_FILE, index=False)

if 'tasks' not in st.session_state:
    st.session_state.tasks = load_data()

# רשימת התחומים המעודכנת שלך
CATEGORIES = [
    "לשכת המדענית משרד החינוך", "בייביסיטר מיוחד במינו", "מחקר איכותני", 
    "מבוא לבריהמ", "כריית נתונים", "פלסטינים", "קורס התמחות", 
    "ועדת חוקה", "בית", "רפואה", "קניות", "אישי"
]

# --- עיצוב CSS פסטלי ואסתטי ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stApp { background-color: #FDFCFB; }
    
    .stat-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        text-align: center;
        border-bottom: 4px solid #E0BBE4;
        margin-bottom: 10px;
    }

    .task-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-right: 8px solid #BEE1E6;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    
    .priority-high { border-right-color: #FFB3BA !important; } 
    .priority-med { border-right-color: #FFDFBA !important; }  
    .priority-low { border-right-color: #BAFFC9 !important; }  

    .stButton>button {
        border-radius: 10px;
        background-color: #E0BBE4;
        color: white;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("המרחב האישי שלי ✨")
st.write(f"היום: {datetime.now().strftime('%d/%m/%Y')} | צעד אחד בכל פעם.")

# --- דאשבורד (לוח בקרה דינמי) ---
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    
    # סיכום כללי
    total = len(df)
    done = df['completed'].sum()
    prog_total = int((done/total)*100) if total > 0 else 0
    
    col1, col2, col3 = st.columns([1,1,1])
    col1.markdown(f"<div class='stat-card'><h3>{total}</h3>משימות לביצוע</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='stat-card'><h3>{done}</h3>הושלמו</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='stat-card'><h3>{prog_total}%</h3>הספק כללי</div>", unsafe_allow_html=True)

    # פירוט לפי תחומים (רק מה שיש בו משימות)
    st.write("### איך אני מתקדמת בכל תחום?")
    
    # מציג את התחומים ב-3 עמודות כדי לחסוך מקום
    cat_cols = st.columns(3)
    active_categories = df['category'].unique()
    
    for i, cat in enumerate(active_categories):
        cat_df = df[df['category'] == cat]
        c_done = cat_df['completed'].sum()
        c_total = len(cat_df)
        c_perc = c_done / c_total
        
        with cat_cols[i % 3]:
            st.write(f"**{cat}** ({c_done}/{c_total})")
            st.progress(c_perc)
else:
    st.info("הרשימה ריקה. זמן להכניס את כל המשימות ולעשות סדר בראש 🌸")

st.write("---")

# --- הוספת משימה חדשה ---
with st.expander("➕ להוסיף משימה חדשה"):
    with st.form("task_form", clear_on_submit=True):
        name = st.text_input("מה המשימה?")
        
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1:
            category = st.selectbox("תחום", CATEGORIES)
        with c_col2:
            prio_label = st.radio("דחיפות", ["🔥 דחוף", "⏳ בקרוב", "☁️ בנחת"], horizontal=True)
            prio_map = {"🔥 דחוף": "גבוהה", "⏳ בקרוב": "בינונית", "☁️ בנחת": "נמוכה"}
            priority = prio_map[prio_label]
        with c_col3:
            due_date = st.date_input("תאריך יעד", datetime.now())
        
        notes = st.text_area("הערות נוספות (לינקים, טלפונים, פרטים...)")
        
        if st.form_submit_button("להוסיף לרשימה ✨"):
            if name:
                st.session_state.tasks.append({
                    "name": name, "category": category, "priority": priority,
                    "due_date": due_date, "notes": notes, "completed": False
                })
                save_data(st.session_state.tasks)
                st.rerun()

# --- הצגת המשימות ---
st.write("### הרשימה שלי")

if st.session_state.tasks:
    # בחירת סינון לפי תחום (אופציונלי)
    filter_cat = st.multiselect("סינון לפי תחום (השאירי ריק להצגת הכל)", CATEGORIES)
    
    # הכנת הרשימה להצגה
    p_order = {"גבוהה": 0, "בינונית": 1, "נמוכה": 2}
    tasks_to_show = enumerate(st.session_state.tasks)
    
    if filter_cat:
        tasks_to_show = [t for t in tasks_to_show if t[1]['category'] in filter_cat]
        
    sorted_tasks = sorted(tasks_to_show, key=lambda x: (x[1]['completed'], p_order.get(x[1]['priority'], 3)))

    for i, task in sorted_tasks:
        p_class = "priority-high" if task['priority'] == "גבוהה" else "priority-med" if task['priority'] == "בינונית" else "priority-low"
        completed_style = "opacity: 0.5; text-decoration: line-through;" if task['completed'] else ""
        
        st.markdown(f"""
            <div class="task-card {p_class}" style="{completed_style}">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <strong>{task['name']}</strong><br>
                        <small>🏷️ {task['category']} | 📅 {task['due_date']} | 🔥 {task['priority']}</small>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col_act1, col_act2, col_act3 = st.columns([0.2, 0.2, 0.6])
        if col_act1.button("בוצע ✅" if not task['completed'] else "בטל", key=f"done_{i}"):
            st.session_state.tasks[i]['completed'] = not st.session_state.tasks[i]['completed']
            save_data(st.session_state.tasks)
            st.rerun()
        if col_act2.button("מחיקה 🗑️", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            save_data(st.session_state.tasks)
            st.rerun()
        if task['notes']:
            col_act3.info(f"📝 {task['notes']}")
