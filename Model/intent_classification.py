# -*- coding: utf-8 -*-
"""Intent Classification

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YzIEQDyTpEdcJxmmRV-HPSzPw3N7ME1d

Using Logistic Regression
"""

#!pip install scikit-learn pyyaml

# import yaml
# import random
# import re
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# from sklearn.pipeline import Pipeline
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report


# def load_intents_from_yaml(file_path):
#     with open(file_path, 'r') as file:
#         data = yaml.safe_load(file)

#     samples = []
#     for item in data.get('nlu', []):
#         intent = item.get('intent')
#         examples_block = item.get('examples', "")
#         examples = re.findall(r'- (.+)', examples_block)
#         for ex in examples:
#             samples.append((ex.strip(), intent))
#     return samples


# samples = load_intents_from_yaml("/content/nlu_extra.yml")
# texts, labels = zip(*samples)


# X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# model = Pipeline([
#     ('tfidf', TfidfVectorizer()),
#     ('clf', LogisticRegression(max_iter=1000))
# ])

# model.fit(X_train, y_train)

# y_pred = model.predict(X_test)
# print(classification_report(y_test, y_pred))

# def predict_intent(text):
#     return model.predict([text])[0]

# def confidence(text):
#   return model.predict_proba([text])[0]

# print("Test: Type your message below to detect intent (type 'exit' to stop):")
# while True:
#     user_input = input("> ")
#     if user_input.lower() == "exit":
#         break
#     intent = predict_intent(user_input)
#     print("Predicted intent:", intent)
#     con= confidence(user_input)
#     print("Confidence:", con)

# import joblib

# joblib.dump(model, 'intent__model.pkl')



"""Bert Model or Intent Classification"""

#!pip install transformers datasets pyyaml scikit-learn pandas

import yaml
import pandas as pd

with open("nlu_extra_small.yml", 'r') as f:
    data = yaml.safe_load(f)

intents = []
texts = []

for item in data['nlu']:
    intent = item['intent']
    examples_block = item['examples']
    examples = [line.strip('- ').strip() for line in examples_block.strip().split('\n') if line.strip()]

    intents.extend([intent] * len(examples))
    texts.extend(examples)

df = pd.DataFrame({'text': texts, 'label': intents})
df.head()

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
df['label_enc'] = le.fit_transform(df['label'])

label2intent = dict(zip(df['label_enc'], df['label']))
intent2label = dict(zip(df['label'], df['label_enc']))

from sklearn.model_selection import train_test_split

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df['text'].tolist(), df['label_enc'].tolist(), test_size=0.1, stratify=df['label_enc'], random_state=42)

from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained("google/bert_uncased_L-2_H-128_A-2")

train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

import torch

class IntentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()} | {
            'labels': torch.tensor(self.labels[idx])
        }

    def __len__(self):
        return len(self.labels)

train_dataset = IntentDataset(train_encodings, train_labels)
val_dataset = IntentDataset(val_encodings, val_labels)

import os
os.environ["WANDB_DISABLED"] = "true"

from transformers import BertForSequenceClassification, Trainer, TrainingArguments

model = BertForSequenceClassification.from_pretrained("prajjwal1/bert-tiny", num_labels=len(label2intent))

training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    logging_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=10,
    weight_decay=0.01,
    load_best_model_at_end=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

trainer.train()

model.save_pretrained("bert_intent_model")
tokenizer.save_pretrained("bert_intent_model")

import json
with open("intent_mapping.json", "w") as f:
    json.dump(label2intent, f)

def predict_intent(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    if next(model.parameters()).is_cuda:
        inputs = {key: val.to(model.device) for key, val in inputs.items()}

    outputs = model(**inputs)
    predicted_class_id = outputs.logits.argmax().item()
    return label2intent[predicted_class_id]

print(predict_intent("I need a laptop as my laptop is not working"))
print(predict_intent("I need a laptop "))
print(predict_intent("my laptop is not working"))
print(predict_intent("I need to manage my account settings."))
print(predict_intent("I'm locked out of my system."))
print(predict_intent("I'm having trouble with my web browser."))
print(predict_intent("Tell me a joke.")) 
print(predict_intent("Emails are not syncing in Outlook."))
print(predict_intent("Print queue is stuck."))
print(predict_intent("I forgot my password. Can I reset it?"))
print(predict_intent("Request help from support"))
print(predict_intent("Push software updates."))
print(predict_intent("Run system optimization."))
print(predict_intent("Audio is not working in Teams."))
print(predict_intent("Connect me to the corporate network via VPN."))
print(predict_intent("No connection found."))


# model.save_pretrained("Bert_Model", safe_serialization=False)  # Save as pytorch_model.bin
# tokenizer.save_pretrained("Bert_Model")

# inputs = tokenizer("I need a laptop as my laptop is not working", return_tensors="pt", truncation=True, padding=True)
# print(tokenizer.decode(inputs['input_ids'][0]))

# text = "I need a laptop as my laptop is not working"
# inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)

# if next(model.parameters()).is_cuda:
#     inputs = {key: val.to(model.device) for key, val in inputs.items()}

# with torch.no_grad():
#     outputs = model(**inputs)
# print("Colab Logits:", outputs.logits)
# print("Predicted ID:", outputs.logits.argmax().item())

# from sklearn.preprocessing import LabelEncoder
# le = LabelEncoder()
# df['label_enc'] = le.fit_transform(df['label'])

# label2intent = dict(enumerate(le.classes_))

# print("Intent Mapping in Colab:")
# print(label2intent)

# import json
# with open("intent_mapping.json", "w") as f:
#     json.dump(label2intent, f)



# number of epoches= 5, smaller dataset then tiny model performance- good training time- few minutes
# epoches-3 , dataset-small, model- base, model performance= belowe average training time few minutes
# epoches - 2, model base, large dataset, model perfromnce - good
# epoches-10,  dataset- small, model- small. perfromance- great