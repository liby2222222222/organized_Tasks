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

if 'editing_index' not in st.session_state:
    st.session_state.editing_index = None

CATEGORIES = [
    "לשכת המדענית משרד החינוך", "בייביסיטר מיוחד במינו", "מחקר איכותני", 
    "מבוא לבריהמ", "כריית נתונים", "פלסטינים", "קורס התמחות", 
    "ועדת חוקה", "בית", "רפואה", "קניות", "אישי"
]

# --- עיצוב CSS מתוקן (כולל תיקון לתקלת התצוגה) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stApp { background-color: #FDFCFB; }
    
    /* תיקון לכותרת ה-Expander שלא תתנגש באייקון */
    .st-ae summary {
        flex-direction: row-reverse;
        justify-content: flex-start;
        gap: 15px;
    }
    .st-ae summary div {
        margin-right: 10px;
    }

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
        margin-bottom: 5px;
        border-right: 8px solid #BEE1E6;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    
    .priority-high { border-right-color: #FFB3BA !important; } 
    .priority-med { border-right-color: #FFDFBA !important; }  
    .priority-low { border-right-color: #BAFFC9 !important; }  
    </style>
    """, unsafe_allow_html=True)

st.title("המרחב האישי שלי ✨")

# --- דאשבורד ---
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    total, done = len(df), df['completed'].sum()
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='stat-card'><h3>{total}</h3>משימות</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='stat-card'><h3>{done}</h3>בוצעו</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='stat-card'><h3>{int((done/total)*100) if total > 0 else 0}%</h3>הספק</div>", unsafe_allow_html=True)

st.write("---")

# --- הוספת משימה ---
with st.expander("➕ להוסיף משימה חדשה"):
    with st.form("task_form", clear_on_submit=True):
        name = st.text_input("מה המשימה?")
        c1, c2, c3 = st.columns(3)
        category = c1.selectbox("תחום", CATEGORIES)
        prio_label = c2.radio("דחיפות", ["🔥 דחוף", "⏳ בקרוב", "☁️ בנחת"], horizontal=True)
        due_date = c3.date_input("יעד", datetime.now())
        notes = st.text_area("הערות")
        if st.form_submit_button("הוספה ✨"):
            prio_map = {"🔥 דחוף": "גבוהה", "⏳ בקרוב": "בינונית", "☁️ בנחת": "נמוכה"}
            st.session_state.tasks.append({
                "name": name, "category": category, "priority": prio_map[prio_label],
                "due_date": due_date, "notes": notes, "completed": False
            })
            save_data(st.session_state.tasks)
            st.rerun()

# --- הצגת משימות ועריכה ---
st.write("### הרשימה שלי")
p_order = {"גבוהה": 0, "בינונית": 1, "נמוכה": 2}

for i, task in enumerate(st.session_state.tasks):
    # מצב עריכה
    if st.session_state.editing_index == i:
        with st.container():
            st.markdown("### עריכת משימה 📝")
            new_name = st.text_input("שם המשימה", task['name'], key=f"edit_name_{i}")
            new_cat = st.selectbox("תחום", CATEGORIES, index=CATEGORIES.index(task['category']), key=f"edit_cat_{i}")
            new_notes = st.text_area("הערות", task['notes'], key=f"edit_note_{i}")
            btn1, btn2 = st.columns(2)
            if btn1.button("שמור שינויים ✅", key=f"save_{i}"):
                st.session_state.tasks[i].update({"name": new_name, "category": new_cat, "notes": new_notes})
                save_data(st.session_state.tasks)
                st.session_state.editing_index = None
                st.rerun()
            if btn2.button("ביטול ❌", key=f"cancel_{i}"):
                st.session_state.editing_index = None
                st.rerun()
    
    # מצב תצוגה רגיל
    else:
        p_class = "priority-high" if task['priority'] == "גבוהה" else "priority-med" if task['priority'] == "בינונית" else "priority-low"
        completed_style = "opacity: 0.5; text-decoration: line-through;" if task['completed'] else ""
        
        st.markdown(f"""
            <div class="task-card {p_class}" style="{completed_style}">
                <strong>{task['name']}</strong> | <small>{task['category']} | יעד: {task['due_date']}</small>
            </div>
        """, unsafe_allow_html=True)
        
        act1, act2, act3, act4 = st.columns([0.15, 0.15, 0.15, 0.55])
        if act1.button("✅", key=f"d_{i}", help="בוצע"):
            st.session_state.tasks[i]['completed'] = not st.session_state.tasks[i]['completed']
            save_data(st.session_state.tasks)
            st.rerun()
        if act2.button("📝", key=f"e_{i}", help="עריכה"):
            st.session_state.editing_index = i
            st.rerun()
        if act3.button("🗑️", key=f"del_{i}", help="מחיקה"):
            st.session_state.tasks.pop(i)
            save_data(st.session_state.tasks)
            st.rerun()
        if task['notes']:
            act4.caption(f"📝 {task['notes']}")

