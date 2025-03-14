import re

from sqlalchemy import create_engine, Column, Integer, String, func, text
from sqlalchemy.orm import declarative_base, sessionmaker
import ollama
from langgraph.graph import Graph, START, END
import json

# Define the database URL (Using SQLite for simplicity)
DATABASE_URL = "sqlite:///example.db"

# Initialize the database engine
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()


# Define the `Customer` and `Order` tables
class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer)
    order_date = Column(String)


# Create tables in the database
Base.metadata.create_all(engine)

# Set up session for database interaction
Session = sessionmaker(bind=engine)

# Adding some sample data (only if the database is empty)
session = Session()
if not session.query(Customer).first():
    session.add_all([Customer(name="John Doe"), Customer(name="Jane Smith")])
    session.commit()

if not session.query(Order).first():
    session.add_all([
        Order(customer_id=1, order_date="2023-03-01"),
        Order(customer_id=1, order_date="2023-03-02"),
        Order(customer_id=2, order_date="2023-03-03")
    ])
    session.commit()


# Extract schema from the database
def extract_schema(session):
    schema_info = {}
    # Get all tables and their columns from Base.metadata
    for table in Base.metadata.tables.values():
        schema_info[table.name] = [column.name for column in table.columns]
    return schema_info


# Ollama integration to generate SQL from query using DeepSeek model
def ollama_generate_sql_with_deepseek(query: str, schema: dict):
    # Convert the schema to a string representation
    schema_str = "\n".join([f"Table: {table}, Columns: {', '.join(columns)}" for table, columns in schema.items()])

    # Construct the message to pass to DeepSeek model
    message = f"""
       Database schema:
       {schema_str}

       User Query: {query}
       Generate only the SQL query. Do **not** provide any explanations, reasoning, or additional commentary. 
        Return **ONLY** the SQL query in the following format:

    \'{{\"query\": \"SELECT ...\"}}\'"
    """

    # Use the DeepSeek model from Ollama
    response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": message}])
    # print(response)
    clean_content = re.sub(r'<think>.*?</think>', '', response['message']['content'], flags=re.DOTALL).strip()
    parsed_resp = json.loads(clean_content)
    return parsed_resp['query']

# LangGraph Workflow to process the query
def process_query(query, session):
    # Extract schema from the database
    schema = extract_schema(session)

    # Generate SQL using Ollama DeepSeek model
    sql_query = ollama_generate_sql_with_deepseek(query, schema)
    print("Generated SQL Query:", sql_query)
    return sql_query


# Execute the generated SQL query using SQLAlchemy session
def execute_dynamic_query(sql, session):
    sql_query = text(sql)
    result = session.execute(sql_query).fetchall()  # Execute raw SQL

    # If result is empty, handle that case
    if not result:
        return result, []

    # Try to extract column names dynamically from the result description (from SQLAlchemy)
    column_names = []
    if result:
        # Access column names using description attribute
        column_names = [desc['name'] for desc in result.cursor.description]

    return result, column_names


# Format the output
def format_output(result):
    output = "\nQuery Result:\n"
    # Iterate over result to handle output properly
    for row in result:
        customer_id, customer_name, order_count = row
        output += f"Customer ID: {customer_id}, Name: {customer_name}, Orders Placed: {order_count}\n"
    return output


# Use LLM to format the output of the query
def format_output_with_llm(result, column_names):
    print(column_names)
    # Prepare the data as a string to pass to LLM for formatting
    result_data = []
    for row in result:
        row_data = dict(zip(column_names, row))  # Create a dictionary with column names as keys
        formatted_row = ', '.join([f"{key}: {value}" for key, value in row_data.items()])
        result_data.append(formatted_row)

    # Convert to string and pass to Ollama model for formatting
    formatted_data = "\n".join(result_data)
    message = f"""
    Below are the results from the query:

    {formatted_data}

    Please format the above information into a well-structured, human-readable report. 
    The result can vary in structure, so format it in a flexible, readable manner. Ensure clarity and readability in the output.
    """

    # Call the LLM for formatting
    response = ollama.chat(model="deepseek-r1:7b", messages=[{"role": "user", "content": message}])
    formatted_output = response['message']['content']
    return formatted_output

# Set up LangGraph Workflow
graph = Graph()

# Add nodes to the workflow
graph.add_node("process_query", lambda query: process_query(query, session))  # Pass session here
graph.add_node("execute_dynamic_query", lambda sql: execute_dynamic_query(sql, session))  # Pass session here
graph.add_node("format_output", format_output_with_llm)

# Connect the nodes (task flow)
graph.add_edge(START, "process_query")
graph.add_edge("process_query", "execute_dynamic_query")
graph.add_edge("execute_dynamic_query", "format_output")
graph.add_edge("format_output", END)

# Test with a user query
query = "How many orders were placed by each customer? I want both the customer details like name, customer ID and the order count"

# Run the LangGraph with the user query
app = graph.compile()

# Execute the query with session passed to the graph
result = app.invoke(query)  # No need to pass session here

# Print the result
print(result)
