import streamlit as st
import mysql.connector
import datetime
import base64
from openpyxl import load_workbook

# Database connection function
def get_database_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='xiezhong'
    )


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

    return [result[0] for result in results]  # Extract the first column from each row


def get_shift_options():
    conn = get_database_connection()
    cursor = conn.cursor()

    query = "SELECT Shift FROM shifts"
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()

    return [result[0] for result in results]  # Extract the first column from each row


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

    query = "SELECT machine_name FROM machine WHERE parc_id = %s"
    cursor.execute(query, (parc_id,))
    results = cursor.fetchall()

    conn.close()

    return [result[0] for result in results]


# Authentication function
def authenticate(username, password):
    conn = get_database_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username = %s AND password = %s"
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
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(query, tuple(form_data.values()))
        conn.commit()

        # Update Excel file
        excel_file_path = r"D:\AppDb\entry.xlsx"
        wb = load_workbook("D:\AppDb\entry.xlsx")
        ws = wb['DataForm']  # Assuming your sheet name is 'DataForm'

        # Extract date components
        date_obj = form_data['date']
        day = date_obj.day
        month = date_obj.month
        year = date_obj.year
        week_number = date_obj.isocalendar()[1]  # Get the week number

        # Append new row to the Excel sheet
        new_row = [
            date_obj.strftime("%d/%m/%Y"),  # Display full date
            day,
            month,
            year,
            week_number,
            form_data['Numéro de bon'],
            form_data['type'],
            form_data['technicien1'],
            form_data['technicien2'],
            form_data['shift'],
            form_data['park'],
            form_data['machine'],
            form_data['localisation'],
            form_data['problem'],
            form_data['root_cause'],
            form_data['description'],
            form_data['machine_stop'],
            form_data['stop_time'],
            form_data['intervention_start'],
            form_data['intervention_end'],
            form_data['spare_parts'],
            form_data['request_status']
        ]

        ws.append(new_row)
        wb.save(excel_file_path)
        st.success("Form submitted successfully!")
    except mysql.connector.Error as e:
        st.error(f"An error occurred: {e}")
    finally:
        conn.close()


# Function to get base64 of binary file
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Function to display the form
def show_form():
    st.subheader("Form View")

    # Date calendar
    date = st.date_input("Date", value=datetime.date.today(), key="date_input")

    # Ticket number
    Numéro_de_bon = st.number_input("Numéro de bon", min_value=1, step=1, key="numero_bon_input")

    # Fetch the types from the database
    type_options = get_type_options()
    selected_type = st.selectbox("Type", type_options, key="type_select")

    technicien_options = get_technicien_options()
    technicien1 = st.selectbox("Technicien 1", technicien_options, key="technicien1_select")
    technicien2 = st.selectbox("Technicien 2 (Optional)", ["None"] + technicien_options, key="technicien2_select")

    # Fetch the shifts from the database
    shift_options = get_shift_options()
    selected_shift = st.selectbox("Shift", shift_options, key="shift_select")

    parc_options = get_parc_options()
    selected_parc_id = st.selectbox("Parc", [parc_name for _, parc_name in parc_options], key="parc_select")

    # Fetch machines based on the selected parc
    selected_parc = next(parc_id for parc_id, parc_name in parc_options if parc_name == selected_parc_id)
    machine_options = get_machine_options(selected_parc)
    selected_machine = st.selectbox("Machine", machine_options, key="machine_select")

    # Text input fields
    localisation = st.text_input("localisation", key="localisation_input")
    problem = st.text_input("Problème", key="problem_input")
    root_cause = st.text_input("Cause Racine", key="root_cause_input")
    description = st.text_area("Description", key="description_input")

    # Machine STOP options
    machine_stop = st.radio("Machine STOP", ["OUI", "NON", "Planifier"], key="machine_stop_radio")

    # Timestamp inputs
    stop_time = st.time_input("Temps début arrêt", step=60, key="stop_time_input")
    intervention_start = st.time_input("Temps début intervention", step=60, key="intervention_start_input")
    intervention_end = st.time_input("Temps fin intervention", step=60, key="intervention_end_input")

    # Spare parts
    spare_parts = st.text_input("Pièces de rechange", key="spare_parts_input")

    # Request status
    status_options = ["En attente", "En cours", "Terminé"]
    request_status = st.selectbox("État de demande", status_options, key="request_status_select")

    if st.button("Submit", key="submit_button"):
        form_data = {
            "date": date,
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
            "stop_time": stop_time.strftime("%H:%M:%S"),
            "intervention_start": intervention_start.strftime("%H:%M:%S"),
            "intervention_end": intervention_end.strftime("%H:%M:%S"),
            "spare_parts": spare_parts,
            "request_status": request_status
        }
        try:
            save_form_data(form_data)
            st.success("Form submitted successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")

def main():
    st.set_page_config(page_title="Login Page", layout="wide")

    # Load and encode the logo
    logo_path = r"C:\Users\PC\Downloads\1617259109587-removebg-preview.png"
    logo_base64 = get_base64_of_bin_file(logo_path)

    # Custom CSS for styling
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

    # Session state management
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Display logo and header
    st.markdown(f"""
    <div class="header">
        <img src="data:image/png;base64,{logo_base64}" class="logo" />
        <div class="title">Xiezhong Maintenance Management</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with logout button
    if st.session_state["authenticated"]:
        with st.sidebar:
            if st.button("Logout"):
                st.session_state["authenticated"] = False
                st.rerun()

    # Authentication page
    if not st.session_state["authenticated"]:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state["authenticated"] = True
                st.success("Login successful!")
                st.rerun()  # Rerun the app to show the form
            else:
                st.error("Invalid username or password")
    else:
        show_form()  # Show form if already authenticated


if __name__ == "__main__":
    main()
