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
    session.add_all([Customer(name="Jacob Peralta"), Customer(name="Igor Karkaroff")])
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
       Ensure to specify table names for all the columns that appear in multiple tables.    
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
    result = session.execute(sql_query)  # Execute raw SQL
    column_names = [col[0] for col in result.cursor.description]  # Get column names from the result description
    rows = result.fetchall()  # Fetch the result rows
    result_data = []
    for row in rows:
        row_data = dict(zip(column_names, row))  # Create a dictionary with column names as keys
        formatted_row = ', '.join([f"{key}: {value}" for key, value in row_data.items()])
        result_data.append(formatted_row)

    # Convert to string and pass to Ollama model for formatting
    formatted_data = "\n".join(result_data)
    return formatted_data
    # return format_output_with_llm(formatted_data)



# Use LLM to format the output of the query
def format_output_with_llm(formatted_data):
    message = f"""
    Below are the results from the query:

    {formatted_data}

    Please format the above information into a well-structured, human-readable report. 
    The result can vary in structure, so format it in a flexible, readable manner. Ensure clarity and readability in the output.
    Give the output in a key, value pairs for each Column Name and its value in a JSON format like so. I want it in a response block:
    
    \'"{{\"response\": [{{\"country\": \"France\", \"capital\": \"Paris\"}}, {{\"country\": \"Germany\", \"capital\": \"Berlin\"}}], \"...\": \"More countries can be added here\"}}\'"
    """
    # Give ONLY the output in a JSON format.
    print(formatted_data)
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

# Query to select all rows from the Customer table
customers = session.query(Customer).all()

# Query to select all rows from the Order table
orders = session.query(Order).all()

# Print the results
for customer in customers:
    print(customer.customer_id, customer.name)  # Adjust according to your model fields

for order in orders:
    print(order.order_id, order.customer_id)  # Adjust according to your model fields

# Run the LangGraph with the user query
app = graph.compile()

# Execute the query with session passed to the graph
result = app.invoke(query)  # No need to pass session here

# Print the result
print(result)
