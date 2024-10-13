# Интеллектуальный помощник оператора службы поддержки

Этот проект предоставляет готовую реализацию **Retrieval-Augmented Generation** (RAG) системы, которая использует языковую модель для генерации ответов на основе поиска по базе данных (retriever). В основе системы лежат предварительно обученные модели LLM и FAISS для поиска релевантных документов.

## Установка

Необходимые библиотеки можно установить с помощью `pip`:

```bash
pip install torch transformers langchain langchain_community faiss-gpu pandas tqdm fastapi xformers sentense-transformers
```


### 1. **Использование LLM**

1. Инициализация модели:

```python
from retriever import RetrieverLLM

rag = RetrieverLLM()
```

2. Поиск и генерация ответа на запрос:

```python
question = ""

# Генерация ответа на запрос
answer = rag.generate_answer(question)
print(answer)
```


### 2. **Запуск API**

```bash
uvicorn api:app —port 1337
tuna http 1337
```
Пример запроса
```python
import requests

response = requests.post("https://my-subdomen.ru.tuna.am/predict", 
                         json={"query": 'льготы для  детей  РЖД?', 'history':''})
print(f"{response.text}")
```
### 3. **Запуск Streamlit**
```bash
streamlit run streamlit_app.py --server.port 1228
ngrok http 1228
```

### 4. **Запуск Tg-бота**
- **Ссылка на телеграм бота**: https://t.me/sashamatveikostyabot
