from flask import Flask, request, jsonify
import joblib

model= joblib.load('intent__model.pkl')

app= Flask(__name__)
@app.route('/predict', methods=['POST'])
def predict():
  data= request.get_json()
  text= data.get('text')
  print(text)

  if not text:
    return jsonify({"error": "No text provided"}), 400

  prediction = model.predict([text])[0]
  con= model.predict_proba([text])[0]
  return jsonify({
    "intent": prediction,
    "confidence_scores": con.tolist()
})


if __name__ == '__main__':
    app.run(debug=True)