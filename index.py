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
    print(data)
    
    response = requests.post(create_url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Created page for {month_str}")
        return response.json()["id"]  # Return the ID of the newly created page
    else:
        print(f"Error creating page for {month_str}: {response.text}")
        return None

# Get the current month’s page ID (if it exists)
def get_current_month_page_id():
    current_month = datetime.datetime.now().strftime("%B")
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    query_data = {
        "filter": {
            "property": "title",
            "text": {
                "contains": current_month
            }
        }
    }
    
    response = requests.post(query_url, headers=headers, json=query_data)
    if response.status_code == 200:
        result = response.json()
        if result["results"]:
            return result["results"][0]["id"]  # Return the existing month's page ID
        else:
            print(f"No page found for {current_month}. Creating a new page...")
            return create_month_page(current_month)
    else:
        print(f"Error fetching current month page: {response.text}")
        return None

# Get the current day's page ID (if it exists)
def get_current_day_page_id(date_str, current_month_page_id):
    if not current_month_page_id:
        print("No current month page found.")
        return None
    
     # Query the blocks inside the current month's page (not a database)
    query_url = f"https://api.notion.com/v1/blocks/{current_month_page_id}/children"

    response = requests.get(query_url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(result)
        # Check for a block (sub-page) with the title that matches the date
        for block in result.get("results", []):
            # Check if the block is a sub-page and its title matches the date
            if block.get("type") == "child_page":
                title = block["child_page"]["title"]
                if date_str in title:  # Check if today's date is in the title
                    return block["id"]  # Return the ID of the sub-page with today's date

        # If no match found
        print(f"No page found for {date_str} inside the current month's page.")
        return None
    else:
        print(f"Error fetching blocks inside the current month page: {response.text}")
        return None

# This function retrieves the blocks from a template page (if you have a template page set up).
def get_template_blocks(template_page_id):
    url = f"https://api.notion.com/v1/blocks/{template_page_id}/children"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["results"]  # Return blocks of the template page
    else:
        print(f"Error fetching template blocks: {response.text}")
        return []

# Get unfinished tasks from yesterday's page (if any)
def get_unfinished_tasks(previous_day_page_id):
    url = f"https://api.notion.com/v1/blocks/{previous_day_page_id}/children"
    response = requests.get(url, headers=headers)
    
    unfinished_tasks = []
    if response.status_code == 200:
        blocks = response.json()["results"]
        # Loop through the blocks to find the tasks (assuming they are checkboxes)
        for block in blocks:
            if block["type"] == "to_do" and block["to_do"]["checked"] is False:
                unfinished_tasks.append(block)  # Add unfinished tasks to the list
    else:
        print(f"Error fetching unfinished tasks: {response.text}")
    return unfinished_tasks

# Create a new page for today (with unfinished tasks from yesterday)
def create_daily_page(date_str, parent_page_id, template_page_id, unfinished_tasks):
    create_url = "https://api.notion.com/v1/pages"
    
    # Step 1: Get blocks from the template page
    template_blocks = get_template_blocks(template_page_id)
    
    # Step 2: Create a new page with the specified date
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
        "children": template_blocks + unfinished_tasks  # Step 3: Add the blocks from the template to the new page
    }

    response = requests.post(create_url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Created page for {date_str}")
    else:
        print(f"Error creating page for {date_str}: {response.text}")

# Main function to run daily
def run_daily_task():
    # Get today's date and format it as "Wednesday, 25.04"
    today = datetime.date.today()
    date_str = today.strftime("%A, %d.%m")
    
    # Get the correct template based on the day of the week
    day_of_week = today.strftime("%A")
    template_id = TEMPLATES.get(day_of_week)  # Get the template ID for that day

    if template_id:
        # Check if today's page exists
        current_month_page_id = get_current_month_page_id()
        if not current_month_page_id:
            print("Failed to create or find the current month page.")
            return

        current_day_page_id = get_current_day_page_id(date_str, current_month_page_id)
        
        if current_day_page_id:
            print(f"Page for {date_str} already exists. Adding unfinished tasks from previous day...")
        else:
            print(f"No page found for {date_str}. Creating a new page...")

        # Get yesterday's page ID, regardless of whether today's page exists or not
        yesterday = today - datetime.timedelta(days=1)
        yesterday_page_id = get_current_day_page_id(yesterday.strftime("%A, %d.%m"), current_month_page_id)
        
        if yesterday_page_id:
            # Get unfinished tasks from yesterday's page
            unfinished_tasks = get_unfinished_tasks(yesterday_page_id)
        else:
            print(f"Error: Could not find {yesterday.strftime('%A, %d.%m')} page.")
            unfinished_tasks = []

        # Create the page for today, whether it existed or not, and add unfinished tasks
        create_daily_page(date_str, current_month_page_id, template_id, unfinished_tasks)
    else:
        print(f"No template found for {day_of_week}")
# Run the script (this would be scheduled to run once per day)
run_daily_task()
