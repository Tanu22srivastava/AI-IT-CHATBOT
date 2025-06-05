from flask import Flask, request, jsonify
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import json

app = Flask(__name__)

model_path = "Bert_Model"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertForSequenceClassification.from_pretrained(model_path)

intent_labels = {
    0: "Account_Management",
    1: "Account_Unlock",
    2: "Browser_Solutions_Menu",
    3: "Fallback_Intent",
    4: "Outlook_Issue",
    5: "Printer_Management",
    6: "Reset_Password",
    7: "Service_Request",
    8: "Software_Deployment",
    9: "System_Optimization_Menu",
    10: "Teams_Troubleshoot",
    11: "VPN_Menu",
    12: "network_problem",
    13: "solve_Chrome_issues",
    14: "solve_Edge_issues",
    15: "solve_Mozilla_issues"
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()  


def predict_intent(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = logits.argmax().item()

    return intent_labels[predicted_class_id]

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        intent = predict_intent(text)
        return jsonify({"intent": intent})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)