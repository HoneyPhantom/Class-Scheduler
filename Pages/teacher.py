import streamlit as st
from Database.models import DAYS, SLOTS
from Utils.shared import shared_db

class TeacherPortal:
    def render(self, college_name, teacher_name):
        data = shared_db.get_college(college_name)
        st.title(f"👨‍🏫 Teacher: {teacher_name}")

        # Grid Header
        cols = st.columns([1] + [2 for _ in SLOTS])
        cols[0].write("**Day**")
        for i, slot in enumerate(SLOTS): cols[i+1].write(f"**{slot}**")

        for day in DAYS:
            cols = st.columns([1] + [2 for _ in SLOTS])
            cols[0].write(f"**{day[:3]}**")
            for i, slot in enumerate(SLOTS):
                with cols[i+1]:
                    match = None
                    for sec in data["sections"]:
                        cid = f"{sec['id']}-{day}-{slot}"
                        if data["schedule"].get(cid, {}).get("teacher") == teacher_name:
                            match = (sec['id'], cid, data["schedule"][cid]["subject"])
                    
                    if match:
                        sec_id, cid, subject = match
                        st.markdown(f"**{subject}** ({sec_id})")
                        
                        # --- CANCEL TOGGLE ---
                        is_cancelled = data.get("cancelled", {}).get(cid, False)
                        if st.toggle("Cancel Class", value=is_cancelled, key=f"can_{cid}"):
                            if "cancelled" not in data: data["cancelled"] = {}
                            data["cancelled"][cid] = True
                            st.caption("🚨 Cancelled")
                        else:
                            data["cancelled"][cid] = False
                            st.caption("✅ Active")

                        # --- NOTES ---
                        note = st.text_area("Notes", value=data["notes"].get(cid, ""), 
                                           key=f"nt_{cid}", height=60, label_visibility="collapsed")
                        data["notes"][cid] = note
                    else:
                        st.write("---")