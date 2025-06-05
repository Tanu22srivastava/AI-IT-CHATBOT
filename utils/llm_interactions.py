import google.generativeai as genai
from config import API_KEY, MODEL_NAME
import json

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    print(f"Error configuring Generative AI model: {e}")
    print("Please ensure GOOGLE_API_KEY is correctly set in your .env file.")
    model = None 

def extract_intent(text):
    if not model:
        print("AI model not initialized. Cannot extract intent.")
        return "unknown" 
    
    prompt = f"""
Classify the following IT helpdesk request into one of these categories:
'install', 'uninstall','update' or 'IT'.

Here are the definitions for each category:
- 'install': The user wants to set up, download, or get new software or applications (e.g., "Install Zoom", "I need to download Chrome").
- 'uninstall': The user wants to remove or delete existing software or applications (e.g., "Remove Python", "Uninstall VSCode").
- 'update': The user wants to upgrade or patch existing software or systems (e.g., "Update my operating system", "Upgrade Adobe Reader").
- 'IT': the user doesn't want to install, uninstall or update.
Request: "{text}"

Respond with only one word from the allowed categories: 'install', 'uninstall', 'update' or 'IT'.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except Exception as e:
        print(f"Error extracting intent with AI model: {e}")
        return "unknown" 

def extract_metadata(text):
    if not model:
        print("AI model not initialized. Cannot extract metadata.")
        return json.dumps({}) 
    prompt = f"""
You are an IT support assistant. Analyze the following email or ticket and extract key metadata in JSON format.

Extract the following:
- summary: a concise 1-2 line summary of the issue or request.
- issue_type: categorize into one of ["Network", "Hardware", "Software", "Account", "Access", "Performance", "Security", "Other"]. If installing software, classify as "Software". If a device is broken, "Hardware". If internet is down, "Network".
- urgency: based on the user's description, categorize as ["Low", "Medium", "High", "Critical"]. "Critical" implies system down or major business impact. "High" implies significant disruption for one user. "Medium" for minor disruption. "Low" for general queries or non-urgent requests.
- affected_item: the specific system, application, hardware, or service mentioned (e.g., "My laptop", "Zoom application", "network", "email account").
- suggested_action: a possible next step along with the proper steps to solve the problem, or to fulfill the request. If it's a software installation, provide clear steps like "Install Zoom application using winget command: winget install Zoom.Zoom".
- needs_ticket: true if this request requires a formal incident or service request ticket in a system like ServiceNow/Jira, false otherwise (e.g., if it's just a general question already answered in suggested_action).

Input:
\"\"\" 
{text} 
\"\"\"

Return JSON only.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return json.dumps({}) 
    

# def extract_intent(text):
#     text = text.lower()
#     if any(word in text for word in ["install", "setup", "download"]):
#         return "install"
#     elif any(word in text for word in ["uninstall", "remove", "delete"]):
#         return "uninstall"
#     elif any(word in text for word in ["update", "upgrade", "patch"]):
#         return "update"
#     elif any(word in text for word in ["issue", "problem", "error", "broken"]):
#         return "incident"
#     elif any(word in text for word in ["request", "need", "access", "enable"]):
#         return "service_request"
#     else:
#         return "general"
