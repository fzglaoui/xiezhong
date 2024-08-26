import streamlit as st
import sqlite3
import datetime
import base64
import requests
import os

# Database connection function
def get_database_connection():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'xiezhong.db')
    return sqlite3.connect(db_path)

def get_technicien_options():
    conn = get_database_connection()
    cursor = conn.cursor()

    query = "SELECT techinicien1 FROM technicien"
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()

    return [result[0] for result in results]

def get_type_options():
    conn = get_database_connection()
    cursor = conn.cursor()

    query = "SELECT Type FROM typemaintenance"
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()

    return [result[0] for result in results]

def get_shift_options():
    conn = get_database_connection()
    cursor = conn.cursor()

    query = "SELECT Shift FROM shifts"
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()

    return [result[0] for result in results]

def get_parc_options():
    conn = get_database_connection()
    cursor = conn.cursor()

    query = "SELECT id, parc_name FROM parc"
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()

    return results

def get_machine_options(parc_id):
    conn = get_database_connection()
    cursor = conn.cursor()

    query = "SELECT machine_name FROM machine WHERE parc_id = ?"
    cursor.execute(query, (parc_id,))
    results = cursor.fetchall()

    conn.close()

    return [result[0] for result in results]

# Authentication function
def authenticate(username, password):
    conn = get_database_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    conn.close()

    return result is not None

# Function to save form data
def save_form_data(form_data):
    conn = get_database_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO maintenance_forms 
    (date, Numéro_de_bon, type, technicien1, technicien2, shift, parc, machine, localisation, problem, root_cause, description, 
    machine_stop, stop_time, intervention_start, intervention_end, spare_parts, request_status) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        cursor.execute(query, tuple(form_data.values()))
        conn.commit()
        st.success("Form submitted successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
    finally:
        conn.close()

# Function to get base64 of image from URL
def get_base64_of_image_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
        return ""

# Function to display the form
def show_form():
    st.subheader("Form View")

    date = st.date_input("Date", value=datetime.date.today(), key="date_input")
    Numéro_de_bon = st.number_input("Numéro de bon", min_value=1, step=1, key="numero_bon_input")

    type_options = get_type_options()
    selected_type = st.selectbox("Type", type_options, key="type_select")

    technicien_options = get_technicien_options()
    technicien1 = st.selectbox("Technicien 1", technicien_options, key="technicien1_select")
    technicien2 = st.selectbox("Technicien 2 (Optional)", ["None"] + technicien_options, key="technicien2_select")

    shift_options = get_shift_options()
    selected_shift = st.selectbox("Shift", shift_options, key="shift_select")

    parc_options = get_parc_options()
    selected_parc_id = st.selectbox("Parc", [parc_name for _, parc_name in parc_options], key="parc_select")

    selected_parc = next(parc_id for parc_id, parc_name in parc_options if parc_name == selected_parc_id)
    machine_options = get_machine_options(selected_parc)
    selected_machine = st.selectbox("Machine", machine_options, key="machine_select")

    localisation = st.text_input("localisation", key="localisation_input")
    problem = st.text_input("Problème", key="problem_input")
    root_cause = st.text_input("Cause Racine", key="root_cause_input")
    description = st.text_area("Description", key="description_input")

    machine_stop = st.radio("Machine STOP", ["OUI", "NON", "Planifier"], key="machine_stop_radio")

    stop_time = st.time_input("Temps début arrêt", step=60, key="stop_time_input")
    intervention_start = st.time_input("Temps début intervention", step=60, key="intervention_start_input")
    intervention_end = st.time_input("Temps fin intervention", step=60, key="intervention_end_input")

    spare_parts = st.text_input("Pièces de rechange", key="spare_parts_input")

    status_options = ["En attente", "En cours", "Terminé"]
    request_status = st.selectbox("État de demande", status_options, key="request_status_select")

    if st.button("Submit", key="submit_button"):
        form_data = {
            "date": date.isoformat(),
            "Numéro de bon": Numéro_de_bon,
            "type": selected_type,
            "technicien1": technicien1,
            "technicien2": technicien2,
            "shift": selected_shift,
            "park": selected_parc_id,
            "machine": selected_machine,
            "localisation": localisation,
            "problem": problem,
            "root_cause": root_cause,
            "description": description,
            "machine_stop": machine_stop,
            "stop_time": stop_time.isoformat(),
            "intervention_start": intervention_start.isoformat(),
            "intervention_end": intervention_end.isoformat(),
            "spare_parts": spare_parts,
            "request_status": request_status
        }
        save_form_data(form_data)

def main():
    st.set_page_config(page_title="Login Page", layout="wide")

    logo_url = "https://i.ibb.co/RYBBYBn/1617259109587-removebg-preview.png"
    logo_base64 = get_base64_of_image_url(logo_url)

    st.markdown(f"""
    <style>
    .stApp {{
        background-color: #1E1E3F;
        color: white;
    }}
    .stTextInput > div > div > input {{
        background-color: #2D2D5F;
        color: white;
    }}
    .stButton > button {{
        background-color: #3498DB;
        color: white;
    }}
    .menu-item {{
        display: inline-block;
        padding: 10px 20px;
        color: #FFFFFF;
        text-decoration: none;
        transition: background-color 0.3s;
    }}
    .menu-item:hover {{
        background-color: rgba(255, 255, 255, 0.1);
    }}
    .header {{
        display: flex;
        align-items: center;
        background-color: #2D2D5F;
        padding: 10px;
    }}
    .logo {{
        width: 50px;
        margin-right: 20px;
    }}
    .title {{
        font-size: 24px;
        font-weight: bold;
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if logo_base64:
        st.markdown(f"""
        <div class="header">
            <img src="data:image/png;base64,{logo_base64}" class="logo" />
            <div class="title">Xiezhong Maintenance Management</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="header">
            <div class="title">Xiezhong Maintenance Management</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state["authenticated"]:
        with st.sidebar:
            if st.button("Logout"):
                st.session_state["authenticated"] = False
                st.rerun()

    if not st.session_state["authenticated"]:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state["authenticated"] = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    else:
        show_form()

if __name__ == "__main__":
    main()
