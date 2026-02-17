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
    "ועדת חוקה", "בית", "רפואה", "קניות", "אישי", "הדגש", "לימודים כללי"
]

# --- עיצוב CSS פסטלי ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stApp { background-color: #FDFCFB; }
    .st-ae summary { flex-direction: row-reverse; justify-content: flex-start; gap: 15px; }

    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        border-bottom: 5px solid #E0BBE4;
    }

    .task-card {
        background: white;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        border-right: 10px solid #BEE1E6;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    }
    .priority-גבוהה { border-right-color: #FFB3BA !important; } 
    .priority-בינונית { border-right-color: #FFDFBA !important; }  
    .priority-נמוכה { border-right-color: #BAFFC9 !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f0f0;
        border-radius: 10px 10px 0 0;
    }
    .stTabs [aria-selected="true"] { background-color: #E0BBE4 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("המרחב האישי שלי ✨")

tab_tasks, tab_dashboard = st.tabs(["📝 ניהול משימות", "📊 דאשבורד התקדמות"])

# --- טאב 1: ניהול משימות ---
with tab_tasks:
    with st.expander("➕ להוסיף משימה חדשה שיושבת לי על הראש"):
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("מה המשימה?")
            c1, c2, c3 = st.columns(3)
            category = c1.selectbox("תחום", CATEGORIES)
            prio_label = c2.radio("דחיפות", ["🔥 דחוף", "⏳ בקרוב", "☁️ בנחת"], horizontal=True)
            due_date = c3.date_input("תאריך יעד", datetime.now())
            notes = st.text_area("הערות או לינקים")
            if st.form_submit_button("להוסיף לרשימה ✨"):
                prio_map = {"🔥 דחוף": "גבוהה", "⏳ בקרוב": "בינונית", "☁️ בנחת": "נמוכה"}
                st.session_state.tasks.append({
                    "name": name, "category": category, "priority": prio_map[prio_label],
                    "due_date": due_date, "notes": notes, "completed": False
                })
                save_data(st.session_state.tasks)
                st.rerun()

    st.write("### הרשימה שלי")
    if not st.session_state.tasks:
        st.info("אין כרגע משימות. זמן לנוח! ☕")
    else:
        # מיון בסיסי
        p_order = {"גבוהה": 0, "בינונית": 1, "נמוכה": 2}
        sorted_tasks = sorted(enumerate(st.session_state.tasks), key=lambda x: (x[1]['completed'], p_order.get(x[1]['priority'], 3)))
        
        # סינון קטגוריות (מחוץ ללופ)
        selected_cats = st.multiselect("לראות רק את... (בחרי תחומים)", CATEGORIES)
        if selected_cats:
            sorted_tasks = [t for t in sorted_tasks if t[1]['category'] in selected_cats]

        # לופ הצגת המשימות (עכשיו הוא מחוץ ל-if של הסינון כדי שיוצגו משימות גם כשלא נבחר כלום)
        for i, task in sorted_tasks:
            if st.session_state.editing_index == i:
                with st.container():
                    st.markdown("---")
                    edit_name = st.text_input("שם המשימה", task['name'], key=f"ed_name_{i}")
                    edit_cat = st.selectbox("תחום", CATEGORIES, index=CATEGORIES.index(task['category']), key=f"ed_cat_{i}")
                    edit_notes = st.text_area("הערות", task['notes'], key=f"ed_note_{i}")
                    eb1, eb2 = st.columns(2)
                    if eb1.button("שמור שינויים ✅", key=f"sv_{i}"):
                        st.session_state.tasks[i].update({"name": edit_name, "category": edit_cat, "notes": edit_notes})
                        save_data(st.session_state.tasks)
                        st.session_state.editing_index = None
                        st.rerun()
                    if eb2.button("ביטול", key=f"cn_{i}"):
                        st.session_state.editing_index = None
                        st.rerun()
            else:
                p_class = f"priority-{task['priority']}"
                comp_style = "opacity: 0.5; text-decoration: line-through;" if task['completed'] else ""
                st.markdown(f"""<div class="task-card {p_class}" style="{comp_style}"><strong>{task['name']}</strong><br><small>{task['category']} | יעד: {task['due_date']} | דחיפות: {task['priority']}</small></div>""", unsafe_allow_html=True)
                
                a1, a2, a3, a4 = st.columns([0.1, 0.1, 0.1, 0.7])
                if a1.button("✅", key=f"d_{i}"):
                    st.session_state.tasks[i]['completed'] = not st.session_state.tasks[i]['completed']
                    save_data(st.session_state.tasks)
                    st.rerun()
                if a2.button("📝", key=f"e_{i}"):
                    st.session_state.editing_index = i
                    st.rerun()
                if a3.button("🗑️", key=f"del_{i}"):
                    st.session_state.tasks.pop(i)
                    save_data(st.session_state.tasks)
                    st.rerun()
                if task['notes']: a4.caption(f"📝 {task['notes']}")

# --- טאב 2: דאשבורד ---
with tab_dashboard:
    st.header("איך אני מתקדמת היום? 📈")
    if st.session_state.tasks:
        df = pd.DataFrame(st.session_state.tasks)
        total_tasks = len(df)
        completed_tasks = df['completed'].sum()
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.markdown(f"<div class='stat-card'><h3>{total_tasks}</h3>משימות סה\"כ</div>", unsafe_allow_html=True)
        col_m2.markdown(f"<div class='stat-card'><h3>{completed_tasks}</h3>משימות שבוצעו ✨</div>", unsafe_allow_html=True)
        col_m3.markdown(f"<div class='stat-card'><h3>{int((completed_tasks/total_tasks)*100)}%</h3>הספק כללי</div>", unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("התקדמות לפי נושאים")
        active_cats = df['category'].unique()
        cat_cols = st.columns(3)
        for index, cat in enumerate(active_cats):
            cat_df = df[df['category'] == cat]
            c_perc = cat_df['completed'].sum() / len(cat_df)
            with cat_cols[index % 3]:
                st.write(f"**{cat}**")
                st.progress(c_perc)
                st.caption(f"{cat_df['completed'].sum()} מתוך {len(cat_df)} הושלמו")
    else:
        st.info("הדאשבורד יתמלא ברגע שתכניסי משימות.")
