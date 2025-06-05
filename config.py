import os
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    raise ValueError("Error: GOOGLE_API_KEY environment variable not set. Please set it in your .env file.")

MODEL_NAME = 'gemini-1.5-flash'


MAPPING_CONFIG = {
    "jira": {
        "summary": "summary",
        "description": "suggested_action",
        "issuetype": "Task",
    },
    "servicenow": {
        "short_description": "summary",
        "description": "suggested_action",
        "urgency": {
            "Low": "3",
            "Medium": "2",
            "High": "1",
            "Critical": "1",    
        },
        "impact": "2", 
        "category": "inquiry",  
    }
}

SERVICENOW_INSTANCE = os.getenv('SERVICENOW_INSTANCE')
SERVICENOW_USERNAME = os.getenv('SERVICENOW_USERNAME')
SERVICENOW_PASSWORD = os.getenv('SERVICENOW_PASSWORD')
SERVICENOW_INCIDENT_TABLE = "incident"
SERVICENOW_SERVICE_REQUEST_TABLE = "sc_request"

if not all([SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD]):
    print("Warning: ServiceNow environment variables (SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD) not fully set. ServiceNow integration might not work.")