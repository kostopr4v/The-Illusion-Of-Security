import os
import pandas as pd
from tqdm import tqdm
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import warnings
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from vllm import LLM
from vllm.sampling_params import SamplingParams
import torch
from langchain.prompts import PromptTemplate
import json
from classifier import Classifier
warnings.simplefilter('ignore')

# систем промпт
system_prompt_template = PromptTemplate(
    input_variables=["question", "documents"],
    template="""
    {system_prompt}
    
    Documents: {documents}
    
    User's question: {question}
    """
)

class RetrieverLLM:
    def __init__(self, embeddings_model_name="deepvk/USER-bge-m3",  device='cuda'):

        self.embeddings_model_name = embeddings_model_name
        self.device = device
        self.embeddings = self.load_embeddings()
        self.baza_db, self.csv_db = self.load_all()
        self.txtdb = self.make_text_faiss()
        self.llm = LLM(model="Vikhrmodels/Vikhr-Nemo-12B-Instruct-R-21-09-24", max_model_len=8000, dtype='float16')
        self.categoryclassifier = Classifier()
        
    def load_embeddings(self):
        # ЛУЧШИЕ ЭМБЕДДИНГИ
        model_kwargs = {'device': self.device}
        encode_kwargs = {'normalize_embeddings': True}
        hf_embeddings = HuggingFaceEmbeddings(
            model_name=self.embeddings_model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs)
        return hf_embeddings

    def load_database(self, path): 
        # Загрузка базы данных для использования при поиске.
        return FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
         
    def load_all(self): 
        # Загрузка баз данных
        baza_db = self.load_database('./bazadf_faiss')
        csv_db = self.load_database('./csvdb_faiss')
        return baza_db, csv_db
        
    def search_db(self, db: FAISS, question: str, number=3) -> list[dict]:
        # Поиск по бд
        question = question.strip().capitalize()
        return db.similarity_search(question, number)

    def make_text_faiss(self):
        # Пересобираем бд если админ ( в стримлите) добавляет новый файл
        all_texts = ''
        path = './uploaded_files_txt'
        files = [os.path.join(path, filename) for filename in os.listdir(path)]
        files = [file for file in files if file.endswith('.txt')]
        print(files)
        if len(files) > 0:
            for i in files:
                with open(i, "r") as file:
                     dogovortxt = file.read()
                     all_texts += dogovortxt
    
            text_txt_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=100)
            txtdocs = text_txt_splitter.create_documents([all_texts])
            
            self.txtdb = FAISS.from_documents(txtdocs, self.embeddings)
            return self.txtdb
        else:
            print('NO FILES UPLOADED')
            return None

    def category_predict(self, question):
        # Предикт категории
        cat = self.categoryclassifier.predict(question)
        return cat
            
    def generate_context(self, query):
        # Собираем контекст воедине
        baza_answers = [doc.dict()['metadata']['Answer'] for doc in self.search_db(self.baza_db, query, number=3)]
        baza_questions = [' '.join(doc.dict()['page_content'].split(' | ')[:3]) for doc in self.search_db(self.baza_db, query, number=3)]
        csv = [str(doc.dict()['page_content']) for doc in self.search_db(self.csv_db, query, number=1)]
        if self.txtdb != None:
            txt = [str(doc.dict()['page_content']) for doc in self.search_db(self.txtdb, query, number=1)]
            return baza_questions, baza_answers, csv, txt
        else:
            txt = None
            return baza_questions, baza_answers, csv, txt
        

    def llm_question_answer(self, question, baza_questions, baza_answers, csv, txt, history) -> str:
        # Генерация ответ через ллм
        sampling_params = SamplingParams(max_tokens=2048, temperature=0.01)
        FIRST_SYSTEM_PROMPT = """
                    Your task is to answer the user's questions using only the information from the provided documents. Give two answers to each question: one with a list of relevant document identifiers and the second with the answer to the question itself, using documents with these identifiers."""


        SECOND_SYSTEM_PROMPT = f"""You are the technical support bot for the company 'РЖД'.
        You receive a question from the user and must answer it, relying only on the appropriate information provided to you (the context).
        1) The answer cannot contain information that is not found in the context. You cannot invent anything on your own.
        2) The answer must be complete and as accurate as possible.
        3) If context has special numbers or sections id ( for example: 2.1, 5000, 3.2.3), you must use them in your answer
        4) The answer must be logically correct."""
        if history == '':
            SECOND_SYSTEM_PROMPT += f' Previous user questions were {history}'
        
        documents = [{"doc_id": 0,"title": baza_questions[0],"content": baza_answers[0]},
                     {"doc_id": 1,"title": baza_questions[1],"content": baza_answers[1]},
                     {"doc_id": 2,"title": baza_questions[2],"content": baza_answers[2]},
                     {"doc_id": 3,"title": '',"content": csv[0]}]
        
        if txt != None:
            documents.append({"doc_id": 4,"title": '',"content": txt[0]})
        document_content = json.dumps(documents, ensure_ascii=False)
        
        first_prompt = system_prompt_template.format(
            system_prompt=FIRST_SYSTEM_PROMPT,
            documents=document_content,
            question=question
        )
        
        messages = [{"role": "system", "content": first_prompt}]
        outputs = self.llm.chat(messages=messages, sampling_params=sampling_params)
        relevant_indexes = json.loads(outputs[0].outputs[0].text)['relevant_doc_ids']
        if relevant_indexes == []:
            return 'К сожалению я не могу ответить на ваш вопрос. Попробуйте переформулировать его и задать снова'
        else:
            category = self.category_predict(question)
            filtered_documents = [doc for doc in documents if doc['doc_id'] in relevant_indexes]
            filtered_document_content = json.dumps(filtered_documents, ensure_ascii=False)
            final_prompt = system_prompt_template.format(
                            system_prompt=SECOND_SYSTEM_PROMPT,
                            documents=filtered_document_content,
                            question=question)
    
            messages = [{"role": "system", "content": final_prompt}]
            outputs = self.llm.chat(messages=messages, sampling_params=sampling_params)
            final_answer = outputs[0].outputs[0].text
    
            return final_answer + '\n\n' + f'Категория вопроса: {category}'


    def generate_answer(self, query, history):
        # Генерация ответа 
        torch.cuda.empty_cache()
        baza_questions, baza_answers, csv, txt = self.generate_context(query)
        answer = self.llm_question_answer(query, baza_questions, baza_answers, csv, txt, history)

        return answer 
