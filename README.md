# DataAnalyticsLangChain

## Pre-Requisites
The following packages are required to run:
```
langgraph
langchain
langchain_ollama
```


### Running the model locally

- Download Ollama LLM - https://ollama.com/
- Pull the DeepSeek model locally using 
```
ollama pull deepseek-r1:1.5b
```

### improvements to make

- update DBUtils methods to have LastEvaluatedKey and startKey functionality, so agent is able to scan through all the entries as required

### final objective

- A data analytics agent, that has modular tools (dynamoDB scan, query etc), that is able to fetch required entries and give out a parsed table or data entry based on the user's query.