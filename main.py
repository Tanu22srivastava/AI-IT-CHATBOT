import json
import threading 
import time 
from utils.llm_interactions import extract_intent, extract_metadata
from api_integration.servicenow import create_servicenow_incident, create_servicenow_service_request
from api_integration.jira import create_jira_ticket 
from db_configuration import insert_ticket_data 
from agent.automated_agent import agent_loop

def handle_it_request(user_query):
    print(f"\n--- Processing new request: '{user_query}' ---")
    intent = extract_intent(user_query)
    print(f"Detected intent: {intent}")

    if intent == "incident":
        output = extract_metadata(user_query)
        cleaned_output = output.strip().strip("```json").strip("```").strip()
        try:
            parsed_output = json.loads(cleaned_output)
            print("Extracted Metadata:", parsed_output)
            insert_ticket_data(parsed_output, source='user_query')
            print("Added to Local Database")

            if parsed_output.get('needs_ticket', False):
                print("Creating incident ticket in ServiceNow for automated agent/manual review...")
                servicenow_result = create_servicenow_incident(parsed_output)
                if servicenow_result:
                    print(f"ServiceNow incident {servicenow_result.get('number')} created.")
                else:
                    print("Failed to create ServiceNow incident. Considering other platforms or manual intervention.")
                    user_input_fallback = input("ServiceNow creation failed. Do you want to create in Jira instead? (yes/no): ").lower()
                    if user_input_fallback == 'yes':
                        create_jira_ticket(parsed_output)
                    else:
                        print("No ticket created.")
            else:
                print("No formal incident ticket needed based on analysis.")

        except json.JSONDecodeError as e:
            print("Failed to parse metadata JSON for incident:")
            print(output)
            print(f"Error: {e}")
    elif intent == "service_request":
        print("Creating service request in ServiceNow...")
        create_servicenow_service_request(user_query)
    else:
        print("Could not determine intent for the request. No action taken.")

if __name__ == "__main__":
    print("Starting automated agent in a background thread...")
    agent_thread = threading.Thread(target=agent_loop, daemon=True) 
    agent_thread.start()
    print("Automated agent is running. You can now submit requests.")
    while True:
        user_input_request = input("\nEnter your IT helpdesk request (or 'exit' to quit): \n")
        if user_input_request.lower() == 'exit':
            print("Exiting application.")
            break
        handle_it_request(user_input_request)
        time.sleep(10) 