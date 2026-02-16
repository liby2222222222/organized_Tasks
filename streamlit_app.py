import streamlit as st
import pandas as pd
import os
from datetime import datetime

# הגדרות עמוד
st.set_page_config(page_title="המרחב השקט שלי", page_icon="✨", layout="centered")

# פונקציה לשמירה וטעינה של נתונים כדי שלא ימחקו
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

# טעינת המשימות לתוך ה-Session State
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_data()

# עיצוב בסיסי בעזרת CSS (לישור לימין)
st.markdown("""
    <style>
    .stApp { text-align: right; direction: rtl; }
    [data-testid="stSidebar"] { text-align: right; direction: rtl; }
    .stCheckbox { display: flex; flex-direction: row-reverse; }
    </style>
    """, unsafe_allow_html=True)

st.title("המרחב השקט שלי ✨")
st.write("צמצום עומס, שלב אחרי שלב.")

# תפריט צד להוספת משימות
with st.sidebar:
    st.header("משימה חדשה 🌸")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("מה צריך לעשות?")
        cat = st.selectbox("תחום", ["לשכת המדענית משרד החינוך","בייביסיטר מיוחד במינו","מחקר איכותני","מבוא לבריהמ","כריית נתונים","פלסטינים","קורס התמחות","ועדת חוקה","בית","רפואה","קניות"])
        priority = st.select_slider("רמת דחיפות", options=["נמוכה", "בינונית", "גבוהה"])
        date = st.date_input("תאריך יעד", datetime.now())
        note = st.text_area("הערות או מחשבות")
        submit = st.form_submit_button("להוסיף לרשימה ✨")
        
        if submit and name:
            st.session_state.tasks.append({
                "name": name, "category": cat, "priority": priority, 
                "due_date": date, "notes": note, "completed": False
            })
            save_data(st.session_state.tasks)
            st.success("נוסף לרשימה!")

# הצגת נתוני התקדמות
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    st.subheader("איך אני מתקדמת? 🚀")
    
    cols = st.columns(4)
    categories = ["אישי", "עבודה", "לימודים", "בית"]
    
    for i, category in enumerate(categories):
        cat_df = df[df["category"] == category]
        if not cat_df.empty:
            done = cat_df["completed"].sum()
            total = len(cat_df)
            percent = int((done / total) * 100)
            cols[i].metric(category, f"{percent}%")
            cols[i].progress(percent / 100)
        else:
            cols[i].metric(category, "0%")
    
    st.write("---")

    # הצגת הרשימה
    st.subheader("הרשימה שלי")
    
    # מיון משימות: קודם לא בוצעו, לפי דחיפות
    priority_map = {"גבוהה": 0, "בינונית": 1, "נמוכה": 2}
    sorted_tasks = sorted(enumerate(st.session_state.tasks), 
                          key=lambda x: (x[1]['completed'], priority_map.get(x[1]['priority'], 3)))

    for i, task in sorted_tasks:
        with st.container():
            col1, col2 = st.columns([0.8, 0.2])
            
            with col1:
                # סימון בוצע
                check = st.checkbox(f"**{task['name']}**", value=task['completed'], key=f"task_{i}")
                if check != task['completed']:
                    st.session_state.tasks[i]['completed'] = check
                    save_data(st.session_state.tasks)
                    st.rerun()
                
                # פרטים נוספים
                color = "🔴" if task['priority'] == "גבוהה" else "🟡" if task['priority'] == "בינונית" else "🟢"
                st.caption(f"{color} דחיפות: {task['priority']} | 📅 יעד: {task['due_date']} | 🏷️ {task['category']}")
                if task['notes']:
                    st.info(f"📝 {task['notes']}")
            
            with col2:
                if st.button("מחיקה", key=f"del_{i}"):
                    st.session_state.tasks.pop(i)
                    save_data(st.session_state.tasks)
                    st.rerun()
            st.write("---")
else:
    st.balloons()
    st.info("אין משימות כרגע. זה הזמן לנשום עמוק ולהירגע ☕")
