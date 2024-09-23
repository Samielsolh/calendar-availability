import streamlit as st
import requests
from datetime import datetime

# Function to fetch availability from Cal.com API
def fetch_availability(api_key, start_date, end_date):
    url = "https://api.cal.com/v1/availability"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Format the start and end dates to ISO format
    params = {
        "start": start_date.isoformat(),
        "end": end_date.isoformat()
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return None

# Streamlit UI
st.title("Cal.com Availability Checker")

# Input for API key
api_key = st.text_input("Enter your Cal.com API Key", type="password")

# Date input for availability
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

# Button to trigger the fetch
if st.button("Fetch Availability"):
    if api_key and start_date and end_date:
        st.write("Fetching availability...")
        availability = fetch_availability(api_key, start_date, end_date)
        
        if availability:
            # Extract and display availability in text format
            available_times = availability.get("available_times", [])
            if available_times:
                st.write("Available times:")
                for time_slot in available_times:
                    time = datetime.fromisoformat(time_slot.replace("Z", "+00:00"))
                    st.write(time.strftime("%A, %B %d, %Y at %I:%M %p"))
            else:
                st.write("No availability found for the selected dates.")
    else:
        st.error("Please provide an API key and select valid dates.")
