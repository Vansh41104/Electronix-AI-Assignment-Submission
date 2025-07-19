# finetune.py

import argparse
import json
import os
import random
import numpy as np
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TFAutoModelForSequenceClassification,
    TrainingArguments, Trainer
)
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    import tensorflow as tf
    tf.random.set_seed(seed)

def load_dataset_from_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
    texts = [item['text'] for item in data]
    labels = [1 if item['label'] == 'positive' else 0 for item in data]
    return Dataset.from_dict({'text': texts, 'label': labels})

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='binary')
    acc = accuracy_score(labels, predictions)
    return {'accuracy': acc, 'f1': f1, 'precision': precision, 'recall': recall}

def main():
    parser = argparse.ArgumentParser(description='Fine-tune a sentiment analysis model.')
    parser.add_argument('--data', required=True, help='Path to JSONL data file.')
    parser.add_argument('--framework', default='pt', choices=['pt', 'tf'], help='Framework to use: pt (PyTorch) or tf (TensorFlow).')
    parser.add_argument('--epochs', type=int, default=3, help='Number of training epochs.')
    parser.add_argument('--lr', type=float, default=2e-5, help='Learning rate.')
    parser.add_argument('--batch_size', type=int, default=16, help='Batch size for training and evaluation.')
    parser.add_argument('--model_name', default='distilbert-base-uncased-finetuned-sst-2-english', help='Pretrained model name from Hugging Face Hub.')
    parser.add_argument('--output_dir', default='./model', help='Directory to save the fine-tuned model.')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility.')
    args = parser.parse_args()

    set_seed(args.seed)

    # Load tokenizer and dataset
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    dataset = load_dataset_from_jsonl(args.data)
    
    def tokenize_function(examples):
        return tokenizer(examples['text'], padding="max_length", truncation=True)
        
    tokenized_datasets = dataset.map(tokenize_function, batched=True)
    
    # Split dataset
    train_test_split = tokenized_datasets.train_test_split(test_size=0.1, seed=args.seed)
    train_dataset = train_test_split['train']
    eval_dataset = train_test_split['test']

    if args.framework == 'pt':
        model = AutoModelForSequenceClassification.from_pretrained(args.model_name, num_labels=2)
        
        training_args = TrainingArguments(
            output_dir=args.output_dir,
            num_train_epochs=args.epochs,
            per_device_train_batch_size=args.batch_size,
            per_device_eval_batch_size=args.batch_size,
            learning_rate=args.lr,
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_steps=10,
            load_best_model_at_end=True,
            metric_for_best_model="accuracy",
            weight_decay=0.01,
            max_grad_norm=1.0,
            seed=args.seed,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=compute_metrics,
            tokenizer=tokenizer,
        )
        
        logger.info("Starting PyTorch training...")
        trainer.train()
        
    else:
        model = TFAutoModelForSequenceClassification.from_pretrained(args.model_name, num_labels=2)
        
        training_args = TrainingArguments(
             output_dir=args.output_dir,
             num_train_epochs=args.epochs,
             per_device_train_batch_size=args.batch_size,
             per_device_eval_batch_size=args.batch_size,
             learning_rate=args.lr,
             eval_strategy="epoch",
             save_strategy="epoch",
             logging_steps=10,
             seed=args.seed,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            compute_metrics=compute_metrics,
            tokenizer=tokenizer,
        )
        
        logger.info("Starting TensorFlow training...")
        trainer.train()

    logger.info(f"Saving model and tokenizer to {args.output_dir}")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    logger.info("Fine-tuning completed successfully!")

if __name__ == '__main__':
    main()