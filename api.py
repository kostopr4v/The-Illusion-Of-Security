from fastapi import FastAPI, Request
from pydantic import BaseModel
from vllm import LLM
from vllm.sampling_params import SamplingParams
from retriever import RetrieverLLM
import uvicorn
import torch

app = FastAPI()
retriever = RetrieverLLM()

class QueryRequest(BaseModel):
    query: str
    history: str

@app.post("/predict")
async def predict(request: QueryRequest):
    print(request)
    query = request.query
    history = request.history
    result_text = retriever.generate_answer(query, history)
    return {"output": result_text}

@app.post("/remakefilesdatabase")
async def predict():
    retriever.make_text_faiss()
    return True