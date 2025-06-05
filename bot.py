import tkinter as tk
from tkinter import scrolledtext
import os
from utils.llm_interactions import extract_intent, extract_metadata
from api_integration.servicenow import create_servicenow_incident, create_servicenow_service_request
from api_integration.jira import create_jira_ticket 
from db_configuration import insert_ticket_data 
from agent.automated_agent import agent_loop

known_software = {
    "zoom": "Zoom.Zoom",
    "slack": "SlackTechnologies.Slack",
    "chrome": "Google.Chrome",
    "outlook": "Microsoft.Outlook",
    "teams": "Microsoft.Teams",
    "vscode": "Microsoft.VisualStudioCode",
    "notepad++": "Notepad++.Notepad++",
    "firefox": "Mozilla.Firefox",
    "python": "Python.Python.3",  
    "nodejs": "OpenJS.NodeJS",
    "git": "Git.Git",
    "skype": "Microsoft.Skype",
    "discord": "Discord.Discord",
    "postman": "Postman.Postman",
    "docker": "Docker.DockerDesktop",
    "spotify": "Spotify.Spotify",
    "adobe reader": "Adobe.Acrobat.Reader.64-bit",
    "java": "Oracle.JavaRuntimeEnvironment",  
    "mysql": "Oracle.MySQL",
    "mongodb": "MongoDB.MongoDBCompass.Full",  
    "xampp": "ApacheFriends.XAMPP"
}

def classify_intent(message):
    message = message.lower()
    if "install" in message:
        return "install"
    elif "uninstall" in message or "remove" in message:
        return "uninstall"
    elif "update" in message:
        return "update"
    else:
        return "unknown"

def extract_software(message):
    for name in known_software:
        if name in message.lower():
            return name
    return None

def execute_action(intent, software):
    if software not in known_software:
        return f"I don't recognize the software '{software}'."
    
    app_id = known_software[software]
    
    if intent == "install":
        os.system(f"winget install --id={app_id} --silent")
        return f"Installing {software}..."
    elif intent == "uninstall":
        os.system(f"winget uninstall --id={app_id}")
        return f"Uninstalling {software}..."
    elif intent == "update":
        os.system(f"winget upgrade --id={app_id}")
        return f"Updating {software}..."
    else:
        return "Sorry, I couldn't understand your request."

def respond_to_user():
    user_input = entry.get()
    if not user_input.strip():
        return
    
    chat_box.insert(tk.END, f"You: {user_input}\n")
    entry.delete(0, tk.END)

    intent = classify_intent(user_input)
    software = extract_software(user_input)

    if intent == "unknown" or software is None:
        bot_reply = "Sorry, please try something like 'install Zoom'."
    else:
        bot_reply = execute_action(intent, software)

    chat_box.insert(tk.END, f"Bot: {bot_reply}\n")

root = tk.Tk()
root.title("Software Installer Bot ")
root.geometry("500x500")

chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12))
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

entry = tk.Entry(root, font=("Arial", 12))
entry.pack(fill=tk.X, padx=10, pady=5)
entry.bind("<Return>", lambda event: respond_to_user())

send_btn = tk.Button(root, text="Send", command=respond_to_user, font=("Arial", 12))
send_btn.pack(pady=5)

root.mainloop()
