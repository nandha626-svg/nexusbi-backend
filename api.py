from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pipeline import ask_question
import duckdb
from datetime import datetime

app = FastAPI(
    title="RAG BI Chatbot API",
    description="Ask business questions in plain English and get AI-generated insights from live sales data",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"
    "https://nexusbi-frontend-three.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QuestionRequest(BaseModel):
    question: str

# Response model
class QuestionResponse(BaseModel):
    question: str
    sql: str
    answer: str
    rows: list
    row_count: int
    timestamp: str

@app.get("/")
def root():
    return {
        "message": "RAG BI Chatbot API is running!",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    try:
        con = duckdb.connect("data/sales.db", read_only=True)
        count = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        latest = con.execute("SELECT Order_Date FROM sales ORDER BY Order_Date DESC LIMIT 1").fetchone()[0]
        con.close()
        return {
            "status": "healthy",
            "total_orders": count,
            "latest_order": str(latest),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    result = ask_question(request.question)

    if result["error"]:
        raise HTTPException(status_code=500, detail=result["error"])

    # Convert dataframe to list of dicts
    rows = result["data"].to_dict(orient="records") if result["data"] is not None else []

    return QuestionResponse(
        question=request.question,
        sql=result["sql"],
        answer=result["answer"],
        rows=rows,
        row_count=len(rows),
        timestamp=datetime.now().isoformat()
    )

@app.get("/stats")
def get_stats():
    try:
        con = duckdb.connect("data/sales.db", read_only=True)
        total_orders = con.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        total_revenue = con.execute("SELECT ROUND(SUM(Sales), 2) FROM sales").fetchone()[0]
        total_profit = con.execute("SELECT ROUND(SUM(Profit), 2) FROM sales").fetchone()[0]
        top_category = con.execute("SELECT Category FROM sales GROUP BY Category ORDER BY SUM(Sales) DESC LIMIT 1").fetchone()[0]
        con.close()
        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "top_category": top_category,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))