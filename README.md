# BambooHR Scripts

This repository contains Python scripts for interacting with BambooHR APIs.

## Scripts

### 1. Timesheet Management (`timesheet.py`)

Submits timesheet entries to BambooHR, converted from the original bash script.

#### Usage:
```bash
python timesheet.py <csrf-token> <month> <day>
```

**Parameters:**
- `csrf-token`: The CSRF token from your BambooHR session
- `month`: Month number (1-12)  
- `day`: Day number (1-31)

**Example:**
```bash
python timesheet.py "your-csrf-token-here" 6 30
```

### 2. Direct Reports Finder (`bamboo_direct_reports.py`)

Connects to BambooHR API to retrieve all employees who report to a given individual, including their full name, title, and photo.

#### Usage:
```bash
python bamboo_direct_reports.py <company_domain> <api_key> <manager_name>
```

**Parameters:**
- `company_domain`: Your BambooHR company subdomain (e.g., if you access BambooHR at `https://yourcompany.bamboohr.com`, use `yourcompany`)
- `api_key`: Your BambooHR API key (generate from your user menu → API Keys)
- `manager_name`: Full name of the manager as it appears in BambooHR (e.g., "John Smith")

**Example:**
```bash
python bamboo_direct_reports.py "mycompany" "your-api-key-here" "John Smith"
```

#### Features:
- Fetches all employees who directly report to the specified manager
- Retrieves full name, job title, and photo for each direct report
- Saves photos to individual files (optional)
- Exports results to JSON file
- Handles employees without photos gracefully

#### Output:
- Console output showing all direct reports with their information
- JSON file: `direct_reports_<manager_name>.json` with structured data
- Photo files: `photos/` directory with individual employee photos (if requested)

#### Getting Your API Key:
1. Log in to BambooHR
2. Click your name in the lower left corner
3. Select "API Keys" from the menu
4. Generate a new API key

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make scripts executable (optional):
   ```bash
   chmod +x timesheet.py
   chmod +x bamboo_direct_reports.py
   ```

## Requirements

- Python 3.6+
- `requests` library
- Valid BambooHR account and API access

## Notes

- **Timesheet Script**: The script is hardcoded for employee ID 5707 and year 2025. You may need to update cookie values if your session expires.
- **Direct Reports Script**: Requires an API key with permission to view employee data and photos. The script only returns active employees.
- Both scripts include proper error handling and informative output.
