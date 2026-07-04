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

# Function to create or get a worksheet
def get_or_create_worksheet(sheet, worksheet_name):
    newly_created = False
    try:
        worksheet = sheet.worksheet(worksheet_name)
        return worksheet, newly_created  # Return the worksheet and newly_created as False
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows="100", cols="20")
        headers = ["Serial Number", "Name", "State ID Number", "Mobile Number", "Gender", "Training Centre", "Category", "Seed"]
        add_headers(worksheet, headers)
        newly_created = True

        # Apply bold formatting to headers
        spreadsheet_id = sheet.id
        sheet_id = next(
            sheet['properties']['sheetId'] for sheet in service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()['sheets']
            if sheet['properties']['title'] == worksheet_name
        )
        apply_bold_formatting(spreadsheet_id, sheet_id, headers)
        return worksheet, newly_created


def add_headers(worksheet, headers):
    worksheet.append_row(headers)

def apply_bold_formatting(spreadsheet_id, sheet_id, headers):
    start_col = 0
    end_col = len(headers)
    range_ = f"{sheet_id}!A1:{chr(65 + end_col - 1)}1"
    
    requests = [{
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": start_col,
                "endColumnIndex": end_col
            },
            "cell": {
                "userEnteredFormat": {
                    "textFormat": {
                        "bold": True
                    }
                }
            },
            "fields": "userEnteredFormat.textFormat.bold"
        }
    }]
    
    body = {
        'requests': requests
    }
    
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

# Function to add a row to Google Sheets
def add_row_to_google_sheet(new_row, worksheet):
    worksheet.append_row(new_row)

# Function to validate mobile number
def validate_mobile_number(mobile_number):
    return len(mobile_number) == 10 and mobile_number.isdigit()

# Function to validate State ID Number
def validate_state_id_number(state_id_number):
    return state_id_number.isdigit()

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

# Logout function
def logout():
    st.session_state['logged_in'] = False
    st.session_state['page'] = "login"
    st.experimental_set_query_params(logged_in="false")  # Remove the query parameter
    st.success("You have been logged out.")


