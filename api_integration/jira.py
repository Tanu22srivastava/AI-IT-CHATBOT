import os
import requests
from requests.auth import HTTPBasicAuth
from config import MAPPING_CONFIG

def create_jira_ticket(data):
    """Creates a ticket in Jira."""
    jira_email = os.getenv('JIRA_EMAIL')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    jira_base_url = os.getenv('JIRA_BASE_URL')
    jira_project_key = os.getenv('JIRA_PROJECT_KEY')

    if not all([jira_email, jira_api_token, jira_base_url, jira_project_key]):
        print("Jira credentials or project key not fully configured. Cannot create Jira ticket.")
        return None

    url = f"{jira_base_url}/rest/api/3/issue"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Jira's description field uses Atlassian Document Format (ADF)
    description_adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": data.get("suggested_action", "No suggested action provided.")
                    }
                ]
            }
        ]
    }

    payload = {
        "fields": {
            "project": {"key": jira_project_key},
            "summary": data.get("summary", "New IT Issue"),
            "description": description_adf,
            "issuetype": {"name": MAPPING_CONFIG["jira"]["issuetype"]} # e.g., "Task", "Bug", "Story"
        }
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            auth=HTTPBasicAuth(jira_email, jira_api_token),
            json=payload
        )
        response.raise_for_status()

        if response.status_code == 201:
            print("Ticket created successfully in Jira")
            print("Issue Key:", response.json()['key'])
            return response.json()
        else:
            print("Failed to create ticket in Jira (unexpected status).")
            print("Status code:", response.status_code)
            print("Response:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error creating Jira ticket: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Jira response: {e.response.text}")
        return None