from pydantic import BaseModel
from typing import Optional,List,Dict,Any

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

class QuizRequest(BaseModel):
    limit: int = 5
    objects: Optional[List[str]]= None  #ds cac vat lam quiz

class QuizResponse(BaseModel):
    success: bool = True
    questions: List[QuizQuestion]
    error: Optional[str] = None