# Dashboard for CRUD operations
def admin_dashboard():
    st.title("Admin Dashboard")

    # Logout button
    if st.sidebar.button("Logout"):
        logout()

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

   # Add Entry Page
    elif page == 'Add Entry':
     st.subheader("Add New Entry")

      # Create input fields for the new row data
      
    new_row = {}
    new_row['Player Name'] = st.text_input("Player Name:", placeholder="Type your name...")
    new_row['State ID Number'] = st.text_input("State ID Number:", placeholder="Type a number...")
    
    # Validate the State ID Number
    if new_row['State ID Number'] and not validate_state_id_number(new_row['State ID Number']):
        st.error("Please enter a valid State ID Number.")

    new_row['Mobile Number'] = st.text_input("Mobile Number:", placeholder="Type your mobile number...")
    
    # Validate the mobile number
    if new_row['Mobile Number'] and not validate_mobile_number(new_row['Mobile Number']):
        st.error("Please enter a valid 10-digit mobile number.")

    new_row['Gender'] = st.radio("Gender:", ["Male", "Female"])
    new_row['Category'] = st.selectbox("Category:", [
        "", "U 9", "U 11", "U 13",
        "U 15", "U 17", "U 19",
        "Open"])
    new_row['Training Centre'] = st.selectbox("Training Centre:", [
        "", "RCC Panjim", "RCC Mapusa", "Khelo India Centre Campal",
        "Salvador De Mundo", "Chicalim", "Don Boasco Oratory",
        "Panjim Gymkhana", "Gaspar Diass Miramar", "Other"
    ])

    st.write("Categories Participating in:")
    if new_row['Gender']:
        new_row['Singles'] = st.checkbox("Singles")
        new_row['Doubles'] = st.checkbox("Doubles")
        new_row['Mixed Doubles'] = st.checkbox("Mixed Doubles")

        new_row['Singles'] = "Singles" if new_row['Singles'] else "-"
        new_row['Doubles'] = "Doubles" if new_row['Doubles'] else "-"
        new_row['Mixed Doubles'] = "Mixed Doubles" if new_row['Mixed Doubles'] else "-"

    if new_row['Doubles'] == "Doubles":
        new_row['Doubles Partner'] = st.text_input("Name of Doubles Partner:")
        new_row['State ID Number of Doubles'] = st.text_input("State ID of Doubles Partner:")
        if new_row['State ID Number of Doubles'] and not validate_state_id_number(str(new_row['State ID Number of Doubles'])):
            st.error("Please enter a valid State ID Number for Doubles Partner.")
    else:
        new_row['Doubles Partner'] = "-"
        new_row['State ID Number of Doubles'] = "-"

    if new_row['Mixed Doubles'] == "Mixed Doubles":
        new_row['Mixed Doubles Partner'] = st.text_input("Name of Mixed Doubles Partner:")
        new_row['State ID Number of Mixed Doubles'] = st.text_input("State ID Number of Mixed Doubles")
        if new_row['State ID Number of Mixed Doubles'] and not validate_state_id_number(str(new_row['State ID Number of Mixed Doubles'])):
            st.error("Please enter a valid State ID Number for Mixed Doubles Partner.")
    else:
        new_row['Mixed Doubles Partner'] = "-"
        new_row['State ID Number of Mixed Doubles'] = "-"

    # Button to add the new row
    if st.button('Add Entry'):
        # Check if mandatory fields are filled
        if not new_row['Player Name'] or not new_row['State ID Number'] or not new_row['Mobile Number'] or not new_row['Gender'] or not new_row['Category'] or not new_row['Training Centre']:
            st.error("Please fill in all the mandatory fields.")
        elif not validate_mobile_number(new_row['Mobile Number']):
            st.error("Please enter a valid 10-digit mobile number.")
        elif not validate_state_id_number(new_row['State ID Number']):
            st.error("Please enter a valid State ID Number.")
        elif new_row['Doubles'] == "Doubles" and (not validate_state_id_number(str(new_row['State ID Number of Doubles']))):
            st.error("Please enter a valid State ID Number for Doubles Partner.")
        elif new_row['Mixed Doubles'] == "Mixed Doubles" and (not validate_state_id_number(str(new_row['State ID Number of Mixed Doubles']))):
            st.error("Please enter a valid State ID Number for Mixed Doubles Partner.")
        else:
            # Prepare data for submission
            category = new_row['Category']
            gender_mapping = {"Male": "Boys", "Female": "Girls"}
            gender = gender_mapping.get(new_row['Gender'], new_row['Gender'])

            sheet = client.open_by_url(GSHEET_URL)

            # Determine the new serial number
            def get_last_serial_number(worksheet, newly_created):
                if newly_created:
                    return 0
                records = worksheet.get_all_records()
                return int(records[-1]["Serial Number"]) if records else 0

            new_serial_number_singles = new_serial_number_doubles = new_serial_number_mixed_doubles = 0

            # For Singles
            if new_row['Singles'] == "Singles":
                worksheet_singles, new_singles_created = get_or_create_worksheet(sheet, f"{category} {gender} Singles")
                last_serial_number_singles = get_last_serial_number(worksheet_singles, new_singles_created)
                new_serial_number_singles = last_serial_number_singles + 1
                Singles_row = [
                    new_serial_number_singles,
                    new_row['Player Name'],
                    new_row['State ID Number'],
                    new_row['Mobile Number'],
                    new_row['Gender'],
                    new_row['Training Centre'],
                    new_row['Singles']
                ]
                add_row_to_google_sheet(Singles_row, worksheet_singles)

            # For Doubles
            if new_row['Doubles'] == "Doubles":
                worksheet_doubles, new_doubles_created = get_or_create_worksheet(sheet, f"{category} {gender} Doubles")
                last_serial_number_doubles = get_last_serial_number(worksheet_doubles, new_doubles_created)
                new_serial_number_doubles = last_serial_number_doubles + 1
                first_half_row = [
                    new_serial_number_doubles,
                    new_row['Player Name'],
                    new_row['State ID Number'],
                    new_row['Mobile Number'],
                    new_row['Gender'],
                    new_row['Training Centre'],
                    new_row['Doubles']
                ]
                second_half_row = [
                    new_serial_number_doubles,
                    new_row['Doubles Partner'],
                    new_row['State ID Number of Doubles'],
                    "",
                    new_row['Gender'],
                    new_row['Training Centre'],
                    new_row['Doubles']
                ]
                add_row_to_google_sheet(first_half_row, worksheet_doubles)
                add_row_to_google_sheet(second_half_row, worksheet_doubles)

            # For Mixed Doubles
            if new_row['Mixed Doubles'] == "Mixed Doubles":
                worksheet_mixed_doubles, new_mixed_doubles_created = get_or_create_worksheet(sheet, f"{category} Mixed Doubles")
                last_serial_number_mixed_doubles = get_last_serial_number(worksheet_mixed_doubles, new_mixed_doubles_created)
                new_serial_number_mixed_doubles = last_serial_number_mixed_doubles + 1

                first_half_row = [
                    new_serial_number_mixed_doubles,
                    new_row['Player Name'],
                    new_row['State ID Number'],
                    new_row['Mobile Number'],
                    new_row['Gender'],
                    new_row['Training Centre'],
                    new_row['Mixed Doubles']
                ]
                second_half_row = [
                    new_serial_number_mixed_doubles,
                    new_row['Mixed Doubles Partner'],
                    new_row['State ID Number of Mixed Doubles'],
                    "",
                    "Female" if gender == "Boys" else "Male",
                    new_row['Training Centre'],
                    new_row['Mixed Doubles']
                ]

                # Ensure female row comes after male row
                if first_half_row[4] == "Female":
                    first_half_row, second_half_row = second_half_row, first_half_row

                add_row_to_google_sheet(first_half_row, worksheet_mixed_doubles)
                add_row_to_google_sheet(second_half_row, worksheet_mixed_doubles)

            st.success("Submitted Successfully!")
             
             
            
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
