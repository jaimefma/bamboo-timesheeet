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

from tools import identify_first_day_of_period, days_to_clock


class BambooHRTimesheetClient:
    """
    Client for interacting with BambooHR API to manage timesheet entries.
    """
    
    def __init__(self, employee_id: str, api_key: str, api_base_url: str):
        """
        Initialize the BambooHR Timesheet Client.
        
        Args:
            employee_id: BambooHR employee ID.
            api_key: BambooHR API key.
            api_base_url: Base URL for BambooHR API. 
        """
        self.employee_id = employee_id
        self.api_key = api_key
        self.api_base_url = api_base_url

    def is_off_day(self, date: datetime.date) -> bool:
        """
        Check if the given date is an off day (time off request).
    
        Returns:
            bool: True if the date is an approved off day, False otherwise
        """
        url = f'{self.api_base_url}/time_off/requests'
        params = {
            'employeeId': self.employee_id,
            'start': date.strftime('%Y-%m-%d'),
            'end': date.strftime('%Y-%m-%d')
        }
        try:
            response = requests.get(
                url,
                params=params,
                auth=(self.api_key, 'x'),
                headers={'Accept': 'application/json'}
            )   
        except requests.exceptions.RequestException as e:
            print(f"Warning: Error checking existing entries: {e}")
            return False
        
        if response and response.status_code == 200:
            off_day_info = response.json()
            # TODO manage multiple entries. It's very unlikely but possible.
            if len(off_day_info) == 1 and off_day_info[0]['status']['status'] == 'approved':
                off_day_info = off_day_info[0]
                print(f"There is an entry of {off_day_info['amount']['amount']} {off_day_info['amount']['unit']} for {off_day_info['type']['name']}")
                return True
            elif len(off_day_info) > 1:
                # TODO manage multiple entries. It's very unlikely but possible.
                print('Sorry, I cannot manage multiple entries. Please check the BambooHR website.')
                return True
        return False

    def get_existing_entries(self, date: datetime.date) -> list:
        """
        Check if there are existing clock entries for the given date.
        
        Args:
            date: datetime.date object representing the date to check
            
        Returns:
            list: List of existing entries for the date, empty if none exist
        """
        date_str = date.strftime('%Y-%m-%d')
        url = f'{self.api_base_url}/time_tracking/timesheet_entries'
        
        # Parameters to filter by employee and date
        params = {
            'employeeIds': self.employee_id,
            'start': date_str,
            'end': date_str
        }
        
        try:
            response = requests.get(
                url,
                params=params,
                auth=(self.api_key, 'x')
            )   
        except requests.exceptions.RequestException as e:
            print(f"Warning: Error checking existing entries: {e}")
            return {}
        else:
            if response.status_code == 200:
                return response.json()
                # Return the entries if they exist
            else:
                print(f"Warning: Could not retrieve existing entries. Status: {response.status_code}")
                return {}

    def clock_day(self, date: datetime.date):
        """
        Register a clock in/out time entry for the given date and time.

        Args:
            date: datetime.date object representing the date of the entry
        """
        print(f"⏰ Clocking for {date}")
        # Define the request payload
        date_str = date.strftime('%Y-%m-%d')
        payload = {
            "entries":[
                {
                    "employeeId": self.employee_id,
                    "date": date_str,
                    "start": "08:00",
                    "end": "13:00",
                },
                {
                    "employeeId": self.employee_id,
                    "date": date_str,
                    "start": "14:00",
                    "end": "17:00",
                }
            ]
        }
        # TODO check there is no entry for that day
        
        if self.get_existing_entries(date):
            print(f"... ❌ CANCELLED because of existing entries")
        elif self.is_off_day(date): 
            print(f"... ❌ CANCELLED because of off day")
        else:
            # Make the API request    
            url = f'{self.api_base_url}/time_tracking/clock_entries/store'
            try:
                response = requests.post(
                    url, 
                    json=payload,
                    auth=(self.api_key, 'x'))
                
                if response.status_code in [200, 201]:
                    print("... ✅ Done")
                
                else:
                    print(f"Request failed with status code: {response.status_code}")
                    print("Response:", response.text)
                    
            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")



if __name__ == "__main__":

    load_dotenv()

    employee_id = os.getenv('BAMBOO_EMPLOYEE_ID')
    api_key = os.getenv("BAMBOO_API_KEY")
    api_base_url = 'https://backbase.bamboohr.com/api/v1'

    if not employee_id:
        print("Error: BAMBOO_EMPLOYEE_ID environment variable is not set.")
        print("Please set it in your .env file or environment.")
        sys.exit(1)

    if not api_key:
        print("Error: BAMBOO_API_KEY environment variable is not set.")
        print("Please set it in your .env file or environment.")
        sys.exit(1)
    
    # Initialize the client
    client = BambooHRTimesheetClient(employee_id, api_key, api_base_url)
    
    # Check command line arguments
    start_date = None
    last_day = None
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

    print("=" * 70)
    print("⚠️  WARNING: This is a BETA script")
    print("=" * 70)
    print("You are responsible for verifying that all information is properly")
    print("logged into BambooHR. Please check your timesheet entries after")
    print("running this script to ensure accuracy.")
    print("=" * 70)
    print()
    print(f"Timesheet for {start_date} to {end_date} is about to be submitted")
    input("Press Enter to continue...")

    for day in days_to_clock(start_date, end_date):
        client.clock_day(day)
    