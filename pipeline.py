from sql_generator import generate_sql
from db_executor import run_query
from answer_generator import generate_answer

def ask_question(question: str) -> dict:
    """
    Full RAG pipeline: question → SQL → data → answer
    """
    # Step 1: Generate SQL from question
    print(f"Generating SQL for: {question}")
    sql = generate_sql(question)
    print(f"SQL: {sql}")

    # Step 2: Execute SQL
    print("Running query...")
    df, error = run_query(sql)

    if error:
        return {
            "sql": sql,
            "data": None,
            "answer": f"I couldn't run that query. Error: {error}",
            "error": error
        }

    # Step 3: Generate natural language answer
    print("Generating insight...")
    answer = generate_answer(question, sql, df)

    return {
        "sql": sql,
        "data": df,
        "answer": answer,
        "error": None
    }

if __name__ == "__main__":
    questions = [
        "Which region has the highest total profit?",
        "What are the top 3 products by total sales?",
        "Which segment places the most orders?"
    ]

    for q in questions:
        print("\n" + "="*60)
        print(f"QUESTION: {q}")
        print("="*60)
        result = ask_question(q)
        print(f"\nANSWER: {result['answer']}")
        print(f"\nDATA:\n{result['data']}")