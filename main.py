from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from src.qa import answer_query

app = FastAPI()

class Query(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    source: str
    document: Optional[str] = ""
    page: Optional[str] = ""
    publisher: Optional[str] = ""
    last_updated: Optional[str] = ""

@app.post("/ask")
def ask(q: Query) -> AnswerResponse:
    """Process a question and return grounded answer with source citation"""
    return answer_query(q.question)
