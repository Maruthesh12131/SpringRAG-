from fastapi import FastAPI
from pydantic import BaseModel
from app.query import answer_question
from fastapi import Request
import json
app = FastAPI()


class QuestionRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "RAG API is running"}

@app.post("/ask")
async def question(request: Request):
    print(request)
    body = await request.body()
    print("RAW BODY:", body)
    data = json.loads(body.decode("utf-8"))
    answer = answer_question(data["question"])
    return {
        "answer": answer 
    }
    # return {
    #     "received": body.decode("utf-8")
    # }