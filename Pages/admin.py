import streamlit as st
from Database.models import DAYS, SLOTS
from Utils.shared import shared_db

class AdminPortal:
    def render(self, college_name):
        data = shared_db.get_college(college_name)
        st.title(f"🛠️ Admin: {college_name}")

        # --- Section Management ---
        with st.expander("📂 Manage Sections"):
            col1, col2 = st.columns(2)
            y = col1.text_input("New Year (e.g. Year 2)")
            n = col2.text_input("New Name (e.g. CS-B)")
            if st.button("➕ Add Section"):
                if y and n:
                    data["sections"].append({"id": f"{y}-{n}", "year": y, "name": n})
                    st.rerun()

            st.divider()
            st.subheader("Current Sections")
            for i, sec in enumerate(data["sections"]):
                c1, c2 = st.columns([3, 1])
                c1.write(f"📍 {sec['id']}")
                if c2.button("🗑️", key=f"del_{sec['id']}"):
                    data["sections"].pop(i)
                    st.rerun()

        # --- Timetable Editor ---
        st.subheader("Schedule Editor")
        sec_ids = [s["id"] for s in data["sections"]]
        selected_sec = st.selectbox("Select Section to Edit", sec_ids)

        if selected_sec:
            # Header Row
            cols = st.columns([1] + [2 for _ in SLOTS])
            cols[0].write("**Day**")
            for i, slot in enumerate(SLOTS): cols[i+1].write(f"**{slot}**")

            for day in DAYS:
                cols = st.columns([1] + [2 for _ in SLOTS])
                cols[0].write(f"**{day[:3]}**")
                for i, slot in enumerate(SLOTS):
                    cid = f"{selected_sec}-{day}-{slot}"
                    cell = data["schedule"].get(cid, {"subject": "", "teacher": ""})
                    with cols[i+1]:
                        s = st.text_input("Sub", value=cell["subject"], key=f"s_{cid}", label_visibility="collapsed", placeholder="Sub")
                        t = st.text_input("Tea", value=cell["teacher"], key=f"t_{cid}", label_visibility="collapsed", placeholder="Tea")
                        data["schedule"][cid] = {"subject": s, "teacher": t}