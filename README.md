# DataAnalyticsLangChain

## Pre-Requisites
The following packages are required to run:
```
langgraph
langchain
langchain_ollama
```
### Setup local dynamodb 
JRE should be installed prior to this
Install Dynamob .zip from http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html
Extract the zip file 
Go to the directory where file is extracted and Run the below commands
cd dynamodb_local_latest
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb

This will start Dynamodb locally on http://localhost:8000 (This is just the api endpoint)
For Ui install NoSQL workbench (straightforward)
To connect NoSQL workbench with dynamodb
Go to Operation Builder > Add connenction > DynamoDB local  (Hit Connect)

### Running the model locally

- Download Ollama LLM - https://ollama.com/
- Pull the model locally using 
```
ollama pull <model-name>
```
Example
```
ollama pull deepseek-r1:1.5b
```
