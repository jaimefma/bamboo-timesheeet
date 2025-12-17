#!/usr/bin/env python3
"""
Utility functions for timesheet management.
"""

import datetime


def identify_first_day_of_period() -> datetime.date:
    """
    Identify the first day of the period to register the timesheet. 
    This usually happens by the end of it or the beginning of the following one.
    
    Returns:
        datetime.date: The first day of the timesheet period
    """
    # Usually it fits with the current month
    now = datetime.datetime.now()
    timesheet_month = now.month
    # If this is run at the beginning of the month, it will be the previous month
    if now.day < 10:
        if timesheet_month == 1:
            return datetime.date(now.year - 1, 12, 1) # December of previous year
        return datetime.date(now.year, timesheet_month - 1, 1) # Previous month
    return datetime.date(now.year, timesheet_month, 1) # Current month


def days_to_clock(start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
    """
    Generate a list of dates between start_date and end_date, both inclusive, excluding weekends.
    TODO holidays and public holidays.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        
    Returns:
        list[datetime.date]: List of workdays between the dates
    """
    days = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:
            days.append(current_date)
        current_date += datetime.timedelta(days=1)
    return days

