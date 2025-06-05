import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"translationdemo-454309-0a1981b5773b.json"
import streamlit as st
import requests
import json
from chatbot_app.chatbot import get_bot_reply
from chatbot_app.installer import install_software,uninstall_software,update_software
from utils.llm_interactions import extract_intent, extract_metadata
from api_integration.servicenow import create_servicenow_incident, create_servicenow_service_request
from api_integration.jira import create_jira_ticket
from db_configuration import insert_ticket_data
from utils.translation_helper import detect_language, translate_to_english, translate_from_english

st.set_page_config(page_title="IT Helpdesk Chatbot", page_icon="🤖")
st.title("IT Helpdesk Chatbot")
if "history" not in st.session_state:
    st.session_state.history = []


def get_model_intent(query: str) -> str:
    try:
        response = requests.post("http://127.0.0.1:5000/predict", json={"text": query})
        if response.status_code == 200:
            return response.json().get("intent", "Fallback_Intent")
    except Exception as e:
        print(f"Model API error: {e}")
    return "Fallback_Intent"


user_input = st.chat_input("Ask me to install software or raise IT support tickets!")
if user_input:
    user_lang = detect_language(user_input)
    translated_input = translate_to_english(user_input)
    st.session_state.history.append(("user", user_input))

    genai_intent = extract_intent(translated_input)
    print("intent from gen", genai_intent)

    if genai_intent in ["install", "uninstall", "update"]:
        action_func = {
            "install": install_software,
            "uninstall": uninstall_software,
            "update": update_software
        }[genai_intent]

        matched = False
        for software in ["zoom", "slack", "chrome", "outlook", "teams", "vscode", "vlc", "python", "discord"]:
            if software in translated_input.lower():
                result = action_func(software)
                st.session_state.history.append(("bot", translate_from_english(result, user_lang)))
                matched = True
                break

        if not matched:
            msg = f"Could not detect which software to {genai_intent}. Please specify clearly."
            st.session_state.history.append(("bot", translate_from_english(msg, user_lang)))

    else:
        model_intent = get_model_intent(translated_input)
        print("model intent", model_intent)

        if model_intent=="Fallback_Intent":
            fallback_msg = "Sorry, I couldn't process your request. Please rephrase or contact support."
            st.session_state.history.append(("bot", translate_from_english(fallback_msg, user_lang)))

        elif model_intent != "Fallback_Intent":
            output = extract_metadata(translated_input)
            cleaned_output = output.strip().strip("```json").strip("```").strip()

            try:
                parsed_output = json.loads(cleaned_output)
                insert_ticket_data(parsed_output, source='user_query')
                msg = "Extracted ticket details and stored in the database."
                st.session_state.history.append(("bot", translate_from_english(msg, user_lang)))

                if parsed_output.get('needs_ticket', False):
                    servicenow_result = create_servicenow_incident(parsed_output)

                    if servicenow_result and servicenow_result.get('number'):
                        msg = f"ServiceNow incident ticket created successfully.\n**Ticket Number**: `{servicenow_result['number']}`"
                    else:
                        msg = "Failed to create ticket in ServiceNow.\nTrying alternate system (Jira)..."
                        st.session_state.history.append(("bot", translate_from_english(msg, user_lang)))

                        jira_result = create_jira_ticket(parsed_output)
                        if jira_result:
                            msg = f"Jira ticket created as fallback.\n**Jira ID**: `{jira_result['key']}`"
                        else:
                            msg = "Failed to create ticket in Jira as well."

                    st.session_state.history.append(("bot", translate_from_english(msg, user_lang)))
                else:
                    msg = "No formal incident ticket needed. I’ve recorded your issue."
                    st.session_state.history.append(("bot", translate_from_english(msg, user_lang)))
            except json.JSONDecodeError:
                error_msg = (
                    "Sorry, I couldn't understand the issue metadata. "
                    "Please rephrase your request or try again later."
                )
                st.session_state.history.append(("bot", translate_from_english(error_msg, user_lang)))
        else:
            fallback_response = get_bot_reply(translated_input)
            st.session_state.history.append(("bot", translate_from_english(fallback_response, user_lang)))

for sender, msg in st.session_state.history:
    with st.chat_message("user" if sender == "user" else "assistant"):
        st.markdown(msg)