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

cur.execute('DROP TABLE IF EXISTS tablecache;')

cur.execute('CREATE TABLE tablecahe (id serial PRIMARY KEY,'
                                 'prompt text  NOT NULL,'
                                 'completion text NOT NULL,'
                                 'completiontokens integer NOT NULL,'
                                 'promptTokens integer NOT NULL,'
                                 'totalTokens integer NOT NULL,'
                                 'model varchar(150) NOT NULL,'   
                                 'date_added date DEFAULT CURRENT_TIMESTAMP);'
        )


cmd = """ALTER TABLE tablecahe  ADD COLUMN dvector vector(1536)  GENERATED ALWAYS AS ( azure_openai.create_embeddings('text-embedding-ada-002', prompt)::vector) STORED; """
cur.execute(cmd)

cm = """CREATE INDEX indextablevector ON tablecahe USING hnsw (dvector vector_l2_ops) WITH (m = 16, ef_construction = 64);"""
cur.execute(cm)

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

cur.execute('INSERT INTO books (title, author, pages_num, review)'
            'VALUES (%s, %s, %s, %s)',
           ('Bàrnabo delle montagne (italiano)',
             'Dino Buzzati',
             132,
             'i suoi compagni e si nasconde. Una volta terminato lassalto, in cui Bertòn rimane ferito ad una gamba, Bàrnabo ritorna dai guardaboschi. Non riuscendo a giustificare la propria assenza, il giovane viene licenziato e scacciato. Amareggiato, si reca dal cugino in campagna e lavora  come contadino. Ma lex-guardaboschi ha nostalgia delle montagne e rimpiange la sua vita passata. Passano alcuni anni. Un giorno, Bàrnabo incontra il suo amico Bertòn, che gli consiglia di tornare. Bàrnabo viene anche a sapere che i briganti hanno nuovamente attaccato. Lanno seguente,  accompagnato da Bertòn, Bàrnabo ritorna; la Polveriera è stata svuotata, munizioni ed esplosivi trasferiti al paese. Bàrnabo accetta di rimanere solo, come unico guardaboschi. I compagni gli promettono di raggiungerlo in occasione di un atteso ritorno dei briganti. Bàrnabo, da solo, attende i briganti, che effettivamente arrivano. Il guardaboschi li prende di mira; ma, ora che non ha più paura e ha la possibilità di rifarsi, sceglie deliberatamente, di non sparare: ormai ha trovato la serenità. I briganti si allontanano per non tornare più, e Bàrnabo resta a vivere in solitudine tra le sue montagne.')
    )


CREATE INDEX books_embedding_diskann_idx ON books USING diskann (dvector vector_cosine_ops)


cmd = """ALTER TABLE books  ADD COLUMN dvector vector(1536)  GENERATED ALWAYS AS ( azure_openai.create_embeddings('text-embedding-ada-002', review)::vector) STORED; """
cur.execute(cmd)

# if diskann is enable replace the following cmd by cmd2 = """CREATE INDEX books_embedding_diskann_idx ON books USING diskann (dvector vector_cosine_ops)"""

cmd2 = """CREATE INDEX indexvector ON books USING hnsw (dvector vector_l2_ops) WITH (m = 16, ef_construction = 64);"""
cur.execute(cmd2)
# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
