Notion Scheduler Automation
===========================

Table of Contents
-----------------

- [Notion Scheduler Automation](#notion-scheduler-automation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
    - [Running Locally](#running-locally)
  - [Deployment](#deployment)
    - [Google Cloud Functions](#google-cloud-functions)
    - [Google Cloud Scheduler](#google-cloud-scheduler)
  - [Environment Variables](#environment-variables)
    - [Example .env File:](#example-env-file)
  - [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)

Overview
--------

The **Notion Scheduler Automation** is a Python script designed to automate the process of creating daily pages within a Notion database. It pulls templates for each day of the week, checks if a page exists for the current month, and creates daily pages for every day of the month. This can be useful for productivity tools or daily tracking workflows.

Features
--------

*   Automatically creates daily pages in a Notion database.
*   Uses template pages to maintain consistent structure.
*   Creates pages for the next month if it's the 28th of the current month.
*   Integrates with Google Cloud Functions for serverless execution.
*   Uses Google Cloud Scheduler to automate the execution of the script every month.

Getting Started
---------------

### Prerequisites

Before you can run the project, ensure you have the following prerequisites installed:

*   **Python 3.8 or later**
*   **pip** (Python's package installer)
*   **Google Cloud SDK** (if deploying to Google Cloud)

### Installation

Clone the repository:

    git clone https://github.com/yourusername/notion-scheduler-automation.git
    cd notion-scheduler-automation

Install dependencies: Ensure you have all required Python packages:

    pip install -r requirements.txt

Usage
-----

### Running Locally

You can run the script locally by executing:

    python index.py

Make sure you have set the required environment variables as specified below.

Deployment
----------

### Google Cloud Functions

This project can be deployed as a serverless function on Google Cloud Functions.

Deploy the function: To deploy the function, use the following command in your terminal (after making sure you've set the proper environment variables):

    gcloud functions deploy notion_schedule \
      --runtime python39 \
      --trigger-http \
      --allow-unauthenticated \
      --region us-central1 \
      --set-env-vars NOTION_API_TOKEN="your-notion-api-token",DATABASE_ID="your-database-id",SCHEDULE_PAGE_ID="your-schedule-page-id"

### Google Cloud Scheduler

To run the function automatically every 28th of the month, use Google Cloud Scheduler to set up a cron job:

Create a new job: Go to Google Cloud Scheduler in the Google Cloud Console and set the following cron expression:

    0 12 28 * *

This cron job will trigger the function at 12:00 PM UTC on the 28th of every month.

Set the job to target the HTTP trigger:

*   **Target:** HTTP
*   **URL:** URL of your deployed Google Cloud Function
*   **HTTP Method:** POST

Environment Variables
---------------------

The following environment variables need to be set in your Google Cloud Function (or locally) to run the script properly:

*   **NOTION\_API\_TOKEN**: Your Notion API token.
*   **DATABASE\_ID**: The ID of your Notion database where monthly pages are stored.
*   **SCHEDULE\_PAGE\_ID**: The ID of the Notion page where the schedule is stored.

### Example .env File:

    NOTION_API_TOKEN="your-notion-api-token"
    DATABASE_ID="your-database-id"
    SCHEDULE_PAGE_ID="your-schedule-page-id"

Contributing
------------

We welcome contributions to improve the functionality of this project! Please feel free to fork the repository, create a branch, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

License
-------

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Contact
-------

For any questions or issues, please reach out to [deniscercasin@gmail.com](mailto:deniscercasin@gmail.com).