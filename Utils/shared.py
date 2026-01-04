import streamlit as st
from datetime import datetime

class SharedDB:
    def __init__(self):
        if "uni_multiverse" not in st.session_state:
            st.session_state.uni_multiverse = {}
            
    def get_college(self, name):
        return st.session_state.uni_multiverse.get(name)

    def register_college(self, name, password):
        if not name or name in st.session_state.get("uni_multiverse" , {}):
            return False
        st.session_state.uni_multiverse[name] = {
            "password": password,
            "sections": [{"id": "Year 1-CS-A", "year": "Year 1", "name": "CS-A"}],
            "schedule": {},   
            "notes": {},      
            "user_vault": {}  
        }
        return True

    def check_password(self, college_name, user_id, password):
        data = self.get_college(college_name)
        if not data: return False
        if user_id not in data["user_vault"]:
            data["user_vault"][user_id] = password
            return True
        return data["user_vault"][user_id] == password

    def get_status(self, slot_day, slot_start_time):
        now = datetime.now()
        current_day = now.strftime("%A")
        current_time = now.strftime("%H:%M")
        
        from Database.models import DAYS
        try:
            now_idx = DAYS.index(current_day)
            slot_idx = DAYS.index(slot_day)
        except: return "future" # Default for debugging

        if slot_idx < now_idx: return "past"
        if slot_idx > now_idx: return "future"
        # Assuming class lasts 1 hour based on your SLOTS
        start_hour = int(slot_start_time.split(":")[0])
        if int(current_time.split(":")[0]) > start_hour:
            return "past"
        return "active"
    
shared_db = SharedDB()