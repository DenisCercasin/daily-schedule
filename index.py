import requests
import datetime
import os

# Notion API token and database IDs
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")  # The database where monthly pages are stored
SCHEDULE_PAGE_ID = os.getenv("SCHEDULE_PAGE_ID")

# Template IDs for each day of the week (Monday to Sunday)
TEMPLATES = {
    "Monday": "1e15d82c8445802fa1addf55d3291e2c",
    "Tuesday": "1e15d82c8445809aab59e5d7d9baace3",
    "Wednesday": "1e15d82c84458082addee96c5f72a3a4",
    "Thursday": "1e15d82c844580a1870ec61a85085215",
    "Friday": "1e15d82c84458041a6aedbae5c02d98f",
    "Saturday": "1e15d82c84458062a1bbc76674b55253",
    "Sunday": "1e15d82c84458089a958c05447de7a7e"
}

# Define headers for API requests
headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2021-05-13"  # Make sure this version is up-to-date
}

# Create a new page for the current month
def create_month_page(month_str):
    create_url = "https://api.notion.com/v1/pages"
    
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "title": [
                {
                    "type": "text",
                    "text": {"content": month_str}
                }
            ]
        }
    }
    
    response = requests.post(create_url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["id"]  # Return the ID of the newly created page
    else:
        print(f"Error creating page for {month_str}: {response.text}")
        return None

# Get the next month's page ID (if it exists)
def get_next_month_page_id():
    # Get the current date and increment the month to get next month's name
    today = datetime.date.today()
    next_month = today.replace(month=(today.month % 12) + 1)
    next_month_name = next_month.strftime("%B")

    # Query the database to find if the page for next month exists
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    query_data = {
        "filter": {
            "property": "title",
            "text": {
                "contains": next_month_name
            }
        }
    }
    
    response = requests.post(query_url, headers=headers, json=query_data)
    if response.status_code == 200:
        result = response.json()
        if result["results"]:
            return result["results"][0]["id"]  # Return the existing month's page ID
        else:
            print(f"No page found for {next_month_name}. Creating a new page...")
            return create_month_page(next_month_name)
    else:
        print(f"Error fetching next month's page: {response.text}")
        return None

# Get the template blocks for the specified day
def get_template_blocks(template_page_id):
    url = f"https://api.notion.com/v1/blocks/{template_page_id}/children"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["results"]  # Return blocks of the template page
    else:
        print(f"Error fetching template blocks: {response.text}")
        return []

# Create a new page for a specific date
def create_daily_page(date_str, parent_page_id, template_page_id):
    create_url = "https://api.notion.com/v1/pages"
    
    # Get blocks from the template page
    template_blocks = get_template_blocks(template_page_id)
    
    # Create a new page with the specified date
    data = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": [
                {
                    "type": "text",
                    "text": {"content": date_str}
                }
            ]
        },
        "children": template_blocks  # Add the blocks from the template to the new page
    }

    response = requests.post(create_url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Created page for {date_str}")
    else:
        print(f"Error creating page for {date_str}: {response.text}")

# Main function to create pages for the entire next month on the 28th of each month
def create_month_pages():
    today = datetime.date.today()
    
    
        
     # Get the next month's page ID
    next_month_page_id = get_next_month_page_id()
    if not next_month_page_id:
        print("Failed to create or find the next month page.")
        return

    # Get the correct template based on the day of the week
    for day in range(1, 32):  # Loop through days of the next month
        try:
                date = datetime.date(today.year, today.month + 1, day)
                date_str = date.strftime("%A, %d.%m")
                
                # Get the correct template based on the day of the week
                day_of_week = date.strftime("%A")  # Get the name of the day (e.g., "Monday")
                template_id = TEMPLATES.get(day_of_week)  # Get the template ID for that day
                
                if template_id:
                    create_daily_page(date_str, next_month_page_id, template_id)
                else:
                    print(f"No template found for {day_of_week}")
                
        except ValueError:
                # Skip invalid dates (e.g., 30th in a month with only 29 days)
            continue

    else:
        print("Today is not the 28th, skipping the creation of pages for the next month.")

# Run the task to create pages for the next month on the 28th of the current month
create_month_pages()
