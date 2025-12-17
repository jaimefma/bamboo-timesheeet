import sys
import calendar
import os
import datetime

from dotenv import load_dotenv
from timesheet import BambooHRTimesheetClient
from tools import identify_first_day_of_period, days_to_clock


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
    