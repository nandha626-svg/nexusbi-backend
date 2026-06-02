import duckdb

def get_schema_context(db_path="data/sales.db"):
    con = duckdb.connect(db_path, read_only=True)
    result = con.execute("DESCRIBE sales").fetchall()
    con.close()

    schema_lines = [
        "Table: sales",
        "Columns:"
    ]
    for col in result:
        schema_lines.append(f"  - {col[0]} ({col[1]})")

    schema_lines.append("\nNotes:")
    schema_lines.append("  - Real-time sales orders, new rows added every 2 seconds")
    schema_lines.append("  - Order_Date is a TIMESTAMP column")
    schema_lines.append("  - Use DuckDB SQL syntax")
    schema_lines.append("  - Sales and Profit are DOUBLE (numeric)")
    schema_lines.append("  - Key columns: Category, Sub_Category, Region, State, Segment, Product_Name")

    return "\n".join(schema_lines)

if __name__ == "__main__":
    print(get_schema_context())