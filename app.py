import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect
from dotenv import dotenv_values


env_name = "example.env" # following example.env template change to your own .env file name
config = dotenv_values(env_name)

# Connect to PostgreSQL

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


@app.route('/', methods=('GET', 'POST'))
def index():
    language = request.cookies.get('language', 'en')  # Default to 'en' if no language is set
    
    if request.method=='POST':
        language = request.form['language']
    
    conn = get_db_connection()
    cur = conn.cursor()
    print (language)
        
    query = f"""SELECT a.id, (unnest(b.translations)).text as title, (unnest(c.translations)).text as author ,a.pages_num, (unnest(d.translations)).text as review , a.date_added  FROM books a, azure_cognitive.translate(title,'""" + language + """') b,  azure_cognitive.translate(author,'""" + language + """') c , azure_cognitive.translate(review,'""" + language + """') d"""
    
    print (query)
    
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


if __name__ == '__main__':
    app.run(debug=True)