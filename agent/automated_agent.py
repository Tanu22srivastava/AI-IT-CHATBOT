import subprocess
import time
from api_integration.servicenow import (
    fetch_open_incidents, close_servicenow_incident, update_servicenow_incident,
    fetch_open_service_requests, fulfill_servicenow_service_request, update_servicenow_service_request
)

def install_software(software):
    commands = {
        "zoom": "winget install Zoom.Zoom --accept-package-agreements --accept-source-agreements",
        "slack": "winget install SlackTechnologies.Slack --accept-package-agreements --accept-source-agreements"
    }

    if software in commands:
        print(f"Attempting to install {software} using winget...")
        try:
            result = subprocess.run(commands[software], shell=True, capture_output=True, text=True, check=False) 
            
            if result.returncode == 0:
                print(f"{software} installation successful.")
                print(f"Winget stdout: \n{result.stdout}")
                return True, result.stdout
            else:
                print(f"{software} installation failed. Error: \n{result.stderr}")
                return False, result.stderr
        except FileNotFoundError:
            return False, "winget command not found. Ensure winget is installed and in PATH."
        except Exception as e:
            return False, f"An unexpected error occurred during installation: {e}"
    print(f"Software '{software}' not recognized for automated installation.")
    return False, "Software not found in automated installation list for automated deployment."

def identify_software_for_installation(description):
    desc = description.lower()
    if "install" in desc:
        for keyword in ["zoom", "slack"]: 
            if keyword in desc:
                return keyword
    return None

def agent_loop():
    print("Automated agent loop started. Checking for tasks every 15 seconds...")
    while True:
        try:
            open_service_requests = fetch_open_service_requests(query_filter="short_descriptionLIKEinstall")
            
            if not open_service_requests:
                print("No open installation service requests found in ServiceNow.")
            else:
                print(f"Found {len(open_service_requests)} open service requests for installation.")
            
            for req in open_service_requests:
                req_sys_id = req.get('sys_id')
                req_number = req.get('number')
                req_short_description = req.get('short_description', '')
                current_req_state = req.get('request_state')

                print(f"Processing ServiceNow Service Request {req_number} (Sys ID: {req_sys_id}, State: {current_req_state}) - '{req_short_description}'")

                software_to_install = identify_software_for_installation(req_short_description)

                if software_to_install:
                    print(f"Identified '{software_to_install}' for automated installation for service request {req_number}.")
                    update_servicenow_service_request(req_sys_id, {
                        "request_state": "2", 
                        "comments": f"Automated agent detected request. Starting software installation for {software_to_install}."
                    }) 

                    success, output_log = install_software(software_to_install)

                    if success:
                        print(f"Automated installation of {software_to_install} for request {req_number} successful.")
                        comments_for_sn = f"Automated action: Successfully installed {software_to_install}. Winget output:\n{output_log}"
                        if fulfill_servicenow_service_request(req_sys_id, comments_for_sn):
                            print(f"ServiceNow Service Request {req_number} fulfilled successfully.")
                        else:
                            print(f"Failed to fulfill ServiceNow Service Request {req_number}.")
                    else:
                        print(f"Automated installation of {software_to_install} for request {req_number} failed.")
                        failure_comment = f"Automated action: Installation of {software_to_install} failed. Please review. Error: \n{output_log}"
                        update_servicenow_service_request(req_sys_id, {
                            "comments": failure_comment,
                            "request_state": "6" 
                        })
                        print(f"ServiceNow Service Request {req_number} updated with failure details. Requires manual review.")
                else:
                    print(f"No specific software for automated installation identified for service request {req_number}.")

        except Exception as e:
            print(f"An unexpected error occurred in agent loop: {e}")

        print("Agent sleeping...")
        time.sleep(15) 