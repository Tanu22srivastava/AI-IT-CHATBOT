
import yaml
import pandas as pd

with open("nlu_extra.yml", 'r') as f:
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

model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(label2intent))

training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    logging_strategy="epoch",
    save_strategy="epoch",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
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