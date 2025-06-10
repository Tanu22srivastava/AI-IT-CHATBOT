import argparse
import yaml
import pandas as pd
import torch
import pickle
import json
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments
)


class IntentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        return {
            **{key: torch.tensor(val[idx]) for key, val in self.encodings.items()},
            'labels': torch.tensor(self.labels[idx])
        }

    def __len__(self):
        return len(self.labels)


def load_data():
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
    return df


def train_model():
    df = load_data()
    le = LabelEncoder()
    df['label_enc'] = le.fit_transform(df['label'])
    label2intent = dict(zip(df['label_enc'], df['label']))
    intent2label = dict(zip(df['label'], df['label_enc']))

    with open("intent_encoder.pkl", "wb") as f:
        pickle.dump({
            "label_encoder": le,
            "label2intent": label2intent,
            "intent2label": intent2label
        }, f)

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        df['text'].tolist(), df['label_enc'].tolist(), test_size=0.1, stratify=df['label_enc'], random_state=42
    )

    tokenizer = BertTokenizer.from_pretrained("google/bert_uncased_L-2_H-128_A-2")
    train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

    train_dataset = IntentDataset(train_encodings, train_labels)
    val_dataset = IntentDataset(val_encodings, val_labels)

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
        logging_dir="./logs",
        save_total_limit=2
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
    print("Training complete and artifacts saved.")


def predict_intent(text):
    tokenizer = BertTokenizer.from_pretrained("bert_intent_model")
    model = BertForSequenceClassification.from_pretrained("bert_intent_model")
    model.eval()

    with open("intent_encoder.pkl", "rb") as f:
        data = pickle.load(f)
        label2intent = data["label2intent"]

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    predicted_class_id = outputs.logits.argmax().item()
    return label2intent[str(predicted_class_id)] if isinstance(predicted_class_id, str) else label2intent[predicted_class_id]


if __name__ == "__main__":
    os.environ["WANDB_DISABLED"] = "true"

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["train", "test"], required=True)
    parser.add_argument("--text", type=str, help="Input text to predict intent (test mode only)")
    args = parser.parse_args()

    if args.mode == "train":
        train_model()
    elif args.mode == "test":
        if not args.text:
            print("Please provide input text using --text for prediction.")
        else:
            result = predict_intent(args.text)
            print(f"Predicted Intent: {result}")
