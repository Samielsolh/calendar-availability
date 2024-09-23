import requests
from datetime import datetime, timedelta
import pytz
import streamlit as st

# Set the title of the web app
st.title("Check Your Availability")

# Get query parameters from the URL
query_params = st.experimental_get_query_params()
default_username = query_params.get("username", ["samielsolh"])[0]
default_event_type_id = query_params.get("event_type_id", ["1027409"])[0]
default_api_key = query_params.get("api_key", [""])[0]

# Input for username, event ID, and API key (from URL if available)
username = st.text_input("Enter your Cal.com username", default_username)
event_type_id = st.text_input("Enter Event Type ID", default_event_type_id)
api_key = st.text_input("Enter API Key", type="password", value=default_api_key)

# Get the current date and time, and the date and time 7 days from now
start_datetime = datetime.now(pytz.UTC)
end_datetime = start_datetime + timedelta(days=7)

# Button to trigger API call
if st.button("Check Availability"):
    # Format dates for the API request (using ISO 8601 format)
    start_datetime_str = start_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
    end_datetime_str = end_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Set up the request
    base_url = "https://api.cal.com/v1"
    url = f"{base_url}/availability"
    params = {
        "apiKey": api_key,
        "eventTypeId": event_type_id,
        "dateFrom": start_datetime_str,
        "dateTo": end_datetime_str,
        "username": username
    }

    headers = {"Content-Type": "application/json"}

    # Display some debugging information
    st.write(f"Making request to URL: {url}")
    st.write(f"Params: {params}")

    # Make the API request
    response = requests.get(url, params=params, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        availability_data = response.json()
        
        # Extract timezone and busy times
        timezone_str = availability_data.get('timeZone', 'UTC')
        timezone = pytz.timezone(timezone_str)
        busy_times = availability_data.get('busy', [])
        
        # Convert busy times to timezone-aware datetime objects
        busy_periods = [(datetime.fromisoformat(period['start'].replace('Z', '+00:00')).astimezone(timezone),
                         datetime.fromisoformat(period['end'].replace('Z', '+00:00')).astimezone(timezone))
                        for period in busy_times]

        # Define the start and end time for the availability window
        day_start_time = datetime.strptime("10:00:00", "%H:%M:%S").time()  # 10 AM
        day_end_time = datetime.strptime("20:00:00", "%H:%M:%S").time()  # 8 PM

        current_date = start_datetime.astimezone(timezone).date()
        end_date = end_datetime.astimezone(timezone).date()

        # Display the availability
        st.write(f"Your availability for the next 7 days (Timezone: {timezone_str}):")

        while current_date <= end_date:
            day_start = timezone.localize(datetime.combine(current_date, day_start_time))
            day_end = timezone.localize(datetime.combine(current_date, day_end_time))
            
            available_slots = []
            current_time = day_start
            
            while current_time < day_end:
                slot_end = current_time + timedelta(minutes=30)  # Assuming 30-minute slots
                is_busy = any(start <= current_time < end for start, end in busy_periods)
                
                if not is_busy:
                    available_slots.append(current_time.strftime("%I:%M %p"))
                
                current_time = slot_end

            # Format and display slots for the day
            if available_slots:
                time_ranges = []
                start_slot = available_slots[0]
                end_slot = available_slots[0]
                
                for i in range(1, len(available_slots)):
                    current_time = datetime.strptime(available_slots[i], "%I:%M %p")
                    previous_time = datetime.strptime(end_slot, "%I:%M %p")
                    if current_time == previous_time + timedelta(minutes=30):
                        end_slot = available_slots[i]
                    else:
                        time_ranges.append(f"{start_slot} - {end_slot}" if start_slot != end_slot else start_slot)
                        start_slot = available_slots[i]
                        end_slot = available_slots[i]
                
                time_ranges.append(f"{start_slot} - {end_slot}" if start_slot != end_slot else start_slot)

                # Format the date
                day_name = current_date.strftime("%A")
                date_str = current_date.strftime("%b %d")
                st.write(f"{day_name}, {date_str}: {', '.join(time_ranges)}")
            else:
                st.write(f"{current_date.strftime('%A')}, {current_date.strftime('%b %d')}: No available slots")
            
            current_date += timedelta(days=1)
    else:
        st.error(f"Failed to fetch availability. Status code: {response.status_code}")
        st.error(f"Response: {response.text[:500]}")

