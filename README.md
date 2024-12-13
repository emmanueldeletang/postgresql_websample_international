# postgresql_websample_international
Flask web app to show the integration with translation to store data and show in multi langage using artifficial intelligence service to help to load , search all in multi langage 


## Features
- web applicaiton to insert book in your langage 
- visualisation of the book with translation in postgresql to show the integration with translation
- add a search engine using the search capacity of vector search in postgreql with adding vector and automation llm
- add the completions in a cache table and if the same question is ask , use the cache ( first question can take seconds , the same some ms ) 


## Requirements
- Tested only with Python 3.12
- Azure Translator service
- azure openAI services with a textembedding model and Gpt model to enable the search 
- Azure Postgresql flexible server


## Setup

- in postgresql run the pgsql script (initextension.psql)
- Create virtual environment: python -m venv .venv
- Activate virtual ennvironment: .venv\scripts\activate
- Install required libraries: pip install -r python-dotenv Flask psycopg2-binary openai
- Replace keys with your own values in example.env
- make sure the templates with the jinja is present ... 
- run python init_db.py
- run python app.py
