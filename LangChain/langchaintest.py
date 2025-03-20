from langchain_ollama.llms import OllamaLLM
import pandas as pd

# Initialize the Ollama LLM
llm = OllamaLLM(model="deepseek-r1:7b")

def analyze_data(df, query):
  """
  Analyzes the DataFrame based on the provided query using the Ollama model.
  
  Parameters:
  - df: Pandas DataFrame containing the data.
  - query: A string query describing the analysis to perform.
  
  Returns:
  - Response from the Ollama model.
  """
  # Convert DataFrame to a string representation
  data_str = df.to_string(index=False)
  
  # Define the prompt
  prompt = f"Here is the dataset:\n{data_str}\n\nQuery: {query}"
  
  # Generate a response
  response = llm.invoke(prompt)
  
  return response


def identify_tables_with_llm(query, schema, foreign_keys):
  """
  Uses an LLM to identify relevant tables for a given query based on the database schema.
  
  Parameters:
  - query: The user's query as a string.
  - schema: A dictionary representing the database schema.
  
  Returns:
  - A list of table names that are relevant to the query.
  """
  # system_prompt = "Please answer this query but giving out a json List of ONLY table names like the following example { [ 'table1', 'table2'] }, or a None in case of any error or failure case"
  # Convert the schema to a string representation
  schema_str = "\n".join([f"{table}: {', '.join(columns)}" for table, columns in schema.items()])
  
  # Define the prompt for the LLM
  # prompt = f"Database Schema:\n{schema_str}\n\nQuery: {query}\n\nWhich tables are required to answer this query?"

  prompt = f"Database Schema:\n{schema_str}\nForeign Keys: \n{foreign_keys} \n\n{few_shot_table_names()}\n\nQ: {query} \n\nGive me the required table for the above query?"
  # onlyAnswerQuery  = f"{system_prompt}\n\nUser: {prompt}\nAI:"
  
  # Generate a response using the LLM
  response = llm.invoke(prompt)
  
  # Extract table names from the response
  tables = [response.split('</think>')[1]] 
  
  return tables


def few_shot_table_names():
    examples = """
    Q: How many orders were placed by each customer?
    A: {"required_tables": ["customers", "orders"]}

    Q: List all products with their prices.
    A: {"required_tables": ["products"]}

    Q: What is the total quantity ordered for each product?
    A: {"required_tables": ["products", "order_items"]}

    Q: Which products have less than 10 items in stock?
    A: {"required_tables": ["products"]}

    Q: What is the total revenue generated from each product?
    A: {"required_tables": ["products", "order_items"]}

    Q: List all customers who have placed more than five orders.
    A: {"required_tables": ["customers", "orders"]}

    Q: What is the average order value for each customer?
    A: {"required_tables": ["customers", "orders"]}

    Q: Which product categories have generated the most revenue?
    A: {"required_tables": ["categories", "products", "product_categories", "order_items"]}

    Q: How many products are there in each category?
    A: {"required_tables": ["categories", "product_categories"]}

    Q: What is the total revenue generated each month?
    A: {"required_tables": ["orders"]}
    """
    return examples


# database_schema = {
#   "customers": ["customer_id", "name", "email"],
#   "orders": ["order_id", "customer_id", "product_id", "quantity"],
#   "products": ["product_id", "name", "price"]
# }

database_schema = {
    "customers": ["customer_id", "name", "email", "address"],
    "products": ["product_id", "name", "description", "price", "stock_quantity"],
    "orders": ["order_id", "customer_id", "order_date", "total_amount"],
    "order_items": ["order_item_id", "order_id", "product_id", "quantity", "price"],
    "categories": ["category_id", "name"],
    "product_categories": ["product_id", "category_id"]
}

foreign_keys = {
    "orders": {"customer_id": "customers.customer_id"},
    "order_items": {
        "order_id": "orders.order_id",
        "product_id": "products.product_id"
    },
    "product_categories": {
        "product_id": "products.product_id",
        "category_id": "categories.category_id"
    }
}


# queries = [
#   # "How many orders were placed by each customer?",
#   # "List all products with their prices.",
#   "What is the total quantity ordered for each product?"
# ]

queries = [
    # "How many orders were placed by each customer?",
    "List all products with their prices.",
    # "What is the total quantity ordered for each product?",
    # "Which products have less than 10 items in stock?",
    # "What is the total revenue generated from each product?",
    # "List all customers and their details who have placed more than five orders.",
    # "What is the average order value for each customer?",
    "Which product categories have generated the most revenue?",
    "How many products are there in each category?",
    # "What is the total revenue generated each month?"
]


# Identify relevant tables for each query
for q in queries:
  tables = identify_tables_with_llm(q, database_schema, foreign_keys)
  print(f"Query: {q}")
  print(f"Relevant tables: {tables}\n")

# # Define the analysis query
# query = "Which product has the highest sales?"
# result = analyze_data(df, query)
# print(result)


# # Test the connection with a simple prompt
# response = llm("what is teh capital f france")
# print(response)