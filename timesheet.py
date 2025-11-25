#!/usr/bin/env python3
"""
Python script to submit timesheet entries to BambooHR.
Actions

"""

import calendar
import datetime
import json
import os
import requests
import sys

from dotenv import load_dotenv


load_dotenv()

BAMBOO_EMPLOYEE_ID = os.getenv('BAMBOO_EMPLOYEE_ID')
BAMBOO_API_KEY = os.getenv("BAMBOO_API_KEY")
BAMBOO_API_BASE_URL = 'https://backbase.bamboohr.com/api/v1'

def was_off_day(date: datetime.date) -> list:
    """
    Get the off days for the given date.
    """
    url = f'{BAMBOO_API_BASE_URL}/time_off/requests'
    params = {
        'employeeId': BAMBOO_EMPLOYEE_ID,
        'start': date.strftime('%Y-%m-%d'),
        'end': date.strftime('%Y-%m-%d')
    }
    try:
        response = requests.get(
            url,
            params=params,
            auth=(BAMBOO_API_KEY, 'x'),
            headers={'Accept': 'application/json'}
        )   
    except requests.exceptions.RequestException as e:
        print(f"Warning: Error checking existing entries: {e}")
        return []
    if response.status_code == 200 and response:
        off_day_info = response.json()
        if len(off_day_info) > 0:
            off_day_info = off_day_info[0]['amount']
            print(f"There is an off details: {off_day_info['amount']} {off_day_info['unit']}")
            return True
    return False


def get_existing_entries(date: datetime.date) -> list:
    """
    Check if there are existing clock entries for the given date.
    
    Args:
        date: datetime.date object representing the date to check
        
    Returns:
        list: List of existing entries for the date, empty if none exist
    """
    date_str = date.strftime('%Y-%m-%d')
    url = f'{BAMBOO_API_BASE_URL}/time_tracking/timesheet_entries'
    
    # Parameters to filter by employee and date
    params = {
        'employeeIds': BAMBOO_EMPLOYEE_ID,
        'start': date_str,
        'end': date_str
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            auth=(BAMBOO_API_KEY, 'x')
        )   
    except requests.exceptions.RequestException as e:
        print(f"Warning: Error checking existing entries: {e}")
        return []
    else:
        if response.status_code == 200:
            return response.json()
            # Return the entries if they exist
        else:
            print(f"Warning: Could not retrieve existing entries. Status: {response.status_code}")
            return []


def clock_day(date: datetime.date):
    """
    Register a clock in/out time entry for the given date and time.

    Args:
        date: datetime.date object representing the date of the entry
        start_time: str representing the start time of the entry in HH:MM format
        end_time: str representing the end time of the entry in HH:MM format
        
    """
    print(f"⏰ Clocking for {date}")
    # Define the request payload
    date_str = date.strftime('%Y-%m-%d')
    payload = {
        "entries":[
            {
                "employeeId": BAMBOO_EMPLOYEE_ID,
                "date": date_str,
                "start": "08:00",
                "end": "13:00",
            },
            {
                "employeeId": BAMBOO_EMPLOYEE_ID,
                "date": date_str,
                "start": "14:00",
                "end": "17:00",
            }
        ]
    }
    # TODO check there is no entry for that day
    
    if get_existing_entries(date):
        print(f"... ❌ CANCELLED because of existing entries")
    elif was_off_day(date): 
        print(f"... ❌ CANCELLED because of off day")
    else:
        # Make the API request    
        url = f'{BAMBOO_API_BASE_URL}/time_tracking/clock_entries/store'
        try:
            response = requests.post(
                url, 
                json=payload,
                auth=(BAMBOO_API_KEY, 'x'))
            
            if response.status_code in [200, 201]:
                print("... ✅ Done")
            
            else:
                print(f"Request failed with status code: {response.status_code}")
                print("Response:", response.text)
                
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            sys.exit(1)


def identify_first_day_of_period():
    """
    Identify the first day of the period to register the timesheet. This isually happens by the end of it or the begining of the following one    
    """
    # Usually it fits with the current month
    now = datetime.datetime.now()
    timesheet_month = now.month
    # If this is run at the begining of the month, it will be the previous month
    if now.day < 10:
        if timesheet_month == 1:
            return datetime.date(now.year - 1, 12, 1) # December of previous year
        return datetime.date(now.year, timesheet_month - 1, 1) # Previous month
    return datetime.date(now.year, timesheet_month, 1) # Current month


def days_to_clock(start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
    """
    Generate a list of dates between start_date and end_date, both inclusive, excluding weekends,
    TODO holidays and public holidays.
    """
    days = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:
            days.append(current_date)
        current_date += datetime.timedelta(days=1)
    return days

if __name__ == "__main__":
    # Check command line arguments
    start_date = None
    num_params = len(sys.argv)
    if num_params >= 2:
        last_day = int(sys.argv[1])
        start_date = identify_first_day_of_period()
    
    if num_params == 3:
        start_date = datetime.datetime.strptime(sys.argv[2], '%d-%m-%Y').date()

    if not start_date:
        print(f"Usage: {sys.argv[0]} <last day int> [first day i.e. 22-1-2025]")
        sys.exit(1)
    
    if last_day:
        end_date = datetime.date(start_date.year, start_date.month, last_day)
    else:
        last_day_of_month = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = datetime.date(start_date.year, start_date.month, last_day_of_month)

    print(f"Timesheet for {start_date} to {end_date} is about to be submitted")
    input("Press Enter to continue...")

    for day in days_to_clock(start_date, end_date):
        clock_day(day)
    