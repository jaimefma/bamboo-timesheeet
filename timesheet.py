#!/usr/bin/env python3
"""
Python script to submit timesheet entries to BambooHR.
Actions

"""
import datetime
import requests


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
            if len(off_day_info) == 1 and off_day_info[0]['status']['status'] == 'approved':
                off_day_info = off_day_info[0]
                print(f"There is an entry of {off_day_info['amount']['amount']} {off_day_info['amount']['unit']} for {off_day_info['type']['name']}")
                return True
            elif len(off_day_info) > 1:
                # TODO manage multiple entries. It's very unlikely but possible.
                print('Sorry, I cannot manage multiple entries. Please check the BambooHR website.')
                return True
        return False

    def is_holiday(self, date: datetime.date) -> bool:
        """
        Check if the given date is a holiday.
        """
        url = f'{self.api_base_url}/time_off/whos_out'
        params = {
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
        else:
            whose_out = response.json()
            holiday = [i for i in whose_out if i['type'] == 'holiday']
            if holiday:
                return True
        return False

    def get_existing_entries(self, from_date: datetime.date, to_date: datetime.date) -> list:
        """
        Check if there are existing clock entries for the given date.
        
        Args:
            date: datetime.date object representing the date to check
            
        Returns:
            list: List of existing entries for the date, empty if none exist
        """
        url = f'{self.api_base_url}/time_tracking/timesheet_entries'
        
        # Parameters to filter by employee and date
        params = {
            'employeeIds': self.employee_id,
            'start': from_date.strftime('%Y-%m-%d'),
            'end': to_date.strftime('%Y-%m-%d')
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
        if self.get_existing_entries(date, date):
            print(f"... ❌ CANCELLED because of existing entries")
        elif self.is_off_day(date): 
            print(f"... ❌ CANCELLED because you have a day off approved")
        elif self.is_holiday(date):
            print(f"... ℹ️ skipped because it's a holiday")
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
        
    def remove_entries(self, from_date: datetime.date, to_date: datetime.date):
        """
        Remove the entries for the given date range.
        """   
        entry_ids = [i['id'] for i in self.get_existing_entries(from_date, to_date)]

        if entry_ids:
            print(f"Removing {len(entry_ids)} clock entries for {from_date} to {to_date}")
            url = f'{self.api_base_url}/time_tracking/clock_entries/delete'
            payload = {
                "clockEntryIds": entry_ids
            }
            import pprint; pprint.pprint(url)
            try:
                response = requests.post(url, json=payload, auth=(self.api_key, 'x'))
            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
            else:
                if response.status_code == 204:
                    print(f"✅ Done. {len(entry_ids)} entries removed.")
                else:
                    print(f"Request failed with status code: {response.status_code}")
                    print("Response:", response.text)