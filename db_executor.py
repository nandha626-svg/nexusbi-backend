import duckdb
import pandas as pd

def run_query(sql: str, db_path="data/sales.db"):
    try:
        con = duckdb.connect(db_path, read_only=True)
        df = con.execute(sql).df()
        con.close()
        return df, None
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    sql = "SELECT Category, SUM(Sales) as Total_Sales FROM sales GROUP BY Category ORDER BY Total_Sales DESC"
    df, err = run_query(sql)
    if err:
        print("Error:", err)
    else:
        print(df)