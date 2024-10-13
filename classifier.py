import pandas as pd
import numpy as np
import random
import torch
import transformers
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, BertModel
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader

rev = {4: 'Забота о работниках', 3: 'Забота компании о работнике', 2: 'ЗОЖ', 1: 'Жилищная политика',
       6: 'Коллективный договор', 11: 'Режим труда и отдыха', 7: 'Молодежная политика', 0: 'Адаптация',
       5: 'Заработная плата', 8: 'Оплата труда', 10: 'Организация труда', 9: 'Организация работы'}

class BertCLS(nn.Module):
    def __init__(self, model, n_classes):
        # Инициализирует BERT
        super(BertCLS, self).__init__()
        self.model = model
        self.fc = nn.Linear(1024, n_classes)

    def forward(self, batch):
        return self.fc(self.model(**batch).pooler_output)
        
class ClassificationDataset_test(Dataset):
    def __init__(self, data):
        # Инициализирует датасет 
        super().__init__()
        self.text = data

    def __getitem__(self, idx):
        text = self.text[idx]
        return text

    def __len__(self):
        return len(self.text)

class Classifier:
    def __init__(self, model_name="deepvk/USER-bge-m3", model_path="model", num_labels=12):
        # Инициализирует токенизатор и модель, загружает  веса 
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = BertModel.from_pretrained(
            model_name,
            ignore_mismatched_sizes=True,
            num_labels=num_labels
        )
        
        self.bert_cls = BertCLS(model, n_classes=num_labels).to(self.device)
        self.bert_cls.load_state_dict(torch.load(model_path, map_location=self.device))
        self.bert_cls = self.bert_cls.to(self.device)

    def collate_fn(self, batch):
        model_input = []
        for text in batch:
            model_input.append(text)

        tok = self.tokenizer(model_input, padding=True,
                             max_length=512, truncation=True,
                             return_tensors='pt')
        return tok

    def get_loader(self, dataset, shuffle, batch_size):
        # Создает DataLoader
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            pin_memory=False,
            num_workers=0,
            collate_fn=self.collate_fn
        )
        return loader

    def ans(self, model, loader):
        pred = []
        model.eval()
        with torch.no_grad():
            pbar = tqdm(loader)
            for batch_idx, data in enumerate(pbar):
                data = data.to(self.device)
                embeddings = model(data)
                pred.extend(embeddings.argmax(-1).detach().cpu().numpy())

        return pred

    def predict(self, s):
        # возвращает название категории.
        test_dtst = ClassificationDataset_test([s])
        test_loader1 = self.get_loader(test_dtst, shuffle=False, batch_size=1)
        preds = self.ans(self.bert_cls, test_loader1)
        fin = []
        for i in preds:
            fin.append(rev[i])
        return fin[0]
