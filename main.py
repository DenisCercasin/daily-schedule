import os
import datetime
from index import create_month_pages  # Import your main logic from index.py

# Google Cloud Function entry point
def notion_schedule(request):
    try:
        # Run the daily task logic
        create_month_pages()
        return "Notion schedule task executed successfully", 200
    except Exception as e:
        return f"Error executing the task: {str(e)}", 500
