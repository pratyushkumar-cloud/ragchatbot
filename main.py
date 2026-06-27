from fastapi import FastAPI
from pydantic import BaseModel
from src.qa import answer_query

app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Query):
    return answer_query(q.question)
