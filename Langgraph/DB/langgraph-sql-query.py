from langgraph.graph import Graph, END, START
from langgraph.graph import StateGraph
from sqlalchemy import create_engine, text

# Set up the database engine
DATABASE_URL = "sqlite:///example.db"  # Replace with your DB URL
engine = create_engine(DATABASE_URL, echo=True)

# Query function
def run_sql_query(query: str):
    with engine.connect() as connection:
        result = connection.execute(text(query))
        return result.fetchall()

# LangGraph Node: Executes SQL query
def query_db_node(query: str):
    return run_sql_query(query)

# LangGraph Node: Formats the result
def format_result(results):
    return f"Query returned {len(results)} rows."

# Create the LangGraph state graph
graph = Graph()

# Add nodes to the graph
graph.add_node("query_db", query_db_node)
graph.add_node("format_result", format_result)

# Connect nodes: Start -> query_db -> format_result -> END
graph.add_edge(START, "query_db")
graph.add_edge("query_db", "format_result")
graph.add_edge("format_result", END)

# Generate SQL query based on the user's query
def generate_query(query: str):
    if "orders" in query and "customer" in query:
        return "SELECT customer_id, COUNT(*) AS order_count FROM orders GROUP BY customer_id"
    elif "products" in query and "prices" in query:
        return "SELECT name, price FROM products"
    else:
        return "SELECT * FROM orders"  # Default query

# User query
user_query = "How many orders were placed by each customer?"
user_query1 = "What were the orders placed by each customer?"

# Generate SQL query based on the user input
sql_query = generate_query(user_query)
sql_query1 = generate_query(user_query1)

# Run the LangGraph
app = graph.compile()

final_result = app.invoke(sql_query)
print(final_result)

new_res = app.invoke(sql_query1)
print(new_res)