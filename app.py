import streamlit as st
from Utils.shared import shared_db
from Pages.admin import AdminPortal
from Pages.teacher import TeacherPortal
from Pages.student import StudentPortal
import datetime

if 'uni_multiverse' not in st.session_state:
    st.session_state.uni_multiverse = {}
    
st.set_page_config(layout="wide", page_title="UniScheduler Pro")

# --- 1. COMPACT MINUTE-BASED TIMER ---

now = datetime.datetime.now()
time_string = now.strftime("%H:%M")
day_string = now.strftime("%A, %d %b")

st.markdown(
    f"""
    <div style="background-color: #1e293b; padding: 10px 20px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #6366f1;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="background: #6366f1; color: white; padding: 4px 12px; border-radius: 5px; font-weight: bold; font-family: monospace; font-size: 1.2rem;">
                {time_string}
            </div>
            <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 500; font-family: 'Inter', sans-serif;">
                {day_string}
            </div>
        </div>
        <div style="color: #6366f1; font-weight: 800; font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase;">
            UniScheduler System Active
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# --- 2. LOGIN GATEKEEPER ---
if "active_college" not in st.session_state:
    st.title("🏛️ UniScheduler Portal")
    t1, t2 = st.tabs(["Login", "Register College"])
    
    with t1:
        c = st.text_input("College Name")
        if st.button("Enter"):
            if shared_db.get_college(c):
                st.session_state.active_college = c
                st.rerun()
            else: st.error("College not found.")
    with t2:
        rn = st.text_input("New College Name")
        rp = st.text_input("Master Password", type="password")
        if st.button("Create"):
            if shared_db.register_college(rn, rp): st.success("Created! Use Login tab.")

# --- 3. APP INTERFACE ---
else:
    college = st.session_state.active_college
    data = shared_db.get_college(college)
    
    st.sidebar.title(f"🏫 {college}")
    role = st.sidebar.selectbox("Role", ["Dashboard", "Admin", "Teacher", "Student"])
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if role == "Dashboard":
        st.header(f"Welcome to {college}")
        st.info("Please select a role and authenticate in the sidebar.")

    elif role == "Admin":
        if st.sidebar.text_input("Admin Password", type="password") == data["password"]:
            AdminPortal().render(college)
        else: st.sidebar.warning("Enter correct password.")

    elif role == "Teacher":
        tn = st.sidebar.text_input("Teacher Name")
        tp = st.sidebar.text_input("Password", type="password")
        if tn and tp:
            user_id = f"T-{tn}"
            if user_id not in data["user_vault"]:
                if st.sidebar.button("Register as New Teacher"):
                    data["user_vault"][user_id] = tp
                    st.rerun()
            elif data["user_vault"][user_id] == tp:
                TeacherPortal().render(college, tn)
            else: st.sidebar.error("Invalid password.")

    elif role == "Student":
        years = sorted(list(set([s['year'] for s in data["sections"]])))
        y = st.sidebar.selectbox("Year", ["-- Select --"] + years)
        sects = [s['name'] for s in data["sections"] if s['year'] == y]
        s = st.sidebar.selectbox("Section", ["-- Select --"] + sects)
        r = st.sidebar.text_input("Roll")
        sp = st.sidebar.text_input("Student Password", type="password")
        
        if y != "-- Select --" and s != "-- Select --" and r and sp:
            user_id = f"S-{y}-{s}-{r}"
            if user_id not in data["user_vault"]:
                if st.sidebar.button("Register Student Account"):
                    data["user_vault"][user_id] = sp
                    st.rerun()
            elif data["user_vault"][user_id] == sp:
                StudentPortal().render(college, y, s, r)
            else: st.sidebar.error("Invalid password.")
