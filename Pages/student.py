import streamlit as st
from Database.models import DAYS, SLOTS
from Utils.shared import shared_db

class StudentPortal:
    def render(self, college_name, year, section, roll):
        data = shared_db.get_college(college_name)
        sec_id = f"{year}-{section}"
        
        st.title(f"🎓 Student Portal: {roll}")
        st.caption(f"Section: {sec_id}")

        # --- 1. DASHBOARD CALCULATIONS ---
        attended_count = 0
        total_conducted = 0
        
        for day in DAYS:
            for slot in SLOTS:
                cid = f"{sec_id}-{day}-{slot}"
                if data["schedule"].get(cid, {}).get("subject"):
                    status = shared_db.get_status(day, slot.split(" - ")[0])
                    if status in ["past", "active"]:
                        total_conducted += 1
                        if data.get("attendance", {}).get(f"att_{cid}_{roll}"):
                            attended_count += 1

        attendance_pct = (attended_count / total_conducted * 100) if total_conducted > 0 else 0
        
        if attendance_pct >= 75: color = "normal" # Green
        elif 60 <= attendance_pct < 75: color = "off" # Amber
        else: color = "inverse" # Red

        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Total Attendance", f"{attendance_pct:.1f}%", 
                      help=f"Calculation: ({attended_count}/{total_conducted}) * 100")
            st.write(f"**Raw Count:** {attended_count} of {total_conducted} sessions")
        with col2:
            st.write("### Attendance Gauge")
            st.progress(attendance_pct / 100)
            if attendance_pct < 75:
                st.warning("Your attendance is below the 75% requirement.")

        st.divider()

        # --- 2. WEEKLY VIEW WITH NOTES & TOGGLE ---
        st.subheader("Weekly Class Schedule")
        
        # Grid Header
        cols = st.columns([0.8] + [2 for _ in SLOTS])
        cols[0].write("**Day**")
        for i, slot in enumerate(SLOTS):
            cols[i+1].write(f"**{slot}**")

        for day in DAYS:
            row = st.columns([0.8] + [2 for _ in SLOTS])
            row[0].write(f"**{day[:3]}**")
            
            for i, slot in enumerate(SLOTS):
                cid = f"{sec_id}-{day}-{slot}"
                cell = data["schedule"].get(cid, {})
                status = shared_db.get_status(day, slot.split(" - ")[0])
                att_key = f"att_{cid}_{roll}"
                
                with row[i+1]:
                    if cell.get("subject"):
                        # Display Subject and Teacher
                        st.markdown(f"**{cell['subject']}**")
                        st.caption(f"👨‍🏫 {cell['teacher']}")
                        
                        # Display Teacher's Notes if they exist
                        session_notes = data.get("notes", {}).get(cid)
                        if session_notes:
                            with st.expander("📝 Session Notes"):
                                st.write(session_notes)

                        # --- ATTENDANCE TOGGLE ---
                        is_present = data.get("attendance", {}).get(att_key, False)
                        
                        if status == "active":
                            # The active toggle for the current session
                            tgl = st.toggle("Mark Present", value=is_present, key=f"t_{cid}")
                            if tgl != is_present:
                                if "attendance" not in data: data["attendance"] = {}
                                data["attendance"][att_key] = tgl
                                st.rerun()
                        
                        elif status == "past":
                            if is_present:
                                st.success("Present")
                            else:
                                st.error("Absent")
                        else:
                            st.info("Upcoming") 
                    else:
                        st.write("\n\n\n---\n\n\n---\n\n\n")
                