import os  # Import the os module for interacting with the operating system
import psycopg2  # Import the psycopg2 module to connect to PostgreSQL databases
from dotenv import dotenv_values  # Import the dotenv_values function to load environment variables from a .env file

# Load environment variables from .env file
env_name = "example.env" # following example.env template change to your own .env file name
config = dotenv_values(env_name)

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=config['pgdbname'],
    user=config['pguser'],
    password=config['pgpassword'],
    host=config['pghost'],
    port=config['pgport']
)
cur = conn.cursor()

# Execute a command: this creates a new table



cur.execute('DROP TABLE IF EXISTS books;')
cur.execute('CREATE TABLE books (id serial PRIMARY KEY,'
                                 'title varchar (150) NOT NULL,'
                                 'author varchar (50) NOT NULL,'
                                 'pages_num integer NOT NULL,'
                                 'review text,'
                                 'date_added date DEFAULT CURRENT_TIMESTAMP);'
                                 )

# Insert data into the table
cur.execute('INSERT INTO books (title, author, pages_num, review)'
            'VALUES (%s, %s, %s, %s)',
            ('le rouge et le noir',
             'Stendhal',
             489,
             'Le roman est divisé en deux parties : la première partie retrace le parcours de Julien Sorel en province, dans une petite ville nommée Verrières, en Franche-Comté puis à Besançon, et plus précisément son entrée chez les Rênal, et sa passion pour Mme de Rênal, de même que son séjour dans un séminaire ; la seconde partie porte sur la vie du héros à Paris comme secrétaire du marquis de La Mole, et la passion qu il a avec sa fille, Mathilde.')
            )

cur.execute('INSERT INTO books (title, author, pages_num, review)'
            'VALUES (%s, %s, %s, %s)',
            ('Le grand livre du Rugby',
             'Jérôme Bureau (Auteur), Patrick Lemoine (Auteur) ',
             154,
             'C est en 1823 qu un jeune homme nommé William Webb Ellis a eu la belle idée, au cours d une partie de  football ,  de prendre le ballon avec les mains sur un terrain du collège de la ville  de Rugby, en Angleterre, et d  inventer  ainsi un sport.C est une fantastique aventure que nous vous racontons ici, des premiers matchs improvisés dans les collèges anglais jusqu C’est en 1823 qu’un jeune homme nommé William Webb Ellis a eu la belle idée, au cours d’une partie de « football »,  de prendre le ballon avec les mains sur un terrain du collège de la ville  de Rugby, en Angleterre, et d  inventer  ainsi un sport.')
            )

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()