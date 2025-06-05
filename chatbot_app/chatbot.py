import google.generativeai as genai

genai.configure(api_key="AIzaSyDBQEmOTdmlwd8SIw1TWyBN8d0XzqCCpOg")

chat = genai.GenerativeModel("gemini-1.5-flash").start_chat(history=[])

def get_bot_reply(message):
    response = chat.send_message(message)
    return response.text
