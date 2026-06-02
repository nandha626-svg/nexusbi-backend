import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd

load_dotenv()

llm = ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0.3,
    max_tokens=600
)

ANSWER_PROMPT = ChatPromptTemplate.from_template("""
You are a business analyst explaining data insights clearly and concisely.

USER QUESTION: {question}

SQL QUERY USED: {sql}

QUERY RESULTS:
{results}

Write a clear 2-4 sentence business insight answering the question.
Be specific with numbers. Highlight the most important finding.
Do not mention SQL or technical details.
""")

answer_chain = ANSWER_PROMPT | llm | StrOutputParser()

def generate_answer(question: str, sql: str, df: pd.DataFrame) -> str:
    results_str = df.head(20).to_string(index=False)
    return answer_chain.invoke({
        "question": question,
        "sql": sql,
        "results": results_str
    })

if __name__ == "__main__":
    import pandas as pd
    sample_df = pd.DataFrame({
        "Category": ["Furniture", "Office Supplies", "Technology"],
        "Total_Sales": [1358609.40, 304146.44, 289305.51]
    })
    sql = "SELECT Category, SUM(Sales) FROM sales GROUP BY Category"
    question = "Which category has the highest sales?"
    print(generate_answer(question, sql, sample_df))