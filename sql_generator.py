import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from schema_reader import get_schema_context

load_dotenv()

llm = ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0,
    max_tokens=500
)

SQL_PROMPT = ChatPromptTemplate.from_template("""
You are a SQL expert. Given a user question and database schema,
write a DuckDB SQL query to answer it.

DATABASE SCHEMA:
{schema}

USER QUESTION: {question}

Rules:
- Return ONLY the SQL query, nothing else
- No markdown, no explanation, no backticks
- Use column names exactly as shown in schema
- For date filtering use: Order_Date >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR
- For ranking/comparison questions return ALL groups, not just top 1
- Only use LIMIT 50 for product/order level queries
- Never use LIMIT 1
""")

sql_chain = SQL_PROMPT | llm | StrOutputParser()

def generate_sql(question: str) -> str:
    schema = get_schema_context()
    sql = sql_chain.invoke({
        "schema": schema,
        "question": question
    })
    return sql.strip()

if __name__ == "__main__":
    q = "What are the top 5 products by total sales?"
    print("Question:", q)
    print("\nGenerated SQL:")
    print(generate_sql(q))