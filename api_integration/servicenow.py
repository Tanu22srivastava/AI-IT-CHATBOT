import os
import requests
from requests.auth import HTTPBasicAuth
from config import MAPPING_CONFIG, SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD, SERVICENOW_INCIDENT_TABLE, SERVICENOW_SERVICE_REQUEST_TABLE

def _get_servicenow_auth():
    return HTTPBasicAuth(SERVICENOW_USERNAME, SERVICENOW_PASSWORD)

def create_servicenow_incident(data):
    if not all([SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD]):
        print("ServiceNow credentials not fully configured. Cannot create incident.")
        return None

    url = f"{SERVICENOW_INSTANCE}/api/now/table/{SERVICENOW_INCIDENT_TABLE}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    urgency_code = MAPPING_CONFIG["servicenow"]["urgency"].get(data.get("urgency", "Medium"), "2")

    payload = {
        "short_description": data.get("summary", "IT Incident Reported"),
        "description": data.get("suggested_action", "No specific action suggested by AI."),
        "urgency": urgency_code,
        "impact": MAPPING_CONFIG["servicenow"]["impact"]
    }

    try:
        response = requests.post(url, auth=_get_servicenow_auth(), headers=headers, json=payload)
        response.raise_for_status() 
        # print("Raw response text:", response.text)


        response_json = response.json()
        if response.status_code == 201:
            print("Ticket created successfully in ServiceNow")
            print("Incident Number:", response_json['result']['number'])
            print("Incident Sys ID:", response_json['result']['sys_id'])
            return response_json['result'] # Return the created incident details
        else:
            print("Failed to create ticket in ServiceNow (unexpected status).")
            print("Status code:", response.status_code)
            print("Response:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error creating ServiceNow incident: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"ServiceNow response: {e.response.text}")
        return None


def create_servicenow_service_request(user_query):
    if not all([SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD]):
        print("ServiceNow credentials not fully configured. Cannot create service request.")
        return None

    url = f"{SERVICENOW_INSTANCE}/api/now/table/{SERVICENOW_SERVICE_REQUEST_TABLE}"
    
    payload = {
        "short_description": user_query,
        "request_state": "requested" 
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(
            url,
            auth=_get_servicenow_auth(),
            headers=headers,
            json=payload
        )
        response.raise_for_status() 

        response_json = response.json()
        if response.status_code in [200, 201]:
            print("Service request created successfully in ServiceNow!")
            print("Request Number:", response_json['result']['number'])
            print("Request Sys ID:", response_json['result']['sys_id'])
            return response_json['result']
        else:
            print("Failed to create service request in ServiceNow (unexpected status).")
            print("Status Code:", response.status_code)
            print("Response:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error creating ServiceNow service request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"ServiceNow response: {e.response.text}")
        return None

def fetch_open_incidents(query_filter=""):
    if not all([SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD]):
        print("ServiceNow credentials not fully configured. Cannot fetch incidents.")
        return []

    base_query = "active=true^stateIN1,2,3" 
    if query_filter:
        query = f"{base_query}^{query_filter}"
    else:
        query = base_query

    url = f"{SERVICENOW_INSTANCE}/api/now/table/{SERVICENOW_INCIDENT_TABLE}?sysparm_query={query}&sysparm_fields=sys_id,number,short_description,description,state"
    
    try:
        response = requests.get(url, auth=_get_servicenow_auth())
        response.raise_for_status()
        return response.json()["result"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching open incidents from ServiceNow: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"ServiceNow response: {e.response.text}")
        return [] 
    
def update_servicenow_incident(ticket_sys_id, update_payload):
    if not all([SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD]):
        print("ServiceNow credentials not fully configured. Cannot update incident.")
        return False
    url = f"{SERVICENOW_INSTANCE}/api/now/table/{SERVICENOW_INCIDENT_TABLE}/{ticket_sys_id}"
    try:
        response = requests.patch(url, auth=_get_servicenow_auth(), json=update_payload)
        response.raise_for_status()
        print(f"ServiceNow incident {ticket_sys_id} updated successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to update ServiceNow incident {ticket_sys_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"ServiceNow response: {e.response.text}")
        return False

def close_servicenow_incident(ticket_sys_id, comments=""):
    payload = {
        "state": "7", 
        "comments": comments or "Automated action: Task completed successfully."
    }
    return update_servicenow_incident(ticket_sys_id, payload)

def fetch_open_service_requests(query_filter=""):
    if not all([SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD]):
        print("ServiceNow credentials not fully configured. Cannot fetch service requests.")
        return []

    base_query = "active=true^request_stateNOTIN3,5,6"
    if query_filter:
        query = f"{base_query}^{query_filter}"
    else:
        query = base_query

    url = f"{SERVICENOW_INSTANCE}/api/now/table/{SERVICENOW_SERVICE_REQUEST_TABLE}?sysparm_query={query}&sysparm_fields=sys_id,number,short_description,description,request_state"
    
    try:
        response = requests.get(url, auth=_get_servicenow_auth())
        response.raise_for_status()
        return response.json()["result"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching open service requests from ServiceNow: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"ServiceNow response: {e.response.text}")
        return []

def update_servicenow_service_request(request_sys_id, update_payload):
    if not all([SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD]):
        print("ServiceNow credentials not fully configured. Cannot update service request.")
        return False
    url = f"{SERVICENOW_INSTANCE}/api/now/table/{SERVICENOW_SERVICE_REQUEST_TABLE}/{request_sys_id}"
    try:
        response = requests.patch(url, auth=_get_servicenow_auth(), json=update_payload)
        response.raise_for_status()
        print(f"ServiceNow service request {request_sys_id} updated successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to update ServiceNow service request {request_sys_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"ServiceNow response: {e.response.text}")
        return False

def fulfill_servicenow_service_request(request_sys_id, comments=""):
    payload = {
        "request_state": "3", 
        "comments": comments or "Automated action: Service request fulfilled successfully."
    }
    return update_servicenow_service_request(request_sys_id, payload)