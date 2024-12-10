# postgresql_websample_international
Flask web app to show the integration with translation to store data and show in multi langage using native API 


## Features
- web applicaiton to insert book in your langage 
- visualisation of the book with translation in postgresql to show the integration with translation


## Requirements
- Tested only with Python 3.12
- Azure Translator service 
- Azure Postgresql flexible server


## Setup

- in postgresql run the pgsql script (initextension.psql)
- Create virtual environment: python -m venv .venv
- Activate virtual ennvironment: .venv\scripts\activate
- Install required libraries: pip install -r python-dotenv Flask psycopg2-binary
- Replace keys with your own values in example.env
- make sure the templates with the jinja is present ... 
- run python init_db.py
- run python app.py
