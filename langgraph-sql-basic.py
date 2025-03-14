import sqlite3
from langgraph.graph import END, StateGraph, START, Graph
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_ollama.llms import OllamaLLM

import re

# Define the schema for the relevant tables
schema = {
    "customers": ["customer_id", "name", "email", "address"],
    "products": ["product_id", "name", "description", "price", "stock_quantity"],
    "orders": ["order_id", "customer_id", "order_date", "total_amount"],
    "order_items": ["order_item_id", "order_id", "product_id", "quantity", "price"],
    "categories": ["category_id", "name"],
    "product_categories": ["product_id", "category_id"]
}

# Step 1: Set up the LLM
llm = OllamaLLM(model="deepseek-r1:7b")

# Define a prompt template for identifying relevant tables from the user query
prompt_template = PromptTemplate(
    input_variables=["query", "schema"],
    template="""
    Given the following schema and user query, **output the result as a dictionary** where:
    - The **key** is the query.
    - The **value** is a list of the relevant table names for that query.
    Do **not provide any reasoning, explanations, or any extra text**. Only output the dictionary.

    **Example 1:**
    Query: "How many orders were placed by each customer?"
    Relevant Tables: \'{{\'How many orders were placed by each customer?\': [\'orders\', \'customers\']}}\'
    

    Schema:
    {schema}

    Query:
    {query}
    """
)

# Create an LLMChain to process the query with the schema
llm_chain = prompt_template | llm


# Step 2: Define the function to process the query using LangChain and LLM
def get_relevant_tables(query: str):
    # Run the LLMChain to get the relevant tables based on the schema and query
    result = llm_chain.invoke({"query": query, "schema": str(schema)})
    return result.strip().split("\n")


# Step 3: Define a LangGraph workflow that uses the LLM to identify relevant tables
def build_langgraph_workflow(query: str):
    graph = Graph()

    # Task 1: Extract relevant tables using the LLM
    graph.add_node("extract_relevant_tables", lambda _: get_relevant_tables(query))

    graph.add_edge(START, "extract_relevant_tables")
    graph.add_edge("extract_relevant_tables", END)

    return graph


# Step 4: Run the LangGraph workflow
def run_workflow(query: str):
    graph = build_langgraph_workflow(query)
    app = graph.compile()
    result = app.invoke(query)  # Start the graph
    tables = [result]
    return tables


# Example user query
# user_query = "Which product categories have generated the most revenue?"

queries = [
    "How many orders were placed by each customer?",
    "List all products with their prices.",
    "What is the total quantity ordered for each product?",
    "Which products have less than 10 items in stock?",
    "What is the total revenue generated from each product?",
    "List all customers and their details who have placed more than five orders.",
    "What is the average order value for each customer?",
    "Which product categories have generated the most revenue?",
    "How many products are there in each category?",
    "What is the total revenue generated each month?"
]

# Get the relevant tables based on the query
for q in queries:
    relevant_tables = run_workflow(q)
    tables = relevant_tables[-1][-1]
    print(f"Query : {q}")
    print(f"Relevant Tables: {tables}")