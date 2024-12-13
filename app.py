import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect
from dotenv import dotenv_values
from openai import AzureOpenAI
import time


env_name = "example.env" # following example.env template change to your own .env file name
config = dotenv_values(env_name)

# Connect to PostgreSQL

openai_endpoint = config['openai_endpoint']
openai_key = config['openai_key']
openai_version = config['openai_version']
openai_chat_model = config['AZURE_OPENAI_CHAT_MODEL']

openai_client = AzureOpenAI(
  api_key = openai_key,  
  api_version = openai_version,  
  azure_endpoint =openai_endpoint 
)

app = Flask(__name__)
"""
    Establish a connection to the PostgreSQL database using credentials from the config.
    Returns the connection object.
"""
def get_db_connection():
    conn = psycopg2.connect(
        dbname=config['pgdbname'],
        user=config['pguser'],
        password=config['pgpassword'],
        host=config['pghost'],
        port=config['pgport'])
    return conn


"""
    Handle the POST request to set the language preference.
    Retrieves the language from the form data, sets a cookie with the language,
    and redirects to the index page.
"""

@app.route('/set_language', methods=['POST'])
def set_language():
    language = request.form['language']
    response = redirect(url_for('index'))
    response.set_cookie('language', language)
    return response


"""
    Handle the GET and POST requests for the index page.
    Retrieves the language preference from cookies or form data,
    establishes a database connection, and renders the index page.
"""
@app.route('/about', methods=('GET', 'POST'))
def about():
    return render_template('about.html')


def get_completion(openai_client, model, prompt: str):    
   
    
    response = openai_client.chat.completions.create(
        model = model,
        messages =   prompt,
        temperature = 0.1
    )   
    
    
    return response.model_dump()

def  ask_dbvector(textuser):  
    
    conn = get_db_connection()
    cur = conn.cursor()
    query = f"""SELECT
     e.title, e.author, e.pages_num, e.review, e.date_added
    FROM books e  where e.dvector <=> azure_openai.create_embeddings('text-embedding-ada-002', ' """ + str(textuser) + """')::vector < 0.25  ORDER BY  e.dvector <=> azure_openai.create_embeddings('text-embedding-ada-002','""" + str(textuser) +"""')::vector  LIMIT 4;"""
 
    
    cur.execute(query)
    resutls = str(cur.fetchall())

    return resutls 

def generatecompletionede(user_prompt) -> str:
    
 
    system_prompt = f'''
    You are an AI assistant that is able to look for information in a book database , base on the review, title, author, and number of pages.
    .the answer should be in the language of the user's choice.the answer should be in the following format:
    title: <title>
    author: <author>
    review: <review>
    resume of the book: <review>
        '''     
    
    messages = [{'role': 'system', 'content': system_prompt}]
    #user prompt
    messages.append({'role': 'user', 'content': user_prompt})
    
    vector_search_results =  ask_dbvector(user_prompt)
    
    for result in vector_search_results:
     
        # res = result[ "title"] + result[ "author" ]+  result["review"] 
        messages.append({'role': 'system', 'content': result})
    
    response = get_completion(openai_client, openai_chat_model, messages)

    return response

def cacheresponse(user_prompt,  response ):

    
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO tablecahe (prompt, completion, completiontokens, promptTokens,totalTokens, model)'
                    'VALUES (%s, %s, %s, %s ,%s, %s)',
                    (user_prompt, response['choices'][0]['message']['content'], response['usage']['completion_tokens'], response['usage']['prompt_tokens'],response['usage']['total_tokens'], response['model']))
    


    print("item inserted into cache.")
    conn.commit()
    cur.close()
    conn.close()


def cachesearch(test):
    conn = get_db_connection()
    cur = conn.cursor()
    query = f"""SELECT e.completion
    FROM tablecahe e  where e.dvector <=> azure_openai.create_embeddings('text-embedding-ada-002', ' """ + str(test) + """')::vector > 0.01  ORDER BY  e.dvector <=> azure_openai.create_embeddings('text-embedding-ada-002','""" + str(test) +"""')::vector  LIMIT 1;"""
    
    cur.execute(query)
    resutls = cur.fetchall()

    return resutls

@app.route('/', methods=('GET', 'POST'))
def index():
    language = request.cookies.get('language', 'en')  # Default to 'en' if no language is set
    
    if request.method=='POST':
        language = request.form['language']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
        
    query = f"""SELECT a.id, (unnest(b.translations)).text as title, (unnest(c.translations)).text as author ,a.pages_num, (unnest(d.translations)).text as review , a.date_added  FROM books a, azure_cognitive.translate(title,'""" + language + """') b,  azure_cognitive.translate(author,'""" + language + """') c , azure_cognitive.translate(review,'""" + language + """') d"""
    
   
    
    cur.execute(query)
    books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', books=books)


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        pages_num = int(request.form['pages_num'])
        review = request.form['review']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO books (title, author, pages_num, review)'
                    'VALUES (%s, %s, %s, %s)',
                    (title, author, pages_num, review))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('create.html')



@app.route('/search/', methods=['GET', 'POST'])
def search():
   
    result2 = None
    if request.method == 'POST':
        user_prompt = request.form['prompt']
        cache_results = cachesearch(user_prompt)
        print(cache_results)
        start_time = time.time()
        if len(cache_results) > 0:
            
            result2 =  str(cache_results[0])
            end_time = time.time()
            elapsed_time = round((end_time - start_time) * 1000, 2)
            details = f"\n (Time: {elapsed_time}ms)" " (Cached)"
            result2 = result2 + details
        else:
           response = generatecompletionede(user_prompt)
           result2 = response['choices'][0]['message']['content']
           cacheresponse(user_prompt, response)
           end_time = time.time()
           elapsed_time = round((end_time - start_time) * 1000, 2)
           details = f"\n (Time: {elapsed_time}ms)"
           result2 = result2 +  details 
        
      
    return render_template('search.html',result2=result2 )


if __name__ == '__main__':
    app.run(debug=True)