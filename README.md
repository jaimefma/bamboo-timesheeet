# BambooHR Timesheet Automation

A Python script to automatically submit timesheet entries to BambooHR via their API.

## Features

- 🕐 Automatically registers 8 hours per working day (08:00-13:00, 14:00-17:00)
- 📅 Processes date ranges with smart month detection
- 🚫 Skips weekends automatically
- 🏖️ Skips days with approved time-off requests
- ✅ Prevents duplicate entries (checks for existing timesheets)
- 🔒 Secure API authentication using environment variables

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- BambooHR account with API access
- Your employee ID and API key from BambooHR

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd bamboo-timesheeet
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp env.template .env
   ```
   
   Edit `.env` and add your credentials:
   ```bash
   BAMBOO_EMPLOYEE_ID=your_employee_id
   BAMBOO_API_KEY=your_api_key
   ```

### Getting Your BambooHR Credentials

**Employee ID:**
- Check your BambooHR profile URL: `https://company.bamboohr.com/employees/employee.php?id=XXXX`
- Ask your HR administrator

**API Key:**
1. Log in to BambooHR
2. Click your name in the lower left corner
3. Select "API Keys"
4. Click "Generate new key"
5. Copy the generated key to your `.env` file

## Usage

The script supports two modes:

### 1. Current/Previous Month (Auto-detect)

Automatically determines the period:
- If run before day 10 of the month → fills previous month
- If run on/after day 10 → fills current month

```bash
uv run timesheet.py <last_day>
```

**Examples:**
```bash
# Fill from month start to the 22nd
uv run timesheet.py 22

# Fill entire month (from 1st to last day of month)
uv run timesheet.py 31
```

### 2. Custom Date Range

Specify both the last day and a custom start date:

```bash
uv run timesheet.py <last_day> <start_date>
```

**Examples:**
```bash
# Fill from January 15 to January 22, 2025
uv run timesheet.py 22 15-01-2025

# Fill from November 1 to November 30, 2025
uv run timesheet.py 30 01-11-2025
```

**Date format:** `DD-MM-YYYY`

## How It Works

For each working day in the specified range:

1. ✅ Checks if the day is a weekend (skips Saturdays and Sundays)
2. ✅ Checks if there are existing timesheet entries (skips if found)
3. ✅ Checks if there's an approved time-off request (skips if found)
4. ✅ Creates two clock entries:
   - **Morning:** 08:00 - 13:00 (5 hours)
   - **Afternoon:** 14:00 - 17:00 (3 hours)
   - **Total:** 8 hours per day

## Output Example

```
Timesheet for 2025-11-01 to 2025-11-22 is about to be submitted
Press Enter to continue...
⏰ Clocking for 2025-11-03
... ✅ Done
⏰ Clocking for 2025-11-04
... ✅ Done
⏰ Clocking for 2025-11-05
... ❌ CANCELLED because of existing entries
⏰ Clocking for 2025-11-06
... ❌ CANCELLED because of off day
```

## Configuration

The script uses the following BambooHR API endpoints:
- Time tracking entries: `/api/v1/time_tracking/timesheet_entries`
- Clock entries: `/api/v1/time_tracking/clock_entries/store`
- Time off requests: `/api/v1/time_off/requests`

Default time entries (hardcoded in script):
- Morning shift: 08:00 - 13:00
- Afternoon shift: 14:00 - 17:00

To modify these times, edit the `clock_day()` function in `timesheet.py`.

## Requirements

- Python 3.13+
- `requests>=2.25.0` - HTTP library for API calls
- `dotenv>=0.9.9` - Environment variable management
- Valid BambooHR account with API access

## Notes

- The script requires a confirmation (press Enter) before submitting entries
- Weekends are automatically excluded
- Days with existing entries are skipped to prevent duplicates
- Days with approved time-off are automatically skipped
- All times are submitted in 24-hour format

## Troubleshooting

**"No module named 'dotenv'"**
```bash
uv sync
```

**"Error making request: 401 Unauthorized"**
- Verify your `BAMBOO_API_KEY` is correct in `.env`
- Generate a new API key if needed

**"Warning: Could not retrieve existing entries"**
- Check your `BAMBOO_EMPLOYEE_ID` is correct
- Verify your API key has the necessary permissions

## License

MIT