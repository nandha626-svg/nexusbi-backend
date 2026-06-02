import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from sql_generator import generate_sql
from db_executor import run_query
from answer_generator import generate_answer
from schema_reader import get_schema_context

load_dotenv()

# Define the state — this is what gets passed between agents
class AgentState(TypedDict):
    question: str
    sql: str
    data: object
    answer: str
    error: str
    retry_count: int
    steps: list

# ── Agent 1: SQL Generator ──────────────────────────────
def sql_agent(state: AgentState) -> AgentState:
    print(f"[SQL Agent] Generating SQL for: {state['question']}")
    try:
        sql = generate_sql(state["question"])
        state["sql"] = sql
        state["steps"].append(f"SQL Agent: Generated → {sql[:60]}...")
        print(f"[SQL Agent] Generated: {sql[:80]}")
    except Exception as e:
        state["error"] = str(e)
        state["steps"].append(f"SQL Agent: Failed → {str(e)}")
    return state

# ── Agent 2: Query Executor ─────────────────────────────
def executor_agent(state: AgentState) -> AgentState:
    print(f"[Executor Agent] Running SQL...")
    df, error = run_query(state["sql"])
    if error:
        state["error"] = error
        state["steps"].append(f"Executor Agent: Failed → {error}")
        print(f"[Executor Agent] Error: {error}")
    else:
        state["data"] = df
        state["error"] = None
        state["steps"].append(f"Executor Agent: Success → {len(df)} rows returned")
        print(f"[Executor Agent] Success: {len(df)} rows")
    return state

# ── Agent 3: SQL Repair ─────────────────────────────────
def repair_agent(state: AgentState) -> AgentState:
    print(f"[Repair Agent] Fixing SQL... (attempt {state['retry_count'] + 1})")
    
    llm = ChatAnthropic(model="claude-haiku-4-5", temperature=0, max_tokens=500)
    schema = get_schema_context()
    
    repair_prompt = f"""
The following SQL query failed with this error:

SQL: {state['sql']}
Error: {state['error']}

Database schema:
{schema}

Write a corrected DuckDB SQL query. Return ONLY the SQL, nothing else.
"""
    response = llm.invoke([HumanMessage(content=repair_prompt)])
    fixed_sql = response.content.strip()
    
    state["sql"] = fixed_sql
    state["retry_count"] += 1
    state["error"] = None
    state["steps"].append(f"Repair Agent: Fixed SQL → {fixed_sql[:60]}...")
    print(f"[Repair Agent] Fixed: {fixed_sql[:80]}")
    return state

# ── Agent 4: Answer Generator ───────────────────────────
def answer_agent(state: AgentState) -> AgentState:
    print(f"[Answer Agent] Generating insight...")
    try:
        answer = generate_answer(
            state["question"],
            state["sql"],
            state["data"]
        )
        state["answer"] = answer
        state["steps"].append(f"Answer Agent: Generated insight successfully")
        print(f"[Answer Agent] Done")
    except Exception as e:
        state["error"] = str(e)
        state["steps"].append(f"Answer Agent: Failed → {str(e)}")
    return state

# ── Router: decide what happens next ────────────────────
def should_retry(state: AgentState) -> str:
    if state.get("error") and state.get("retry_count", 0) < 2:
        print(f"[Router] Error detected, routing to repair agent...")
        return "repair"
    elif state.get("error"):
        print(f"[Router] Max retries reached, ending...")
        return "end"
    else:
        return "answer"

# ── Build the Graph ─────────────────────────────────────
def build_agent():
    workflow = StateGraph(AgentState)

    # Add all agents as nodes
    workflow.add_node("sql_agent", sql_agent)
    workflow.add_node("executor_agent", executor_agent)
    workflow.add_node("repair_agent", repair_agent)
    workflow.add_node("answer_agent", answer_agent)

    # Define the flow
    workflow.set_entry_point("sql_agent")
    workflow.add_edge("sql_agent", "executor_agent")

    # After executor: decide to repair, answer, or end
    workflow.add_conditional_edges(
        "executor_agent",
        should_retry,
        {
            "repair": "repair_agent",
            "answer": "answer_agent",
            "end": END
        }
    )

    # After repair: try executing again
    workflow.add_edge("repair_agent", "executor_agent")
    workflow.add_edge("answer_agent", END)

    return workflow.compile()

# ── Main function to use in pipeline ────────────────────
def ask_with_agent(question: str) -> dict:
    agent = build_agent()

    initial_state = AgentState(
        question=question,
        sql="",
        data=None,
        answer="",
        error=None,
        retry_count=0,
        steps=[]
    )

    final_state = agent.invoke(initial_state)

    return {
        "question": question,
        "sql": final_state["sql"],
        "data": final_state["data"],
        "answer": final_state["answer"],
        "error": final_state.get("error"),
        "steps": final_state["steps"]
    }

# ── Test it ──────────────────────────────────────────────
if __name__ == "__main__":
    questions = [
        "Which region has the highest profit?",
        "What are the top 3 categories by total sales?",
    ]

    for q in questions:
        print("\n" + "="*60)
        print(f"QUESTION: {q}")
        print("="*60)
        result = ask_with_agent(q)
        print(f"\nSTEPS TAKEN:")
        for step in result["steps"]:
            print(f"  → {step}")
        print(f"\nANSWER: {result['answer']}")