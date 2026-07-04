import streamlit as st
import gspread
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Retrieve secrets from Streamlit's secrets management
GSHEET_URL = st.secrets["gcp_gsheet"]["url"]
gcp_service_account = st.secrets["gcp_service_account"]

# Use the secrets to create a credentials object
credentials = service_account.Credentials.from_service_account_info(
    gcp_service_account,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

# Initialize Google Sheets API clients
client = gspread.authorize(credentials)
service = build('sheets', 'v4', credentials=credentials)

# Sample username and password for authentication
USERNAME = "admin"
PASSWORD = "password"

# Login page
def login_page():
    st.title("Login")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state['logged_in'] = True
            st.session_state['page'] = "dashboard"
            # Instead of st.experimental_rerun(), use set_query_params to trigger a refresh
            st.experimental_set_query_params(logged_in="true")
        else:
            st.error("Incorrect username or password.")

# Dashboard for CRUD operations
def admin_dashboard():
    st.title("Admin Dashboard")

    # Sidebar for navigation
    page = st.sidebar.radio("Go to", ['View Data', 'Add Entry', 'Edit Entry', 'Delete Entry'])

    # Google Sheets connection
    sheet = client.open_by_url(GSHEET_URL).sheet1

    # View Data
    if page == 'View Data':
        st.subheader("View Data")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        st.dataframe(df)

    # Add Entry
    elif page == 'Add Entry':
        st.subheader("Add New Entry")
        new_row = []
        new_row.append(st.text_input("Serial Number:"))
        new_row.append(st.text_input("Name:"))
        new_row.append(st.text_input("State ID Number:"))
        new_row.append(st.text_input("Mobile Number:"))
        new_row.append(st.selectbox("Gender:", ["Male", "Female"]))
        new_row.append(st.text_input("Training Centre:"))
        new_row.append(st.selectbox("Category:", ["", "U 9", "U 11", "U 13", "U 15", "U 17", "U 19", "Open"]))
        new_row.append(st.text_input("Seed:"))

        if st.button("Submit"):
            if all(new_row):
                sheet.append_row(new_row)
                st.success("Entry added successfully!")
            else:
                st.error("Please fill in all fields.")

    # Edit Entry
    elif page == 'Edit Entry':
        st.subheader("Edit Entry")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        st.dataframe(df)

        row_to_edit = st.number_input("Enter the serial number of the row to edit:", min_value=1, max_value=len(df), step=1)
        if row_to_edit:
            selected_row = df.loc[row_to_edit - 1]
            updated_data = [
                st.text_input("Serial Number", selected_row['Serial Number']),
                st.text_input("Name", selected_row['Name']),
                st.text_input("State ID Number", selected_row['State ID Number']),
                st.text_input("Mobile Number", selected_row['Mobile Number']),
                st.selectbox("Gender", ["Male", "Female"], index=0 if selected_row['Gender'] == "Male" else 1),
                st.text_input("Training Centre", selected_row['Training Centre']),
                st.selectbox("Category", ["", "U 9", "U 11", "U 13", "U 15", "U 17", "U 19", "Open"], index=0),
                st.text_input("Seed", selected_row['Seed'])
            ]

            if st.button("Update"):
                cell_range = f"A{row_to_edit+1}:H{row_to_edit+1}"
                sheet.update(cell_range, [updated_data])
                st.success(f"Row {row_to_edit} updated successfully!")
                st.experimental_set_query_params(updated="true")

    # Delete Entry
    elif page == 'Delete Entry':
        st.subheader("Delete Entry")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        st.dataframe(df)

        row_to_delete = st.number_input("Enter the serial number of the row to delete:", min_value=1, max_value=len(df), step=1)
        if st.button("Delete"):
            sheet.delete_row(row_to_delete + 1)  # Add 1 because sheet is 1-indexed
            st.success(f"Row {row_to_delete} deleted successfully!")
            st.experimental_set_query_params(deleted="true")

# Main app function
def main():
    # Check query parameters to mimic page refreshes
    query_params = st.experimental_get_query_params()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if query_params.get("logged_in") == ["true"]:
        st.session_state['logged_in'] = True

    if st.session_state['logged_in']:
        admin_dashboard()
    else:
        login_page()

if __name__ == '__main__':
    main()
